#!/bin/bash
# Run the ASA-Database host (server) with Docker Compose
set -e

echo "Starting ASA-Database host (server) with Docker Compose..."
docker compose up --build
