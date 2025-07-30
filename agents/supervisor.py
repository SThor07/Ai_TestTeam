from __future__ import annotations
from loguru import logger
from core.llm import OllamaLLM, ChatMessage, LLMConfig
from core.messages import EpisodeLog


SYSTEM_PROMPT = (
    "You are a Supervisor Agent. You read full QA logs and recommend improvements: "
    "better prompts, missing subgoals, robustness to modals, etc."
)


class SupervisorAgent:
    def __init__(self, llm_cfg: LLMConfig, report_dir: str):
        self.llm = OllamaLLM(llm_cfg)
        self.report_dir = report_dir

    def review(self, ep_log: EpisodeLog):
        content = self.llm.chat([
            ChatMessage(role="system", content=SYSTEM_PROMPT),
            ChatMessage(role="user", content=f"Episode Log: {ep_log.model_dump_json(indent=2)}\n"
                                             f"Return a markdown report with sections: prompt improvements, plan flaws, coverage expansion.")
        ])
        path = f"{self.report_dir}/supervisor_report.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Supervisor report written to {path}")