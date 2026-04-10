FROM python:3.11-slim

WORKDIR /scheduler

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./scheduler /scheduler
COPY ./app /app

CMD ["python", "scheduler.py"]