FROM python:3.9-slim

# Installa curl per gli healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8000
ENV FLASK_APP=app.py
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
RUN mkdir -p /var/log/web-server && chmod 777 /var/log/web-server

CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]