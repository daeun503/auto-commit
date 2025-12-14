from pathlib import Path
from typing import Any, Dict

import yaml

from flows.dtos import DiffFiles

__all__ = [
    "DiffConsole",
    "diff_console",
]


class DiffConsole:
    """
    DiffFiles를 콘솔에 출력하는 클래스
    - 아이콘 매핑(YAML) 로드
    - 포함/제외 목록 출력
    - 선택된 메시지 출력 UX
    """

    ICON_PATH = "config/file_icons.yaml"

    def _load_icons(self) -> Dict[str, Any]:
        path = Path(self.ICON_PATH)
        if not path.exists():
            return {"extensions": {}, "filenames": {}, "default": "📄"}

        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        data.setdefault("extensions", {})
        data.setdefault("filenames", {})
        data.setdefault("default", "📄")
        return data

    def _get_icon(self, icons: Dict[str, Any], file_path: str) -> str:
        filename = file_path.replace("\\", "/").split("/")[-1]
        suffix = Path(file_path).suffix

        return (
            icons["filenames"].get(filename)
            or icons["extensions"].get(suffix)
            or icons["default"]
        )

    def print_diff_files(self, files: DiffFiles) -> None:
        icons = self._load_icons()

        print()
        print("📦 커밋 대상 파일 (LLM 전달됨)")

        if not files.included:
            print("  (없음)")
        else:
            for f in files.included:
                icon = self._get_icon(icons, f)
                print(f"  {icon} {f}")

        if files.excluded:
            print()
            print("🚫 제외된 파일")
            for f in files.excluded:
                icon = self._get_icon(icons, f)
                print(f"\033[90m  {icon} {f}\033[0m")

        print()

    def print_selected_message(self, message: str) -> None:
        print()
        print("선택된 커밋 메시지:")
        print(f"  ✅ {message}")
        print()


diff_console = DiffConsole()
