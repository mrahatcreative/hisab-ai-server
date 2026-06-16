FROM python:3.12-slim

WORKDIR /app

COPY router.py .
COPY requirements-router.txt .

RUN pip install -q --no-cache-dir -r requirements-router.txt

EXPOSE 5328

CMD ["uvicorn", "router:app", "--host", "0.0.0.0", "--port", "5328"]
