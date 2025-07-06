/* resource "docker_image" "cassandra" {
  name = "cassandra:latest"
}

resource "docker_container" "cassandra" {
    name ="cassandra"
    image = docker_image.cassandra.latest
    networks_advanced {
    name = docker_network.pipeline_network.name
  }
    ports {
      internal = 9042
      external = 9042
    }
    env = [
        "CASSANDRA_CLUSTER_NAME=NYCStreamCluster",
        "CASSANDRA_NUM_TOKENS=50",
        "CASSANDRA_DC=DC1",
        "CASSANDRA_RACK=RAC1"

    ]
    volumes {
      container_path = "/var/lib/cassandra"
      host_path      = "D:/a-new-project-todiscover/terraform/data/cassandra"
    }

  # if we want our cassandra to wait for an other container for the mean time it does not need to wait
  # depends_on = [docker_container.zookeeper] 
} */