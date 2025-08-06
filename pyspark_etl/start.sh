#!/bin/bash
source config.env
export $(cat config.env | xargs)
spark-submit --packages "org.postgresql:postgresql:42.7.2,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1" main.py