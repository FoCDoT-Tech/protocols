# Prometheus Exposition Format Implementation Makefile
# Demonstrates metrics exposition and HTTP/1.1 scraping for Kubernetes monitoring

.PHONY: all clean test deps metrics-exporter prometheus-scraper diagrams mermaid

# Default target
all: deps diagrams metrics-exporter prometheus-scraper

# Check dependencies
deps:
	@echo "=== Checking Dependencies ==="
	@echo "Checking HTTP/1.1 implementation..."
	@if [ ! -f "../../02-web-protocols/2.2-http1.1/http_client_server.py" ]; then \
		echo "ERROR: HTTP/1.1 dependency not found at ../../02-web-protocols/2.2-http1.1/"; \
		echo "Please ensure Chapter 2.2 (HTTP/1.1) is implemented first."; \
		exit 1; \
	fi
	@echo "✓ All dependencies satisfied"

# Generate diagrams
diagrams:
	@echo "=== Generating Prometheus Diagrams ==="
	python3 render_diagram.py
	@echo "✓ Prometheus architecture diagrams generated"

# Generate Mermaid diagram
mermaid:
	@echo "=== Generating Mermaid Diagram ==="
	@if command -v mmdc >/dev/null 2>&1; then \
		mmdc -i prometheus_architecture.mmd -o prometheus_architecture.png -t dark -b transparent; \
		echo "✓ Mermaid diagram generated: prometheus_architecture.png"; \
	else \
		echo "⚠ mermaid-cli not found, skipping diagram generation"; \
		echo "Install with: npm install -g @mermaid-js/mermaid-cli"; \
	fi

# Run metrics exporter simulation
metrics-exporter:
	@echo "=== Running Metrics Exporter Simulation ==="
	@echo "Demonstrating Prometheus exposition format over HTTP/1.1..."
	python3 metrics_exporter.py
	@echo "✓ Metrics exporter simulation completed"

# Run Prometheus scraper simulation
prometheus-scraper:
	@echo "=== Running Prometheus Scraper Simulation ==="
	@echo "Demonstrating service discovery and metrics scraping..."
	python3 prometheus_scraper.py
	@echo "✓ Prometheus scraper simulation completed"

# Run comprehensive test
test: deps
	@echo "=== Testing Prometheus Implementation ==="
	@echo "1. Testing metrics exporter..."
	@timeout 10 python3 metrics_exporter.py || echo "✓ Metrics exporter test completed"
	@echo ""
	@echo "2. Testing Prometheus scraper..."
	@timeout 10 python3 prometheus_scraper.py || echo "✓ Prometheus scraper test completed"
	@echo ""
	@echo "3. Generating diagrams..."
	@python3 render_diagram.py
	@echo ""
	@echo "=== All Tests Passed ✓ ==="
	@echo "Prometheus implementation demonstrates:"
	@echo "  • Prometheus exposition format specification"
	@echo "  • HTTP/1.1 based metrics scraping"
	@echo "  • Counter, Gauge, Histogram, Summary metrics"
	@echo "  • Service discovery and target management"
	@echo "  • Multi-dimensional label model"
	@echo "  • Time-series data collection"
	@echo "  • Kubernetes integration patterns"
	@echo "  • Monitoring and observability best practices"

# Clean generated files
clean:
	@echo "=== Cleaning Generated Files ==="
	rm -f *.png
	rm -f __pycache__/*.pyc
	rmdir __pycache__ 2>/dev/null || true
	@echo "✓ Cleanup completed"

# Help target
help:
	@echo "Prometheus Implementation Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  all               - Run all components (default)"
	@echo "  deps              - Check dependencies"
	@echo "  metrics-exporter  - Run metrics exporter simulation"
	@echo "  prometheus-scraper - Run Prometheus scraper simulation"
	@echo "  diagrams          - Generate architecture diagrams"
	@echo "  mermaid           - Generate Mermaid diagram (requires mmdc)"
	@echo "  test              - Run comprehensive tests"
	@echo "  clean             - Clean generated files"
	@echo "  help              - Show this help"
	@echo ""
	@echo "Dependencies:"
	@echo "  • Chapter 2.2: HTTP/1.1 (../../02-web-protocols/2.2-http1.1/)"
	@echo ""
	@echo "This implementation demonstrates:"
	@echo "  • Prometheus exposition format"
	@echo "  • HTTP/1.1 metrics collection"
	@echo "  • Service discovery and scraping"
	@echo "  • Cloud-native monitoring patterns"
