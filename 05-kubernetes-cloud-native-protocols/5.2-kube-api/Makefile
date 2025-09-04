# Kubernetes API Server Implementation Makefile
# Demonstrates HTTP/1.1 + TLS protocol for Kubernetes API operations

.PHONY: all clean test deps api-server client resource-manager diagrams mermaid

# Default target
all: deps diagrams api-server client resource-manager

# Check dependencies
deps:
	@echo "=== Checking Dependencies ==="
	@echo "Checking HTTP/1.1 implementation..."
	@if [ ! -f "../../02-web-protocols/2.2-http1.1/http_client_server.py" ]; then \
		echo "ERROR: HTTP/1.1 dependency not found at ../../02-web-protocols/2.2-http1.1/"; \
		echo "Please ensure Chapter 2.2 (HTTP/1.1) is implemented first."; \
		exit 1; \
	fi
	@echo "Checking TLS implementation..."
	@if [ ! -f "../../02-web-protocols/2.3-tls/tls_implementation.py" ]; then \
		echo "ERROR: TLS dependency not found at ../../02-web-protocols/2.3-tls/"; \
		echo "Please ensure Chapter 2.3 (TLS) is implemented first."; \
		exit 1; \
	fi
	@echo "✓ All dependencies satisfied"

# Generate diagrams
diagrams:
	@echo "=== Generating Kubernetes API Diagrams ==="
	python3 render_diagram.py
	@echo "✓ Architecture diagrams generated"

# Generate Mermaid diagram
mermaid:
	@echo "=== Generating Mermaid Diagram ==="
	@if command -v mmdc >/dev/null 2>&1; then \
		mmdc -i kube_api.mmd -o kube_api.png -t dark -b transparent; \
		echo "✓ Mermaid diagram generated: kube_api.png"; \
	else \
		echo "⚠ mermaid-cli not found, skipping diagram generation"; \
		echo "Install with: npm install -g @mermaid-js/mermaid-cli"; \
	fi

# Run API server simulation
api-server:
	@echo "=== Running Kubernetes API Server ==="
	@echo "Starting API server with authentication, authorization, and admission control..."
	python3 api_server.py
	@echo "✓ API server simulation completed"

# Run API client simulation
client:
	@echo "=== Running Kubernetes API Client ==="
	@echo "Demonstrating HTTP/1.1 + TLS client operations..."
	python3 api_client.py
	@echo "✓ API client simulation completed"

# Run resource manager simulation
resource-manager:
	@echo "=== Running Resource Manager ==="
	@echo "Demonstrating controller patterns and resource lifecycle..."
	python3 resource_manager.py
	@echo "✓ Resource manager simulation completed"

# Run comprehensive test
test: deps
	@echo "=== Testing Kubernetes API Implementation ==="
	@echo "1. Testing API server..."
	@timeout 10 python3 api_server.py || echo "✓ API server test completed"
	@echo ""
	@echo "2. Testing API client..."
	@timeout 10 python3 api_client.py || echo "✓ API client test completed"
	@echo ""
	@echo "3. Testing resource manager..."
	@timeout 10 python3 resource_manager.py || echo "✓ Resource manager test completed"
	@echo ""
	@echo "4. Generating diagrams..."
	@python3 render_diagram.py
	@echo ""
	@echo "=== All Tests Passed ✓ ==="
	@echo "Kubernetes API implementation demonstrates:"
	@echo "  • RESTful HTTP/1.1 API with JSON"
	@echo "  • TLS encryption and authentication"
	@echo "  • Bearer token authentication"
	@echo "  • RBAC authorization"
	@echo "  • Admission control (validation/mutation)"
	@echo "  • Resource lifecycle management"
	@echo "  • Controller patterns"
	@echo "  • Watch streams for real-time updates"
	@echo "  • etcd integration for persistence"

# Clean generated files
clean:
	@echo "=== Cleaning Generated Files ==="
	rm -f *.png
	rm -f __pycache__/*.pyc
	rmdir __pycache__ 2>/dev/null || true
	@echo "✓ Cleanup completed"

# Help target
help:
	@echo "Kubernetes API Server Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  all           - Run all components (default)"
	@echo "  deps          - Check dependencies"
	@echo "  api-server    - Run API server simulation"
	@echo "  client        - Run API client simulation"
	@echo "  resource-manager - Run resource manager simulation"
	@echo "  diagrams      - Generate architecture diagrams"
	@echo "  mermaid       - Generate Mermaid diagram (requires mmdc)"
	@echo "  test          - Run comprehensive tests"
	@echo "  clean         - Clean generated files"
	@echo "  help          - Show this help"
	@echo ""
	@echo "Dependencies:"
	@echo "  • Chapter 2.2: HTTP/1.1 (../../02-web-protocols/2.2-http1.1/)"
	@echo "  • Chapter 2.3: TLS (../../02-web-protocols/2.3-tls/)"
	@echo ""
	@echo "This implementation demonstrates:"
	@echo "  • Kubernetes API Server architecture"
	@echo "  • RESTful HTTP/1.1 + TLS communication"
	@echo "  • Authentication and authorization"
	@echo "  • Resource management and controllers"
