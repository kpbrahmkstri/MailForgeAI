"""
Centralized path management for MailForgeAI.
Supports both local and Hugging Face Spaces deployments.
"""

from pathlib import Path
import os
from typing import Optional


def get_project_root() -> Path:
    """
    Get the project root directory.
    Works for both local and Hugging Face Spaces deployments.
    """
    # Try to find from current file location
    # path_utils.py is at: project_root/src/utils/path_utils.py
    # So we need to go up 3 levels: utils -> src -> project_root
    path = Path(__file__).parent.parent.parent
    
    # Fallback to environment variable if set (useful for containerized deployments)
    if "PROJECT_ROOT" in os.environ:
        return Path(os.environ["PROJECT_ROOT"])
    
    return path


def get_data_dir() -> Path:
    """Get the data directory path."""
    data_dir = get_project_root() / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_config_dir() -> Path:
    """Get the config directory path."""
    config_dir = get_project_root() / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_memory_dir() -> Path:
    """Get the memory/user profiles directory path."""
    memory_dir = get_project_root() / "src" / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    return memory_dir


def get_templates_dir() -> Path:
    """Get the knowledge base templates directory path."""
    templates_dir = get_data_dir() / "kb" / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    return templates_dir


def get_chroma_dir() -> Path:
    """Get the Chroma vector store directory path."""
    chroma_dir = get_data_dir() / "chroma_templates"
    chroma_dir.mkdir(parents=True, exist_ok=True)
    return chroma_dir


def get_user_profiles_path() -> Path:
    """Get the user profiles JSON file path."""
    return get_memory_dir() / "user_profiles.json"


def get_tone_samples_dir() -> Path:
    """Get the tone samples directory path."""
    tone_dir = get_data_dir() / "tone_samples"
    tone_dir.mkdir(parents=True, exist_ok=True)
    return tone_dir


def get_output_dir() -> Path:
    """Get the output directory for diagrams and reports."""
    output_dir = get_project_root() / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


# Dictionary for convenient access
PATHS = {
    "project_root": get_project_root(),
    "data": get_data_dir(),
    "config": get_config_dir(),
    "memory": get_memory_dir(),
    "templates": get_templates_dir(),
    "chroma": get_chroma_dir(),
    "user_profiles": get_user_profiles_path(),
    "tone_samples": get_tone_samples_dir(),
    "output": get_output_dir(),
}
