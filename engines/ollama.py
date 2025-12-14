import json

import requests

from .base import CommitMessageEngine


class OllamaEngine(CommitMessageEngine):
    name = "Ollama"

    def __init__(self, model: str):
        if not model:
            raise RuntimeError(
                "Ollama 엔진을 사용하려면 --ollama-model 옵션이 필요합니다.\n"
                "예: --engine ollama --ollama-model llama3"
            )
        self.model = model

    def _generate(self, diff: str) -> str:
        prompt = self.get_prompt(diff)

        try:
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "num_predict": 128,
                    "temperature": 0.2,
                    "top_p": 0.9,
                },
                timeout=300,
            )
        except requests.RequestException as e:
            raise RuntimeError(
                "Ollama 서버에 연결할 수 없습니다.\n"
                "Ollama가 실행 중인지 확인하세요 (ollama serve)."
            ) from e

        if resp.status_code != 200:
            raise RuntimeError(
                f"Ollama API 호출 실패 (HTTP {resp.status_code}):\n{resp.text}"
            )

        try:
            data = resp.json()
        except json.JSONDecodeError:
            raise RuntimeError(f"Ollama 응답이 JSON이 아닙니다:\n{resp.text}")

        if "error" in data:
            raise RuntimeError(
                f"Ollama 오류: {data['error']}\n"
                f"모델이 설치되어 있는지 확인하세요:\n"
                f"  ollama pull {self.model}"
            )

        out = (data.get("response") or "").strip()
        if not out:
            raise RuntimeError("Ollama 응답이 비어 있습니다.")

        return out
