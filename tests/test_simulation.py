from __future__ import annotations

from models.path_model import Path, TranslationTarget
from models.simulation import simulate_path


def test_simulate_path_generates_trail():
    path = Path()
    path.path_elements.append(TranslationTarget(x_meters=0.0, y_meters=0.0))
    path.path_elements.append(TranslationTarget(x_meters=3.0, y_meters=1.0))

    config = {
        "default_max_velocity_meters_per_sec": 2.0,
        "default_max_acceleration_meters_per_sec2": 4.0,
        "default_max_velocity_deg_per_sec": 90.0,
        "default_max_acceleration_deg_per_sec2": 180.0,
    }

    result = simulate_path(path, config, dt_s=0.01)

    assert result.total_time_s > 0.0
    assert result.trail_points
    assert 0.0 in result.poses_by_time
