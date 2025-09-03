# UDP Subchapter Makefile
# Runs all Python scripts and generates diagrams

.PHONY: all run diagrams clean test

# Default target
all: run diagrams

# Run all Python scripts
run:
	@echo "Running UDP demonstrations..."
	@echo "=== UDP Client-Server Communication ==="
	@python3 udp_client_server.py
	@echo "\n=== UDP Gaming Protocol ==="
	@python3 udp_gaming.py
	@echo "\n=== UDP Streaming Applications ==="
	@python3 udp_streaming.py

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
