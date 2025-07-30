from __future__ import annotations
from pydantic import BaseModel
from typing import Any, Dict, List


class PlannerOutput(BaseModel):
    subgoals: List[Dict[str, str]]
    reasoning: str


class ExecutorResult(BaseModel):
    success: bool
    observation: Dict[str, Any]
    action_taken: Dict[str, Any]
    error: str | None = None


class Verification(BaseModel):
    passed: bool
    reason: str
    expected_state: Dict[str, Any] | None = None


class EpisodeLog(BaseModel):
    planner_goal: str
    steps: List[Dict[str, Any]]
    final_verdict: str