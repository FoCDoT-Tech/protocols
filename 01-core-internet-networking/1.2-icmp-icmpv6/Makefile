# ICMP / ICMPv6 Subchapter Makefile
# Runs all Python scripts and generates diagrams

.PHONY: all run diagrams clean test

# Default target
all: run diagrams

# Run all Python scripts
run:
	@echo "Running ICMP/ICMPv6 demonstrations..."
	@echo "=== ICMP Ping Simulation ==="
	@python3 icmp_ping.py
	@echo "\n=== ICMP Traceroute Simulation ==="
	@python3 icmp_traceroute.py
	@echo "\n=== ICMPv6 Neighbor Discovery ==="
	@python3 neighbor_discovery.py

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
