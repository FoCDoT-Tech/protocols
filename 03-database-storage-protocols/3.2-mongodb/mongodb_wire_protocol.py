#!/usr/bin/env python3
"""
MongoDB Wire Protocol Simulation
Demonstrates MongoDB's binary wire protocol operations including BSON encoding,
message types, authentication, and database operations.
"""

import struct
import time
import random
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import hashlib
import base64

class BSONEncoder:
    """BSON (Binary JSON) encoder for MongoDB wire protocol"""
    
    def __init__(self):
        self.type_codes = {
            'double': 0x01,
            'string': 0x02,
            'document': 0x03,
            'array': 0x04,
            'binary': 0x05,
            'objectid': 0x07,
            'boolean': 0x08,
            'datetime': 0x09,
            'null': 0x0A,
            'int32': 0x10,
            'int64': 0x12
        }
    
    def encode_document(self, doc: Dict[str, Any]) -> bytes:
        """Encode a document to BSON format"""
        bson_data = b''
        
        for key, value in doc.items():
            if isinstance(value, str):
                bson_data += struct.pack('B', self.type_codes['string'])
                bson_data += key.encode('utf-8') + b'\x00'
                str_bytes = value.encode('utf-8')
                bson_data += struct.pack('<I', len(str_bytes) + 1)
                bson_data += str_bytes + b'\x00'
            elif isinstance(value, int):
                if -2147483648 <= value <= 2147483647:
                    bson_data += struct.pack('B', self.type_codes['int32'])
                    bson_data += key.encode('utf-8') + b'\x00'
                    bson_data += struct.pack('<i', value)
                else:
                    bson_data += struct.pack('B', self.type_codes['int64'])
                    bson_data += key.encode('utf-8') + b'\x00'
                    bson_data += struct.pack('<q', value)
            elif isinstance(value, bool):
                bson_data += struct.pack('B', self.type_codes['boolean'])
                bson_data += key.encode('utf-8') + b'\x00'
                bson_data += struct.pack('B', 1 if value else 0)
            elif isinstance(value, dict):
                bson_data += struct.pack('B', self.type_codes['document'])
                bson_data += key.encode('utf-8') + b'\x00'
                subdoc = self.encode_document(value)
                bson_data += subdoc
        
        # Add document length and terminator
        doc_length = len(bson_data) + 5  # +4 for length, +1 for terminator
        return struct.pack('<I', doc_length) + bson_data + b'\x00'

class MongoWireMessage:
    """MongoDB wire protocol message structure"""
    
    def __init__(self, opcode: int, request_id: int = None):
        self.opcode = opcode
        self.request_id = request_id or random.randint(1, 2**31)
        self.response_to = 0
        self.flags = 0
        self.body = b''
    
    def set_body(self, body: bytes):
        """Set message body"""
        self.body = body
    
    def to_bytes(self) -> bytes:
        """Convert message to wire format"""
        message_length = 16 + len(self.body)  # Header + body
        header = struct.pack('<IIII', 
                           message_length,
                           self.request_id,
                           self.response_to,
                           self.opcode)
        return header + self.body

class MongoWireProtocol:
    """MongoDB Wire Protocol implementation"""
    
    def __init__(self, host: str = "localhost", port: int = 27017):
        self.host = host
        self.port = port
        self.connection_id = random.randint(1000, 9999)
        self.bson_encoder = BSONEncoder()
        
        # MongoDB operation codes
        self.opcodes = {
            'OP_REPLY': 1,
            'OP_MSG': 1000,
            'OP_UPDATE': 2001,
            'OP_INSERT': 2002,
            'OP_QUERY': 2004,
            'OP_GET_MORE': 2005,
            'OP_DELETE': 2006,
            'OP_KILL_CURSORS': 2007,
            'OP_COMPRESSED': 2012
        }
        
        print(f"🍃 MongoDB Wire Protocol initialized")
        print(f"   Host: {self.host}:{self.port}")
        print(f"   Connection ID: {self.connection_id}")
    
    def create_query_message(self, collection: str, query: Dict[str, Any], 
                           limit: int = 0, skip: int = 0) -> MongoWireMessage:
        """Create OP_QUERY message"""
        msg = MongoWireMessage(self.opcodes['OP_QUERY'])
        
        # Query flags (0 = no flags)
        flags = 0
        
        # Full collection name (database.collection)
        full_collection = f"ecommerce.{collection}".encode('utf-8') + b'\x00'
        
        # Number to skip and return
        skip_bytes = struct.pack('<I', skip)
        limit_bytes = struct.pack('<I', limit)
        
        # Query document in BSON
        query_bson = self.bson_encoder.encode_document(query)
        
        # Assemble message body
        body = (struct.pack('<I', flags) + 
                full_collection + 
                skip_bytes + 
                limit_bytes + 
                query_bson)
        
        msg.set_body(body)
        return msg
    
    def create_insert_message(self, collection: str, documents: List[Dict[str, Any]]) -> MongoWireMessage:
        """Create OP_INSERT message"""
        msg = MongoWireMessage(self.opcodes['OP_INSERT'])
        
        # Insert flags (0 = no flags)
        flags = 0
        
        # Full collection name
        full_collection = f"ecommerce.{collection}".encode('utf-8') + b'\x00'
        
        # Encode documents
        docs_bson = b''
        for doc in documents:
            docs_bson += self.bson_encoder.encode_document(doc)
        
        # Assemble message body
        body = struct.pack('<I', flags) + full_collection + docs_bson
        
        msg.set_body(body)
        return msg
    
    def create_update_message(self, collection: str, selector: Dict[str, Any], 
                            update: Dict[str, Any], upsert: bool = False, 
                            multi: bool = False) -> MongoWireMessage:
        """Create OP_UPDATE message"""
        msg = MongoWireMessage(self.opcodes['OP_UPDATE'])
        
        # Update flags
        flags = 0
        if upsert:
            flags |= 1
        if multi:
            flags |= 2
        
        # Full collection name
        full_collection = f"ecommerce.{collection}".encode('utf-8') + b'\x00'
        
        # Encode selector and update documents
        selector_bson = self.bson_encoder.encode_document(selector)
        update_bson = self.bson_encoder.encode_document(update)
        
        # Assemble message body
        body = (struct.pack('<I', 0) +  # ZERO (reserved)
                full_collection + 
                struct.pack('<I', flags) + 
                selector_bson + 
                update_bson)
        
        msg.set_body(body)
        return msg
    
    def create_delete_message(self, collection: str, selector: Dict[str, Any], 
                            single: bool = False) -> MongoWireMessage:
        """Create OP_DELETE message"""
        msg = MongoWireMessage(self.opcodes['OP_DELETE'])
        
        # Delete flags
        flags = 1 if single else 0
        
        # Full collection name
        full_collection = f"ecommerce.{collection}".encode('utf-8') + b'\x00'
        
        # Encode selector document
        selector_bson = self.bson_encoder.encode_document(selector)
        
        # Assemble message body
        body = (struct.pack('<I', 0) +  # ZERO (reserved)
                full_collection + 
                struct.pack('<I', flags) + 
                selector_bson)
        
        msg.set_body(body)
        return msg
    
    def create_msg_command(self, database: str, command: Dict[str, Any]) -> MongoWireMessage:
        """Create OP_MSG command (MongoDB 3.6+)"""
        msg = MongoWireMessage(self.opcodes['OP_MSG'])
        
        # Message flags (0 = no flags)
        flags = 0
        
        # Add $db field to command
        command['$db'] = database
        
        # Encode command document
        command_bson = self.bson_encoder.encode_document(command)
        
        # OP_MSG body: flags + kind 0 + document
        body = struct.pack('<I', flags) + struct.pack('B', 0) + command_bson
        
        msg.set_body(body)
        return msg
    
    def simulate_authentication(self, username: str, password: str) -> Dict[str, Any]:
        """Simulate SCRAM-SHA-256 authentication"""
        print(f"\n🔐 SCRAM-SHA-256 Authentication")
        print(f"   Username: {username}")
        
        # Client first message
        client_nonce = base64.b64encode(random.randbytes(24)).decode('ascii')
        client_first_bare = f"n={username},r={client_nonce}"
        client_first = f"n,,{client_first_bare}"
        
        print(f"   Client First: {client_first}")
        
        # Server first message (simulated)
        server_nonce = client_nonce + base64.b64encode(random.randbytes(12)).decode('ascii')
        salt = base64.b64encode(random.randbytes(16)).decode('ascii')
        iterations = 4096
        server_first = f"r={server_nonce},s={salt},i={iterations}"
        
        print(f"   Server First: {server_first}")
        
        # Client final message (simplified)
        channel_binding = "c=biws"  # base64("n,,")
        client_final_without_proof = f"{channel_binding},r={server_nonce}"
        
        # Simulate proof calculation
        salted_password = hashlib.pbkdf2_hmac('sha256', password.encode(), 
                                            base64.b64decode(salt), iterations)
        client_key = hashlib.new('sha256', salted_password + b'Client Key').digest()
        client_proof = base64.b64encode(client_key[:20]).decode('ascii')
        
        client_final = f"{client_final_without_proof},p={client_proof}"
        print(f"   Client Final: {client_final}")
        
        # Authentication result
        auth_result = {
            'ok': 1,
            'conversationId': random.randint(1, 1000000),
            'done': True
        }
        
        print(f"   ✅ Authentication successful")
        return auth_result
    
    def demonstrate_operations(self) -> Dict[str, Any]:
        """Demonstrate various MongoDB wire protocol operations"""
        results = {}
        
        print(f"\n=== MongoDB Wire Protocol Operations ===")
        
        # Authentication
        auth_result = self.simulate_authentication("app_user", "secure_password")
        results['authentication'] = auth_result
        
        # Query operation
        print(f"\n📋 Query Operation (OP_QUERY)")
        query_msg = self.create_query_message("products", 
                                             {"category": "electronics", "price": {"$lt": 1000}}, 
                                             limit=10)
        query_bytes = query_msg.to_bytes()
        print(f"   Collection: ecommerce.products")
        print(f"   Query: category='electronics', price < 1000")
        print(f"   Message Size: {len(query_bytes)} bytes")
        print(f"   Request ID: {query_msg.request_id}")
        
        # Simulate query response
        query_response = {
            'cursor': {
                'id': random.randint(1000000, 9999999),
                'ns': 'ecommerce.products',
                'firstBatch': [
                    {'_id': f'prod_{i}', 'name': f'Product {i}', 'price': random.randint(100, 999)}
                    for i in range(5)
                ]
            },
            'ok': 1
        }
        results['query'] = query_response
        print(f"   Results: {len(query_response['cursor']['firstBatch'])} documents")
        
        # Insert operation
        print(f"\n📝 Insert Operation (OP_INSERT)")
        new_products = [
            {'name': 'Wireless Headphones', 'category': 'electronics', 'price': 299, 'stock': 50},
            {'name': 'Gaming Mouse', 'category': 'electronics', 'price': 79, 'stock': 100}
        ]
        insert_msg = self.create_insert_message("products", new_products)
        insert_bytes = insert_msg.to_bytes()
        print(f"   Collection: ecommerce.products")
        print(f"   Documents: {len(new_products)} items")
        print(f"   Message Size: {len(insert_bytes)} bytes")
        
        insert_response = {'n': len(new_products), 'ok': 1}
        results['insert'] = insert_response
        print(f"   Inserted: {insert_response['n']} documents")
        
        # Update operation
        print(f"\n✏️ Update Operation (OP_UPDATE)")
        update_msg = self.create_update_message("products", 
                                               {"name": "Wireless Headphones"}, 
                                               {"$set": {"price": 279, "on_sale": True}})
        update_bytes = update_msg.to_bytes()
        print(f"   Collection: ecommerce.products")
        print(f"   Selector: name='Wireless Headphones'")
        print(f"   Update: Set price=279, on_sale=true")
        print(f"   Message Size: {len(update_bytes)} bytes")
        
        update_response = {'n': 1, 'nModified': 1, 'ok': 1}
        results['update'] = update_response
        print(f"   Modified: {update_response['nModified']} documents")
        
        # Delete operation
        print(f"\n🗑️ Delete Operation (OP_DELETE)")
        delete_msg = self.create_delete_message("products", 
                                               {"category": "discontinued"}, 
                                               single=False)
        delete_bytes = delete_msg.to_bytes()
        print(f"   Collection: ecommerce.products")
        print(f"   Selector: category='discontinued'")
        print(f"   Message Size: {len(delete_bytes)} bytes")
        
        delete_response = {'n': 3, 'ok': 1}
        results['delete'] = delete_response
        print(f"   Deleted: {delete_response['n']} documents")
        
        # Modern OP_MSG command
        print(f"\n⚡ Modern Command (OP_MSG)")
        aggregation_pipeline = [
            {"$match": {"category": "electronics"}},
            {"$group": {"_id": "$category", "avgPrice": {"$avg": "$price"}, "count": {"$sum": 1}}},
            {"$sort": {"avgPrice": -1}}
        ]
        
        agg_command = {
            "aggregate": "products",
            "pipeline": aggregation_pipeline,
            "cursor": {"batchSize": 100}
        }
        
        msg_cmd = self.create_msg_command("ecommerce", agg_command)
        msg_bytes = msg_cmd.to_bytes()
        print(f"   Database: ecommerce")
        print(f"   Command: aggregate with 3-stage pipeline")
        print(f"   Message Size: {len(msg_bytes)} bytes")
        
        agg_response = {
            'cursor': {
                'id': 0,
                'ns': 'ecommerce.products',
                'firstBatch': [
                    {'_id': 'electronics', 'avgPrice': 456.78, 'count': 127}
                ]
            },
            'ok': 1
        }
        results['aggregation'] = agg_response
        print(f"   Results: {len(agg_response['cursor']['firstBatch'])} aggregated groups")
        
        return results

def demonstrate_mongodb_features():
    """Demonstrate advanced MongoDB wire protocol features"""
    print(f"\n=== Advanced MongoDB Features ===")
    
    # Connection pooling simulation
    print(f"\n🔄 Connection Pooling")
    pool_config = {
        'minPoolSize': 5,
        'maxPoolSize': 50,
        'maxIdleTimeMS': 300000,
        'waitQueueTimeoutMS': 10000
    }
    
    print(f"   Min Pool Size: {pool_config['minPoolSize']}")
    print(f"   Max Pool Size: {pool_config['maxPoolSize']}")
    print(f"   Max Idle Time: {pool_config['maxIdleTimeMS']}ms")
    
    # Simulate connection usage
    active_connections = random.randint(8, 25)
    print(f"   Active Connections: {active_connections}/{pool_config['maxPoolSize']}")
    print(f"   Pool Utilization: {(active_connections/pool_config['maxPoolSize']*100):.1f}%")
    
    # Compression demonstration
    print(f"\n🗜️ Wire Compression")
    compression_types = ['snappy', 'zlib', 'zstd']
    original_size = 1024 * 50  # 50KB message
    
    for comp_type in compression_types:
        if comp_type == 'snappy':
            compressed_size = int(original_size * 0.4)  # ~60% compression
            speed = "Very Fast"
        elif comp_type == 'zlib':
            compressed_size = int(original_size * 0.3)  # ~70% compression
            speed = "Medium"
        else:  # zstd
            compressed_size = int(original_size * 0.25)  # ~75% compression
            speed = "Fast"
        
        compression_ratio = (1 - compressed_size/original_size) * 100
        print(f"   {comp_type.upper()}: {original_size}B → {compressed_size}B ({compression_ratio:.1f}% reduction, {speed})")
    
    # Change streams simulation
    print(f"\n📡 Change Streams")
    change_events = [
        {'operationType': 'insert', 'ns': {'db': 'ecommerce', 'coll': 'orders'}, 'documentKey': {'_id': 'order_123'}},
        {'operationType': 'update', 'ns': {'db': 'ecommerce', 'coll': 'inventory'}, 'documentKey': {'_id': 'prod_456'}},
        {'operationType': 'delete', 'ns': {'db': 'ecommerce', 'coll': 'sessions'}, 'documentKey': {'_id': 'sess_789'}}
    ]
    
    for event in change_events:
        print(f"   {event['operationType'].upper()}: {event['ns']['db']}.{event['ns']['coll']} - {event['documentKey']['_id']}")
    
    # GridFS for large files
    print(f"\n📁 GridFS Large File Storage")
    file_info = {
        'filename': 'product_catalog.pdf',
        'length': 15728640,  # 15MB
        'chunkSize': 261120,  # 255KB chunks
        'uploadDate': datetime.now().isoformat(),
        'md5': 'a1b2c3d4e5f6789012345678901234567890abcd'
    }
    
    chunks_count = (file_info['length'] + file_info['chunkSize'] - 1) // file_info['chunkSize']
    print(f"   File: {file_info['filename']}")
    print(f"   Size: {file_info['length']:,} bytes ({file_info['length']/1024/1024:.1f}MB)")
    print(f"   Chunks: {chunks_count} × {file_info['chunkSize']:,} bytes")
    print(f"   MD5: {file_info['md5']}")

if __name__ == "__main__":
    # Initialize MongoDB wire protocol
    mongo_protocol = MongoWireProtocol()
    
    # Demonstrate core operations
    operation_results = mongo_protocol.demonstrate_operations()
    
    # Demonstrate advanced features
    demonstrate_mongodb_features()
    
    print(f"\n🎯 MongoDB wire protocol enables efficient document database operations")
    print(f"💡 Key benefits: binary encoding, rich data types, flexible queries")
    print(f"🚀 Production features: sharding, replication, change streams, GridFS")
