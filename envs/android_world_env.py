from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict
from android_env import loader
from android_env.loader import load
from omegaconf import OmegaConf
import dm_env

from android_env.environment import AndroidEnv
from android_env.components.simulators.fake.fake_simulator import FakeSimulator
from android_env.components.coordinator import Coordinator
from android_env.components.task_manager import TaskManager
from android_env.components.device_settings import DeviceSettings
from android_env.proto.task_pb2 import Task

def ensure_android_env(task_name: str, fs_config):
    simulator = FakeSimulator(fs_config)
    task_manager = TaskManager(Task(name = task_name))
    device_settings = DeviceSettings(simulator)
    coordinator = Coordinator(simulator, task_manager, device_settings)
    return AndroidEnv(simulator, coordinator, task_manager)


@dataclass
class AndroidState:
    ui_tree: Dict[str, Any]
    screenshot_path: str | None = None


class AndroidWorldWrapper:
    def __init__(self, task_name: str, trace_dir: str, fs_config, render_rgb: bool = True):
        self.env = ensure_android_env(task_name, fs_config)
        self.trace_dir = trace_dir
        self.render_rgb = render_rgb
        self._frame_id = 0
        self._latest_obs = None  # cache the latest observation

    def reset(self) -> AndroidState:
        timestep = self.env.reset()
        self._latest_obs = timestep.observation
        return self._obs_to_state(self._latest_obs)

    def step(self, action: Dict[str, Any]):
        timestep = self.env.step(action)
        self._latest_obs = timestep.observation
        reward = timestep.reward
        done = timestep.last()
        info = {}  # extend as needed
        return self._obs_to_state(self._latest_obs), reward, done, info

    def render(self, path: str | None = None):
        if not self.render_rgb or self._latest_obs is None:
            return None

        frame = self._latest_obs.get("pixels")
        if frame is not None and path is not None:
            import imageio
            imageio.imwrite(path, frame)
        return frame

    def _obs_to_state(self, obs: Dict[str, Any]) -> AndroidState:
        screenshot_path = None
        if self.render_rgb:
            screenshot_path = f"{self.trace_dir}/frame_{self._frame_id:05d}.png"
            self.render(path=screenshot_path)
            self._frame_id += 1
        return AndroidState(ui_tree=obs.get("ui_tree", {}), screenshot_path=screenshot_path)
