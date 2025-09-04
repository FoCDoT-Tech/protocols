.PHONY: all clean test client multipart analytics diagrams deps

# S3 API Protocol Subchapter
# Dependencies: HTTP/1.1 (2.2), TLS (2.3)

all: deps client multipart analytics diagrams test

deps:
	@echo "🔍 Checking dependencies for S3 API Protocol..."
	@if [ ! -f "../../02-web-protocols/2.2-http1.1/http_client_server.py" ]; then \
		echo "❌ Missing dependency: HTTP/1.1 (2.2) - run 'make' in 02-web-protocols/2.2-http1.1 first"; \
		exit 1; \
	fi
	@if [ ! -f "../../02-web-protocols/2.3-tls/tls_handshake.py" ]; then \
		echo "❌ Missing dependency: TLS (2.3) - run 'make' in 02-web-protocols/2.3-tls first"; \
		exit 1; \
	fi
	@echo "✅ All dependencies satisfied"

client:
	@echo "☁️ Running S3 API client simulation..."
	@python3 s3_client.py

multipart:
	@echo "📦 Running S3 multipart upload demonstration..."
	@python3 s3_multipart.py

analytics:
	@echo "📊 Running S3 storage analytics..."
	@python3 s3_analytics.py

diagrams:
	@echo "🎨 Generating S3 API protocol diagrams..."
	@python3 render_diagram.py
	@if command -v mmdc >/dev/null 2>&1; then \
		echo "📊 Rendering Mermaid diagram..."; \
		mmdc -i s3_api_protocol.mmd -o s3_api_protocol_mermaid.png; \
	else \
		echo "⚠️  Mermaid CLI not found, skipping .mmd rendering"; \
	fi

test:
	@echo "🧪 Testing S3 API Protocol implementation..."
	@python3 -c "\
import s3_client as s3c; \
import s3_multipart as s3m; \
import s3_analytics as s3a; \
from s3_client import S3StorageClass, S3Client; \
client = s3c.S3Client('https://s3.amazonaws.com', 'test-bucket'); \
client.authenticate('test-key', 'test-secret'); \
assert client.authenticated == True; \
assert client.bucket == 'test-bucket'; \
print('✅ S3 Client: initialization and authentication tests passed'); \
uploader = s3m.S3MultipartUploader(client, 'test-file.dat'); \
assert uploader.key == 'test-file.dat'; \
assert uploader.chunk_size == 5 * 1024 * 1024; \
print('✅ S3 Multipart: uploader initialization tests passed'); \
analytics = s3a.S3Analytics(client); \
assert len(analytics.storage_costs) == 5; \
assert 'STANDARD' in analytics.storage_costs; \
print('✅ S3 Analytics: cost analysis tests passed'); \
print('🎯 All S3 API Protocol tests passed!')"

clean:
	@echo "🧹 Cleaning up generated files..."
	@rm -f *.png
	@rm -rf __pycache__/
	@echo "✅ Cleanup completed"

summary:
	@echo ""
	@echo "=== S3 API Protocol Summary ==="
	@echo "📋 Protocol: Amazon S3 Compatible Storage API"
	@echo "🎯 Purpose: Scalable cloud object storage with REST API"
	@echo "🔧 Features: Bucket/object operations, multipart uploads, lifecycle management"
	@echo "⚡ Performance: Multi-GB/s throughput, global distribution, 99.999999999% durability"
	@echo "🌐 Use Cases: Web assets, backups, data lakes, content distribution"
	@echo ""
