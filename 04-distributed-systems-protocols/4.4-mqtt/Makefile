.PHONY: all clean test broker client iot diagrams deps

# MQTT (Message Queuing Telemetry Transport) Subchapter
# Dependencies: TCP (1.3)

all: deps broker client iot diagrams test

deps:
	@echo "🔍 Checking dependencies for MQTT..."
	@if [ ! -f "../../01-core-internet-networking/1.3-tcp/tcp_client_server.py" ]; then \
		echo "❌ Missing dependency: TCP (1.3) - run 'make' in 01-core-internet-networking/1.3-tcp first"; \
		exit 1; \
	fi
	@echo "✅ All dependencies satisfied"

broker:
	@echo "🏭 Running MQTT broker simulation..."
	@python3 mqtt_broker.py

client:
	@echo "📱 Running MQTT client demonstration..."
	@python3 mqtt_client.py

iot:
	@echo "🏠 Running IoT device simulation..."
	@timeout 35s python3 iot_simulation.py || true

diagrams:
	@echo "🎨 Generating MQTT diagrams..."
	@python3 render_diagram.py
	@if command -v mmdc >/dev/null 2>&1; then \
		echo "📊 Rendering Mermaid diagram..."; \
		mmdc -i mqtt_architecture.mmd -o mqtt_architecture_mermaid.png; \
	else \
		echo "⚠️  Mermaid CLI not found, skipping .mmd rendering"; \
	fi

test:
	@echo "🧪 Testing MQTT implementations..."
	@python3 -c "\
import mqtt_broker as mb; \
import mqtt_client as mc; \
import iot_simulation as iot; \
from mqtt_broker import MQTTBroker, MQTTMessage, QoSLevel; \
from mqtt_client import MQTTClient, MQTTClientConfig; \
broker = mb.MQTTBroker(); \
assert broker.port == 1883; \
assert len(broker.sessions) == 0; \
print('✅ MQTT Broker: initialization tests passed'); \
config = mc.MQTTClientConfig(); \
client = mc.MQTTClient(config); \
assert config.broker_host == 'localhost'; \
assert config.broker_port == 1883; \
assert not client.is_connected(); \
print('✅ MQTT Client: connection tests passed'); \
msg = mb.MQTTMessage('test/topic', 'test payload', QoSLevel.AT_LEAST_ONCE); \
assert msg.topic == 'test/topic'; \
assert msg.payload == 'test payload'; \
assert msg.qos == QoSLevel.AT_LEAST_ONCE; \
print('✅ MQTT Message: message tests passed'); \
device = iot.IoTDevice('test_device', iot.DeviceType.TEMPERATURE_SENSOR, 'test_room', broker); \
assert device.device_id == 'test_device'; \
assert device.device_type == iot.DeviceType.TEMPERATURE_SENSOR; \
assert device.location == 'test_room'; \
print('✅ IoT Device: device tests passed'); \
print('🎯 All MQTT tests passed!')"

clean:
	@echo "🧹 Cleaning up generated files..."
	@rm -f *.png
	@rm -rf __pycache__/
	@echo "✅ Cleanup completed"

summary:
	@echo ""
	@echo "=== MQTT Summary ==="
	@echo "📋 Protocol: Message Queuing Telemetry Transport"
	@echo "🎯 Purpose: Lightweight publish-subscribe for IoT devices"
	@echo "🔧 Features: QoS levels, retained messages, Last Will & Testament"
	@echo "⚡ Benefits: Minimal overhead, reliable delivery, session persistence"
	@echo "🌐 Use Cases: Smart homes, industrial IoT, connected vehicles"
	@echo ""
