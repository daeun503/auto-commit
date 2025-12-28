#!/usr/bin/env python3

import argparse
import sys

from engines import ChatGPTEngine, CopilotEngine, OllamaEngine
from flows import CommitFlow, DiffConsole, DiffProcessor
from git import GitClient


def make_base_parser():
    """
    required arguments:
        --engine     LLM engine to generate commit messages.
        --model      name to use with the selected engine.
    optional arguments:
        --icons          Icon theme for file list output. (default: emoji)
        --branch-prefix  If enabled, prepend the current branch name to the commit message.
        --edit-gitmoji-prefix  If enabled, allows editing of the gitmoji and prefix of the generated commit message.
    """

    p = argparse.ArgumentParser()

    # ---------- required ----------
    p.add_argument(
        "--engine",
        required=True,
        help="LLM engine to generate commit messages.",
    )

    p.add_argument(
        "--model",
        required=True,
        help=(
            "model name to use with the selected engine.\n"
            "Examples: llama3, mistral, qwen3:8b, gpt-4.1, gpt-4.1-mini, claude-sonnet-4.5. etc."
        ),
    )

    # ---------- optional ----------
    p.add_argument(
        "--icons",
        default="emoji",
        choices=["emoji", "nerd"],
        help="Icon theme for file list output.",
    )

    p.add_argument(
        "--branch-prefix",
        action="store_true",
        default=False,
        help=(
            "If enabled, prepend the current branch name to the commit message.\n"
            "For example, when the branch is 'PROD-123', the commit message will start with '[PROD-123]'"
        ),
    )

    p.add_argument(
        "--no-edit-gitmoji-prefix",
        action="store_true",
        default=False,
        help="Disable interactive editing of gitmoji and prefix.",
    )

    return p


def load_engine(args):
    engine_name = args.engine

    if engine_name == "ollama":
        return OllamaEngine(model=args.model)

    if engine_name == "chatgpt":
        return ChatGPTEngine(model=args.model)

    if engine_name == "copilot":
        return CopilotEngine(model=args.model)

    raise RuntimeError(f"알 수 없는 engine: {engine_name}")


def main(engine, args, extra_args) -> None:
    try:
        git = GitClient()

        diff_console = DiffConsole(icons=args.icons)
        diff_processor = DiffProcessor()

        flow = CommitFlow(
            engine=engine,
            git=git,
            diff_processor=diff_processor,
            console=diff_console,
        )

        commit = flow.run(
            use_branch_prefix=args.branch_prefix,
            edit_gitmoji_prefix=not args.no_edit_gitmoji_prefix,
            extra_args=extra_args,
        )
        sys.exit(commit)
    except KeyboardInterrupt:
        print("  ❌ 커밋이 취소되었습니다.")
        sys.exit(0)

    except Exception as e:
        print(f"  ❌ {engine.name} 오류:", file=sys.stderr)
        print(str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    p = make_base_parser()
    args, extra_args = p.parse_known_args(sys.argv[1:])

    engine = load_engine(args)
    print(f"🔧 사용 중인 엔진: {engine.name} & 모델: {engine.model}")

    main(engine, args, extra_args)
