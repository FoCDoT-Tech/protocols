# GraphQL Protocol Subchapter Makefile
# Demonstrates GraphQL query language, schema, real-time subscriptions

.PHONY: all server client subscriptions diagrams test clean dependencies

# Check dependencies
dependencies:
	@echo "Checking GraphQL subchapter dependencies..."
	@if [ ! -f "../2.2-http1.1/Makefile" ]; then \
		echo "❌ Error: HTTP/1.1 subchapter (2.2) must be completed first"; \
		exit 1; \
	fi
	@echo "✅ Dependencies satisfied: HTTP/1.1 available"

# Run GraphQL server simulation
server: dependencies
	@echo "🚀 Running GraphQL server simulation..."
	@python3 graphql_server.py

# Run GraphQL client simulation
client: dependencies
	@echo "📱 Running GraphQL client simulation..."
	@python3 graphql_client.py

# Run GraphQL subscriptions demo
subscriptions: dependencies
	@echo "📡 Running GraphQL subscriptions demo..."
	@python3 graphql_subscriptions.py

# Generate all diagrams
diagrams: dependencies
	@echo "📊 Generating GraphQL protocol diagrams..."
	@python3 render_diagram.py

# Run all tests and demos
test: dependencies server client subscriptions diagrams
	@echo ""
	@echo "=== GraphQL Protocol Test Summary ==="
	@echo "✅ GraphQL server simulation completed"
	@echo "✅ GraphQL client simulation completed"
	@echo "✅ GraphQL subscriptions demo completed"
	@echo "✅ Protocol diagrams generated"
	@echo ""
	@echo "📋 Generated files:"
	@ls -la *.png 2>/dev/null || echo "No diagram files found"
	@echo ""
	@echo "🎯 GraphQL subchapter validation complete!"
	@echo "   - Single endpoint with flexible queries"
	@echo "   - Strong type system and schema validation"
	@echo "   - Real-time subscriptions via WebSocket"
	@echo "   - Efficient data fetching and performance"

# Run everything
all: test

# Clean generated files
clean:
	@echo "🧹 Cleaning GraphQL generated files..."
	@rm -f *.png
	@echo "✅ Cleanup complete"
