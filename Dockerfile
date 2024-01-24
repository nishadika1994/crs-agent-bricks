FROM python:3.10.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 8000

CMD ["python", "-m", "panel", "serve", "crs_multiagent.py", "--port", "8000", "--address", "0.0.0.0", "--allow-websocket-origin=*"]