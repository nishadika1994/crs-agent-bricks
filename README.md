# crs-agent-bricks
# AutoGen Multi-Agent Chat Window

## Run below commands#

```shell
pip install -r requirements.txt
pip install panel
pip install spacy
python -m spacy download en_core_web_sm
```

## Build docker image
```shell
docker build -f Dockerfile --tag bistecglobal/pghbricks-agent:1.0.0 .
```

## Run docker image
```shell
docker run -it -p 8000:8000 -e OPENAI_API_KEY='sk-******' bistecglobal/pghbricks-agent:1.0.0
```
