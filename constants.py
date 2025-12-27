from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


class Constants:
    class Paths:
        EMOJI_PATH = PROJECT_ROOT / "icons/emoji.yaml"
        NERD_PATH = PROJECT_ROOT / "icons/nerd.yaml"
        PROMPT_PATH = PROJECT_ROOT / "prompts/commit_message.md"

    MAX_DIFF_CHARS = 12000
    COLORS = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "gray": "\033[90m",
        "reset": "\033[0m",
    }

    class ExcludeRules:
        FILES = {
            ".gitignore",
            "poetry.lock",
            "Pipfile.lock",
            "package-lock.json",
            "yarn.lock",
        }
        SUFFIXES = {".lock", ".min.js", ".map"}
        DIRS = {"node_modules/", "dist/", "build/", ".venv/", "__pycache__/"}
