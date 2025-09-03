# QUIC Subchapter Makefile
# Runs all Python scripts and generates diagrams

.PHONY: all run diagrams clean test

# Default target
all: run diagrams

# Run all Python scripts
run:
	@echo "Running QUIC demonstrations..."
	@echo "=== QUIC Handshake and Connection Management ==="
	@python3 quic_handshake.py
	@echo "\n=== QUIC Stream Multiplexing ==="
	@python3 quic_streams.py
	@echo "\n=== QUIC Performance Analysis ==="
	@python3 quic_performance.py

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
