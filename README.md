# How to use

## Quick Setup

```shell
git clone https://github.com/daeun503/auto-commit.git
cd auto-commit

pip install -r requirements.txt
chmod +x main.py
```

### engine 1 : Ollama

```shell
brew install ollama
ollama pull qwen3:8b

echo "alias accommit=\"$(pwd)/main.py --engine ollama --model qwen3:8b\"" >> ~/.zshrc
source ~/.zshrc

git add .
accommit
```

### engine 2 : Copilot (recommend)

```shell
brew install --cask copilot-cli
copilot # copilot cli 실행
/login # copilot 로그인 수행 (pro 요금제 필요)

echo "alias accommit=\"$(pwd)/main.py --engine copilot --model gpt-4.1\"" >> ~/.zshrc
source ~/.zshrc

git add .
accommit
```

### engine 3 : ChatGPT

```shell
# openai api key 필요 (과금 필요)
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.zshrc
source ~/.zshrc
echo $OPENAI_API_KEY # API_KEY 잘 들어갔는지 확인

echo "alias accommit=\"$(pwd)/main.py --engine chatgpt --model gpt-4.1-mini\"" >> ~/.zshrc
source ~/.zshrc

git add .
accommit
```

<img width="978" height="570" alt="image" src="https://github.com/user-attachments/assets/30389c4f-ab5b-462a-b4f7-d89efdc6b3f9" />


---

## Nerd Font

```shell
# nerd font 설치 후 터미널 폰트를 nerd font 로 변경 (사진 참고)
brew install --cask font-jetbrains-mono-nerd-font
echo "alias accommit=\"$(pwd)/main.py --engine copilot --icons nerd\"" >> ~/.zshrc
```
<img width="1102" height="428" alt="image" src="https://github.com/user-attachments/assets/30433905-a66a-4074-a22d-aca2e5958425" />
<img width="661" height="386" alt="image" src="https://github.com/user-attachments/assets/90933e00-489b-48b5-bc29-0d0bdb712b2f" />

만약 아이콘을 추가하고 싶으면 icons/ 폴더에 있는 파일을 참고해서 추가

https://www.nerdfonts.com/cheat-sheet

## Extra Option

```
--icons ["emoji", "nerd"] # 아이콘 스타일 선택
--branch-prefix store_true # 브랜치 이름에 커밋 메시지 추가
```