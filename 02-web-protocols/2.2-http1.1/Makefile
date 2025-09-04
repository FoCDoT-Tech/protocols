# HTTP/1.1 Protocol Demonstration Makefile
# Runs all HTTP/1.1 simulations and generates diagrams

.PHONY: all test clean diagrams client-server rest-api performance

# Default target
all: diagrams test

# Generate all diagrams
diagrams:
	@echo "=== Generating HTTP/1.1 Diagrams ==="
	python3 render_diagram.py

# Run HTTP client-server simulation
client-server:
	@echo "=== HTTP/1.1 Client-Server Communication ==="
	python3 http_client_server.py

# Run REST API simulation
rest-api:
	@echo "=== HTTP/1.1 RESTful API Simulation ==="
	python3 http_rest_api.py

# Run performance analysis
performance:
	@echo "=== HTTP/1.1 Performance Analysis ==="
	python3 http_performance.py

# Run all tests
test: client-server rest-api performance
	@echo "=== All HTTP/1.1 tests completed successfully! ==="

# Clean generated files
clean:
	@echo "=== Cleaning HTTP/1.1 generated files ==="
	rm -f *.png
	rm -f *.pyc
	rm -rf __pycache__

# Help target
help:
	@echo "Available targets:"
	@echo "  all          - Generate diagrams and run all tests (default)"
	@echo "  diagrams     - Generate HTTP/1.1 protocol diagrams"
	@echo "  client-server - Run HTTP client-server simulation"
	@echo "  rest-api     - Run RESTful API simulation"
	@echo "  performance  - Run HTTP performance analysis"
	@echo "  test         - Run all simulations"
	@echo "  clean        - Remove generated files"
	@echo "  help         - Show this help message"
