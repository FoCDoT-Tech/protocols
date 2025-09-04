# OAuth 2.0 Protocol Subchapter Makefile
# Demonstrates OAuth authorization flows, security features, and token management

.PHONY: all server client security diagrams test clean dependencies

# Check dependencies
dependencies:
	@echo "Checking OAuth subchapter dependencies..."
	@if [ ! -f "../2.2-http1.1/Makefile" ]; then \
		echo "❌ Error: HTTP/1.1 subchapter (2.2) must be completed first"; \
		exit 1; \
	fi
	@if [ ! -f "../2.3-tls/Makefile" ]; then \
		echo "❌ Error: TLS subchapter (2.3) must be completed first"; \
		exit 1; \
	fi
	@echo "✅ Dependencies satisfied: HTTP/1.1 and TLS available"

# Run OAuth authorization server simulation
server: dependencies
	@echo "🔐 Running OAuth authorization server simulation..."
	@python3 oauth_server.py

# Run OAuth client application simulation
client: dependencies
	@echo "📱 Running OAuth client application simulation..."
	@python3 oauth_client.py

# Run OAuth security analysis
security: dependencies
	@echo "🛡️ Running OAuth security analysis..."
	@python3 oauth_security.py

# Generate all diagrams
diagrams: dependencies
	@echo "📊 Generating OAuth protocol diagrams..."
	@python3 render_diagram.py

# Run all tests and demos
test: dependencies server client security diagrams
	@echo ""
	@echo "=== OAuth 2.0 Protocol Test Summary ==="
	@echo "✅ OAuth authorization server simulation completed"
	@echo "✅ OAuth client application simulation completed"
	@echo "✅ OAuth security analysis completed"
	@echo "✅ Protocol diagrams generated"
	@echo ""
	@echo "📋 Generated files:"
	@ls -la *.png 2>/dev/null || echo "No diagram files found"
	@echo ""
	@echo "🎯 OAuth subchapter validation complete!"
	@echo "   - Authorization Code flow with PKCE protection"
	@echo "   - Client Credentials flow for service-to-service"
	@echo "   - Comprehensive security threat analysis"
	@echo "   - Token lifecycle and refresh mechanisms"

# Run everything
all: test

# Clean generated files
clean:
	@echo "🧹 Cleaning OAuth generated files..."
	@rm -f *.png
	@echo "✅ Cleanup complete"
