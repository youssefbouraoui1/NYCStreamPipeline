#!/bin/bash

echo "Refreshing materialized views inside Docker container..."

docker exec -i postgres psql -U admin -d NycTrafficStreamDatabase -c "
REFRESH MATERIALIZED VIEW mv_incidents_by_borough_month;
REFRESH MATERIALIZED VIEW mv_top_streets_by_injuries;
REFRESH MATERIALIZED VIEW mv_vehicle_type_incidents;
"

echo "Done refreshing views."
