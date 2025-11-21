from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, fields
from typing import Any, Dict, List, Mapping, Optional, Tuple

from PySide6.QtCore import QSettings

from models.path_model import Path
from utils.project_io import create_example_paths, deserialize_path, serialize_path


@dataclass
class ProjectConfig:
    robot_length_meters: float = 0.5
    robot_width_meters: float = 0.5
    default_max_velocity_meters_per_sec: float = 4.5
    default_max_acceleration_meters_per_sec2: float = 7.0
    default_intermediate_handoff_radius_meters: float = 0.2
    default_max_velocity_deg_per_sec: float = 720.0
    default_max_acceleration_deg_per_sec2: float = 1500.0
    default_end_translation_tolerance_meters: float = 0.03
    default_end_rotation_tolerance_deg: float = 2.0

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> "ProjectConfig":
        cfg = cls()
        if data:
            cfg.update_from_mapping(data)
        return cfg

    def update_from_mapping(self, data: Mapping[str, Any]) -> None:
        for field in fields(self):
            if field.name not in data:
                continue
            value = data[field.name]
            if value is None:
                continue
            try:
                setattr(self, field.name, float(value))
            except (TypeError, ValueError):
                continue

    def to_dict(self) -> Dict[str, float]:
        raw = asdict(self)
        return {k: float(v) for k, v in raw.items()}

    def get_default_optional_value(self, key: str) -> Optional[float]:
        # Prefer default_* keys but fall back to raw key to handle legacy lookups
        default_key = f"default_{key}"
        if hasattr(self, default_key):
            return float(getattr(self, default_key))
        if hasattr(self, key):
            return float(getattr(self, key))
        return None


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


class ProjectManager:
    """Handles project directory, config.json, and path JSON load/save.

    Persists last project dir and last opened path via QSettings.
    """

    SETTINGS_ORG = "FRC-PTP-GUI"
    SETTINGS_APP = "FRC-PTP-GUI"
    KEY_LAST_PROJECT_DIR = "project/last_project_dir"
    KEY_LAST_PATH_FILE = "project/last_path_file"
    KEY_RECENT_PROJECTS = "project/recent_projects"

    def __init__(self):
        self.settings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)
        self.project_dir: Optional[str] = None
        self.config = ProjectConfig()
        self.current_path_file: Optional[str] = None  # filename like "example.json"

    # --------------- Project directory ---------------
    def _is_frc_repo_root(self, directory: str) -> bool:
        """Check if the directory appears to be an FRC repository root (contains src/main/deploy/)."""
        deploy_path = os.path.join(directory, "src", "main", "deploy")
        return os.path.isdir(deploy_path)

    def _get_effective_project_dir(self, selected_dir: str) -> str:
        """Get the effective project directory, handling FRC repo structure automatically."""
        selected_dir = os.path.abspath(selected_dir)

        # If this is already an autos directory, use it directly
        if os.path.basename(selected_dir) == "autos":
            return selected_dir

        # Check if selected directory is an FRC repo root
        if self._is_frc_repo_root(selected_dir):
            autos_dir = os.path.join(selected_dir, "src", "main", "deploy", "autos")
            return autos_dir

        # For non-FRC directories, use as-is
        return selected_dir

    def set_project_dir(self, directory: str) -> None:
        directory = os.path.abspath(directory)
        effective_dir = self._get_effective_project_dir(directory)
        self.project_dir = effective_dir
        self.settings.setValue(
            self.KEY_LAST_PROJECT_DIR, directory
        )  # Store original selected dir for UI
        self.ensure_project_structure()
        # Track recents only after ensuring structure exists
        self._add_recent_project(effective_dir)
        self.load_config()

    def get_paths_dir(self) -> Optional[str]:
        if not self.project_dir:
            return None
        return os.path.join(self.project_dir, "paths")

    def ensure_project_structure(self) -> None:
        if not self.project_dir:
            return
        _ensure_dir(self.project_dir)
        paths_dir = os.path.join(self.project_dir, "paths")
        _ensure_dir(paths_dir)
        # Create default config if missing
        cfg_path = os.path.join(self.project_dir, "config.json")
        if not os.path.exists(cfg_path):
            self.save_config()
        # Create example files if paths folder empty
        try:
            if not os.listdir(paths_dir):
                create_example_paths(paths_dir)
        except Exception:
            pass

    def has_valid_project(self) -> bool:
        if not self.project_dir:
            return False
        cfg = os.path.join(self.project_dir, "config.json")
        paths = os.path.join(self.project_dir, "paths")
        return os.path.isdir(self.project_dir) and os.path.isfile(cfg) and os.path.isdir(paths)

    def load_last_project(self) -> bool:
        last_dir = self.settings.value(self.KEY_LAST_PROJECT_DIR, type=str)
        if not last_dir:
            return False

        # Get the effective project directory (handles FRC repo redirection)
        effective_dir = self._get_effective_project_dir(last_dir)

        # Validate without creating any files. Only accept if already valid.
        cfg = os.path.join(effective_dir, "config.json")
        paths = os.path.join(effective_dir, "paths")
        if os.path.isdir(effective_dir) and os.path.isfile(cfg) and os.path.isdir(paths):
            # Use the original last_dir to maintain the same behavior for set_project_dir
            self.set_project_dir(last_dir)
            return True
        return False

    # --------------- Recent Projects ---------------
    def recent_projects(self) -> List[str]:
        raw = self.settings.value(self.KEY_RECENT_PROJECTS)
        if not raw:
            return []
        # QSettings may return list or str
        if isinstance(raw, list):
            items = [str(x) for x in raw]
        else:
            try:
                items = json.loads(str(raw))
                if not isinstance(items, list):
                    items = []
            except Exception:
                items = []
        # Filter only existing dirs, and resolve FRC repo paths to their effective directories
        filtered_items = []
        for p in items:
            if isinstance(p, str) and os.path.isdir(p):
                effective_dir = self._get_effective_project_dir(p)
                if os.path.isdir(effective_dir):
                    filtered_items.append(effective_dir)
        # unique while preserving order
        seen = set()
        uniq = []
        for p in filtered_items:
            if p not in seen:
                seen.add(p)
                uniq.append(p)
        return uniq[:10]

    def _add_recent_project(self, directory: str) -> None:
        if not directory:
            return
        items = self.recent_projects()
        # move to front
        items = [d for d in items if d != directory]
        items.insert(0, directory)
        items = items[:10]
        # Store as JSON string to be robust
        try:
            self.settings.setValue(self.KEY_RECENT_PROJECTS, json.dumps(items))
        except Exception:
            pass

    # --------------- Config ---------------
    def load_config(self) -> ProjectConfig:
        if not self.project_dir:
            return self.config
        cfg_path = os.path.join(self.project_dir, "config.json")
        try:
            if os.path.exists(cfg_path):
                with open(cfg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self.config = ProjectConfig.from_mapping(data)
        except Exception:
            # Keep existing config on error
            pass
        return self.config

    def save_config(self, new_config: Optional[Mapping[str, Any]] = None) -> None:
        if new_config is not None:
            self.config.update_from_mapping(new_config)
        if not self.project_dir:
            return
        cfg_path = os.path.join(self.project_dir, "config.json")
        try:
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(self.config.to_dict(), f, indent=2)
        except Exception:
            pass

    def get_default_optional_value(self, key: str) -> Optional[float]:
        return self.config.get_default_optional_value(key)

    def config_as_dict(self) -> Dict[str, float]:
        return self.config.to_dict()

    # --------------- Paths listing ---------------
    def list_paths(self) -> List[str]:
        paths_dir = self.get_paths_dir()
        if not paths_dir or not os.path.isdir(paths_dir):
            return []
        files = [f for f in os.listdir(paths_dir) if f.lower().endswith(".json")]
        files.sort()
        return files

    # --------------- Path IO ---------------
    def load_path(self, filename: str) -> Optional[Path]:
        """Load a path from the paths directory by filename (e.g., 'my_path.json')."""
        paths_dir = self.get_paths_dir()
        if not self.project_dir or not paths_dir:
            return None
        filepath = os.path.join(paths_dir, filename)
        if not os.path.isfile(filepath):
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            path = deserialize_path(data, self.get_default_optional_value)
            self.current_path_file = filename
            # Remember in settings
            self.settings.setValue(self.KEY_LAST_PATH_FILE, filename)
            return path
        except Exception:
            return None

    def save_path(self, path: Path, filename: Optional[str] = None) -> Optional[str]:
        """Save path to filename in the paths dir. If filename is None, uses current_path_file
        or creates 'untitled.json'. Returns the filename used on success.
        """
        if filename is None:
            filename = self.current_path_file
        if filename is None:
            filename = "untitled.json"
        paths_dir = self.get_paths_dir()
        if not self.project_dir or not paths_dir:
            return None
        _ensure_dir(paths_dir)
        filepath = os.path.join(paths_dir, filename)
        try:
            serialized = serialize_path(path)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(serialized, f, indent=2)
            self.current_path_file = filename
            self.settings.setValue(self.KEY_LAST_PATH_FILE, filename)
            return filename
        except Exception:
            return None

    def delete_path(self, filename: str) -> bool:
        """Delete a path file from the paths directory. Returns True if successful."""
        paths_dir = self.get_paths_dir()
        if not self.project_dir or not paths_dir:
            return False
        filepath = os.path.join(paths_dir, filename)
        if not os.path.isfile(filepath):
            return False
        try:
            os.remove(filepath)
            # If this was the current path, clear it
            if self.current_path_file == filename:
                self.current_path_file = None
                self.settings.remove(self.KEY_LAST_PATH_FILE)
            return True
        except Exception:
            return False

    def load_last_or_first_or_create(self) -> Tuple[Path, str]:
        """Attempt to load last path (from settings). If unavailable, load first available
        path in directory. If none exist, create 'untitled.json' empty path and return it.
        Returns (Path, filename).
        """
        # Try last used
        last_file = self.settings.value(self.KEY_LAST_PATH_FILE, type=str)
        if last_file:
            p = self.load_path(last_file)
            if p is not None:
                return p, last_file
        # Try first available
        files = self.list_paths()
        if files:
            first = files[0]
            p = self.load_path(first)
            if p is not None:
                return p, first
        # Create a new empty path
        new_path = Path()
        used = self.save_path(new_path, "untitled.json")
        if used is None:
            used = "untitled.json"
        return new_path, used
