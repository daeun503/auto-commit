#!/usr/bin/env python3

import argparse
import sys

from engines.chatgpt import ChatGPTEngine
from engines.copilot import CopilotEngine
from engines.ollama import OllamaEngine
from flows.commit_flow import CommitFlow
from flows.diff_console import DiffConsole
from flows.diff_processor import DiffProcessor, processConfig
from git.client import GitClient


def parse_args(argv: list[str]):
    p = argparse.ArgumentParser()

    p.add_argument(
        "--icons",
        default="emoji",
        choices=["emoji", "nerd"],
        help="Icon theme for file list output.",
    )

    p.add_argument(
        "--engine",
        choices=["ollama", "chatgpt", "copilot"],
        default="copilot",
        help="LLM engine to generate commit messages.",
    )

    p.add_argument(
        "--ollama-model",
        help=(
            "Ollama model name to use when --engine is 'ollama'. "
            "Examples: llama3, mistral, qwen3:8b"
        ),
    )

    args, extra_args = p.parse_known_args(argv)
    return args, extra_args


def load_engine(args):
    engine_name = args.engine

    if engine_name == "ollama":
        return OllamaEngine(model=args.ollama_model)

    if engine_name == "chatgpt":
        return ChatGPTEngine()

    if engine_name == "copilot":
        return CopilotEngine()

    raise RuntimeError(f"알 수 없는 engine: {engine_name}")


def main() -> None:
    args, extra_args = parse_args(sys.argv[1:])
    engine = load_engine(args)
    print(f"🔧 사용 중인 엔진: {engine.name}")

    try:
        git = GitClient()

        diff_console = DiffConsole(icons=args.icons)
        diff_processor = DiffProcessor(config=processConfig)

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
