FROM python:3.9-slim

WORKDIR /app

RUN pip install kafka-python pymongo

COPY basic_consumer.py .

CMD ["python", "-u", "basic_consumer.py"]