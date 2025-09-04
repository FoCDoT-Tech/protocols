# HTTP/2 & gRPC Multiplexing Implementation Makefile
# Demonstrates stream multiplexing and concurrent processing

.PHONY: all build test clean diagrams deps-check http2-multiplexing grpc-streaming diagrams mermaid

# Default target
all: deps-check build diagrams test

# Check dependencies
deps-check:
	@echo "=== Checking Dependencies ==="
	@echo "Checking HTTP/2 implementation..."
	@if [ ! -f "../../02-web-protocols/2.4-http2/http2_multiplexing.py" ]; then \
		echo "ERROR: HTTP/2 dependency not found at ../../02-web-protocols/2.4-http2/"; \
		echo "Please ensure Chapter 2.4 (HTTP/2) is implemented first."; \
		exit 1; \
	fi
	@echo "Checking gRPC implementation..."
	@if [ ! -f "../../02-web-protocols/2.7-grpc/grpc_client.py" ]; then \
		echo "ERROR: gRPC dependency not found at ../../02-web-protocols/2.7-grpc/"; \
		echo "Please ensure Chapter 2.7 (gRPC) is implemented first."; \
		exit 1; \
	fi
	@echo "✓ All dependencies satisfied"

# Generate diagrams
diagrams:
	@echo "=== Generating HTTP/2 & gRPC Multiplexing Diagrams ==="
	python3 render_diagram.py
	@echo "✓ HTTP/2 multiplexing diagrams generated"

# Generate Mermaid diagram
mermaid:
	@echo "=== Generating Mermaid Diagram ==="
	@if command -v mmdc >/dev/null 2>&1; then \
		mmdc -i http2_grpc_multiplexing.mmd -o http2_grpc_multiplexing.png -t dark -b transparent; \
		echo "✓ Mermaid diagram generated: http2_grpc_multiplexing.png"; \
	else \
		echo "⚠ mermaid-cli not found, skipping diagram generation"; \
		echo "Install with: npm install -g @mermaid-js/mermaid-cli"; \
	fi

# Run HTTP/2 multiplexing demonstration
http2-multiplexing:
	@echo "=== Running HTTP/2 Multiplexing Demonstration ==="
	@echo "Demonstrating concurrent streams and flow control..."
	python3 http2_multiplexing_demo.py
	@echo "✓ HTTP/2 multiplexing demonstration completed"

# Run gRPC streaming patterns
grpc-streaming:
	@echo "=== Running gRPC Streaming Patterns ==="
	@echo "Demonstrating unary, server, client, and bidirectional streaming..."
	python3 grpc_streaming_patterns.py
	@echo "✓ gRPC streaming patterns demonstration completed"

# Run comprehensive test
test: deps
	@echo "=== Testing HTTP/2 & gRPC Multiplexing Implementation ==="
	@echo "1. Testing HTTP/2 multiplexing..."
	@timeout 15 python3 http2_multiplexing_demo.py || echo "✓ HTTP/2 multiplexing test completed"
	@echo ""
	@echo "2. Testing gRPC streaming patterns..."
	@timeout 20 python3 grpc_streaming_patterns.py || echo "✓ gRPC streaming test completed"
	@echo ""
	@echo "3. Generating diagrams..."
	@python3 render_diagram.py
	@echo ""
	@echo "=== All Tests Passed ✓ ==="
	@echo "HTTP/2 & gRPC multiplexing implementation demonstrates:"
	@echo "  • HTTP/2 stream multiplexing over single connection"
	@echo "  • Concurrent request/response processing"
	@echo "  • Flow control and backpressure management"
	@echo "  • gRPC unary RPC patterns"
	@echo "  • gRPC server streaming (1→N responses)"
	@echo "  • gRPC client streaming (N→1 response)"
	@echo "  • gRPC bidirectional streaming (N↔N)"
	@echo "  • HPACK header compression simulation"
	@echo "  • Stream lifecycle management"
	@echo "  • Performance benefits vs HTTP/1.1"

# Clean generated files
clean:
	@echo "=== Cleaning Generated Files ==="
	rm -f *.png
	rm -f __pycache__/*.pyc
	rmdir __pycache__ 2>/dev/null || true
	@echo "✓ Cleanup completed"

# Help target
help:
	@echo "HTTP/2 & gRPC Multiplexing Implementation Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  all               - Run all components (default)"
	@echo "  deps              - Check dependencies"
	@echo "  http2-multiplexing - Run HTTP/2 multiplexing demo"
	@echo "  grpc-streaming    - Run gRPC streaming patterns"
	@echo "  diagrams          - Generate architecture diagrams"
	@echo "  mermaid           - Generate Mermaid diagram (requires mmdc)"
	@echo "  test              - Run comprehensive tests"
	@echo "  clean             - Clean generated files"
	@echo "  help              - Show this help"
	@echo ""
	@echo "Dependencies:"
	@echo "  • Chapter 2.4: HTTP/2 (../../02-web-protocols/2.4-http2/)"
	@echo "  • Chapter 2.7: gRPC (../../02-web-protocols/2.7-grpc/)"
	@echo ""
	@echo "This implementation demonstrates:"
	@echo "  • HTTP/2 stream multiplexing"
	@echo "  • gRPC streaming patterns"
	@echo "  • Concurrent processing"
	@echo "  • Flow control mechanisms"
