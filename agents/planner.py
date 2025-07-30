from __future__ import annotations
from typing import List, Dict, Any
from loguru import logger

from core.llm import OllamaLLM, ChatMessage, LLMConfig
from core.messages import PlannerOutput


SYSTEM_PROMPT = (
    "You are a Planner Agent for Android QA automation. "
    "Your job is to take a high-level goal and break it down into a JSON object with two fields:\n"
    "- `subgoals`: a list of steps, where each step is a dictionary with 'step' and 'reference'.\n"
    "- `reasoning`: a short explanation string.\n\n"
    "⚠️ IMPORTANT:\n"
    "- Only respond with a valid JSON object.\n"
    "- Do not include any extra commentary, markdown, or explanation outside the JSON.\n"
    "- Use double quotes only (\"), not single quotes.\n"
    "- The output must be parseable by `json.loads()` in Python."
)


class PlannerAgent:
    def __init__(self, llm_cfg: LLMConfig):
        self.llm = OllamaLLM(llm_cfg)

    def plan(self, goal: str, task: str | None = None) -> PlannerOutput:
        task_line = f"Task: {task}\n" if task else ""
        prompt = (
            f"{task_line}"
            f"Given this goal: \"{goal}\"\n"
            "Generate a valid JSON object like this:\n"
            "{\n"
            "  \"subgoals\": [\n"
            "    {\"step\": \"<Step description>\", \"reference\": \"<Relevant UI Component or Activity>\"},\n"
            "    {\"step\": \"<Another step>\", \"reference\": \"<Another component>\"}\n"
            "  ],\n"
            "  \"reasoning\": \"Brief reasoning for why these steps achieve the goal.\"\n"
            "}"
        )
        content = self.llm.chat([
            ChatMessage(role="system", content=SYSTEM_PROMPT),
            ChatMessage(role="user", content=prompt),
        ])
        parsed = self._safe_json(content)
        return PlannerOutput.model_validate(parsed)

    def replan(self, goal: str, past_steps: List[Dict[str, Any]], last_error: str, task: str | None = None) -> PlannerOutput:
        task_line = f"Original Task: {task}\n" if task else ""
        prompt = (
                    f"We failed verifying the last step. Error: {last_error}\n"
                    f"Past steps: {past_steps}\n"
                    f"{task_line}"
                    f"Original goal: {goal}\n\n"
                    "Provide a revised JSON object containing only:\n"
                    "- `subgoals`: list of remaining steps (as dicts with 'step' and 'reference')\n"
                    "- `reasoning`: a string\n\n"
                    "⚠️ No commentary or extra text. Strict JSON only."
                )
        content = self.llm.chat([
            ChatMessage(role="system", content=SYSTEM_PROMPT),
            ChatMessage(role="user", content=prompt),
        ])
        parsed = self._safe_json(content)
        return PlannerOutput.model_validate(parsed)

    @staticmethod
    def _safe_json(txt: str) -> Dict[str, Any]:
        import json, re
        match = re.search(r"\{[\s\S]*\}", txt)
        if not match:
            logger.error(f"Planner returned non-JSON: {txt}")
            return {"subgoals": [], "reasoning": "invalid"}
        json_text = match.group(0)
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            # Try to fix common issues
            try:
                cleaned = json_text.replace("'", '"')  # crude but often effective
                return json.loads(cleaned)
            except Exception as e:
                logger.exception("JSON parse error (even after quote fix)")
                return {"subgoals": [], "reasoning": f"parse_error: {e}"}
