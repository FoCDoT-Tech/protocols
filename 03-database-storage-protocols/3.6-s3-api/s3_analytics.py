#!/usr/bin/env python3
"""
S3 Storage Analytics and Cost Management
Demonstrates S3 storage analytics, lifecycle management,
and cost optimization strategies.
"""

import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict

@dataclass
class StorageMetrics:
    """Storage usage metrics"""
    total_objects: int
    total_size_bytes: int
    storage_class_breakdown: Dict[str, int]
    access_patterns: Dict[str, int]
    cost_breakdown: Dict[str, float]

@dataclass
class LifecycleRule:
    """S3 lifecycle management rule"""
    rule_id: str
    prefix: str
    enabled: bool
    transitions: List[Tuple[int, str]]  # (days, storage_class)
    expiration_days: Optional[int] = None

class S3Analytics:
    """S3 storage analytics and optimization"""
    
    def __init__(self, s3_client):
        self.s3_client = s3_client
        self.storage_costs = {
            'STANDARD': 0.023,  # per GB/month
            'STANDARD_IA': 0.0125,
            'ONEZONE_IA': 0.01,
            'GLACIER': 0.004,
            'DEEP_ARCHIVE': 0.00099
        }
        self.request_costs = {
            'PUT': 0.0005,  # per 1000 requests
            'GET': 0.0004,
            'LIST': 0.0005,
            'DELETE': 0.0
        }
        
        print("📊 S3 Analytics initialized")
        print(f"   Storage cost rates loaded for {len(self.storage_costs)} classes")
    
    def analyze_storage_usage(self) -> StorageMetrics:
        """Analyze current storage usage patterns"""
        print(f"\n📈 Analyzing Storage Usage")
        
        # Simulate storage analysis
        storage_classes = ['STANDARD', 'STANDARD_IA', 'ONEZONE_IA', 'GLACIER', 'DEEP_ARCHIVE']
        
        # Generate realistic storage distribution
        total_objects = random.randint(10000, 100000)
        total_size_gb = random.randint(500, 5000)
        
        storage_breakdown = {}
        size_breakdown = {}
        remaining_objects = total_objects
        remaining_size = total_size_gb
        
        # Distribute across storage classes (weighted toward STANDARD)
        weights = [0.5, 0.25, 0.1, 0.1, 0.05]
        
        for i, storage_class in enumerate(storage_classes[:-1]):
            objects = int(remaining_objects * weights[i])
            size = int(remaining_size * weights[i])
            
            storage_breakdown[storage_class] = objects
            size_breakdown[storage_class] = size
            
            remaining_objects -= objects
            remaining_size -= size
        
        # Assign remainder to last class
        storage_breakdown[storage_classes[-1]] = remaining_objects
        size_breakdown[storage_classes[-1]] = remaining_size
        
        # Simulate access patterns
        access_patterns = {
            'frequent': int(total_objects * 0.3),
            'infrequent': int(total_objects * 0.5),
            'archive': int(total_objects * 0.2)
        }
        
        # Calculate costs
        cost_breakdown = {}
        total_storage_cost = 0
        
        for storage_class, size_gb in size_breakdown.items():
            monthly_cost = size_gb * self.storage_costs[storage_class]
            cost_breakdown[storage_class] = monthly_cost
            total_storage_cost += monthly_cost
        
        cost_breakdown['total_storage'] = total_storage_cost
        cost_breakdown['estimated_requests'] = total_objects * 0.1 * self.request_costs['GET']
        cost_breakdown['total_monthly'] = total_storage_cost + cost_breakdown['estimated_requests']
        
        metrics = StorageMetrics(
            total_objects=total_objects,
            total_size_bytes=total_size_gb * 1024 * 1024 * 1024,
            storage_class_breakdown=size_breakdown,
            access_patterns=access_patterns,
            cost_breakdown=cost_breakdown
        )
        
        print(f"   Total Objects: {metrics.total_objects:,}")
        print(f"   Total Size: {total_size_gb:,} GB")
        print(f"   Monthly Cost: ${cost_breakdown['total_monthly']:.2f}")
        
        print(f"\n   Storage Class Distribution:")
        for storage_class, size_gb in size_breakdown.items():
            percentage = (size_gb / total_size_gb) * 100
            cost = cost_breakdown.get(storage_class, 0)
            print(f"     {storage_class}: {size_gb:,} GB ({percentage:.1f}%) - ${cost:.2f}/month")
        
        return metrics
    
    def recommend_lifecycle_policies(self, metrics: StorageMetrics) -> List[LifecycleRule]:
        """Recommend lifecycle management policies"""
        print(f"\n🔄 Generating Lifecycle Recommendations")
        
        rules = []
        
        # Rule 1: Transition logs to IA after 30 days, Glacier after 90 days
        rules.append(LifecycleRule(
            rule_id="logs-lifecycle",
            prefix="logs/",
            enabled=True,
            transitions=[
                (30, "STANDARD_IA"),
                (90, "GLACIER")
            ],
            expiration_days=2555  # 7 years
        ))
        
        # Rule 2: Transition backups to IA after 7 days, Deep Archive after 30 days
        rules.append(LifecycleRule(
            rule_id="backups-lifecycle",
            prefix="backups/",
            enabled=True,
            transitions=[
                (7, "STANDARD_IA"),
                (30, "DEEP_ARCHIVE")
            ]
        ))
        
        # Rule 3: Transition temp files to IA after 1 day, delete after 7 days
        rules.append(LifecycleRule(
            rule_id="temp-cleanup",
            prefix="temp/",
            enabled=True,
            transitions=[
                (1, "STANDARD_IA")
            ],
            expiration_days=7
        ))
        
        # Rule 4: Transition analytics data based on access patterns
        if metrics.access_patterns['archive'] > metrics.total_objects * 0.15:
            rules.append(LifecycleRule(
                rule_id="analytics-archive",
                prefix="analytics/",
                enabled=True,
                transitions=[
                    (60, "STANDARD_IA"),
                    (180, "GLACIER"),
                    (365, "DEEP_ARCHIVE")
                ]
            ))
        
        print(f"   Generated {len(rules)} lifecycle rules:")
        for rule in rules:
            print(f"     {rule.rule_id}: {rule.prefix}")
            for days, storage_class in rule.transitions:
                print(f"       → {storage_class} after {days} days")
            if rule.expiration_days:
                print(f"       → DELETE after {rule.expiration_days} days")
        
        return rules
    
    def calculate_cost_savings(self, metrics: StorageMetrics, lifecycle_rules: List[LifecycleRule]) -> Dict[str, float]:
        """Calculate potential cost savings from lifecycle policies"""
        print(f"\n💰 Calculating Cost Savings")
        
        current_monthly_cost = metrics.cost_breakdown['total_monthly']
        
        # Simulate cost savings
        savings_by_rule = {}
        total_savings = 0
        
        for rule in lifecycle_rules:
            if rule.prefix == "logs/":
                # Assume 20% of data is logs
                affected_size_gb = sum(metrics.storage_class_breakdown.values()) * 0.2
                
                # Calculate savings from transitioning to cheaper storage
                standard_cost = affected_size_gb * self.storage_costs['STANDARD']
                ia_cost = affected_size_gb * 0.7 * self.storage_costs['STANDARD_IA']  # 70% transitions
                glacier_cost = affected_size_gb * 0.3 * self.storage_costs['GLACIER']  # 30% to Glacier
                
                new_cost = ia_cost + glacier_cost
                rule_savings = standard_cost - new_cost
                
            elif rule.prefix == "backups/":
                # Assume 15% of data is backups
                affected_size_gb = sum(metrics.storage_class_breakdown.values()) * 0.15
                
                standard_cost = affected_size_gb * self.storage_costs['STANDARD']
                deep_archive_cost = affected_size_gb * self.storage_costs['DEEP_ARCHIVE']
                
                rule_savings = standard_cost - deep_archive_cost
                
            elif rule.prefix == "temp/":
                # Assume 5% of data is temp files
                affected_size_gb = sum(metrics.storage_class_breakdown.values()) * 0.05
                
                # Savings from deletion
                rule_savings = affected_size_gb * self.storage_costs['STANDARD']
                
            else:
                # Generic savings estimate
                affected_size_gb = sum(metrics.storage_class_breakdown.values()) * 0.1
                rule_savings = affected_size_gb * self.storage_costs['STANDARD'] * 0.3
            
            savings_by_rule[rule.rule_id] = rule_savings
            total_savings += rule_savings
        
        savings_percentage = (total_savings / current_monthly_cost) * 100
        annual_savings = total_savings * 12
        
        print(f"   Current Monthly Cost: ${current_monthly_cost:.2f}")
        print(f"   Potential Monthly Savings: ${total_savings:.2f} ({savings_percentage:.1f}%)")
        print(f"   Potential Annual Savings: ${annual_savings:.2f}")
        
        print(f"\n   Savings by Rule:")
        for rule_id, savings in savings_by_rule.items():
            print(f"     {rule_id}: ${savings:.2f}/month")
        
        return {
            'current_monthly_cost': current_monthly_cost,
            'monthly_savings': total_savings,
            'annual_savings': annual_savings,
            'savings_percentage': savings_percentage,
            'savings_by_rule': savings_by_rule
        }
    
    def analyze_access_patterns(self) -> Dict[str, Any]:
        """Analyze object access patterns for optimization"""
        print(f"\n🔍 Analyzing Access Patterns")
        
        # Simulate access pattern analysis
        patterns = {
            'hot_objects': {
                'count': random.randint(1000, 5000),
                'access_frequency': 'daily',
                'recommendation': 'Keep in STANDARD'
            },
            'warm_objects': {
                'count': random.randint(5000, 15000),
                'access_frequency': 'weekly',
                'recommendation': 'Consider STANDARD_IA'
            },
            'cold_objects': {
                'count': random.randint(10000, 30000),
                'access_frequency': 'monthly',
                'recommendation': 'Move to GLACIER'
            },
            'frozen_objects': {
                'count': random.randint(5000, 20000),
                'access_frequency': 'yearly',
                'recommendation': 'Move to DEEP_ARCHIVE'
            }
        }
        
        # Calculate access costs
        total_gets = sum(pattern['count'] for pattern in patterns.values())
        monthly_request_cost = (total_gets / 1000) * self.request_costs['GET']
        
        print(f"   Access Pattern Analysis:")
        for pattern_name, data in patterns.items():
            print(f"     {pattern_name}: {data['count']:,} objects ({data['access_frequency']}) → {data['recommendation']}")
        
        print(f"   Monthly Request Cost: ${monthly_request_cost:.2f}")
        
        return {
            'patterns': patterns,
            'total_requests': total_gets,
            'monthly_request_cost': monthly_request_cost
        }
    
    def generate_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        print(f"\n📋 Generating Optimization Report")
        
        # Analyze current state
        metrics = self.analyze_storage_usage()
        access_analysis = self.analyze_access_patterns()
        
        # Generate recommendations
        lifecycle_rules = self.recommend_lifecycle_policies(metrics)
        cost_savings = self.calculate_cost_savings(metrics, lifecycle_rules)
        
        # Additional recommendations
        recommendations = []
        
        # Storage class optimization
        standard_percentage = (metrics.storage_class_breakdown.get('STANDARD', 0) / 
                             sum(metrics.storage_class_breakdown.values())) * 100
        
        if standard_percentage > 60:
            recommendations.append({
                'type': 'storage_class',
                'priority': 'high',
                'description': 'High percentage of data in STANDARD storage',
                'action': 'Implement lifecycle policies to transition older data to cheaper storage classes',
                'potential_savings': f"${cost_savings['monthly_savings']:.2f}/month"
            })
        
        # Request optimization
        if access_analysis['monthly_request_cost'] > 50:
            recommendations.append({
                'type': 'request_optimization',
                'priority': 'medium',
                'description': 'High request costs detected',
                'action': 'Implement caching layer or optimize access patterns',
                'potential_savings': f"${access_analysis['monthly_request_cost'] * 0.3:.2f}/month"
            })
        
        # Multipart upload optimization
        recommendations.append({
            'type': 'upload_optimization',
            'priority': 'low',
            'description': 'Optimize large file uploads',
            'action': 'Use multipart uploads for files >100MB to improve performance',
            'potential_savings': 'Improved upload reliability and speed'
        })
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'storage_metrics': metrics,
            'access_analysis': access_analysis,
            'lifecycle_rules': lifecycle_rules,
            'cost_savings': cost_savings,
            'recommendations': recommendations,
            'summary': {
                'total_objects': metrics.total_objects,
                'total_size_gb': metrics.total_size_bytes // (1024**3),
                'current_monthly_cost': cost_savings['current_monthly_cost'],
                'potential_monthly_savings': cost_savings['monthly_savings'],
                'optimization_score': min(100, int(cost_savings['savings_percentage'] * 2))
            }
        }
        
        return report
    
    def print_optimization_report(self, report: Dict[str, Any]):
        """Print formatted optimization report"""
        print(f"\n📊 S3 Storage Optimization Report")
        print(f"   Generated: {report['timestamp']}")
        
        summary = report['summary']
        print(f"\n📈 Summary")
        print(f"   Total Objects: {summary['total_objects']:,}")
        print(f"   Total Storage: {summary['total_size_gb']:,} GB")
        print(f"   Current Monthly Cost: ${summary['current_monthly_cost']:.2f}")
        print(f"   Potential Savings: ${summary['potential_monthly_savings']:.2f}/month")
        print(f"   Optimization Score: {summary['optimization_score']}/100")
        
        print(f"\n🎯 Recommendations")
        for i, rec in enumerate(report['recommendations'], 1):
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[rec['priority']]
            print(f"   {i}. {priority_emoji} {rec['description']}")
            print(f"      Action: {rec['action']}")
            print(f"      Savings: {rec['potential_savings']}")
        
        print(f"\n🔄 Lifecycle Rules")
        for rule in report['lifecycle_rules']:
            status = "✅" if rule.enabled else "❌"
            print(f"   {status} {rule.rule_id} ({rule.prefix})")

def demonstrate_s3_analytics():
    """Demonstrate S3 analytics and optimization"""
    print("=== S3 Storage Analytics Demonstration ===")
    
    # Import S3Client
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from s3_client import S3Client
    
    # Initialize S3 client and analytics
    s3_client = S3Client("https://s3.amazonaws.com", "analytics-bucket", "us-east-1")
    s3_client.authenticate("AKIAIOSFODNN7EXAMPLE", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY")
    
    analytics = S3Analytics(s3_client)
    
    # Generate and display optimization report
    report = analytics.generate_optimization_report()
    analytics.print_optimization_report(report)
    
    # Simulate implementing lifecycle policies
    print(f"\n🚀 Simulating Lifecycle Policy Implementation")
    
    for rule in report['lifecycle_rules']:
        print(f"   Implementing {rule.rule_id}...")
        time.sleep(0.5)  # Simulate API call
        print(f"   ✅ {rule.rule_id} activated")
    
    # Show projected savings over time
    print(f"\n📅 Projected Savings Timeline")
    monthly_savings = report['cost_savings']['monthly_savings']
    
    timeline = [
        (1, monthly_savings * 0.2),   # Month 1: 20% savings
        (3, monthly_savings * 0.5),   # Month 3: 50% savings
        (6, monthly_savings * 0.8),   # Month 6: 80% savings
        (12, monthly_savings * 1.0)   # Month 12: 100% savings
    ]
    
    cumulative_savings = 0
    for month, savings in timeline:
        cumulative_savings += savings
        print(f"   Month {month:2d}: ${savings:.2f}/month (cumulative: ${cumulative_savings:.2f})")
    
    print(f"\n💡 Additional Optimization Tips:")
    tips = [
        "Enable S3 Intelligent-Tiering for automatic cost optimization",
        "Use S3 Transfer Acceleration for faster uploads from distant locations",
        "Implement CloudFront CDN to reduce GET request costs",
        "Use S3 Select to query data without downloading entire objects",
        "Enable S3 Analytics to get detailed storage class analysis",
        "Consider using S3 Batch Operations for large-scale object management"
    ]
    
    for i, tip in enumerate(tips, 1):
        print(f"   {i}. {tip}")

if __name__ == "__main__":
    demonstrate_s3_analytics()
    
    print(f"\n🎯 S3 analytics enable data-driven storage optimization")
    print(f"💡 Key benefits: cost reduction, performance improvement, automated management")
    print(f"🚀 Best practices: lifecycle policies, access pattern analysis, storage class optimization")
