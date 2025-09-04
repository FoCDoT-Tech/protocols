# gRPC Protocol Makefile
# Demonstrates gRPC communication patterns, streaming, and performance

.PHONY: all test clean server client streaming diagrams deps

# Check dependencies
deps:
	@echo "Checking gRPC dependencies..."
	@if [ ! -f "../2.4-http2/explainer.md" ]; then \
		echo "❌ Error: HTTP/2 (2.4) is required for gRPC"; \
		exit 1; \
	fi
	@echo "✓ HTTP/2 dependency satisfied"

# Generate all diagrams
diagrams:
	@echo "Generating gRPC diagrams..."
	python3 render_diagram.py
	@echo "✓ All diagrams generated"

# Run gRPC server simulation
server: deps
	@echo "Running gRPC server simulation..."
	python3 grpc_server.py
	@echo "✓ gRPC server simulation completed"

# Run gRPC client simulation
client: deps
	@echo "Running gRPC client simulation..."
	python3 grpc_client.py
	@echo "✓ gRPC client simulation completed"

# Run gRPC streaming patterns demo
streaming: deps
	@echo "Running gRPC streaming patterns demo..."
	python3 grpc_streaming.py
	@echo "✓ gRPC streaming demo completed"

# Run all tests
test: deps server client streaming diagrams
	@echo "All gRPC tests completed successfully!"
	@echo ""
	@echo "gRPC Protocol Summary:"
	@echo "- High-performance RPC framework using HTTP/2 and Protocol Buffers"
	@echo "- Four streaming patterns: Unary, Server, Client, and Bidirectional"
	@echo "- 50-90% smaller payloads and 2-10x faster serialization vs REST/JSON"
	@echo "- Type-safe APIs with cross-language support and built-in features"
	@echo "- Ideal for microservices, real-time streaming, and high-performance applications"

# Run everything
all: test

# Clean generated files
clean:
	rm -f *.png *.pyc __pycache__/*
	@echo "Cleaned generated files"
