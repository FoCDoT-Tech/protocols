# HTTP/2 Protocol Implementation and Testing
# Dependencies: HTTP/1.1 (2.2), TLS (2.3)

.PHONY: all test clean diagrams deps

# Check dependencies first
deps:
	@echo "Checking HTTP/2 dependencies..."
	@if [ ! -f "../2.2-http1.1/Makefile" ]; then \
		echo "❌ HTTP/1.1 dependency missing (required for HTTP/2)"; \
		exit 1; \
	fi
	@if [ ! -f "../2.3-tls/Makefile" ]; then \
		echo "❌ TLS dependency missing (required for HTTP/2)"; \
		exit 1; \
	fi
	@echo "✓ All dependencies satisfied"

# Run all HTTP/2 demonstrations
all: deps test

test: deps
	@echo "🚀 Running HTTP/2 Protocol Demonstrations..."
	@echo
	@echo "=== HTTP/2 Stream Multiplexing ==="
	@python3 http2_multiplexing.py
	@echo
	@echo "=== HTTP/2 Performance Analysis ==="
	@python3 http2_performance.py
	@echo
	@echo "=== HTTP/2 Server Push ==="
	@python3 http2_server_push.py
	@echo
	@echo "=== HTTP/2 Diagrams ==="
	@python3 render_diagram.py
	@echo
	@echo "✅ All HTTP/2 demonstrations completed successfully!"

# Generate diagrams only
diagrams:
	@echo "📊 Generating HTTP/2 diagrams..."
	@python3 render_diagram.py

# Individual test targets
multiplexing:
	@echo "Testing HTTP/2 multiplexing..."
	@python3 http2_multiplexing.py

performance:
	@echo "Testing HTTP/2 performance..."
	@python3 http2_performance.py

server-push:
	@echo "Testing HTTP/2 server push..."
	@python3 http2_server_push.py

# Clean generated files
clean:
	@echo "🧹 Cleaning HTTP/2 generated files..."
	@rm -f *.png
	@rm -f *.pyc
	@rm -rf __pycache__
	@echo "✓ Cleanup completed"

# Help target
help:
	@echo "HTTP/2 Protocol Makefile"
	@echo "Dependencies: HTTP/1.1 (2.2), TLS (2.3)"
	@echo ""
	@echo "Available targets:"
	@echo "  all          - Run all HTTP/2 demonstrations (default)"
	@echo "  test         - Run all tests and demonstrations"
	@echo "  deps         - Check dependencies"
	@echo "  diagrams     - Generate HTTP/2 protocol diagrams"
	@echo "  multiplexing - Test HTTP/2 multiplexing features"
	@echo "  performance  - Test HTTP/2 performance analysis"
	@echo "  server-push  - Test HTTP/2 server push"
	@echo "  clean        - Remove generated files"
	@echo "  help         - Show this help message"
