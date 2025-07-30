from __future__ import annotations
from typing import Dict, Any
from core.llm import OllamaLLM, ChatMessage, LLMConfig
from core.messages import Verification, ExecutorResult
from loguru import logger

SYSTEM_PROMPT = (
    "You are a Verifier Agent for Android QA. Compare expected vs current UI state. "
    "Return ONLY a valid JSON object like this:\n"
    "{\"passed\": true, \"reason\": \"...\"}\n"
    "Always include a short but clear explanation of the decision in the 'reason'."
)


class VerifierAgent:
    def __init__(self, llm_cfg: LLMConfig):
        self.llm = OllamaLLM(llm_cfg)

    def verify(self, goal: str, subgoal: str, exec_result: ExecutorResult) -> Verification:
        prompt = (
            f"High-level goal: {goal}\n"
            f"Subgoal: {subgoal}\n"
            f"Executor success: {exec_result.success}, error: {exec_result.error}\n"
            f"Current ui_tree (partial): {str(exec_result.observation.get('ui_tree', {}) )[:5000]}\n"
            "Return ONLY valid JSON object: {\"passed\": bool, \"reason\": str}"
        )

        content = self.llm.chat([
            ChatMessage(role="system", content=SYSTEM_PROMPT),
            ChatMessage(role="user", content=prompt),
        ])

        logger.debug(f"Verifier raw LLM response: {content}")

        import json, re
        m = re.search(r"\{[\s\S]*?\}", content.strip())
        if not m:
            logger.error("Verifier response does not contain a JSON object")
            return Verification(passed=False, reason="non-json response")

        json_str = m.group(0)

        try:
            data = json.loads(json_str)
            return Verification(**data)
        except Exception as e:
            logger.exception(f"JSON parse error in Verifier: {e}\nExtracted: {json_str}")
            return Verification(passed=False, reason="json parse error")
