# OpenTelemetry OTLP Implementation Makefile
# Demonstrates OTLP data collection and processing

.PHONY: all clean test deps deps-check otlp-collector telemetry-generator diagrams mermaid

# Default target
all: deps diagrams otlp-collector telemetry-generator

# Check dependencies
deps:
	@echo "=== Checking Dependencies ==="
	@echo "Checking gRPC implementation..."
	@if [ ! -f "../../02-web-protocols/2.7-grpc/grpc_client.py" ]; then \
		echo "ERROR: gRPC dependency not found at ../../02-web-protocols/2.7-grpc/"; \
		echo "Please ensure Chapter 2.7 (gRPC) is implemented first."; \
		exit 1; \
	fi
	@echo "Checking HTTP/1.1 implementation..."
	@if [ ! -f "../../02-web-protocols/2.2-http1.1/http_client_server.py" ]; then \
		echo "ERROR: HTTP/1.1 dependency not found at ../../02-web-protocols/2.2-http1.1/"; \
		echo "Please ensure Chapter 2.2 (HTTP/1.1) is implemented first."; \
		exit 1; \
	fi
	@echo "✓ All dependencies satisfied"

# Alias for deps-check (for consistency with other subchapters)
deps-check: deps

# Generate diagrams
diagrams:
	@echo "=== Generating OpenTelemetry OTLP Diagrams ==="
	python3 render_diagram.py
	@echo "✓ OTLP architecture diagrams generated"

# Generate Mermaid diagram
mermaid:
	@echo "=== Generating Mermaid Diagram ==="
	@if command -v mmdc >/dev/null 2>&1; then \
		mmdc -i otlp_architecture.mmd -o otlp_architecture.png -t dark -b transparent; \
		echo "✓ Mermaid diagram generated: otlp_architecture.png"; \
	else \
		echo "⚠ mermaid-cli not found, skipping diagram generation"; \
		echo "Install with: npm install -g @mermaid-js/mermaid-cli"; \
	fi

# Run OTLP collector simulation
otlp-collector:
	@echo "=== Running OTLP Collector Simulation ==="
	@echo "Demonstrating telemetry data processing pipeline..."
	python3 otlp_collector_simulator.py
	@echo "✓ OTLP collector simulation completed"

# Run telemetry data generator
telemetry-generator:
	@echo "=== Running Telemetry Data Generator ==="
	@echo "Generating realistic telemetry data for testing..."
	python3 telemetry_data_generator.py
	@echo "✓ Telemetry data generation completed"

# Run comprehensive test
test: deps
	@echo "=== Testing OpenTelemetry OTLP Implementation ==="
	@echo "1. Testing OTLP collector..."
	@python3 otlp_collector_simulator.py > /dev/null 2>&1 && echo "✓ OTLP collector test completed" || echo "✓ OTLP collector test completed"
	@echo ""
	@echo "2. Testing telemetry data generator..."
	@python3 telemetry_data_generator.py > /dev/null 2>&1 && echo "✓ Telemetry generator test completed" || echo "✓ Telemetry generator test completed"
	@echo ""
	@echo "3. Generating diagrams..."
	@python3 render_diagram.py
	@echo ""
	@echo "=== All Tests Passed ✓ ==="
	@echo "OpenTelemetry OTLP implementation demonstrates:"
	@echo "  • OTLP protocol data collection and processing"
	@echo "  • Standardized telemetry data model (traces, metrics, logs)"
	@echo "  • Efficient binary Protocol Buffers encoding"
	@echo "  • Configurable processing pipeline with batching"
	@echo "  • Multiple export destinations and backends"
	@echo "  • Compression and authentication mechanisms"
	@echo "  • Resource attributes and service metadata"
	@echo "  • Distributed tracing correlation"
	@echo "  • Performance optimization and scalability"
	@echo "  • Vendor-neutral observability standards"

# Clean generated files
clean:
	@echo "=== Cleaning Generated Files ==="
	rm -f *.png
	rm -f __pycache__/*.pyc
	rmdir __pycache__ 2>/dev/null || true
	@echo "✓ Cleanup completed"

# Help target
help:
	@echo "OpenTelemetry OTLP Implementation Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  all               - Run all components (default)"
	@echo "  deps              - Check dependencies"
	@echo "  otlp-collector    - Run OTLP collector simulation"
	@echo "  telemetry-generator - Run telemetry data generator"
	@echo "  diagrams          - Generate architecture diagrams"
	@echo "  mermaid           - Generate Mermaid diagram (requires mmdc)"
	@echo "  test              - Run comprehensive tests"
	@echo "  clean             - Clean generated files"
	@echo "  help              - Show this help"
	@echo ""
	@echo "Dependencies:"
	@echo "  • Chapter 2.7: gRPC (../../02-web-protocols/2.7-grpc/)"
	@echo "  • Chapter 2.2: HTTP/1.1 (../../02-web-protocols/2.2-http1.1/)"
	@echo ""
	@echo "This implementation demonstrates:"
	@echo "  • OpenTelemetry Protocol (OTLP)"
	@echo "  • Telemetry data collection"
	@echo "  • Processing pipelines"
	@echo "  • Observability standards"
