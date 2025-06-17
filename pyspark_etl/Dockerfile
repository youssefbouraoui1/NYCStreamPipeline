# Dockerfile
FROM bitnami/spark:3.5.1

USER root

# Install Python, pip, and dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install pyspark==3.5.1 python-dotenv

# Add PostgreSQL JDBC driver
ADD https://jdbc.postgresql.org/download/postgresql-42.7.2.jar /opt/bitnami/spark/jars/

WORKDIR /app

COPY main.py .
COPY config.env .

CMD ["spark-submit", "--packages", "org.postgresql:postgresql:42.7.2", "main.py"]
