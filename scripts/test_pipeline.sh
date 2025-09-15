#!/bin/bash
# Test the pipeline components

echo "Testing Reddit Streaming Pipeline..."

# Test Kafka
echo "Testing Kafka..."
docker exec kafka kafka-topics --list --bootstrap-server localhost:29092

# Test MongoDB
echo "Testing MongoDB..."
docker exec mongodb mongosh --eval "db.adminCommand('ping')"

# Check logs
echo "Checking producer logs..."
docker logs reddit-producer --tail 10

echo "Checking consumer logs..."
docker logs spark-consumer --tail 10

echo "Pipeline test complete!"