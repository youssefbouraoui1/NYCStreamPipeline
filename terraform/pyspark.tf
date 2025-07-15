/* resource "docker_image" "pyspark_etl_master" {
  name  = "pyspark_etl"
  build {
    path = "${path.module}/../pyspark_etl"
    dockerfile = "${path.module}/../pyspark_etl/Dockerfile"
  }
} */

resource "docker_image" "spark" {
  name = "pyspark_etl:latest"
  
}

resource "docker_container" "spark_NYC_master" {
  name  = "spark-NYC-master"
  image = docker_image.spark.latest

  networks_advanced {
    name = docker_network.pipeline_network.name
  }

  env = [
    "SPARK_MODE=master",
    "KAFKA_BROKER=kafka:9092",
    "KAFKA_TOPIC=raw_incidents",
    "PG_URL=jdbc:postgresql://postgres:5432/NycTrafficStreamDatabase",
    "PG_USER=admin",
    "PG_PASSWORD=admin123"
  ]

  ports {
    internal = 7077
    external = 7077
  }

  ports {
    internal = 8081
    external = 8081
  }

  restart = "always"
}

resource "docker_container" "spark_worker1" {
  name  = "spark-worker-1"
  image = docker_image.spark.latest

  networks_advanced {
    name = docker_network.pipeline_network.name
  }

  env = [
    "SPARK_MODE=worker",
    "SPARK_MASTER_URL=spark://spark-NYC-master:7077"
  ]

  ports {
    internal = 8082
    external = 8082
  }

  

  depends_on = [docker_container.spark_NYC_master]
}
