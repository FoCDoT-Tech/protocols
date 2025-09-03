#!/usr/bin/env python3
"""
TCP Flow Control and Congestion Control Simulation
Demonstrates sliding window, congestion window, and retransmission
"""

import time
import random

class TCPFlowControl:
    def __init__(self):
        self.window_size = 8  # Initial window size
        self.cwnd = 1  # Congestion window
        self.ssthresh = 16  # Slow start threshold
        self.rtt = 0.1  # Round trip time in seconds
        self.sequence_base = 1000
        self.next_seq = 1000
        
    def simulate_sliding_window(self):
        """Simulate TCP sliding window protocol"""
        print("=== TCP Sliding Window Protocol ===\n")
        
        data_to_send = list(range(1, 21))  # 20 segments to send
        sent_segments = {}
        acked_segments = set()
        
        print(f"Initial window size: {self.window_size}")
        print(f"Data to send: {len(data_to_send)} segments\n")
        
        i = 0
        while i < len(data_to_send) or len(sent_segments) > len(acked_segments):
            # Send segments within window
            while (i < len(data_to_send) and 
                   len(sent_segments) - len(acked_segments) < self.window_size):
                segment_id = data_to_send[i]
                seq_num = self.sequence_base + i
                sent_segments[segment_id] = seq_num
                print(f"Send: Segment {segment_id}, Seq={seq_num}")
                i += 1
                time.sleep(0.02)
            
            # Simulate ACKs (with occasional loss)
            for segment_id in list(sent_segments.keys()):
                if segment_id not in acked_segments:
                    # 90% chance of successful ACK
                    if random.random() < 0.9:
                        acked_segments.add(segment_id)
                        seq_num = sent_segments[segment_id]
                        print(f"Recv: ACK for Segment {segment_id}, Seq={seq_num}")
                        time.sleep(0.01)
                    else:
                        print(f"Lost: Segment {segment_id} (timeout)")
                        # Retransmit
                        seq_num = sent_segments[segment_id]
                        print(f"Retx: Segment {segment_id}, Seq={seq_num}")
                        time.sleep(0.02)
            
            time.sleep(0.05)
        
        print(f"\n✓ All segments transmitted and acknowledged")
    
    def simulate_congestion_control(self):
        """Simulate TCP congestion control algorithms"""
        print("\n=== TCP Congestion Control ===\n")
        
        print(f"Initial: cwnd={self.cwnd}, ssthresh={self.ssthresh}")
        
        # Slow Start phase
        print("\n--- Slow Start Phase ---")
        rtt_count = 0
        while self.cwnd < self.ssthresh:
            rtt_count += 1
            old_cwnd = self.cwnd
            self.cwnd *= 2  # Double every RTT
            print(f"RTT {rtt_count}: cwnd {old_cwnd} -> {self.cwnd}")
            time.sleep(0.1)
        
        # Congestion Avoidance phase
        print("\n--- Congestion Avoidance Phase ---")
        for rtt in range(5):
            rtt_count += 1
            old_cwnd = self.cwnd
            self.cwnd += 1  # Linear increase
            print(f"RTT {rtt_count}: cwnd {old_cwnd} -> {self.cwnd}")
            time.sleep(0.1)
        
        # Simulate congestion (packet loss)
        print("\n--- Congestion Detected (Packet Loss) ---")
        print(f"Packet loss detected! cwnd={self.cwnd}")
        self.ssthresh = max(self.cwnd // 2, 2)
        self.cwnd = 1
        print(f"Reset: cwnd={self.cwnd}, ssthresh={self.ssthresh}")
        
        # Fast Recovery simulation
        print("\n--- Fast Recovery ---")
        self.cwnd = self.ssthresh
        print(f"Fast recovery: cwnd set to ssthresh={self.cwnd}")

class TCPRetransmission:
    def __init__(self):
        self.rto = 1.0  # Retransmission timeout
        self.rtt_samples = []
        
    def simulate_retransmission(self):
        """Simulate TCP retransmission mechanism"""
        print("\n=== TCP Retransmission ===\n")
        
        segments = [
            {"id": 1, "data": "HTTP GET request", "success": True},
            {"id": 2, "data": "User-Agent header", "success": False},  # Lost
            {"id": 3, "data": "Host header", "success": True},
            {"id": 4, "data": "Connection header", "success": False}  # Lost
        ]
        
        for segment in segments:
            print(f"Send: Segment {segment['id']} - {segment['data']}")
            
            if segment['success']:
                # Simulate successful transmission
                rtt = random.uniform(0.05, 0.15)
                self.rtt_samples.append(rtt)
                print(f"Recv: ACK for segment {segment['id']} (RTT: {rtt:.3f}s)")
            else:
                # Simulate timeout and retransmission
                print(f"Timeout: No ACK for segment {segment['id']} after {self.rto}s")
                print(f"Retx: Segment {segment['id']} - {segment['data']}")
                
                # Successful retransmission
                rtt = random.uniform(0.05, 0.15)
                self.rtt_samples.append(rtt)
                print(f"Recv: ACK for segment {segment['id']} (RTT: {rtt:.3f}s)")
                
                # Update RTO (simplified)
                self.rto = min(self.rto * 2, 60)  # Exponential backoff
                print(f"Update: RTO increased to {self.rto}s")
            
            time.sleep(0.1)
        
        # Show RTT statistics
        if self.rtt_samples:
            avg_rtt = sum(self.rtt_samples) / len(self.rtt_samples)
            print(f"\nRTT Statistics:")
            print(f"  Samples: {len(self.rtt_samples)}")
            print(f"  Average RTT: {avg_rtt:.3f}s")
            print(f"  Final RTO: {self.rto}s")

def demonstrate_tcp_advanced():
    """Demonstrate advanced TCP features"""
    print("=== Advanced TCP Features ===\n")
    
    # Flow control
    flow_control = TCPFlowControl()
    flow_control.simulate_sliding_window()
    flow_control.simulate_congestion_control()
    
    # Retransmission
    retransmission = TCPRetransmission()
    retransmission.simulate_retransmission()
    
    # TCP Options demonstration
    print("\n=== TCP Options ===")
    options = [
        ("MSS", "Maximum Segment Size", "1460 bytes"),
        ("Window Scale", "Window scaling factor", "8 (scale by 256)"),
        ("SACK", "Selective Acknowledgment", "Enabled"),
        ("Timestamp", "Round-trip time measurement", "Enabled")
    ]
    
    for option, description, value in options:
        print(f"{option:<12}: {description:<30} = {value}")

if __name__ == "__main__":
    demonstrate_tcp_advanced()
