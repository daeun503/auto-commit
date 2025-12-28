import os

from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    BadRequestError,
    OpenAI,
    RateLimitError,
)

from .base import CommitMessageEngine


class ChatGPTEngine(CommitMessageEngine):
    name = "ChatGPT"

    def __init__(self, model: str) -> None:
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError(
                "OPENAI_API_KEY가 설정되어 있지 않습니다.\n"
                "예: export OPENAI_API_KEY='sk-...'"
            )
        self.client = OpenAI()

        if not model:
            raise RuntimeError(
                "ChatGPT 엔진을 사용하려면 --model 옵션이 필요합니다.\n"
                "예: --engine chatgpt --model gpt-4.1-mini"
            )
        self.model = model

    def _generate(self, diff: str) -> str:
        prompt = self.get_prompt(diff)

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You generate git commit messages."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=200,
            )
        except AuthenticationError as e:
            raise RuntimeError(
                "ChatGPT 인증 실패: OPENAI_API_KEY가 잘못되었거나 권한이 없습니다.\n"
                "키를 다시 확인하세요."
            ) from e
        except RateLimitError as e:
            raise RuntimeError(
                "ChatGPT 요청이 제한되었습니다(rate limit/quota).\n"
                "잠시 후 다시 시도하거나 플랜/쿼터를 확인하세요."
            ) from e
        except BadRequestError as e:
            raise RuntimeError(
                "ChatGPT 요청이 잘못되었습니다(프롬프트가 너무 길거나 형식 문제일 수 있음).\n"
                "diff 길이를 줄이거나 프롬프트를 점검하세요."
            ) from e
        except APIConnectionError as e:
            raise RuntimeError(
                "ChatGPT 서버에 연결할 수 없습니다(네트워크/방화벽/프록시 문제일 수 있음)."
            ) from e
        except APIStatusError as e:
            raise RuntimeError(
                f"ChatGPT API 오류(HTTP {e.status_code}).\n"
                "잠시 후 재시도하거나 상태를 확인하세요."
            ) from e
        except Exception as e:
            raise RuntimeError(f"ChatGPT 알 수 없는 오류: {e}") from e

        out = (resp.choices[0].message.content or "").strip()
        if not out:
            raise RuntimeError("ChatGPT 응답이 비어 있습니다.")

        return out
