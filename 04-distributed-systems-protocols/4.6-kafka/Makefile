.PHONY: all clean test broker producer consumer stream diagrams deps

# Kafka (Apache Kafka) Subchapter
# Dependencies: TCP (1.3)

all: deps broker producer consumer stream diagrams test

deps:
	@echo "🔍 Checking dependencies for Kafka..."
	@if [ ! -f "../../01-core-internet-networking/1.3-tcp/tcp_client_server.py" ]; then \
		echo "❌ Missing dependency: TCP (1.3) - run 'make' in 01-core-internet-networking/1.3-tcp first"; \
		exit 1; \
	fi
	@echo "✅ All dependencies satisfied"

broker:
	@echo "🏭 Running Kafka broker simulation..."
	@python3 kafka_broker.py

producer:
	@echo "📤 Running Kafka producer demonstration..."
	@python3 kafka_producer.py

consumer:
	@echo "📥 Running Kafka consumer demonstration..."
	@python3 kafka_consumer.py

stream:
	@echo "🌊 Running Kafka stream processing demo..."
	@timeout 40s python3 stream_processing.py || true

diagrams:
	@echo "🎨 Generating Kafka diagrams..."
	@python3 render_diagram.py
	@if command -v mmdc >/dev/null 2>&1; then \
		echo "📊 Rendering Mermaid diagram..."; \
		mmdc -i kafka_architecture.mmd -o kafka_architecture_mermaid.png; \
	else \
		echo "⚠️  Mermaid CLI not found, skipping .mmd rendering"; \
	fi

test:
	@echo "🧪 Testing Kafka implementations..."
	@python3 -c "\
import kafka_broker as kb; \
import kafka_producer as kp; \
import kafka_consumer as kc; \
import stream_processing as sp; \
from kafka_broker import KafkaBroker, KafkaMessage, TopicPartition; \
from kafka_producer import KafkaProducer, ProducerConfig, ProducerRecord; \
from kafka_consumer import KafkaConsumer, ConsumerConfig; \
broker = kb.KafkaBroker(broker_id=1); \
assert broker.broker_id == 1; \
assert broker.host == 'localhost'; \
assert broker.port == 9092; \
assert len(broker.topics) == 0; \
print('✅ Kafka Broker: initialization tests passed'); \
config = kp.ProducerConfig(); \
producer = kp.KafkaProducer(config); \
assert config.client_id == 'kafka-producer'; \
assert config.batch_size == 16384; \
print('✅ Kafka Producer: initialization tests passed'); \
consumer_config = kc.ConsumerConfig(); \
consumer = kc.KafkaConsumer(['test'], consumer_config); \
assert consumer_config.client_id == 'kafka-consumer'; \
assert consumer_config.max_poll_records == 500; \
print('✅ Kafka Consumer: initialization tests passed'); \
stream_proc = sp.StreamProcessor('test-app', broker); \
assert stream_proc.application_id == 'test-app'; \
assert len(stream_proc.sources) == 0; \
print('✅ Stream Processor: initialization tests passed'); \
print('🎯 All Kafka tests passed!')"

clean:
	@echo "🧹 Cleaning up generated files..."
	@rm -f *.png
	@rm -rf __pycache__/
	@echo "✅ Cleanup completed"

summary:
	@echo ""
	@echo "=== Kafka Summary ==="
	@echo "📋 Protocol: Apache Kafka Distributed Streaming Platform"
	@echo "🎯 Purpose: High-throughput, fault-tolerant real-time data streaming"
	@echo "🔧 Features: Partitioned topics, replication, consumer groups, stream processing"
	@echo "⚡ Benefits: Horizontal scaling, durability, exactly-once semantics"
	@echo "🌐 Use Cases: Event sourcing, real-time analytics, data integration"
	@echo ""
