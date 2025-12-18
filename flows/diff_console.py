from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import yaml

from flows.dtos import DiffFiles
from utils import PROJECT_ROOT

__all__ = [
    "DiffConsole",
]


@dataclass(frozen=True)
class IconEntry:
    icon: str
    color: Optional[str] = None


@dataclass(frozen=True)
class IconsConfig:
    default: IconEntry
    extensions: Dict[str, IconEntry]
    filenames: Dict[str, IconEntry]


class DiffConsole:
    """
    DiffFiles를 콘솔에 출력하는 클래스

    - emoji.yaml / nerd.yaml 포맷 모두 지원
    - 파일 포함/제외 목록 출력
    - 선택된 커밋 메시지 출력
    """

    EMOJI_PATH = PROJECT_ROOT / "icons/emoji.yaml"
    NERD_PATH = PROJECT_ROOT / "icons/nerd.yaml"

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

    def __init__(self, icons: str | None = None) -> None:
        self.icon_path = self.EMOJI_PATH
        if icons == "nerd":
            self.icon_path = self.NERD_PATH

    def _load_icons(self) -> IconsConfig:
        path = Path(self.icon_path)

        if not path.exists():
            return IconsConfig(
                default=IconEntry("📄"),
                extensions={},
                filenames={},
            )

        with path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

        return IconsConfig(
            default=self._normalize_entry(raw.get("default", "📄")),
            extensions={
                k: self._normalize_entry(v)
                for k, v in raw.get("extensions", {}).items()
            },
            filenames={
                k: self._normalize_entry(v) for k, v in raw.get("filenames", {}).items()
            },
        )

    def _normalize_entry(self, value: dict | str) -> IconEntry:
        """
        emoji.yaml (string) / nerd.yaml (dict) 를
        내부 표준 IconEntry 로 변환
        """
        if isinstance(value, dict):
            return IconEntry(
                icon=value.get("icon", ""),
                color=value.get("color"),
            )

        if isinstance(value, str):
            return IconEntry(icon=value)

        return IconEntry(icon="")

    def _render_icon(
        self,
        icons: IconsConfig,
        file_path: str,
    ) -> str:
        filename = file_path.replace("\\", "/").split("/")[-1]
        suffix = Path(file_path).suffix

        entry = (
            icons.filenames.get(filename)
            or icons.extensions.get(suffix)
            or icons.default
        )

        parts: list[str] = []

        if entry.color:
            parts.append(self.COLORS.get(entry.color, ""))

        parts.append(entry.icon)
        parts.append(self.COLORS["reset"])

        return "".join(parts)

    # ---------- public ----------
    def print_diff_files(self, files: DiffFiles) -> None:
        icons = self._load_icons()
        gray = self.COLORS["gray"]
        reset = self.COLORS["reset"]

        print()
        print("🤖 LLM 입력에 포함됨")

        if not files.included:
            print("  (없음)")
        else:
            for f in files.included:
                icon = self._render_icon(icons, f)
                print(f"  {icon} {f}")

        if files.excluded:
            print()
            print("🚫 LLM 입력에서 제외됨")
            for f in files.excluded:
                icon = self._render_icon(icons, f)
                print(f"  {icon} {gray}{f}{reset}")  # 파일명 dim 처리

        print()

    def print_selected_message(self, message: str) -> None:
        print()
        print("선택된 커밋 메시지:")
        print(f"  {message}")
        print()
