.PHONY: all clean test nfs smb monitor diagrams deps

# NFS & SMB Network File System Protocols Subchapter
# Dependencies: TCP (1.3), UDP (1.4)

all: deps nfs smb monitor diagrams test

deps:
	@echo "🔍 Checking dependencies for NFS & SMB protocols..."
	@if [ ! -f "../../01-core-internet-networking/1.3-tcp/tcp_simulation.py" ]; then \
		echo "❌ Missing dependency: TCP (1.3) - run 'make' in 01-core-internet-networking/1.3-tcp first"; \
		exit 1; \
	fi
	@if [ ! -f "../../01-core-internet-networking/1.4-udp/udp_simulation.py" ]; then \
		echo "❌ Missing dependency: UDP (1.4) - run 'make' in 01-core-internet-networking/1.4-udp first"; \
		exit 1; \
	fi
	@echo "✅ All dependencies satisfied"

nfs:
	@echo "📁 Running NFS protocol simulation..."
	@python3 nfs_client.py

smb:
	@echo "🖥️ Running SMB protocol simulation..."
	@python3 smb_client.py

monitor:
	@echo "📊 Running file system performance monitoring..."
	@python3 file_system_monitor.py

diagrams:
	@echo "🎨 Generating NFS & SMB protocol diagrams..."
	@python3 render_diagram.py
	@if command -v mmdc >/dev/null 2>&1; then \
		echo "📊 Rendering Mermaid diagram..."; \
		mmdc -i nfs_smb_protocol.mmd -o nfs_smb_protocol_mermaid.png; \
	else \
		echo "⚠️  Mermaid CLI not found, skipping .mmd rendering"; \
	fi

test:
	@echo "🧪 Testing NFS & SMB protocol implementations..."
	@python3 -c "\
import nfs_client as nfs; \
import smb_client as smb; \
import file_system_monitor as monitor; \
from nfs_client import NFSVersion, NFSProcedure; \
from smb_client import SMBVersion, SMBCommand; \
nfs_client = nfs.NFSClient('test-server', NFSVersion.V4); \
assert nfs_client.server == 'test-server'; \
assert nfs_client.version == NFSVersion.V4; \
print('✅ NFS Client: initialization tests passed'); \
smb_client = smb.SMBClient('test-server', 'test-share', SMBVersion.SMB30); \
assert smb_client.server == 'test-server'; \
assert smb_client.share == 'test-share'; \
print('✅ SMB Client: initialization tests passed'); \
fs_monitor = monitor.FileSystemMonitor(); \
fs_monitor.add_file_system('NFS', 'test-server', '/export'); \
assert len(fs_monitor.stats) == 1; \
print('✅ File System Monitor: monitoring tests passed'); \
print('🎯 All NFS & SMB protocol tests passed!')"

clean:
	@echo "🧹 Cleaning up generated files..."
	@rm -f *.png
	@rm -rf __pycache__/
	@echo "✅ Cleanup completed"

summary:
	@echo ""
	@echo "=== NFS & SMB Protocol Summary ==="
	@echo "📋 Protocols: Network File System (NFS) & Server Message Block (SMB)"
	@echo "🎯 Purpose: Distributed file system access over networks"
	@echo "🔧 Features: Remote file operations, caching, authentication, clustering"
	@echo "⚡ Performance: 50-300 MB/s throughput, 0.5-5ms latency"
	@echo "🌐 Use Cases: Enterprise file servers, home directories, shared storage"
	@echo ""
