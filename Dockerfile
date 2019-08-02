FROM python:3.7-slim
WORKDIR /app
RUN pip install gunicorn["gevent"]
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY run.py .
CMD ["gunicorn", "run:app"]
