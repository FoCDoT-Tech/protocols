# HTTP/3 Protocol Implementation and Testing
# Dependencies: QUIC (1.5), HTTP/2 (2.4)

.PHONY: all test clean diagrams deps

# Check dependencies first
deps:
	@echo "Checking HTTP/3 dependencies..."
	@if [ ! -f "../../01-core-internet-networking/1.5-quic/Makefile" ]; then \
		echo "❌ QUIC dependency missing (required for HTTP/3)"; \
		exit 1; \
	fi
	@if [ ! -f "../2.4-http2/Makefile" ]; then \
		echo "❌ HTTP/2 dependency missing (required for HTTP/3)"; \
		exit 1; \
	fi
	@echo "✓ All dependencies satisfied"

# Run all HTTP/3 demonstrations
all: deps test

test: deps
	@echo "🚀 Running HTTP/3 Protocol Demonstrations..."
	@echo
	@echo "=== HTTP/3 Connection Management ==="
	@python3 http3_connection.py
	@echo
	@echo "=== HTTP/3 Performance Analysis ==="
	@python3 http3_performance.py
	@echo
	@echo "=== HTTP/3 Connection Migration ==="
	@python3 http3_migration.py
	@echo
	@echo "=== HTTP/3 Diagrams ==="
	@python3 render_diagram.py
	@echo
	@echo "✅ All HTTP/3 demonstrations completed successfully!"

# Generate diagrams only
diagrams:
	@echo "📊 Generating HTTP/3 diagrams..."
	@python3 render_diagram.py

# Individual test targets
connection:
	@echo "Testing HTTP/3 connection management..."
	@python3 http3_connection.py

performance:
	@echo "Testing HTTP/3 performance..."
	@python3 http3_performance.py

migration:
	@echo "Testing HTTP/3 connection migration..."
	@python3 http3_migration.py

# Clean generated files
clean:
	@echo "🧹 Cleaning HTTP/3 generated files..."
	@rm -f *.png
	@rm -f *.pyc
	@rm -rf __pycache__
	@echo "✓ Cleanup completed"

# Help target
help:
	@echo "HTTP/3 Protocol Makefile"
	@echo "Dependencies: QUIC (1.5), HTTP/2 (2.4)"
	@echo ""
	@echo "Available targets:"
	@echo "  all          - Run all HTTP/3 demonstrations (default)"
	@echo "  test         - Run all tests and demonstrations"
	@echo "  deps         - Check dependencies"
	@echo "  diagrams     - Generate HTTP/3 protocol diagrams"
	@echo "  connection   - Test HTTP/3 connection management"
	@echo "  performance  - Test HTTP/3 performance analysis"
	@echo "  migration    - Test HTTP/3 connection migration"
	@echo "  clean        - Remove generated files"
	@echo "  help         - Show this help message"
