#!/usr/bin/env python3
"""
UDP Streaming Protocol Simulation
Demonstrates UDP usage in video/audio streaming applications
"""

import time
import random

class StreamingServer:
    def __init__(self, bitrate_kbps=1000):
        self.bitrate_kbps = bitrate_kbps
        self.frame_size = bitrate_kbps * 125 // 30  # bytes per frame at 30 FPS
        self.sequence_number = 0
        
    def generate_frame(self, frame_type='P'):
        """Generate a video frame packet"""
        self.sequence_number += 1
        
        # Different frame sizes based on type
        if frame_type == 'I':  # Keyframe
            size = self.frame_size * 3
        elif frame_type == 'P':  # Predicted frame
            size = self.frame_size
        else:  # B-frame
            size = self.frame_size // 2
            
        return {
            'sequence': self.sequence_number,
            'timestamp': time.time(),
            'frame_type': frame_type,
            'size': size,
            'data': f"Frame_{self.sequence_number}_{frame_type}"
        }
    
    def stream_video(self, duration_seconds=5):
        """Simulate video streaming"""
        print(f"=== Video Streaming Simulation ===")
        print(f"Bitrate: {self.bitrate_kbps} kbps")
        print(f"Frame rate: 30 FPS")
        print(f"Duration: {duration_seconds} seconds\n")
        
        frames_to_send = duration_seconds * 30
        keyframe_interval = 30  # Every 1 second
        
        for frame_num in range(frames_to_send):
            # Determine frame type
            if frame_num % keyframe_interval == 0:
                frame_type = 'I'  # Keyframe
            elif frame_num % 3 == 1:
                frame_type = 'B'  # B-frame
            else:
                frame_type = 'P'  # P-frame
            
            frame = self.generate_frame(frame_type)
            
            # Simulate network transmission
            if random.random() < 0.95:  # 95% delivery rate
                print(f"Sent frame {frame['sequence']:3d} ({frame_type}) - {frame['size']:4d} bytes")
            else:
                print(f"Lost frame {frame['sequence']:3d} ({frame_type}) - {frame['size']:4d} bytes")
            
            # Maintain frame rate
            time.sleep(1/30)  # 30 FPS

class StreamingClient:
    def __init__(self):
        self.received_frames = []
        self.buffer_size = 10
        self.playout_buffer = []
        
    def receive_frame(self, frame):
        """Receive and buffer frame"""
        self.received_frames.append(frame)
        
        # Add to playout buffer
        if len(self.playout_buffer) < self.buffer_size:
            self.playout_buffer.append(frame)
    
    def play_frame(self):
        """Play frame from buffer"""
        if self.playout_buffer:
            frame = self.playout_buffer.pop(0)
            return frame
        return None

def simulate_dns_over_udp():
    """Simulate DNS queries using UDP"""
    print("\n=== DNS over UDP Simulation ===\n")
    
    dns_queries = [
        ("www.google.com", "A"),
        ("mail.example.com", "MX"),
        ("example.com", "NS"),
        ("ftp.example.com", "CNAME"),
        ("example.com", "TXT")
    ]
    
    for domain, record_type in dns_queries:
        query_id = random.randint(1000, 9999)
        
        print(f"DNS Query ID {query_id}:")
        print(f"  Domain: {domain}")
        print(f"  Type: {record_type}")
        print(f"  Protocol: UDP")
        print(f"  Port: 53")
        
        # Simulate query time
        query_time = random.uniform(0.01, 0.05)
        time.sleep(query_time)
        
        # Simulate response (95% success rate)
        if random.random() < 0.95:
            if record_type == "A":
                response = f"192.168.{random.randint(1,254)}.{random.randint(1,254)}"
            elif record_type == "MX":
                response = f"mail.{domain}"
            elif record_type == "NS":
                response = f"ns1.{domain}"
            elif record_type == "CNAME":
                response = f"www.{domain}"
            else:
                response = "v=spf1 include:_spf.google.com ~all"
            
            print(f"  Response: {response}")
            print(f"  Query time: {query_time*1000:.1f}ms")
        else:
            print(f"  Response: TIMEOUT")
        
        print()

def udp_header_analysis():
    """Analyze UDP header structure"""
    print("=== UDP Header Analysis ===\n")
    
    # Simulate UDP packet
    packet = {
        'source_port': 12345,
        'dest_port': 53,
        'length': 64,
        'checksum': 0x1a2b,
        'data': 'DNS query for www.example.com'
    }
    
    print("UDP Header Structure:")
    print(f"  Source Port:      {packet['source_port']:5d} (16 bits)")
    print(f"  Destination Port: {packet['dest_port']:5d} (16 bits)")
    print(f"  Length:           {packet['length']:5d} (16 bits)")
    print(f"  Checksum:         0x{packet['checksum']:04x} (16 bits)")
    print(f"  Total Header:     8 bytes")
    print(f"  Data Length:      {len(packet['data'])} bytes")
    print(f"  Total Packet:     {8 + len(packet['data'])} bytes")
    
    print(f"\nHeader Efficiency:")
    efficiency = len(packet['data']) / (8 + len(packet['data'])) * 100
    print(f"  Data/Total Ratio: {efficiency:.1f}%")

def simulate_voip_call():
    """Simulate VoIP call using UDP"""
    print("\n=== VoIP Call Simulation ===\n")
    
    # VoIP parameters
    codec = "G.711"
    sample_rate = 8000  # Hz
    packet_interval = 20  # ms
    payload_size = 160  # bytes for 20ms of G.711
    
    print(f"VoIP Call Parameters:")
    print(f"  Codec: {codec}")
    print(f"  Sample Rate: {sample_rate} Hz")
    print(f"  Packet Interval: {packet_interval} ms")
    print(f"  Payload Size: {payload_size} bytes")
    print()
    
    # Simulate call duration
    call_duration = 3  # seconds
    packets_per_second = 1000 // packet_interval
    total_packets = call_duration * packets_per_second
    
    print(f"Simulating {call_duration} second call...")
    
    jitter_buffer = []
    packet_loss_count = 0
    
    for packet_num in range(total_packets):
        timestamp = packet_num * packet_interval
        
        # Simulate packet transmission
        if random.random() < 0.98:  # 98% delivery rate
            # Simulate network jitter
            jitter = random.uniform(-5, 5)  # ±5ms jitter
            arrival_time = timestamp + jitter
            
            packet = {
                'sequence': packet_num,
                'timestamp': timestamp,
                'arrival_time': arrival_time,
                'payload_size': payload_size
            }
            
            jitter_buffer.append(packet)
            
            if packet_num % 25 == 0:  # Show every 500ms
                print(f"  Packet {packet_num:3d}: sent at {timestamp:3d}ms, "
                      f"arrived at {arrival_time:6.1f}ms (jitter: {jitter:+4.1f}ms)")
        else:
            packet_loss_count += 1
            if packet_num % 25 == 0:
                print(f"  Packet {packet_num:3d}: LOST")
        
        time.sleep(packet_interval / 1000)  # Convert to seconds
    
    # Calculate statistics
    loss_rate = (packet_loss_count / total_packets) * 100
    avg_jitter = sum(abs(p['arrival_time'] - p['timestamp']) for p in jitter_buffer) / len(jitter_buffer)
    
    print(f"\nCall Statistics:")
    print(f"  Total Packets: {total_packets}")
    print(f"  Packets Lost: {packet_loss_count}")
    print(f"  Loss Rate: {loss_rate:.1f}%")
    print(f"  Average Jitter: {avg_jitter:.1f}ms")
    print(f"  Call Quality: {'Good' if loss_rate < 1 and avg_jitter < 10 else 'Poor'}")

if __name__ == "__main__":
    # Video streaming simulation
    server = StreamingServer(bitrate_kbps=500)
    server.stream_video(duration_seconds=2)
    
    # DNS simulation
    simulate_dns_over_udp()
    
    # UDP header analysis
    udp_header_analysis()
    
    # VoIP simulation
    simulate_voip_call()
