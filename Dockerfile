FROM python:3.11.7-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN pip install panel
RUN pip install spacy
RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 8000

CMD ["python", "-m", "panel", "serve", "crs_multiagent.py", "--address 0.0.0.0", "--port 8000", "--allow-websocket-origin=pghbricks-agent.azurewebsites.net" ]