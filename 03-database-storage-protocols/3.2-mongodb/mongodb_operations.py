#!/usr/bin/env python3
"""
MongoDB Operations and Aggregation Pipeline Simulation
Demonstrates advanced MongoDB operations including aggregation pipelines,
indexing strategies, sharding, and replica set operations.
"""

import random
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class MongoIndex:
    """MongoDB index definition"""
    name: str
    keys: Dict[str, int]  # 1 for ascending, -1 for descending
    unique: bool = False
    sparse: bool = False
    background: bool = True

@dataclass
class ShardKey:
    """MongoDB shard key definition"""
    field: str
    type: str  # 'hashed' or 'ranged'

class MongoAggregationPipeline:
    """MongoDB aggregation pipeline builder and executor"""
    
    def __init__(self):
        self.stages = []
        self.execution_stats = {}
    
    def match(self, criteria: Dict[str, Any]) -> 'MongoAggregationPipeline':
        """Add $match stage"""
        self.stages.append({"$match": criteria})
        return self
    
    def group(self, group_spec: Dict[str, Any]) -> 'MongoAggregationPipeline':
        """Add $group stage"""
        self.stages.append({"$group": group_spec})
        return self
    
    def sort(self, sort_spec: Dict[str, int]) -> 'MongoAggregationPipeline':
        """Add $sort stage"""
        self.stages.append({"$sort": sort_spec})
        return self
    
    def project(self, projection: Dict[str, Any]) -> 'MongoAggregationPipeline':
        """Add $project stage"""
        self.stages.append({"$project": projection})
        return self
    
    def limit(self, count: int) -> 'MongoAggregationPipeline':
        """Add $limit stage"""
        self.stages.append({"$limit": count})
        return self
    
    def lookup(self, from_collection: str, local_field: str, 
              foreign_field: str, as_field: str) -> 'MongoAggregationPipeline':
        """Add $lookup stage for joins"""
        self.stages.append({
            "$lookup": {
                "from": from_collection,
                "localField": local_field,
                "foreignField": foreign_field,
                "as": as_field
            }
        })
        return self
    
    def unwind(self, path: str, preserve_null: bool = False) -> 'MongoAggregationPipeline':
        """Add $unwind stage"""
        unwind_spec = {"path": path}
        if preserve_null:
            unwind_spec["preserveNullAndEmptyArrays"] = True
        self.stages.append({"$unwind": unwind_spec})
        return self
    
    def execute(self, collection: str) -> Dict[str, Any]:
        """Execute aggregation pipeline"""
        start_time = time.time()
        
        # Simulate execution
        docs_examined = random.randint(1000, 50000)
        docs_returned = random.randint(10, 1000)
        index_usage = random.choice([True, False])
        
        execution_time = time.time() - start_time + random.uniform(0.01, 0.5)
        
        self.execution_stats = {
            'collection': collection,
            'stages': len(self.stages),
            'docsExamined': docs_examined,
            'docsReturned': docs_returned,
            'indexUsed': index_usage,
            'executionTimeMS': round(execution_time * 1000, 2)
        }
        
        # Generate sample results based on pipeline
        results = self._generate_sample_results()
        
        return {
            'results': results,
            'stats': self.execution_stats
        }
    
    def _generate_sample_results(self) -> List[Dict[str, Any]]:
        """Generate sample results based on pipeline stages"""
        if any('$group' in str(stage) for stage in self.stages):
            # Aggregation results
            return [
                {'_id': 'electronics', 'totalSales': 125000, 'avgPrice': 299.99, 'count': 450},
                {'_id': 'clothing', 'totalSales': 89000, 'avgPrice': 79.99, 'count': 1200},
                {'_id': 'books', 'totalSales': 45000, 'avgPrice': 24.99, 'count': 1800}
            ]
        else:
            # Document results
            return [
                {'_id': f'doc_{i}', 'name': f'Product {i}', 'price': random.randint(10, 500)}
                for i in range(random.randint(5, 20))
            ]

class MongoReplicaSet:
    """MongoDB replica set simulation"""
    
    def __init__(self, name: str, members: List[str]):
        self.name = name
        self.members = members
        self.primary = members[0]
        self.secondaries = members[1:-1] if len(members) > 2 else []
        self.arbiter = members[-1] if len(members) > 2 else None
        self.oplog_size = 1024  # MB
    
    def simulate_election(self) -> Dict[str, Any]:
        """Simulate primary election"""
        print(f"\n🗳️ Replica Set Election")
        print(f"   Replica Set: {self.name}")
        
        # Simulate election process
        old_primary = self.primary
        if self.secondaries:
            self.primary = random.choice(self.secondaries)
            self.secondaries = [m for m in self.members if m != self.primary and m != self.arbiter]
            if old_primary != self.arbiter:
                self.secondaries.append(old_primary)
        
        election_result = {
            'newPrimary': self.primary,
            'oldPrimary': old_primary,
            'electionTime': random.uniform(1.0, 5.0),
            'votes': len(self.members) // 2 + 1
        }
        
        print(f"   New Primary: {election_result['newPrimary']}")
        print(f"   Election Time: {election_result['electionTime']:.2f}s")
        print(f"   Votes Required: {election_result['votes']}")
        
        return election_result
    
    def simulate_replication_lag(self) -> Dict[str, float]:
        """Simulate replication lag across secondaries"""
        lag_data = {}
        
        for secondary in self.secondaries:
            # Simulate varying lag times
            lag_ms = random.uniform(5, 200)
            lag_data[secondary] = lag_ms
        
        print(f"\n📊 Replication Lag")
        for member, lag in lag_data.items():
            status = "⚠️" if lag > 100 else "✅"
            print(f"   {member}: {lag:.1f}ms {status}")
        
        return lag_data

class MongoShardedCluster:
    """MongoDB sharded cluster simulation"""
    
    def __init__(self, name: str):
        self.name = name
        self.config_servers = ["config1:27019", "config2:27019", "config3:27019"]
        self.mongos_routers = ["mongos1:27017", "mongos2:27017"]
        self.shards = {
            "shard01": ["shard01a:27018", "shard01b:27018", "shard01c:27018"],
            "shard02": ["shard02a:27018", "shard02b:27018", "shard02c:27018"],
            "shard03": ["shard03a:27018", "shard03b:27018", "shard03c:27018"]
        }
        self.shard_keys = {}
    
    def add_shard_key(self, collection: str, shard_key: ShardKey):
        """Add shard key for collection"""
        self.shard_keys[collection] = shard_key
        print(f"🔑 Shard Key Added")
        print(f"   Collection: {collection}")
        print(f"   Key: {shard_key.field} ({shard_key.type})")
    
    def simulate_chunk_distribution(self, collection: str) -> Dict[str, Any]:
        """Simulate chunk distribution across shards"""
        if collection not in self.shard_keys:
            raise ValueError(f"No shard key defined for {collection}")
        
        # Generate chunk distribution
        total_chunks = random.randint(50, 200)
        chunk_distribution = {}
        
        for shard in self.shards.keys():
            chunk_count = random.randint(10, 30)
            chunk_distribution[shard] = {
                'chunks': chunk_count,
                'dataSize': random.randint(500, 2000),  # MB
                'docCount': random.randint(10000, 100000)
            }
        
        # Normalize to total chunks
        total_assigned = sum(data['chunks'] for data in chunk_distribution.values())
        for shard_data in chunk_distribution.values():
            shard_data['chunks'] = int(shard_data['chunks'] * total_chunks / total_assigned)
        
        print(f"\n📊 Chunk Distribution - {collection}")
        for shard, data in chunk_distribution.items():
            print(f"   {shard}: {data['chunks']} chunks, {data['dataSize']}MB, {data['docCount']:,} docs")
        
        return {
            'collection': collection,
            'totalChunks': total_chunks,
            'distribution': chunk_distribution
        }
    
    def simulate_balancer_activity(self) -> Dict[str, Any]:
        """Simulate balancer chunk migrations"""
        migrations = []
        
        # Simulate 3-5 migrations
        for i in range(random.randint(3, 5)):
            from_shard = random.choice(list(self.shards.keys()))
            to_shard = random.choice([s for s in self.shards.keys() if s != from_shard])
            
            migration = {
                'from': from_shard,
                'to': to_shard,
                'collection': 'ecommerce.orders',
                'chunkRange': f"[ObjectId('...'), ObjectId('...'))",
                'duration': random.uniform(2.5, 15.0),
                'status': random.choice(['completed', 'in_progress', 'failed'])
            }
            migrations.append(migration)
        
        print(f"\n⚖️ Balancer Activity")
        for migration in migrations:
            status_icon = {"completed": "✅", "in_progress": "🔄", "failed": "❌"}[migration['status']]
            print(f"   {migration['from']} → {migration['to']}: {migration['duration']:.1f}s {status_icon}")
        
        return {'migrations': migrations}

class MongoIndexManager:
    """MongoDB index management simulation"""
    
    def __init__(self):
        self.indexes = {}
    
    def create_index(self, collection: str, index: MongoIndex) -> Dict[str, Any]:
        """Create index on collection"""
        if collection not in self.indexes:
            self.indexes[collection] = []
        
        # Simulate index creation time
        doc_count = random.randint(10000, 1000000)
        creation_time = doc_count / 50000  # Rough estimate
        
        index_info = {
            'name': index.name,
            'keys': index.keys,
            'unique': index.unique,
            'sparse': index.sparse,
            'background': index.background,
            'size': random.randint(50, 500),  # MB
            'creationTime': creation_time,
            'docCount': doc_count
        }
        
        self.indexes[collection].append(index_info)
        
        print(f"🔍 Index Created")
        print(f"   Collection: {collection}")
        print(f"   Name: {index.name}")
        print(f"   Keys: {index.keys}")
        print(f"   Size: {index_info['size']}MB")
        print(f"   Creation Time: {creation_time:.2f}s")
        
        return index_info
    
    def analyze_query_performance(self, collection: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze query performance with available indexes"""
        collection_indexes = self.indexes.get(collection, [])
        
        # Simple index matching logic
        index_used = None
        for index in collection_indexes:
            index_fields = set(index['keys'].keys())
            query_fields = set(query.keys())
            
            if query_fields.intersection(index_fields):
                index_used = index
                break
        
        if index_used:
            docs_examined = random.randint(1, 100)
            execution_time = random.uniform(1, 10)
        else:
            docs_examined = random.randint(10000, 100000)
            execution_time = random.uniform(100, 1000)
        
        performance = {
            'indexUsed': index_used['name'] if index_used else None,
            'docsExamined': docs_examined,
            'docsReturned': random.randint(1, docs_examined),
            'executionTimeMS': execution_time,
            'isOptimal': index_used is not None
        }
        
        print(f"\n📈 Query Performance Analysis")
        print(f"   Query: {query}")
        print(f"   Index Used: {performance['indexUsed'] or 'NONE (Collection Scan)'}")
        print(f"   Docs Examined: {performance['docsExamined']:,}")
        print(f"   Execution Time: {performance['executionTimeMS']:.2f}ms")
        print(f"   Optimal: {'✅' if performance['isOptimal'] else '❌'}")
        
        return performance

def demonstrate_mongodb_operations():
    """Demonstrate comprehensive MongoDB operations"""
    print("=== MongoDB Operations Demonstration ===")
    
    # Aggregation Pipeline
    print("\n📊 Aggregation Pipeline")
    pipeline = (MongoAggregationPipeline()
                .match({"status": "active", "category": {"$in": ["electronics", "books"]}})
                .lookup("reviews", "product_id", "_id", "product_reviews")
                .unwind("$product_reviews", preserve_null=True)
                .group({
                    "_id": "$category",
                    "avgRating": {"$avg": "$product_reviews.rating"},
                    "totalSales": {"$sum": "$sales"},
                    "productCount": {"$sum": 1}
                })
                .sort({"totalSales": -1})
                .limit(10))
    
    result = pipeline.execute("products")
    print(f"   Pipeline Stages: {result['stats']['stages']}")
    print(f"   Docs Examined: {result['stats']['docsExamined']:,}")
    print(f"   Docs Returned: {result['stats']['docsReturned']:,}")
    print(f"   Execution Time: {result['stats']['executionTimeMS']}ms")
    print(f"   Results: {len(result['results'])} categories")
    
    # Index Management
    print("\n🔍 Index Management")
    index_manager = MongoIndexManager()
    
    # Create compound index
    compound_idx = MongoIndex(
        name="category_price_idx",
        keys={"category": 1, "price": -1},
        background=True
    )
    index_manager.create_index("products", compound_idx)
    
    # Create text index
    text_idx = MongoIndex(
        name="text_search_idx",
        keys={"name": "text", "description": "text"},
        background=True
    )
    index_manager.create_index("products", text_idx)
    
    # Analyze query performance
    query = {"category": "electronics", "price": {"$lt": 500}}
    index_manager.analyze_query_performance("products", query)
    
    # Replica Set Operations
    print("\n🔄 Replica Set Operations")
    replica_set = MongoReplicaSet("rs0", [
        "mongo1:27017", "mongo2:27017", "mongo3:27017", "arbiter:27017"
    ])
    
    replica_set.simulate_election()
    replica_set.simulate_replication_lag()
    
    # Sharded Cluster Operations
    print("\n🌐 Sharded Cluster Operations")
    cluster = MongoShardedCluster("production-cluster")
    
    # Add shard keys
    cluster.add_shard_key("orders", ShardKey("customer_id", "hashed"))
    cluster.add_shard_key("products", ShardKey("category", "ranged"))
    
    # Simulate chunk distribution
    cluster.simulate_chunk_distribution("orders")
    cluster.simulate_balancer_activity()

if __name__ == "__main__":
    demonstrate_mongodb_operations()
    
    print(f"\n🎯 MongoDB operations enable scalable document database management")
    print(f"💡 Key features: aggregation pipelines, indexing, replication, sharding")
    print(f"🚀 Production capabilities: high availability, horizontal scaling, performance optimization")
