FROM bitnami/spark:3.5.1

USER root

RUN apt-get update && \
    apt-get install -y python3 python3-pip dos2unix file && \
    pip3 install pyspark==3.5.1 python-dotenv

ADD https://jdbc.postgresql.org/download/postgresql-42.7.2.jar /opt/bitnami/spark/jars/

WORKDIR /app

COPY main.py .
COPY config.env .
COPY start.sh .
COPY test.py .

RUN dos2unix config.env

RUN dos2unix start.sh && chmod +x start.sh

RUN ls -la /app && file /app/start.sh

ENTRYPOINT ["/app/start.sh"]
