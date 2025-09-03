# Chapter 1: Core Internet & Networking - Master Makefile
# Runs all subchapter tests and generates comprehensive reports

.PHONY: all test clean subchapters 1.1 1.2 1.3 1.4 1.5

# Default target - run all subchapters
all: test

# Test all subchapters in dependency order
test: subchapters
	@echo "=========================================="
	@echo "Chapter 1: Core Internet & Networking"
	@echo "All subchapter tests completed successfully!"
	@echo "=========================================="

# Run all subchapters
subchapters: 1.1 1.2 1.3 1.4 1.5

# Individual subchapter targets
1.1:
	@echo "Testing 1.1 - IPv4 & IPv6..."
	@cd 1.1-ipv4-ipv6 && $(MAKE) test
	@echo "✓ 1.1 - IPv4 & IPv6 completed"

1.2: 1.1
	@echo "Testing 1.2 - ICMP & ICMPv6..."
	@cd 1.2-icmp-icmpv6 && $(MAKE) test
	@echo "✓ 1.2 - ICMP & ICMPv6 completed"

1.3: 1.1
	@echo "Testing 1.3 - TCP..."
	@cd 1.3-tcp && $(MAKE) test
	@echo "✓ 1.3 - TCP completed"

1.4: 1.1
	@echo "Testing 1.4 - UDP..."
	@cd 1.4-udp && $(MAKE) test
	@echo "✓ 1.4 - UDP completed"

1.5: 1.4
	@echo "Testing 1.5 - QUIC (depends on UDP)..."
	@cd 1.5-quic && $(MAKE) test
	@echo "✓ 1.5 - QUIC completed"

# Clean all subchapters
clean:
	@echo "Cleaning Chapter 1 artifacts..."
	@for dir in 1.1-ipv4-ipv6 1.2-icmp-icmpv6 1.3-tcp 1.4-udp 1.5-quic; do \
		if [ -d "$$dir" ]; then \
			echo "Cleaning $$dir..."; \
			cd "$$dir" && $(MAKE) clean && cd ..; \
		fi; \
	done
	@echo "Chapter 1 cleanup completed"

# Generate summary report
report:
	@echo "=========================================="
	@echo "Chapter 1: Core Internet & Networking"
	@echo "Protocol Learning Content Summary"
	@echo "=========================================="
	@echo "1.1 - IPv4 & IPv6: Internet Protocol fundamentals"
	@echo "1.2 - ICMP & ICMPv6: Internet Control Message Protocol"
	@echo "1.3 - TCP: Transmission Control Protocol"
	@echo "1.4 - UDP: User Datagram Protocol"
	@echo "1.5 - QUIC: Quick UDP Internet Connections"
	@echo "=========================================="
	@echo "Dependencies resolved:"
	@echo "  - 1.2, 1.3, 1.4 depend on 1.1 (IP foundation)"
	@echo "  - 1.5 depends on 1.4 (UDP foundation)"
	@echo "=========================================="
