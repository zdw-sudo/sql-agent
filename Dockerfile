FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app
COPY scripts ./scripts

RUN pip install --no-cache-dir -e .

COPY .env.example .env.example

EXPOSE 8000

CMD bash -c "python scripts/init_db.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"
