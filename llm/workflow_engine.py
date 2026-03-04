import logging
import time
from typing import Dict, List, Callable, Any, Optional

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """
    Execute multi-step workflows with status callbacks and error handling
    """

    def __init__(self, action_executor: Callable[[Dict], tuple[bool, str]]):
        """
        Initialize workflow engine

        Args:
            action_executor: Function that executes a single action
                            Should return (success: bool, message: str)
        """
        self._action_executor = action_executor
        self._status_callback: Optional[Callable[[str, int, int], None]] = None
        self._step_callback: Optional[Callable[[int, str, bool, str], None]] = None

    def set_status_callback(self, callback: Callable[[str, int, int], None]):
        """
        Set callback for overall workflow status updates

        Args:
            callback: Function(message, current_step, total_steps)
        """
        self._status_callback = callback

    def set_step_callback(self, callback: Callable[[int, str, bool, str], None]):
        """
        Set callback for individual step completion

        Args:
            callback: Function(step_index, status, success, message)
        """
        self._step_callback = callback

    def execute_workflow(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute a multi-step workflow

        Args:
            steps: List of action dictionaries to execute in order

        Returns:
            Dict with workflow execution results:
            {
                "success": bool,
                "completed_steps": int,
                "total_steps": int,
                "results": List[Dict],
                "message": str
            }
        """
        if not steps:
            return {
                "success": False,
                "completed_steps": 0,
                "total_steps": 0,
                "results": [],
                "message": "No steps to execute",
            }

        total_steps = len(steps)
        results = []
        completed_steps = 0

        logger.info(f"Starting workflow execution: {total_steps} steps")

        for i, step in enumerate(steps):
            step_num = i + 1
            action_name = step.get("action", "unknown")

            # Notify status
            if self._status_callback:
                self._status_callback(
                    f"Executing step {step_num}/{total_steps}: {action_name}",
                    step_num,
                    total_steps,
                )

            logger.info(f"Step {step_num}/{total_steps}: {step}")

            try:
                # Execute the action
                success, message = self._action_executor(step)

                result = {
                    "step_index": i,
                    "action": step,
                    "success": success,
                    "message": message,
                }
                results.append(result)

                # Notify step completion
                if self._step_callback:
                    self._step_callback(i, action_name, success, message)

                if success:
                    completed_steps += 1
                    logger.info(f"Step {step_num} succeeded: {message}")

                    # Brief pause between steps for stability
                    if i < total_steps - 1:  # Don't pause after last step
                        time.sleep(0.3)
                else:
                    # Step failed - decide whether to continue or abort
                    logger.warning(f"Step {step_num} failed: {message}")

                    # For now, abort on first failure
                    # Future: could add retry logic or continue-on-error option
                    return {
                        "success": False,
                        "completed_steps": completed_steps,
                        "total_steps": total_steps,
                        "results": results,
                        "message": f"Workflow failed at step {step_num}: {message}",
                    }

            except Exception as e:
                logger.error(f"Step {step_num} error: {e}")

                result = {
                    "step_index": i,
                    "action": step,
                    "success": False,
                    "message": f"Exception: {str(e)}",
                }
                results.append(result)

                if self._step_callback:
                    self._step_callback(i, action_name, False, f"Exception: {e}")

                return {
                    "success": False,
                    "completed_steps": completed_steps,
                    "total_steps": total_steps,
                    "results": results,
                    "message": f"Workflow error at step {step_num}: {e}",
                }

        # All steps completed successfully
        return {
            "success": True,
            "completed_steps": completed_steps,
            "total_steps": total_steps,
            "results": results,
            "message": f"Workflow completed: {completed_steps}/{total_steps} steps successful",
        }

    def execute_with_retry(
        self, steps: List[Dict[str, Any]], max_retries: int = 1
    ) -> Dict[str, Any]:
        """
        Execute workflow with retry on failure

        Args:
            steps: List of action dictionaries
            max_retries: Number of retry attempts per failed step

        Returns:
            Workflow execution results
        """
        # TODO: Implement retry logic for failed steps
        # For now, just use standard execution
        return self.execute_workflow(steps)
