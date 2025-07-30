from __future__ import annotations
from typing import Dict, Any
from loguru import logger

from envs.android_world_env import AndroidWorldWrapper
from core.messages import ExecutorResult


class ExecutorAgent:
    def __init__(self, env: AndroidWorldWrapper):
        self.env = env
        self.state = self.env.reset()

    def _select_action(self, subgoal: str) -> Dict[str, Any]:
        """
        Uses a simple keyword-based search to find a matching UI element by text and returns a touch action.
        You can improve this with a smarter LLM-based grounding strategy.
        """
        ui_tree = self.state.ui_tree
        candidates = ui_tree.get("nodes", [])
        for node in candidates:
            if "text" in node and node["text"] and node["text"].lower() in subgoal.lower():
                return {
                    "action_type": "touch",
                    "element_id": node.get("id")
                }
        return {"action_type": "noop"}  # fallback if no match

    def execute(self, subgoal: str) -> ExecutorResult:
        try:
            action = self._select_action(subgoal)
            next_state, reward, done, info = self.env.step(action)
            self.state = next_state
            return ExecutorResult(
                success=True,
                observation={"ui_tree": next_state.ui_tree, "reward": reward, "done": done, "info": info},
                action_taken=action,
            )
        except Exception as e:
            logger.exception("Execution error")
            return ExecutorResult(
                success=False,
                observation={"ui_tree": self.state.ui_tree},
                action_taken={},
                error=str(e),
            )