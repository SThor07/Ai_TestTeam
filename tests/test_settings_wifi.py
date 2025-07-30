import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from pathlib import Path
from omegaconf import OmegaConf

from core.llm import LLMConfig
from envs.android_world_env import AndroidWorldWrapper
from agents.planner import PlannerAgent


def test_planner_generates_steps(tmp_path):
    cfg = OmegaConf.load("configs/default.yaml")
    llm_cfg = LLMConfig(model=cfg.llm.model)
    planner = PlannerAgent(llm_cfg)
    output = planner.plan("Test turning Wi-Fi on and off")
    assert len(output.subgoals) > 0