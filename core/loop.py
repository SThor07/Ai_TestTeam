from __future__ import annotations
from typing import List
from loguru import logger

from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.verifier import VerifierAgent
from agents.supervisor import SupervisorAgent
from core.messages import EpisodeLog


class QALoop:
    def __init__(self, planner: PlannerAgent, executor: ExecutorAgent,
                 verifier: VerifierAgent, supervisor: SupervisorAgent | None = None):
        self.planner = planner
        self.executor = executor
        self.verifier = verifier
        self.supervisor = supervisor

    def run(self, high_level_goal: str, high_level_task: str) -> EpisodeLog:
        logger.info(f"Received goal: {high_level_goal}")
        plan = self.planner.plan(high_level_goal, high_level_task)
        logger.info(f"Initial plan: {plan.subgoals}")

        step_logs = []
        max_replans = 2
        replans = 0

        for idx, subgoal in enumerate(plan.subgoals):
            logger.info(f"[Step {idx}] Subgoal: {subgoal}")
            result = self.executor.execute(subgoal)
            logger.info(f"Executor result: success={result.success}, obs_keys={list(result.observation.keys())}")

            verification = self.verifier.verify(
                goal=high_level_goal,
                subgoal=subgoal,
                exec_result=result,
            )
            logger.info(f"Verifier: passed={verification.passed} reason={verification.reason}")

            step_logs.append({
                "subgoal": subgoal,
                "executor": result.model_dump(),
                "verifier": verification.model_dump(),
            })

            if not verification.passed:
                logger.warning(f"Verification failed for subgoal {idx}: {subgoal} → reason: {verification.reason}")
                # dynamic replanning
                if replans >= max_replans:
                    logger.error("Too many replans. Aborting.")
                    break

                replans += 1
                plan = self.planner.replan(
                    high_level_goal,
                    past_steps=step_logs,
                    last_error=verification.reason,
                    task=high_level_task
                )
                logger.info(f"New plan: {plan.subgoals}")


        final_verdict = "passed" if all(s["verifier"]["passed"] for s in step_logs) else "failed"

        ep_log = EpisodeLog(
            planner_goal=high_level_goal,
            steps=step_logs,
            final_verdict=final_verdict,
        )

        if self.supervisor:
            self.supervisor.review(ep_log)

        return ep_log