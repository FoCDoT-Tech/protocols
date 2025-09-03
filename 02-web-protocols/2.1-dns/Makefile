# DNS Subchapter Makefile
# Runs all Python scripts and generates diagrams

.PHONY: all run diagrams clean test

# Default target
all: run diagrams

# Run all Python scripts
run:
	@echo "Running DNS demonstrations..."
	@echo "=== DNS Resolver and Query Process ==="
	@python3 dns_resolver.py
	@echo "\n=== DNS Security and DNSSEC ==="
	@python3 dns_security.py
	@echo "\n=== DNS for Microservices ==="
	@python3 dns_microservices.py

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
