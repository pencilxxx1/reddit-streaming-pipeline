#!/bin/bash
# Stop all services

echo "Stopping Reddit Streaming Pipeline..."

# Stop services
docker-compose down

# Optional: Remove volumes (uncomment if needed)
# docker-compose down -v

echo "Pipeline stopped successfully!"