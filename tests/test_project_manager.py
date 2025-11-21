from __future__ import annotations

from pathlib import Path

from models.path_model import Path as PathModel, TranslationTarget
from utils.project_manager import ProjectConfig, ProjectManager


class DummySettings:
    def __init__(self):
        self._store: dict[str, str] = {}

    def setValue(self, key: str, value):
        self._store[key] = value

    def value(self, key: str, type=None):
        return self._store.get(key)

    def remove(self, key: str):
        self._store.pop(key, None)


def test_project_config_updates():
    cfg = ProjectConfig()
    cfg.update_from_mapping({"robot_length_meters": 0.75})
    assert cfg.robot_length_meters == 0.75
    assert (
        cfg.get_default_optional_value("max_velocity_meters_per_sec")
        == cfg.default_max_velocity_meters_per_sec
    )


def test_project_manager_saves_and_loads_paths(tmp_path: Path):
    pm = ProjectManager()
    pm.settings = DummySettings()
    pm.set_project_dir(str(tmp_path))

    path = PathModel()
    path.path_elements.append(TranslationTarget(x_meters=1.0, y_meters=2.0))
    saved_name = pm.save_path(path, "unit_test.json")
    assert saved_name == "unit_test.json"

    loaded = pm.load_path("unit_test.json")
    assert loaded is not None
    assert len(loaded.path_elements) == 1
