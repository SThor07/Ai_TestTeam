import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import argparse
from loguru import logger
from omegaconf import OmegaConf

from core.loop import QALoop
from core.llm import LLMConfig
from core.messages import EpisodeLog
from envs.android_world_env import AndroidWorldWrapper
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.verifier import VerifierAgent
from agents.supervisor import SupervisorAgent

import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, default=None)
    parser.add_argument("--goal", type=str, default="Test turning Wi-Fi on and off")
    parser.add_argument("--config", type=str, default="configs/default.yaml")
    parser.add_argument("--llm.model", dest="llm_model", type=str, default=None)
    args = parser.parse_args()

    cfg = OmegaConf.load(args.config)

    if args.llm_model is not None:
        cfg.llm.model = args.llm_model
    if args.task is not None:
        cfg.android_world.task = args.task

    logger.info(f"Running with task: {cfg.android_world.task}")

    os.makedirs(cfg.log_dir, exist_ok=True)
    os.makedirs(cfg.trace_dir, exist_ok=True)
    os.makedirs(cfg.report_dir, exist_ok=True)

    llm_cfg = LLMConfig(
        model=cfg.llm.model,
        base_url=cfg.llm.base_url,
        temperature=cfg.llm.temperature,
        max_tokens=cfg.llm.max_tokens,
    )

    env = AndroidWorldWrapper(cfg.android_world.task, trace_dir=cfg.trace_dir, fs_config=cfg.fs_config, render_rgb=cfg.android_world.render_rgb)

    planner = PlannerAgent(llm_cfg)
    executor = ExecutorAgent(env)
    verifier = VerifierAgent(llm_cfg)
    supervisor = SupervisorAgent(llm_cfg, cfg.report_dir) if cfg.supervisor.enabled else None

    loop = QALoop(planner, executor, verifier, supervisor)
    ep_log: EpisodeLog = loop.run(args.goal, cfg.android_world.task)

    out_path = os.path.join(cfg.log_dir, "episode_log.json")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(ep_log.model_dump_json(indent=2))
    logger.info(f"Episode log written to {out_path}")


if __name__ == "__main__":
    main()