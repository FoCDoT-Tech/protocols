# IPv4 & IPv6 Subchapter Makefile
# Runs all Python scripts and generates diagrams

.PHONY: all run diagrams clean test

# Default target
all: run diagrams

# Run all Python scripts
run:
	@echo "Running IPv4/IPv6 demonstrations..."
	@echo "=== IPv4 Packet Parser ==="
	@python3 ipv4_packet_parser.py
	@echo "\n=== IPv6 Packet Parser ==="
	@python3 ipv6_packet_parser.py
	@echo "\n=== Network Simulation ==="
	@python3 network_simulation.py

# Generate Mermaid diagrams
diagrams:
	@echo "Generating diagrams..."
	@for f in *.mmd; do \
		if [ -f "$$f" ]; then \
			echo "Rendering $$f"; \
			python3 render_diagram.py "$$f" || exit 1; \
		fi; \
	done

# Test that all components work
test: run diagrams
	@echo "All tests passed successfully!"

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	@rm -f *.pyc
	@rm -rf __pycache__
	@rm -f *.png
	@rm -f *.txt
