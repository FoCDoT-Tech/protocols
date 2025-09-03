# TCP Subchapter Makefile
# Runs all Python scripts and generates diagrams

.PHONY: all run diagrams clean test

# Default target
all: run diagrams

# Run all Python scripts
run:
	@echo "Running TCP demonstrations..."
	@echo "=== TCP Handshake Simulation ==="
	@python3 tcp_handshake.py
	@echo "\n=== TCP Flow Control ==="
	@python3 tcp_flow_control.py
	@echo "\n=== TCP Performance Optimization ==="
	@python3 tcp_performance.py

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
