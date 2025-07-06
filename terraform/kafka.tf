resource "docker_image" "zookeeper" {
  name = "confluentinc/cp-zookeeper:7.4.0"
}

resource "docker_container" "zookeeper" {
  name     = "zookeeper"
  hostname = "zookeeper"
  image    = docker_image.zookeeper.latest
  networks_advanced {
    name = docker_network.pipeline_network.name
  }
  ports {
    internal = 2181
    external = 2181
  }
  env = [
    "ZOOKEEPER_CLIENT_PORT=2181",
    "ZOOKEEPER_TICK_TIME=2000"
  ]
}

resource "docker_image" "kafka" {
  name = "confluentinc/cp-kafka:7.4.0"
}

resource "docker_container" "kafka" {
  name     = "kafka"
  hostname = "kafka"
  image    = docker_image.kafka.latest
  networks_advanced {
    name = docker_network.pipeline_network.name
  }
  ports {
    internal = 9092
    external = 9092
  }

  entrypoint = ["/bin/sh", "-c"]
  command    = ["sleep 10 && /etc/confluent/docker/run"]

  env = [
    "KAFKA_BROKER_ID=1",
    "KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181",
    "KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092",
    "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1",
    "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT",
    "KAFKA_AUTO_CREATE_TOPICS_ENABLE=true",
    "KAFKA_ZOOKEEPER_SESSION_TIMEOUT_MS=60000",
    "KAFKA_ZOOKEEPER_CONNECTION_TIMEOUT_MS=60000",
    "KAFKA_ZOOKEEPER_SYNC_TIME_MS=2000",

  ]
  depends_on = [docker_container.zookeeper]
}

#for confluent

resource "docker_image" "schema_registry" {
  name = "confluentinc/cp-schema-registry:7.4.0"
}

resource "docker_container" "schema_registry" {
  name  = "schema-registry"
  image = docker_image.schema_registry.latest

  networks_advanced {
    name = docker_network.pipeline_network.name
  }

  

  env = [
    "SCHEMA_REGISTRY_HOST_NAME=schema-registry",
    "SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS=PLAINTEXT://kafka:9092"
  ]

  ports {
    internal = 8081
    external = 8083
  }


  depends_on = [docker_container.kafka]
}

#confluent control center

resource "docker_image" "control_center" {
  name = "confluentinc/cp-enterprise-control-center:7.4.0"
}

resource "docker_container" "control_center" {
  name  = "control-center"
  image = docker_image.control_center.latest

  networks_advanced {
    name = docker_network.pipeline_network.name
  }

  

  env = [
    "CONTROL_CENTER_BOOTSTRAP_SERVERS=PLAINTEXT://kafka:9092",
    "CONTROL_CENTER_SCHEMA_REGISTRY_URL=http://schema-registry:8083",
    "CONTROL_CENTER_REPLICATION_FACTOR=1"

  ]

  ports {
    internal = 9021
    external = 9021
  }

  depends_on = [docker_container.schema_registry]
}

