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
