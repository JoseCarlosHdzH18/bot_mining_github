FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code

ENV PYTHONPATH=/code

CMD ["rq", "worker", "github_jobs", "--url", "redis://redis:6379/0"]