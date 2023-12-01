# syntax=docker/dockerfile:1

#FROM python:3.10-slim-buster
FROM python:3.10-rc-slim-buster

WORKDIR /app

COPY memory_consumer memory_consumer/
COPY patterns patterns/
COPY setup.py .
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
RUN pip3 install .

ENTRYPOINT ["python3", "memory_consumer/start_mem_consumer.py"]

CMD ["-h"]

