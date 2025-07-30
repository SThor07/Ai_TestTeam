from __future__ import annotations
from typing import List, Dict, Any
from dataclasses import dataclass
from pydantic import BaseModel
import ollama


class ChatMessage(BaseModel):
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMConfig:
    model: str = "llama3.2:latest"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.2
    max_tokens: int = 512


class OllamaLLM:
    def __init__(self, cfg: LLMConfig):
        self.cfg = cfg

    def chat(self, messages: List[ChatMessage]) -> str:
        # ollama python client auto-detects local server; base_url can be exported via OLLAMA_HOST
        response = ollama.chat(
            model=self.cfg.model,
            messages=[m.model_dump() for m in messages],
            options={
                "temperature": self.cfg.temperature,
            },
        )
        return response["message"]["content"]