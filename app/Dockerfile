FROM python:3.10

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

COPY .. /app

ENV PYTHONPATH "${PYTHONPATH}:/app"