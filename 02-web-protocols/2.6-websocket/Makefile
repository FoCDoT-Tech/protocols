# WebSocket Protocol Makefile
# Demonstrates WebSocket communication, applications, and performance

.PHONY: all test clean server client applications diagrams deps

# Check dependencies
deps:
	@echo "Checking WebSocket dependencies..."
	@if [ ! -f "../2.2-http1.1/explainer.md" ]; then \
		echo "❌ Error: HTTP/1.1 (2.2) is required for WebSocket"; \
		exit 1; \
	fi
	@echo "✓ HTTP/1.1 dependency satisfied"

# Generate all diagrams
diagrams:
	@echo "Generating WebSocket diagrams..."
	python3 render_diagram.py
	@echo "✓ All diagrams generated"

# Run WebSocket server simulation
server: deps
	@echo "Running WebSocket server simulation..."
	python3 websocket_server.py
	@echo "✓ WebSocket server simulation completed"

# Run WebSocket client simulation
client: deps
	@echo "Running WebSocket client simulation..."
	python3 websocket_client.py
	@echo "✓ WebSocket client simulation completed"

# Run WebSocket applications demo
applications: deps
	@echo "Running WebSocket applications demo..."
	python3 websocket_applications.py
	@echo "✓ WebSocket applications demo completed"

# Run all tests
test: deps server client applications diagrams
	@echo "All WebSocket tests completed successfully!"
	@echo ""
	@echo "WebSocket Protocol Summary:"
	@echo "- Full-duplex communication over single TCP connection"
	@echo "- Minimal frame overhead for efficient real-time communication"
	@echo "- Supports text and binary data with control frames"
	@echo "- Ideal for chat, gaming, live feeds, and collaborative applications"
	@echo "- Significant performance benefits over HTTP polling"

# Run everything
all: test

# Clean generated files
clean:
	rm -f *.png *.pyc __pycache__/*
	@echo "Cleaned generated files"
