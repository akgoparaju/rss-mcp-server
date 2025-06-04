FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--port", "8008"]
