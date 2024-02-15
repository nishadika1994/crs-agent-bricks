FROM python:3.11-slim

# Copy application files and install dependencies
COPY . /app
COPY ./config /app/config
RUN pip install --upgrade pip
WORKDIR /app
RUN pip install -r requirements.txt && pip install autogenstudio

# Set the path
ENV PATH="/home/app/.local/bin:${PATH}"

# set python path
ENV PYTHONPATH="/home/app/.local/bin:/app:${PYTHONPATH}"

RUN autogenstudio version

EXPOSE 8088

ENTRYPOINT [ "autogenstudio", "ui", "--host", "0.0.0.0", "--port", "8088"]