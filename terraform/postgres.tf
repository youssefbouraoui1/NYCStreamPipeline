resource "docker_image" "postgres" {
    name = "postgres:latest"
}


resource "docker_container" "postgres" {
    name = "postgres"
    image = docker_image.postgres.latest
    networks_advanced {
      name = docker_network.pipeline_network.name
    }

    ports {
       internal = 5432
       external = 5432
    }

    env = [
        "POSTGRES_USER=admin",
        "POSTGRES_PASSWORD=admin123",
        "POSTGRES_DB=NycTrafficStreamDatabase"
    ]

    volumes {
      container_path = "/var/lib/postgresql/data"
      host_path      = "D:/a-new-project-todiscover/terraform/data/postgres"
    }
}