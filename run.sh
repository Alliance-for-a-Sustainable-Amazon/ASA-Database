#!/bin/bash
# One-click script to start the app with Docker Compose (Linux/Mac)
set -e

echo "Starting ASA-Database with Docker Compose..."
docker-compose up --build
