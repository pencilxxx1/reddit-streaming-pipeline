#!/bin/bash
# Start all services

echo "Starting Reddit Streaming Pipeline..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    exit 1
fi

# Start services
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check service status
docker-compose ps

echo "Pipeline started successfully!"
echo "Dashboard: http://localhost:8501"
echo "MongoDB: mongodb://localhost:27017"
echo "Kafka: localhost:9092"