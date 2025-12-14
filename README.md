# How to use

## Installation

```shell
# clone 한 후 폴더 root 경로에서 실행
echo "alias accommit=\"$(pwd)/main.py\"" >> ~/.zshrc
chmod +x main.py

which accommit # main.py 파일 경로 확인
```

## Usage

```shell
git add .
accommit
```

### engine 1 : Ollama

```
brew install ollama
ollama pull qwen3:8b

git add .
accommit
```

### engine 2 : Copilot (default)

```shell
brew install copilot
copliot # copilot cli 실행
/login # copilot 로그인 수행 (pro 요금제 필요)

git add .
accommit
```

### engine 3 : ChatGPT

```shell
# openai api key 필요 (과금 필요)
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.zshrc

source ~/.zshrc
echo $OPENAI_API_KEY # API_KEY 잘 들어갔는지 확인

git add .
accommit
```

<img width="978" height="570" alt="image" src="https://github.com/user-attachments/assets/30389c4f-ab5b-462a-b4f7-d89efdc6b3f9" />
