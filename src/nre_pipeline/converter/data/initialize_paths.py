import os
from pathlib import Path
from typing import Optional, Tuple
from loguru import logger
from datetime import datetime

from ...common.env_vars import EnvValues


CONFIG_DIR_NAME = "config"
LOOKUP_DIR_NAME = "lookup"


def verify_project_name(func):
    def wrapper(project_name, *args, **kwargs):
        if project_name is None:
            project_name = EnvValues.get_project_name()
        if len(project_name) < 3:
            logger.warning(
                "Project name must be at least 3 characters long; adding unique suffix"
            )
            project_name += f"_{datetime.now().strftime('%m_%d_%Y__%H_%M_%S')}"
        return func(project_name, *args, **kwargs)

    return wrapper


def initialize_csv_to_lookup_root():
    csv_to_lookup_root = Path("/output/csv_to_dict_lookup")
    csv_to_lookup_root.mkdir(parents=True, exist_ok=True)
    return csv_to_lookup_root


@verify_project_name
def get_project_config_output_path(project_name: str) -> Path:
    config_output_path: Path = (
        initialize_csv_to_lookup_root() / CONFIG_DIR_NAME / project_name
    )
    config_output_path.mkdir(parents=True, exist_ok=True)
    return config_output_path


@verify_project_name
def get_project_lookup_output_path(project_name: Optional[str] = None) -> Path:
    assert project_name is not None
    lookup_output_path: Path = (
        initialize_csv_to_lookup_root() / LOOKUP_DIR_NAME / project_name
    )
    lookup_output_path.mkdir(parents=True, exist_ok=True)
    return lookup_output_path


@verify_project_name
def get_project_paths(project_name: str) -> Tuple[Path, Path]:
    config_output_path: Path = get_project_config_output_path(project_name)
    lookup_output_path: Path = get_project_lookup_output_path(project_name)
    return config_output_path, lookup_output_path
