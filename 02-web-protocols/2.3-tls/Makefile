# TLS Protocol Demonstration Makefile
# Runs all TLS simulations and generates diagrams

.PHONY: all test clean diagrams handshake security implementation

# Default target
all: diagrams test

# Generate all diagrams
diagrams:
	@echo "=== Generating TLS Diagrams ==="
	python3 render_diagram.py

# Run TLS handshake simulation
handshake:
	@echo "=== TLS Handshake Simulation ==="
	python3 tls_handshake.py

# Run TLS security analysis
security:
	@echo "=== TLS Security Features Analysis ==="
	python3 tls_security.py

# Run TLS implementation patterns
implementation:
	@echo "=== TLS Implementation Patterns ==="
	python3 tls_implementation.py

# Run all tests
test: handshake security implementation
	@echo "=== All TLS tests completed successfully! ==="

# Clean generated files
clean:
	@echo "=== Cleaning TLS generated files ==="
	rm -f *.png
	rm -f *.pyc
	rm -rf __pycache__

# Help target
help:
	@echo "Available targets:"
	@echo "  all          - Generate diagrams and run all tests (default)"
	@echo "  diagrams     - Generate TLS protocol diagrams"
	@echo "  handshake    - Run TLS handshake simulation"
	@echo "  security     - Run TLS security analysis"
	@echo "  implementation - Run TLS implementation patterns"
	@echo "  test         - Run all simulations"
	@echo "  clean        - Remove generated files"
	@echo "  help         - Show this help message"
