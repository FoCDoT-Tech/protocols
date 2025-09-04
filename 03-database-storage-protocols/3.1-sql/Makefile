# SQL Wire Protocol Subchapter Makefile
# Demonstrates SQL database protocols, connection pooling, and performance optimization

.PHONY: all test clean protocols pooling diagrams dependencies

# Check dependencies (TCP must exist)
dependencies:
	@echo "🔍 Checking SQL dependencies..."
	@if [ ! -f "../../01-core-internet-networking/1.3-tcp/Makefile" ]; then \
		echo "❌ TCP dependency missing"; exit 1; \
	fi
	@echo "✅ Dependencies satisfied: TCP"

# Run SQL wire protocol simulation
protocols:
	@echo "📡 Running SQL wire protocol simulation..."
	@python3 sql_wire_protocol.py

# Run connection pooling demonstration
pooling:
	@echo "🔄 Running connection pooling demonstration..."
	@python3 sql_connection_pool.py

# Generate SQL protocol diagrams
diagrams:
	@echo "🎨 Generating SQL protocol diagrams..."
	@python3 render_diagram.py

# Run all SQL demonstrations
all: dependencies protocols pooling diagrams
	@echo ""
	@echo "=== SQL Wire Protocol Subchapter Complete ==="
	@echo "✅ Wire protocol implementations demonstrated"
	@echo "✅ Connection pooling patterns shown"
	@echo "✅ Visual diagrams generated"
	@echo "🗄️ SQL protocols enable efficient database communication"

# Test all components
test: all
	@echo "🧪 Testing SQL components..."
	@python3 -c "\
import sys; \
sys.path.append('.'); \
from sql_wire_protocol import SQLWireProtocol; \
from sql_connection_pool import ConnectionPool, DatabaseLoadTester; \
mysql_protocol = SQLWireProtocol('mysql'); \
mysql_results = mysql_protocol.demonstrate_sql_protocols(); \
assert len(mysql_results) == 4, 'MySQL should have 4 protocol results'; \
pool = ConnectionPool('postgresql', min_size=2, max_size=5); \
load_tester = DatabaseLoadTester(pool); \
load_results = load_tester.simulate_load(num_requests=10, concurrent_threads=2); \
assert load_results['total_requests'] == 10, 'Load test should execute 10 requests'; \
print('✅ All SQL tests passed')"
	@echo "✅ SQL wire protocol tests completed successfully"

# Clean generated files
clean:
	@echo "🧹 Cleaning SQL generated files..."
	@rm -f *.png
	@echo "✅ Cleanup complete"
