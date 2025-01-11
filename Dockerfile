FROM python:3.12-slim-bookworm

ENV BOT_TOKEN=""

WORKDIR /app

COPY ./app/r.txt /app/r.txt

RUN pip install --no-cache-dir --upgrade -r /app/r.txt

COPY ./app /app

CMD ["python", "main.py" ]