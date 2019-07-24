FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt .
COPY run.py .

RUN pip install -r requirements.txt
RUN pip install gunicorn["gevent"]

CMD ["gunicorn", "run:app"]
