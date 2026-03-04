import logging
from typing import Dict, Any, Optional
from config import config
from llm.gemini_processor import GeminiProcessor
from llm.processor import LLMProcessor

logger = logging.getLogger(__name__)


class HybridLLMProcessor:
    """
    Hybrid LLM processor that intelligently switches between Gemini and Ollama

    Priority:
    1. Gemini API (if available and enabled)
    2. Ollama (local fallback)
    3. Error if neither available

    Mode configuration via config.llm_mode:
    - "gemini": Use Gemini only (fail if unavailable)
    - "ollama": Use Ollama only (ignore Gemini)
    - "hybrid": Try Gemini first, fallback to Ollama
    """

    def __init__(self):
        self._gemini = None
        self._ollama = None
        self._active_processor = None
        self._last_used = None

        # Initialize processors based on mode
        self._initialize_processors()

    def _initialize_processors(self):
        """Initialize Gemini and/or Ollama processors based on config"""
        mode = config.llm_mode

        if mode in ("gemini", "hybrid"):
            # Try to initialize Gemini
            try:
                self._gemini = GeminiProcessor()
                if self._gemini.is_available():
                    logger.info("Gemini processor initialized and available")
                else:
                    logger.warning(
                        "Gemini processor initialized but not available (missing API key or error)"
                    )
                    self._gemini = None
            except Exception as e:
                logger.error(f"Failed to initialize Gemini processor: {e}")
                self._gemini = None

        if mode in ("ollama", "hybrid"):
            # Initialize Ollama
            try:
                self._ollama = LLMProcessor()
                logger.info("Ollama processor initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Ollama processor: {e}")
                self._ollama = None

        # Select active processor
        self._select_active_processor()

    def _select_active_processor(self):
        """Select which processor to use based on availability"""
        mode = config.llm_mode

        if mode == "gemini":
            # Gemini-only mode
            if self._gemini and self._gemini.is_available():
                self._active_processor = self._gemini
                self._last_used = "gemini"
                logger.info("Active processor: Gemini (gemini-only mode)")
            else:
                self._active_processor = None
                self._last_used = None
                logger.error("Gemini not available in gemini-only mode")

        elif mode == "ollama":
            # Ollama-only mode
            if self._ollama:
                self._active_processor = self._ollama
                self._last_used = "ollama"
                logger.info("Active processor: Ollama (ollama-only mode)")
            else:
                self._active_processor = None
                self._last_used = None
                logger.error("Ollama not available in ollama-only mode")

        elif mode == "hybrid":
            # Hybrid mode - prefer Gemini, fallback to Ollama
            if self._gemini and self._gemini.is_available():
                self._active_processor = self._gemini
                self._last_used = "gemini"
                logger.info("Active processor: Gemini (hybrid mode, Gemini preferred)")
            elif self._ollama:
                self._active_processor = self._ollama
                self._last_used = "ollama"
                logger.info(
                    "Active processor: Ollama (hybrid mode, Gemini unavailable)"
                )
            else:
                self._active_processor = None
                self._last_used = None
                logger.error("No LLM processor available in hybrid mode")

        else:
            logger.error(
                f"Unknown llm_mode: {mode}. Use 'gemini', 'ollama', or 'hybrid'"
            )
            self._active_processor = None
            self._last_used = None

    def process_command(self, command_text: str) -> Dict[str, Any]:
        """
        Process a voice command using the active LLM processor

        Args:
            command_text: The voice command text

        Returns:
            Dict with action or workflow, or error if no processor available
        """
        if not self._active_processor:
            return {
                "action": "error",
                "message": "No LLM processor available. Check Gemini API key or Ollama connection.",
            }

        # Try active processor
        try:
            result = self._active_processor.process_command(command_text)

            # Check if result is an error
            if result.get("action") == "error":
                # If using Gemini and fallback is enabled, try Ollama
                if (
                    self._last_used == "gemini"
                    and config.gemini_fallback_enabled
                    and self._ollama
                ):
                    logger.warning(
                        f"Gemini error: {result.get('message')}. Falling back to Ollama."
                    )
                    return self._fallback_to_ollama(command_text)

            return result

        except Exception as e:
            logger.error(f"LLM processor error: {e}")

            # Try fallback if available
            if (
                self._last_used == "gemini"
                and config.gemini_fallback_enabled
                and self._ollama
            ):
                logger.warning(f"Gemini exception: {e}. Falling back to Ollama.")
                return self._fallback_to_ollama(command_text)

            return {"action": "error", "message": f"LLM processing error: {str(e)}"}

    def _fallback_to_ollama(self, command_text: str) -> Dict[str, Any]:
        """
        Fallback to Ollama when Gemini fails

        Args:
            command_text: The voice command text

        Returns:
            Result from Ollama processor
        """
        if not self._ollama:
            return {
                "action": "error",
                "message": "Gemini failed and Ollama not available",
            }

        try:
            logger.info("Using Ollama fallback")
            result = self._ollama.process_command(command_text)

            # Mark that we used fallback (for UI notification)
            if "metadata" not in result:
                result["metadata"] = {}
            result["metadata"]["used_fallback"] = True
            result["metadata"]["fallback_from"] = "gemini"
            result["metadata"]["fallback_to"] = "ollama"

            return result

        except Exception as e:
            logger.error(f"Ollama fallback also failed: {e}")
            return {
                "action": "error",
                "message": f"Both Gemini and Ollama failed: {str(e)}",
            }

    def get_status(self) -> Dict[str, Any]:
        """
        Get status of all LLM processors

        Returns:
            Dict with status information
        """
        return {
            "mode": config.llm_mode,
            "active_processor": self._last_used,
            "gemini_available": self._gemini.is_available() if self._gemini else False,
            "ollama_available": self._ollama is not None,
            "fallback_enabled": config.gemini_fallback_enabled,
        }

    def check_connection(self) -> tuple[bool, str]:
        """
        Check connection to active LLM processor

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self._active_processor:
            return False, "No LLM processor available"

        # For Gemini processor
        if self._last_used == "gemini" and self._gemini:
            return self._gemini.test_connection()

        # For Ollama processor
        if self._last_used == "ollama" and self._ollama:
            connected, has_model, models = self._ollama.check_connection()
            if not connected:
                return False, f"Cannot connect to Ollama at {config.ollama_url}"
            if not has_model:
                return (
                    False,
                    f"Model '{config.ollama_model}' not found. Available: {models}",
                )
            return True, f"Connected to Ollama ({config.ollama_model})"

        return False, "Unknown processor state"

    def clear_history(self):
        """Clear conversation history for all processors"""
        if self._gemini:
            self._gemini.clear_history()
        if self._ollama:
            self._ollama.clear_history()
        logger.info("Cleared conversation history for all processors")

    def switch_mode(self, mode: str) -> bool:
        """
        Switch LLM mode dynamically

        Args:
            mode: "gemini", "ollama", or "hybrid"

        Returns:
            True if switch successful, False otherwise
        """
        if mode not in ("gemini", "ollama", "hybrid"):
            logger.error(f"Invalid mode: {mode}")
            return False

        config.set("llm_mode", mode)
        self._select_active_processor()
        logger.info(f"Switched to {mode} mode")
        return True
