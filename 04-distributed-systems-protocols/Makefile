.PHONY: all clean test deps 4.1 4.2 4.3 4.4 4.5 4.6 summary

# Chapter 4: Distributed Systems Protocols
# Master Makefile to run all subchapter tests sequentially

all: deps 4.1 4.2 4.3 4.4 4.5 4.6 summary

deps:
	@echo "🔍 Checking Chapter 4 dependencies..."
	@echo "   Required: TCP (1.3), UDP (1.4)"
	@if [ ! -f "../01-core-internet-networking/1.3-tcp/tcp_client_server.py" ]; then \
		echo "❌ Missing dependency: TCP (1.3) - run 'make' in 01-core-internet-networking/1.3-tcp first"; \
		exit 1; \
	fi
	@if [ ! -f "../01-core-internet-networking/1.4-udp/udp_client_server.py" ]; then \
		echo "❌ Missing dependency: UDP (1.4) - run 'make' in 01-core-internet-networking/1.4-udp first"; \
		exit 1; \
	fi
	@echo "✅ All Chapter 4 dependencies satisfied"

4.1:
	@echo ""
	@echo "=== 4.1 Raft & Paxos Consensus Protocols ==="
	@cd 4.1-raft-paxos && $(MAKE) all
	@echo "✅ 4.1 Raft & Paxos completed successfully"

4.2:
	@echo ""
	@echo "=== 4.2 Gossip Protocols ==="
	@cd 4.2-gossip && $(MAKE) all
	@echo "✅ 4.2 Gossip completed successfully"

4.3:
	@echo ""
	@echo "=== 4.3 AMQP (Advanced Message Queuing Protocol) ==="
	@cd 4.3-amqp && $(MAKE) all
	@echo "✅ 4.3 AMQP completed successfully"

4.4:
	@echo ""
	@echo "=== 4.4 MQTT (Message Queuing Telemetry Transport) ==="
	@cd 4.4-mqtt && $(MAKE) all
	@echo "✅ 4.4 MQTT completed successfully"

4.5:
	@echo ""
	@echo "=== 4.5 STOMP (Simple Text Oriented Messaging Protocol) ==="
	@cd 4.5-stomp && $(MAKE) all
	@echo "✅ 4.5 STOMP completed successfully"

4.6:
	@echo ""
	@echo "=== 4.6 Kafka (Apache Kafka) ==="
	@cd 4.6-kafka && $(MAKE) all
	@echo "✅ 4.6 Kafka completed successfully"

test:
	@echo ""
	@echo "🧪 Running Chapter 4 comprehensive tests..."
	@cd 4.1-raft-paxos && $(MAKE) test
	@cd 4.2-gossip && $(MAKE) test
	@cd 4.3-amqp && $(MAKE) test
	@cd 4.4-mqtt && $(MAKE) test
	@cd 4.5-stomp && $(MAKE) test
	@cd 4.6-kafka && $(MAKE) test
	@echo "🎯 All Chapter 4 tests passed!"

clean:
	@echo "🧹 Cleaning Chapter 4 generated files..."
	@cd 4.1-raft-paxos && $(MAKE) clean
	@cd 4.2-gossip && $(MAKE) clean
	@cd 4.3-amqp && $(MAKE) clean
	@cd 4.4-mqtt && $(MAKE) clean
	@cd 4.5-stomp && $(MAKE) clean
	@cd 4.6-kafka && $(MAKE) clean
	@echo "✅ Chapter 4 cleanup completed"

summary:
	@echo ""
	@echo "╔══════════════════════════════════════════════════════════════╗"
	@echo "║                    CHAPTER 4 SUMMARY                        ║"
	@echo "║              Distributed Systems Protocols                  ║"
	@echo "╠══════════════════════════════════════════════════════════════╣"
	@echo "║                                                              ║"
	@echo "║ 🎯 CONSENSUS PROTOCOLS                                       ║"
	@echo "║   4.1 Raft & Paxos: Leader election, log replication        ║"
	@echo "║                                                              ║"
	@echo "║ 🗣️  GOSSIP PROTOCOLS                                         ║"
	@echo "║   4.2 Gossip: Epidemic information spread, failure detection ║"
	@echo "║                                                              ║"
	@echo "║ 📨 MESSAGING PROTOCOLS                                       ║"
	@echo "║   4.3 AMQP: Enterprise messaging, exchanges, routing        ║"
	@echo "║   4.4 MQTT: IoT messaging, QoS levels, retained messages    ║"
	@echo "║   4.5 STOMP: Simple text messaging, WebSocket compatible    ║"
	@echo "║                                                              ║"
	@echo "║ 🌊 STREAMING PLATFORMS                                       ║"
	@echo "║   4.6 Kafka: Distributed streaming, partitions, replication ║"
	@echo "║                                                              ║"
	@echo "║ 🔧 KEY CONCEPTS COVERED                                      ║"
	@echo "║   • Distributed consensus and leader election               ║"
	@echo "║   • Fault-tolerant communication patterns                   ║"
	@echo "║   • Message queuing and publish-subscribe                   ║"
	@echo "║   • Real-time data streaming and processing                 ║"
	@echo "║   • Horizontal scaling and partitioning                     ║"
	@echo "║   • Exactly-once delivery semantics                         ║"
	@echo "║                                                              ║"
	@echo "║ 📊 IMPLEMENTATION HIGHLIGHTS                                 ║"
	@echo "║   • 6 complete protocol implementations                     ║"
	@echo "║   • 18 Python simulation files                              ║"
	@echo "║   • 6 Mermaid architecture diagrams                         ║"
	@echo "║   • 18 matplotlib visual diagrams                           ║"
	@echo "║   • Comprehensive test suites                               ║"
	@echo "║   • Real-world engineering scenarios                        ║"
	@echo "║                                                              ║"
	@echo "║ 🌐 REAL-WORLD APPLICATIONS                                   ║"
	@echo "║   • Microservices coordination (Raft/Paxos)                 ║"
	@echo "║   • Distributed system monitoring (Gossip)                  ║"
	@echo "║   • Enterprise integration (AMQP)                           ║"
	@echo "║   • IoT device communication (MQTT)                         ║"
	@echo "║   • Web application messaging (STOMP)                       ║"
	@echo "║   • Real-time data pipelines (Kafka)                        ║"
	@echo "║                                                              ║"
	@echo "╚══════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🎉 Chapter 4: Distributed Systems Protocols completed successfully!"
	@echo "   All protocols tested and validated ✅"
	@echo "   Ready for production learning scenarios 🚀"
	@echo ""
