#!/usr/bin/env python3
"""
Prometheus Scraper Implementation
Demonstrates HTTP/1.1 based metrics collection and service discovery
"""

import time
import threading
import requests
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import urllib.parse

class ScrapeResult(Enum):
    """Scrape result status"""
    SUCCESS = "success"
    TIMEOUT = "timeout"
    ERROR = "error"
    NOT_FOUND = "not_found"

@dataclass
class ScrapeTarget:
    """Prometheus scrape target"""
    job_name: str
    instance: str
    metrics_path: str = "/metrics"
    scrape_interval: int = 15
    scrape_timeout: int = 10
    scheme: str = "http"
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class ScrapeSample:
    """Individual metric sample from scrape"""
    metric_name: str
    labels: Dict[str, str]
    value: float
    timestamp: float

@dataclass
class ScrapeJob:
    """Scrape job result"""
    target: ScrapeTarget
    status: ScrapeResult
    samples: List[ScrapeSample] = field(default_factory=list)
    scrape_duration: float = 0.0
    error_message: str = ""

class ServiceDiscovery:
    """
    Service discovery for Prometheus targets
    Simulates Kubernetes service discovery
    """
    
    def __init__(self):
        self.targets: List[ScrapeTarget] = []
        self.discovery_interval = 30
        self.running = False
        
        # Initialize with static targets
        self._add_static_targets()
        
        print("[Service Discovery] Initialized")
    
    def _add_static_targets(self):
        """Add static scrape targets"""
        static_targets = [
            ScrapeTarget(
                job_name="demo-app",
                instance="localhost:8080",
                labels={"service": "web", "environment": "demo"}
            ),
            ScrapeTarget(
                job_name="node-exporter",
                instance="localhost:9100",
                labels={"service": "node-exporter", "environment": "demo"}
            ),
            ScrapeTarget(
                job_name="kube-state-metrics",
                instance="localhost:8081",
                metrics_path="/metrics",
                labels={"service": "kube-state-metrics", "environment": "demo"}
            )
        ]
        
        self.targets.extend(static_targets)
        print(f"[Service Discovery] Added {len(static_targets)} static targets")
    
    def discover_kubernetes_targets(self) -> List[ScrapeTarget]:
        """Simulate Kubernetes service discovery"""
        # In real implementation, this would query Kubernetes API
        discovered_targets = []
        
        # Simulate discovered pods with metrics
        pods = [
            {"name": "web-pod-1", "ip": "10.244.1.10", "port": 8080, "labels": {"app": "web"}},
            {"name": "api-pod-1", "ip": "10.244.1.20", "port": 8080, "labels": {"app": "api"}},
            {"name": "worker-pod-1", "ip": "10.244.1.30", "port": 9090, "labels": {"app": "worker"}}
        ]
        
        for pod in pods:
            target = ScrapeTarget(
                job_name="kubernetes-pods",
                instance=f"{pod['ip']}:{pod['port']}",
                labels={
                    "pod_name": pod["name"],
                    "app": pod["labels"]["app"],
                    "kubernetes_namespace": "default"
                }
            )
            discovered_targets.append(target)
        
        return discovered_targets
    
    def start_discovery(self):
        """Start service discovery loop"""
        self.running = True
        
        def discovery_loop():
            while self.running:
                try:
                    # Discover new targets
                    k8s_targets = self.discover_kubernetes_targets()
                    
                    # Update target list (simplified merge)
                    existing_instances = {t.instance for t in self.targets if t.job_name == "kubernetes-pods"}
                    new_instances = {t.instance for t in k8s_targets}
                    
                    # Add new targets
                    for target in k8s_targets:
                        if target.instance not in existing_instances:
                            self.targets.append(target)
                            print(f"[Service Discovery] Added target: {target.instance}")
                    
                    # Remove stale targets (simplified)
                    self.targets = [t for t in self.targets 
                                  if t.job_name != "kubernetes-pods" or t.instance in new_instances]
                    
                except Exception as e:
                    print(f"[Service Discovery] Error: {e}")
                
                time.sleep(self.discovery_interval)
        
        discovery_thread = threading.Thread(target=discovery_loop)
        discovery_thread.daemon = True
        discovery_thread.start()
        
        print("[Service Discovery] Started discovery loop")
    
    def stop_discovery(self):
        """Stop service discovery"""
        self.running = False
        print("[Service Discovery] Stopped discovery loop")
    
    def get_targets(self) -> List[ScrapeTarget]:
        """Get current list of targets"""
        return self.targets.copy()

class MetricsParser:
    """
    Parser for Prometheus exposition format
    """
    
    @staticmethod
    def parse_metrics(content: str, target: ScrapeTarget) -> List[ScrapeSample]:
        """Parse metrics from exposition format"""
        samples = []
        lines = content.strip().split('\n')
        current_metric = None
        
        for line in lines:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                if line.startswith('# TYPE'):
                    # Extract metric name from TYPE comment
                    parts = line.split()
                    if len(parts) >= 3:
                        current_metric = parts[2]
                continue
            
            # Parse metric line
            try:
                sample = MetricsParser._parse_metric_line(line, target)
                if sample:
                    samples.append(sample)
            except Exception as e:
                print(f"[Parser] Error parsing line '{line}': {e}")
        
        return samples
    
    @staticmethod
    def _parse_metric_line(line: str, target: ScrapeTarget) -> Optional[ScrapeSample]:
        """Parse individual metric line"""
        # Regular expression to parse metric lines
        # Format: metric_name{label1="value1",label2="value2"} value [timestamp]
        pattern = r'^([a-zA-Z_:][a-zA-Z0-9_:]*?)(\{[^}]*\})?\s+([^\s]+)(?:\s+([0-9]+))?$'
        match = re.match(pattern, line)
        
        if not match:
            return None
        
        metric_name = match.group(1)
        labels_str = match.group(2) or ""
        value_str = match.group(3)
        timestamp_str = match.group(4)
        
        # Parse labels
        labels = {}
        if labels_str:
            labels_str = labels_str[1:-1]  # Remove { }
            if labels_str:
                for label_pair in labels_str.split(','):
                    if '=' in label_pair:
                        key, value = label_pair.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"')
                        labels[key] = value
        
        # Add target labels
        labels.update(target.labels)
        labels['instance'] = target.instance
        labels['job'] = target.job_name
        
        # Parse value
        try:
            if value_str.lower() in ['nan', '+inf', '-inf']:
                return None  # Skip special values for demo
            value = float(value_str)
        except ValueError:
            return None
        
        # Parse timestamp
        timestamp = float(timestamp_str) if timestamp_str else time.time()
        
        return ScrapeSample(
            metric_name=metric_name,
            labels=labels,
            value=value,
            timestamp=timestamp
        )

class PrometheusScraper:
    """
    Prometheus scraper implementation
    Collects metrics via HTTP/1.1 from discovered targets
    """
    
    def __init__(self):
        self.service_discovery = ServiceDiscovery()
        self.scrape_jobs: List[ScrapeJob] = []
        self.running = False
        self.global_config = {
            "scrape_interval": 15,
            "scrape_timeout": 10,
            "evaluation_interval": 15
        }
        
        print("[Prometheus Scraper] Initialized")
    
    def start_scraping(self):
        """Start scraping loop"""
        self.running = True
        self.service_discovery.start_discovery()
        
        def scrape_loop():
            while self.running:
                targets = self.service_discovery.get_targets()
                
                # Group targets by scrape interval
                interval_groups = {}
                for target in targets:
                    interval = target.scrape_interval
                    if interval not in interval_groups:
                        interval_groups[interval] = []
                    interval_groups[interval].append(target)
                
                # Scrape each group
                for interval, group_targets in interval_groups.items():
                    self._scrape_targets(group_targets)
                
                time.sleep(1)  # Check every second
        
        scrape_thread = threading.Thread(target=scrape_loop)
        scrape_thread.daemon = True
        scrape_thread.start()
        
        print("[Prometheus Scraper] Started scraping loop")
    
    def stop_scraping(self):
        """Stop scraping"""
        self.running = False
        self.service_discovery.stop_discovery()
        print("[Prometheus Scraper] Stopped scraping")
    
    def _scrape_targets(self, targets: List[ScrapeTarget]):
        """Scrape a group of targets"""
        for target in targets:
            # Check if it's time to scrape this target
            last_scrape = getattr(target, '_last_scrape', 0)
            if time.time() - last_scrape < target.scrape_interval:
                continue
            
            target._last_scrape = time.time()
            
            # Scrape target in background
            scrape_thread = threading.Thread(target=self._scrape_target, args=(target,))
            scrape_thread.daemon = True
            scrape_thread.start()
    
    def _scrape_target(self, target: ScrapeTarget):
        """Scrape individual target"""
        start_time = time.time()
        
        try:
            # Build URL
            url = f"{target.scheme}://{target.instance}{target.metrics_path}"
            
            # Make HTTP request
            headers = {
                'User-Agent': 'Prometheus/2.40.0',
                'Accept': 'text/plain;version=0.0.4;q=1,*/*;q=0.1',
                'Accept-Encoding': 'gzip'
            }
            
            response = requests.get(
                url,
                headers=headers,
                timeout=target.scrape_timeout
            )
            
            scrape_duration = time.time() - start_time
            
            if response.status_code == 200:
                # Parse metrics
                samples = MetricsParser.parse_metrics(response.text, target)
                
                job = ScrapeJob(
                    target=target,
                    status=ScrapeResult.SUCCESS,
                    samples=samples,
                    scrape_duration=scrape_duration
                )
                
                print(f"[Scraper] Scraped {len(samples)} samples from {target.instance} in {scrape_duration:.3f}s")
                
            else:
                job = ScrapeJob(
                    target=target,
                    status=ScrapeResult.ERROR,
                    scrape_duration=scrape_duration,
                    error_message=f"HTTP {response.status_code}"
                )
                
                print(f"[Scraper] Error scraping {target.instance}: HTTP {response.status_code}")
            
            # Store job result
            self.scrape_jobs.append(job)
            
            # Keep only recent jobs (last 100)
            if len(self.scrape_jobs) > 100:
                self.scrape_jobs = self.scrape_jobs[-100:]
                
        except requests.exceptions.Timeout:
            job = ScrapeJob(
                target=target,
                status=ScrapeResult.TIMEOUT,
                scrape_duration=time.time() - start_time,
                error_message="Scrape timeout"
            )
            self.scrape_jobs.append(job)
            print(f"[Scraper] Timeout scraping {target.instance}")
            
        except Exception as e:
            job = ScrapeJob(
                target=target,
                status=ScrapeResult.ERROR,
                scrape_duration=time.time() - start_time,
                error_message=str(e)
            )
            self.scrape_jobs.append(job)
            print(f"[Scraper] Error scraping {target.instance}: {e}")
    
    def get_scrape_stats(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        if not self.scrape_jobs:
            return {"total_scrapes": 0}
        
        total_scrapes = len(self.scrape_jobs)
        successful_scrapes = len([j for j in self.scrape_jobs if j.status == ScrapeResult.SUCCESS])
        failed_scrapes = total_scrapes - successful_scrapes
        
        durations = [j.scrape_duration for j in self.scrape_jobs if j.status == ScrapeResult.SUCCESS]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        total_samples = sum(len(j.samples) for j in self.scrape_jobs if j.status == ScrapeResult.SUCCESS)
        
        return {
            "total_scrapes": total_scrapes,
            "successful_scrapes": successful_scrapes,
            "failed_scrapes": failed_scrapes,
            "success_rate": successful_scrapes / total_scrapes if total_scrapes > 0 else 0,
            "avg_scrape_duration": avg_duration,
            "total_samples": total_samples,
            "targets_count": len(self.service_discovery.get_targets())
        }
    
    def get_recent_samples(self, limit: int = 10) -> List[ScrapeSample]:
        """Get recent metric samples"""
        recent_samples = []
        
        for job in reversed(self.scrape_jobs[-10:]):
            if job.status == ScrapeResult.SUCCESS:
                recent_samples.extend(job.samples[:limit])
                if len(recent_samples) >= limit:
                    break
        
        return recent_samples[:limit]

def demonstrate_prometheus_scraper():
    """Demonstrate Prometheus scraper functionality"""
    print("=== Prometheus Scraper Demo ===")
    
    # Initialize scraper
    scraper = PrometheusScraper()
    
    # Start scraping
    scraper.start_scraping()
    
    print("\n1. Starting scraping process...")
    print("   Note: This demo will attempt to scrape localhost:8080")
    print("   Run metrics_exporter.py in another terminal for full demo")
    
    # Let it run for a while
    time.sleep(8)
    
    # Show statistics
    print("\n2. Scraping statistics...")
    stats = scraper.get_scrape_stats()
    print(f"   Total scrapes: {stats['total_scrapes']}")
    print(f"   Successful: {stats['successful_scrapes']}")
    print(f"   Failed: {stats['failed_scrapes']}")
    print(f"   Success rate: {stats['success_rate']:.1%}")
    print(f"   Avg duration: {stats['avg_scrape_duration']:.3f}s")
    print(f"   Total samples: {stats['total_samples']}")
    print(f"   Active targets: {stats['targets_count']}")
    
    # Show recent samples
    print("\n3. Recent metric samples...")
    samples = scraper.get_recent_samples(5)
    for sample in samples:
        labels_str = ",".join([f'{k}="{v}"' for k, v in sample.labels.items()])
        print(f"   {sample.metric_name}{{{labels_str}}} = {sample.value}")
    
    # Show targets
    print("\n4. Discovered targets...")
    targets = scraper.service_discovery.get_targets()
    for target in targets:
        print(f"   {target.job_name}: {target.instance} (interval: {target.scrape_interval}s)")
    
    # Cleanup
    print("\n5. Stopping scraper...")
    scraper.stop_scraping()
    
    print("\n=== Prometheus Scraper Demo Complete ===")

if __name__ == "__main__":
    demonstrate_prometheus_scraper()
