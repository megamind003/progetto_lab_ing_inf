FROM python:3.9-slim

WORKDIR /app
COPY client_simulator.py .
RUN pip install requests  && mkdir -p /var/log/client && chmod 777 /var/log/client
CMD ["python", "client_simulator.py"]