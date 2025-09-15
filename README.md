# Reddit Real-Time Streaming Pipeline

A scalable real-time data pipeline that streams Reddit data using Kafka, processes it with Apache Spark, and stores it in MongoDB.

## 🏗️ Architecture

```
Reddit API → Kafka Producer → Kafka → Spark Streaming → MongoDB → Dashboard
                                ↑                              ↓
                            Zookeeper                    Mongo Express
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose V2
- 8GB+ RAM recommended
- Reddit API credentials

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/pencilxxx1/reddit-streaming-pipeline.git
cd reddit-streaming-pipeline
```

2. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your Reddit API credentials
```

3. **Start the pipeline:**
```bash
chmod +x scripts/start.sh
./scripts/start.sh
```

4. **Access the services:**

| Service | URL | Credentials |
|---------|-----|-------------|
| **Streamlit Dashboard** | http://localhost:8501 | No auth required |
| **Mongo Express** | http://localhost:8081 | Username: `admin`<br>Password: `adminpw` |
| **MongoDB Direct** | mongodb://localhost:27017 | Username: `new_user300`<br>Password: `Sulaimon1` |
| **Kafka** | localhost:9092 | No auth required |

5. **Stop the pipeline:**
```bash
./scripts/stop.sh
```

## 📊 Features

- **Real-time streaming** from Reddit API
- **Sentiment analysis** using TextBlob
- **Language detection** for multilingual content
- **Entity extraction** from posts and comments
- **Interactive dashboard** with real-time metrics
- **MongoDB web UI** via Mongo Express
- **Health checks** for service reliability
- **Scalable architecture** using Docker containers
- **Fault tolerance** with Kafka message persistence

## 🛠️ Tech Stack

- **Data Ingestion**: Reddit API (PRAW)
- **Message Broker**: Apache Kafka 7.5.0
- **Stream Processing**: Apache Spark Structured Streaming
- **Storage**: MongoDB 7.0
- **Database UI**: Mongo Express 1.0.2
- **Visualization**: Streamlit
- **Orchestration**: Docker Compose V2
- **Coordination**: Apache Zookeeper

## 📁 Project Structure

```
reddit-streaming-pipeline/
├── producer/           # Reddit data producer
├── spark-consumer/     # Spark streaming consumer
├── dashboard/          # Streamlit dashboard
├── mongodb/           # MongoDB initialization
│   └── init-mongo.js  # Database setup script
├── scripts/           # Utility scripts
├── docker-compose.yml # Service orchestration (Compose V2)
├── .env              # Environment variables
└── README.md         # This file
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Reddit API Credentials
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent
REDDIT_SUBREDDITS=AskReddit,worldnews,technology

# MongoDB Configuration
MONGO_ROOT_USERNAME=new_user300
MONGO_ROOT_PASSWORD=Sulaimon1

# Mongo Express Web UI
ME_BASIC_AUTH_USER=admin
ME_BASIC_AUTH_PASS=adminpw

# Kafka Configuration
KAFKA_BROKER=kafka:29092
KAFKA_TOPIC=reddit-stream
```

## 📈 Service Details

### Service Ports & Access

| Service | Container Port | Host Port | Internal Access | External Access |
|---------|---------------|-----------|-----------------|-----------------|
| **Zookeeper** | 2181 | 2181 | zookeeper:2181 | localhost:2181 |
| **Kafka** | 29092, 9092 | 9092, 9101 | kafka:29092 | localhost:9092 |
| **MongoDB** | 27017 | 27017 | mongodb:27017 | localhost:27017 |
| **Mongo Express** | 8081 | 8081 | - | http://localhost:8081 |
| **Dashboard** | 8501 | 8501 | - | http://localhost:8501 |

### Service Dependencies & Health Checks

- **Kafka** waits for Zookeeper and includes health checks
- **Reddit Producer** waits for Kafka health check
- **Spark Consumer** waits for both Kafka and MongoDB
- All services configured with `restart: unless-stopped`

## 📊 Monitoring

### View Service Logs
```bash
# All services
docker-compose logs -f

# Specific services
docker-compose logs -f reddit-producer
docker-compose logs -f spark-consumer
docker-compose logs -f kafka
```

### Check Service Status
```bash
# Service health
docker-compose ps

# Detailed status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Test Pipeline Components
```bash
# Test Kafka
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Test MongoDB
docker exec mongodb mongosh --eval "db.adminCommand('ping')"

# Check data flow
./scripts/test_pipeline.sh
```

## 🖥️ Using Mongo Express

1. **Access**: http://localhost:8081
2. **Login**: `admin` / `adminpw`
3. **Navigate**:
   - Click `reddit_data` database
   - Click `processed_posts` collection
   - View, query, and export data

## 📊 Dashboard Features

Access at http://localhost:8501:

- **Real-time Metrics**: Total posts, average score, sentiment percentage
- **Visualizations**: 
  - Sentiment distribution pie chart
  - Top subreddits bar chart
  - Activity time series
  - Language distribution
  - Word cloud from posts
- **Data Table**: Recent posts with filtering
- **Auto-refresh**: Optional 10-second refresh

## 🐛 Troubleshooting

### Common Issues

1. **Kafka Connection Error**
   - Wait 30-60 seconds for Kafka to fully start
   - Check health: `docker-compose ps`
   - Verify: `docker exec kafka kafka-topics --list --bootstrap-server localhost:9092`

2. **MongoDB Authentication Failed**
   - Verify credentials in `.env` match `init-mongo.js`
   - Check connection: `docker exec mongodb mongosh -u new_user300 -p Sulaimon1`

3. **No Data in Dashboard**
   - Check producer logs: `docker logs reddit-producer`
   - Verify Reddit API credentials are valid
   - Check Mongo Express for data: http://localhost:8081

4. **Reddit API Rate Limiting**
   - Reduce `BATCH_SIZE` in `.env`
   - Use specific subreddits instead of "all"

5. **Memory Issues**
   - Increase Docker Desktop memory to 6-8GB
   - Reduce Spark memory usage in configuration

### Reset Everything
```bash
# Complete cleanup
docker-compose down -v
docker system prune -f
docker-compose up -d
```

## 🔍 Data Verification

### Via Mongo Express (Web UI)
- http://localhost:8081
- Login with `admin` / `adminpw`
- Browse `reddit_data` → `processed_posts`

### Via MongoDB Shell
```bash
docker exec -it mongodb mongosh -u new_user300 -p Sulaimon1
use reddit_data
db.processed_posts.countDocuments()
db.processed_posts.find().limit(5)
```

### Via MongoDB Compass (Desktop App)
- Connection: `mongodb://new_user300:Sulaimon1@localhost:27017/`
- Database: `reddit_data`

## 📝 Development

### Modify Components
- **Producer**: Edit `producer/reddit_producer.py`
- **Consumer**: Edit `spark-consumer/spark_consumer.py`
- **Dashboard**: Edit `dashboard/app.py`

### Rebuild After Changes
```bash
docker-compose build [service-name]
docker-compose up -d [service-name]
```

### View Network Details
```bash
docker network inspect reddit-streaming-pipeline_reddit-network
```

## 👥 Contributors

- Akeem Agboola ([@pencilxxx1](https://github.com/pencilxxx1))

## 🙏 Acknowledgments

- Reddit API for data access
- Apache Spark community
- Confluent for Kafka Docker images
- MongoDB team for Mongo Express

## 📄 License

MIT License - See LICENSE file for details

---

**Last Updated**: 2024
**Docker Compose Version**: V2 (no version key required)
**Tested On**: Docker Desktop 4.x+