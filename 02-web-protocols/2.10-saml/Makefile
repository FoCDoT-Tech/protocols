# SAML 2.0 Subchapter Makefile
# Demonstrates SAML Identity Provider, Service Provider, and Federation flows

.PHONY: all test clean idp sp federation diagrams dependencies

# Check dependencies (HTTP/1.1 and TLS must exist)
dependencies:
	@echo "🔍 Checking SAML dependencies..."
	@if [ ! -f "../2.2-http1.1/Makefile" ]; then \
		echo "❌ HTTP/1.1 dependency missing"; exit 1; \
	fi
	@if [ ! -f "../2.3-tls/Makefile" ]; then \
		echo "❌ TLS dependency missing"; exit 1; \
	fi
	@echo "✅ Dependencies satisfied: HTTP/1.1, TLS"

# Run SAML Identity Provider simulation
idp:
	@echo "🏢 Running SAML Identity Provider simulation..."
	@python3 saml_idp.py

# Run SAML Service Provider simulation  
sp:
	@echo "📱 Running SAML Service Provider simulation..."
	@python3 saml_sp.py

# Run SAML Federation scenarios
federation:
	@echo "🤝 Running SAML Federation scenarios..."
	@python3 saml_federation.py

# Generate SAML diagrams
diagrams:
	@echo "🎨 Generating SAML diagrams..."
	@python3 render_diagram.py

# Run all SAML demonstrations
all: dependencies idp sp federation diagrams
	@echo ""
	@echo "=== SAML 2.0 Subchapter Complete ==="
	@echo "✅ Identity Provider flows demonstrated"
	@echo "✅ Service Provider integration shown"
	@echo "✅ Federation scenarios executed"
	@echo "✅ Visual diagrams generated"
	@echo "🔐 SAML 2.0 enables secure enterprise SSO and federation"

# Test all components
test: all
	@echo "🧪 Testing SAML components..."
	@python3 -c "\
import sys; \
sys.path.append('.'); \
from saml_idp import SAMLIdentityProvider; \
from saml_sp import SAMLServiceProvider; \
from saml_federation import SAMLFederation; \
idp = SAMLIdentityProvider(); \
idp_results = idp.demonstrate_saml_idp_flows(); \
assert len(idp_results) == 4, 'IdP should have 4 flow results'; \
sp = SAMLServiceProvider('https://app.example.com', 'https://idp.example.com'); \
sp_results = sp.demonstrate_saml_sp_flows(); \
assert len(sp_results) == 4, 'SP should have 4 flow results'; \
federation = SAMLFederation(); \
fed_results = federation.demonstrate_saml_federation(); \
assert len(fed_results) == 4, 'Federation should have 4 scenario results'; \
print('✅ All SAML tests passed')"
	@echo "✅ SAML 2.0 tests completed successfully"

# Clean generated files
clean:
	@echo "🧹 Cleaning SAML generated files..."
	@rm -f *.png
	@echo "✅ Cleanup complete"
