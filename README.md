
```shell
# clone 한 후 폴더 root 경로에서 실행
echo "alias acommit=\"$(pwd)/main.py\"" >> ~/.zshrc
chmod +x main.py

which acommit # main.py 파일 경로 확인
```

- git add 한 후 acommit 명령어 실행
- 코파일럿 을 사용할 경우 pro 이상의 요금제 필요
- chatgpt 사용할 경우 openai api key 필요 (과금 O)

```shell
echo 'export OPENAI_API_KEY="API_KEY"' >> ~/.zshrc

source ~/.zshrc
echo $OPENAI_API_KEY # API_KEY 잘 들어갔는지 확인
```
