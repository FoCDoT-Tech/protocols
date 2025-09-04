#!/usr/bin/env python3
"""
SQL Wire Protocol Diagram Renderer
Generates visual diagrams for SQL database protocols, connection pooling, and performance analysis
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_sql_protocol_comparison():
    """Create SQL protocol comparison diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # Protocol columns
    protocols = [
        ("MySQL", "#4479A1", 2),
        ("PostgreSQL", "#336791", 6), 
        ("SQL Server", "#CC2927", 10)
    ]
    
    # Protocol features
    features = [
        ("Handshake/Startup", 8.5),
        ("Authentication", 7.5),
        ("Query Execution", 6.5),
        ("Prepared Statements", 5.5),
        ("Result Sets", 4.5),
        ("Transaction Control", 3.5),
        ("Connection Management", 2.5),
        ("Error Handling", 1.5)
    ]
    
    for protocol, color, x_pos in protocols:
        # Protocol header
        header_box = FancyBboxPatch((x_pos-1.5, 9), 3, 1,
                                   boxstyle="round,pad=0.1",
                                   facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(header_box)
        ax.text(x_pos, 9.5, protocol, ha='center', va='center', 
               fontsize=12, fontweight='bold', color='white')
        
        # Protocol features
        for feature, y_pos in features:
            feature_box = FancyBboxPatch((x_pos-1.4, y_pos-0.3), 2.8, 0.6,
                                        boxstyle="round,pad=0.05",
                                        facecolor='lightgray', edgecolor=color, linewidth=1)
            ax.add_patch(feature_box)
            
            # Feature-specific content
            if protocol == "MySQL" and "Handshake" in feature:
                content = "Protocol v10\nSalt + Capabilities"
            elif protocol == "PostgreSQL" and "Startup" in feature:
                content = "Protocol v3.0\nParameters"
            elif protocol == "SQL Server" and "Handshake" in feature:
                content = "TDS Login\nVersion 7.4"
            elif "Authentication" in feature:
                if protocol == "MySQL":
                    content = "caching_sha2_password\nSSL Support"
                elif protocol == "PostgreSQL":
                    content = "SCRAM-SHA-256\nGSSAPI/SSPI"
                else:
                    content = "SQL Auth\nWindows Auth"
            elif "Query" in feature:
                content = "Binary Protocol\nText Protocol"
            elif "Prepared" in feature:
                content = "Statement Cache\nParameter Binding"
            else:
                content = "Standard\nImplementation"
            
            ax.text(x_pos, y_pos, content, ha='center', va='center', 
                   fontsize=8, color='black')
    
    # Add comparison arrows
    for i in range(len(protocols)-1):
        x1 = protocols[i][2] + 1.5
        x2 = protocols[i+1][2] - 1.5
        ax.annotate('', xy=(x2, 5), xytext=(x1, 5),
                   arrowprops=dict(arrowstyle='<->', color='gray', lw=2))
    
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 11)
    ax.set_title('SQL Wire Protocol Comparison', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/Users/focdot/01Projects/LEARN/Protocols/03-database-storage-protocols/3.1-sql/sql_protocol_comparison.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_connection_pool_diagram():
    """Create connection pool architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Application layer
    app_box = FancyBboxPatch((1, 6), 10, 1.5,
                            boxstyle="round,pad=0.1",
                            facecolor="#e1f5fe", edgecolor='blue', linewidth=2)
    ax.add_patch(app_box)
    ax.text(6, 6.75, "Application Layer\n(Multiple Threads/Processes)", 
           ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Connection pool
    pool_box = FancyBboxPatch((2, 4), 8, 1.5,
                             boxstyle="round,pad=0.1",
                             facecolor="#f3e5f5", edgecolor='purple', linewidth=2)
    ax.add_patch(pool_box)
    ax.text(6, 4.75, "Connection Pool\n(Min: 5, Max: 20, Timeout: 30s)", 
           ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Individual connections
    connection_positions = [(3, 2.5), (5, 2.5), (7, 2.5), (9, 2.5)]
    connection_states = ["Idle", "Active", "Idle", "Validating"]
    connection_colors = ["#4CAF50", "#FF9800", "#4CAF50", "#2196F3"]
    
    for i, ((x, y), state, color) in enumerate(zip(connection_positions, connection_states, connection_colors)):
        conn_box = FancyBboxPatch((x-0.6, y-0.4), 1.2, 0.8,
                                 boxstyle="round,pad=0.05",
                                 facecolor=color, edgecolor='black', linewidth=1, alpha=0.7)
        ax.add_patch(conn_box)
        ax.text(x, y, f"Conn {i+1}\n{state}", ha='center', va='center', 
               fontsize=9, fontweight='bold', color='white')
        
        # Connection to pool
        ax.annotate('', xy=(x, y+0.4), xytext=(x, 4),
                   arrowprops=dict(arrowstyle='-', color='gray', lw=1))
    
    # Database
    db_box = FancyBboxPatch((4, 0.5), 4, 1,
                           boxstyle="round,pad=0.1",
                           facecolor="#e8f5e8", edgecolor='green', linewidth=2)
    ax.add_patch(db_box)
    ax.text(6, 1, "Database Server\n(MySQL/PostgreSQL/SQL Server)", 
           ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Arrows from app to pool
    ax.annotate('', xy=(6, 5.5), xytext=(6, 6),
               arrowprops=dict(arrowstyle='<->', color='blue', lw=2))
    
    # Arrows from connections to database
    for (x, _), _, _ in zip(connection_positions, connection_states, connection_colors):
        ax.annotate('', xy=(6, 1.5), xytext=(x, 2.1),
                   arrowprops=dict(arrowstyle='->', color='green', lw=1, alpha=0.7))
    
    # Pool statistics
    stats_text = """Pool Statistics:
• Active: 1/4 connections
• Idle: 2/4 connections  
• Validating: 1/4 connections
• Pool Efficiency: 87%
• Avg Response Time: 15ms"""
    
    ax.text(0.5, 4, stats_text, fontsize=9, va='center',
           bbox=dict(boxstyle="round,pad=0.3", facecolor='lightyellow', alpha=0.8))
    
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.set_title('Database Connection Pool Architecture', fontsize=14, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/Users/focdot/01Projects/LEARN/Protocols/03-database-storage-protocols/3.1-sql/connection_pool_architecture.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_sql_performance_chart():
    """Create SQL protocol performance comparison chart"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Query execution time comparison
    protocols = ['MySQL\n(Binary)', 'PostgreSQL\n(Extended)', 'SQL Server\n(TDS)', 'HTTP API\n(REST)']
    query_times = [2.3, 2.8, 2.1, 45.2]  # milliseconds
    colors = ['#4479A1', '#336791', '#CC2927', '#FF6B6B']
    
    bars1 = ax1.bar(protocols, query_times, color=colors, alpha=0.7)
    ax1.set_ylabel('Query Execution Time (ms)', fontsize=12)
    ax1.set_title('Query Performance Comparison', fontsize=14, fontweight='bold')
    ax1.set_ylim(0, 50)
    
    # Add value labels on bars
    for bar, time in zip(bars1, query_times):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{time}ms', ha='center', va='bottom', fontweight='bold')
    
    # Connection overhead comparison
    connection_types = ['Pooled\nConnection', 'New TCP\nConnection', 'HTTP\nConnection']
    overhead_times = [0.1, 25.3, 12.8]  # milliseconds
    overhead_colors = ['#4CAF50', '#FF9800', '#2196F3']
    
    bars2 = ax2.bar(connection_types, overhead_times, color=overhead_colors, alpha=0.7)
    ax2.set_ylabel('Connection Overhead (ms)', fontsize=12)
    ax2.set_title('Connection Establishment Overhead', fontsize=14, fontweight='bold')
    ax2.set_ylim(0, 30)
    
    # Add value labels on bars
    for bar, time in zip(bars2, overhead_times):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{time}ms', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/Users/focdot/01Projects/LEARN/Protocols/03-database-storage-protocols/3.1-sql/sql_performance_comparison.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_sql_security_features():
    """Create SQL security features diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Security layers
    layers = [
        (6, 7, "Network Security", "#ffebee", "TLS/SSL encryption, VPN, firewall rules"),
        (6, 5.5, "Authentication", "#e8f5e8", "Username/password, certificates, LDAP, Kerberos"),
        (6, 4, "Authorization", "#e1f5fe", "Role-based access, fine-grained permissions"),
        (6, 2.5, "Data Protection", "#fff3e0", "Encryption at rest, column-level encryption"),
        (6, 1, "Audit & Monitoring", "#f3e5f5", "Query logging, access tracking, anomaly detection")
    ]
    
    for x, y, title, color, desc in layers:
        # Main security layer box
        main_box = FancyBboxPatch((x-4, y-0.4), 8, 0.8,
                                 boxstyle="round,pad=0.1",
                                 facecolor=color, edgecolor='black', linewidth=1.5)
        ax.add_patch(main_box)
        ax.text(x, y, title, ha='center', va='center', 
               fontsize=12, fontweight='bold')
        
        # Description box
        desc_box = FancyBboxPatch((x-3.5, y-0.8), 7, 0.3,
                                 boxstyle="round,pad=0.05",
                                 facecolor='white', edgecolor='gray', linewidth=1)
        ax.add_patch(desc_box)
        ax.text(x, y-0.65, desc, ha='center', va='center', 
               fontsize=9, color='#666')
    
    # Security protocols on the side
    protocols_box = FancyBboxPatch((0.5, 3), 3, 2,
                                  boxstyle="round,pad=0.1",
                                  facecolor="#f5f5f5", edgecolor='gray', linewidth=1)
    ax.add_patch(protocols_box)
    
    protocols_text = """Security Protocols:
• TLS 1.2/1.3
• SASL/SCRAM
• Kerberos/GSSAPI
• X.509 Certificates
• OAuth 2.0/JWT"""
    
    ax.text(2, 4, protocols_text, ha='center', va='center', 
           fontsize=10, fontweight='bold')
    
    # Threats mitigated
    threats_box = FancyBboxPatch((8.5, 3), 3, 2,
                                boxstyle="round,pad=0.1",
                                facecolor="#ffcdd2", edgecolor='red', linewidth=1)
    ax.add_patch(threats_box)
    
    threats_text = """Threats Mitigated:
• SQL Injection
• Man-in-the-Middle
• Credential Theft
• Data Exfiltration
• Privilege Escalation"""
    
    ax.text(10, 4, threats_text, ha='center', va='center', 
           fontsize=10, fontweight='bold', color='#d32f2f')
    
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.set_title('SQL Database Security Architecture', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/Users/focdot/01Projects/LEARN/Protocols/03-database-storage-protocols/3.1-sql/sql_security_features.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_sql_packet_structure():
    """Create SQL packet structure diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    
    # MySQL packet structure
    mysql_y = 6
    ax.text(1, mysql_y + 0.5, "MySQL Packet Structure", fontsize=14, fontweight='bold', color='#4479A1')
    
    mysql_fields = [
        ("Length", 1, "#e3f2fd"),
        ("Sequence", 1, "#bbdefb"),
        ("Payload", 8, "#90caf9")
    ]
    
    x_offset = 1
    for field, width, color in mysql_fields:
        field_box = FancyBboxPatch((x_offset, mysql_y-0.3), width, 0.6,
                                  boxstyle="round,pad=0.02",
                                  facecolor=color, edgecolor='blue', linewidth=1)
        ax.add_patch(field_box)
        ax.text(x_offset + width/2, mysql_y, field, ha='center', va='center', 
               fontsize=10, fontweight='bold')
        x_offset += width
    
    # PostgreSQL message structure
    pg_y = 4
    ax.text(1, pg_y + 0.5, "PostgreSQL Message Structure", fontsize=14, fontweight='bold', color='#336791')
    
    pg_fields = [
        ("Type", 1, "#e8f5e8"),
        ("Length", 1, "#c8e6c9"),
        ("Message Body", 8, "#a5d6a7")
    ]
    
    x_offset = 1
    for field, width, color in pg_fields:
        field_box = FancyBboxPatch((x_offset, pg_y-0.3), width, 0.6,
                                  boxstyle="round,pad=0.02",
                                  facecolor=color, edgecolor='green', linewidth=1)
        ax.add_patch(field_box)
        ax.text(x_offset + width/2, pg_y, field, ha='center', va='center', 
               fontsize=10, fontweight='bold')
        x_offset += width
    
    # TDS packet structure
    tds_y = 2
    ax.text(1, tds_y + 0.5, "SQL Server TDS Packet Structure", fontsize=14, fontweight='bold', color='#CC2927')
    
    tds_fields = [
        ("Type", 1, "#ffebee"),
        ("Status", 1, "#ffcdd2"),
        ("Length", 1, "#ef9a9a"),
        ("SPID", 1, "#e57373"),
        ("Data", 6, "#ef5350")
    ]
    
    x_offset = 1
    for field, width, color in tds_fields:
        field_box = FancyBboxPatch((x_offset, tds_y-0.3), width, 0.6,
                                  boxstyle="round,pad=0.02",
                                  facecolor=color, edgecolor='red', linewidth=1)
        ax.add_patch(field_box)
        ax.text(x_offset + width/2, tds_y, field, ha='center', va='center', 
               fontsize=10, fontweight='bold')
        x_offset += width
    
    # Add byte indicators
    for i in range(11):
        ax.text(i + 1.5, 0.5, f"Byte {i}", ha='center', va='center', 
               fontsize=8, color='gray')
        ax.axvline(x=i+1, ymin=0, ymax=0.1, color='gray', linestyle='--', alpha=0.5)
    
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.set_title('SQL Wire Protocol Packet Structures', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/Users/focdot/01Projects/LEARN/Protocols/03-database-storage-protocols/3.1-sql/sql_packet_structure.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def render_all_diagrams():
    """Render all SQL protocol diagrams"""
    print("🎨 Rendering SQL Wire Protocol diagrams...")
    
    diagrams = [
        ("Protocol Comparison", create_sql_protocol_comparison),
        ("Connection Pool Architecture", create_connection_pool_diagram),
        ("Performance Comparison", create_sql_performance_chart),
        ("Security Features", create_sql_security_features),
        ("Packet Structure", create_sql_packet_structure)
    ]
    
    for name, func in diagrams:
        print(f"  📊 Generating {name}...")
        func()
        print(f"  ✅ {name} completed")
    
    print("🎨 All SQL protocol diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
