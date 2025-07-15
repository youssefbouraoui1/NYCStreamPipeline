# Dockerfile
FROM bitnami/spark:latest

USER root

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install pyspark==3.5.1 python-dotenv

ADD https://jdbc.postgresql.org/download/postgresql-42.7.2.jar /opt/bitnami/spark/jars/

WORKDIR /app

COPY main.py .
COPY config.env .

ENTRYPOINT ["spark-submit", "--packages", "org.postgresql:postgresql:42.7.2,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1"]
CMD ["main.py"]