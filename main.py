#!/usr/bin/env python3

import sys
from pathlib import Path

from engines.chatgpt import ChatGPTEngine
from engines.copilot import CopilotEngine
from engines.ollama import OllamaEngine
from flows.commit_flow import CommitFlow
from flows.diff_console import diff_console
from flows.diff_processor import diff_processor
from git.client import GitClient


def load_engine():
    engine_name = Path("config/engine.txt").read_text().strip().split("\n")[0].lower()

    if engine_name == "ollama":
        return OllamaEngine()
    if engine_name == "chatgpt":
        return ChatGPTEngine()
    if engine_name == "copilot":
        return CopilotEngine()

    raise RuntimeError(f"알 수 없는 engine: {engine_name}")


def main() -> None:
    extra_args = sys.argv[1:]

    engine = load_engine()
    print(f"🔧 사용 중인 엔진: {engine.name}")

    try:
        git = GitClient()

        flow = CommitFlow(
            engine=engine,
            git=git,
            diff_processor=diff_processor,
            console=diff_console,
        )

        code = flow.run(extra_args)
        sys.exit(code)
    except KeyboardInterrupt:
        print("  ❌ 커밋이 취소되었습니다.")
        sys.exit(0)

    except Exception as e:
        print(f"  ❌ {engine.name} 오류:", file=sys.stderr)
        print(str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
