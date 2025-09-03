FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

COPY . /app
RUN if [ -f "/app/packages/shared/pyproject.toml" ]; then pip install -e /app/packages/shared; fi

WORKDIR /app/apps/trainer

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]