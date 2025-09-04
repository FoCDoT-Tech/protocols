#!/usr/bin/env python3
"""
Storage Provisioner Implementation
Demonstrates dynamic volume provisioning and storage class management
"""

import json
import time
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

class VolumeBindingMode(Enum):
    """Volume binding modes"""
    IMMEDIATE = "Immediate"
    WAIT_FOR_FIRST_CONSUMER = "WaitForFirstConsumer"

class ReclaimPolicy(Enum):
    """Volume reclaim policies"""
    DELETE = "Delete"
    RETAIN = "Retain"
    RECYCLE = "Recycle"

@dataclass
class StorageClass:
    """Kubernetes StorageClass specification"""
    name: str
    provisioner: str
    parameters: Dict[str, str] = field(default_factory=dict)
    volume_binding_mode: VolumeBindingMode = VolumeBindingMode.IMMEDIATE
    allow_volume_expansion: bool = True
    reclaim_policy: ReclaimPolicy = ReclaimPolicy.DELETE
    mount_options: List[str] = field(default_factory=list)

@dataclass
class PersistentVolumeClaim:
    """Kubernetes PVC specification"""
    name: str
    namespace: str
    storage_class: str
    access_modes: List[str]
    size: str
    selector: Dict[str, Any] = field(default_factory=dict)
    volume_mode: str = "Filesystem"

@dataclass
class PersistentVolume:
    """Kubernetes PV specification"""
    name: str
    capacity: str
    access_modes: List[str]
    reclaim_policy: ReclaimPolicy
    storage_class: str
    csi_driver: str
    volume_handle: str
    node_affinity: Dict[str, Any] = field(default_factory=dict)

class StorageProvisioner:
    """
    Dynamic Storage Provisioner
    Handles automatic volume provisioning based on StorageClasses
    """
    
    def __init__(self, provisioner_name: str):
        self.provisioner_name = provisioner_name
        self.storage_classes: Dict[str, StorageClass] = {}
        self.pvcs: Dict[str, PersistentVolumeClaim] = {}
        self.pvs: Dict[str, PersistentVolume] = {}
        self.bindings: Dict[str, str] = {}  # pvc_key -> pv_name
        
        # Register default storage classes
        self._register_default_storage_classes()
        
        print(f"[Provisioner] Initialized {provisioner_name}")
    
    def _register_default_storage_classes(self):
        """Register default storage classes"""
        # Fast SSD storage class
        fast_ssd = StorageClass(
            name="fast-ssd",
            provisioner=self.provisioner_name,
            parameters={
                "type": "gp3",
                "iops": "3000",
                "throughput": "125",
                "encrypted": "true"
            },
            volume_binding_mode=VolumeBindingMode.WAIT_FOR_FIRST_CONSUMER,
            allow_volume_expansion=True
        )
        
        # Standard storage class
        standard = StorageClass(
            name="standard",
            provisioner=self.provisioner_name,
            parameters={
                "type": "gp2",
                "encrypted": "false"
            },
            volume_binding_mode=VolumeBindingMode.IMMEDIATE,
            allow_volume_expansion=True
        )
        
        # Archive storage class
        archive = StorageClass(
            name="archive",
            provisioner=self.provisioner_name,
            parameters={
                "type": "sc1",
                "encrypted": "true"
            },
            volume_binding_mode=VolumeBindingMode.IMMEDIATE,
            allow_volume_expansion=False,
            reclaim_policy=ReclaimPolicy.RETAIN
        )
        
        self.storage_classes["fast-ssd"] = fast_ssd
        self.storage_classes["standard"] = standard
        self.storage_classes["archive"] = archive
        
        print(f"[Provisioner] Registered {len(self.storage_classes)} storage classes")
    
    def create_storage_class(self, storage_class: StorageClass):
        """Create new storage class"""
        self.storage_classes[storage_class.name] = storage_class
        print(f"[Provisioner] Created storage class: {storage_class.name}")
    
    def create_pvc(self, pvc: PersistentVolumeClaim) -> bool:
        """Create PVC and trigger provisioning"""
        pvc_key = f"{pvc.namespace}/{pvc.name}"
        
        if pvc_key in self.pvcs:
            print(f"[Provisioner] PVC {pvc_key} already exists")
            return False
        
        # Validate storage class
        if pvc.storage_class not in self.storage_classes:
            print(f"[Provisioner] Storage class {pvc.storage_class} not found")
            return False
        
        storage_class = self.storage_classes[pvc.storage_class]
        
        # Store PVC
        self.pvcs[pvc_key] = pvc
        print(f"[Provisioner] Created PVC {pvc_key}")
        
        # Provision volume based on binding mode
        if storage_class.volume_binding_mode == VolumeBindingMode.IMMEDIATE:
            self._provision_volume(pvc_key)
        else:
            print(f"[Provisioner] PVC {pvc_key} waiting for first consumer")
        
        return True
    
    def _provision_volume(self, pvc_key: str) -> Optional[str]:
        """Provision volume for PVC"""
        if pvc_key not in self.pvcs:
            return None
        
        pvc = self.pvcs[pvc_key]
        storage_class = self.storage_classes[pvc.storage_class]
        
        print(f"[Provisioner] Provisioning volume for PVC {pvc_key}")
        
        # Generate unique PV name
        pv_name = f"pvc-{uuid.uuid4().hex[:8]}"
        volume_handle = f"vol-{uuid.uuid4().hex[:16]}"
        
        # Create PV
        pv = PersistentVolume(
            name=pv_name,
            capacity=pvc.size,
            access_modes=pvc.access_modes,
            reclaim_policy=storage_class.reclaim_policy,
            storage_class=pvc.storage_class,
            csi_driver=storage_class.provisioner,
            volume_handle=volume_handle
        )
        
        # Add topology constraints if needed
        if "zone" in storage_class.parameters:
            pv.node_affinity = {
                "required": {
                    "nodeSelectorTerms": [{
                        "matchExpressions": [{
                            "key": "topology.kubernetes.io/zone",
                            "operator": "In",
                            "values": [storage_class.parameters["zone"]]
                        }]
                    }]
                }
            }
        
        # Simulate volume creation time
        time.sleep(1)
        
        # Store PV and create binding
        self.pvs[pv_name] = pv
        self.bindings[pvc_key] = pv_name
        
        print(f"[Provisioner] Provisioned volume {pv_name} for PVC {pvc_key}")
        return pv_name
    
    def bind_volume_on_scheduling(self, pvc_key: str, node_name: str) -> Optional[str]:
        """Bind volume when pod is scheduled (WaitForFirstConsumer)"""
        if pvc_key not in self.pvcs:
            return None
        
        if pvc_key in self.bindings:
            return self.bindings[pvc_key]
        
        pvc = self.pvcs[pvc_key]
        storage_class = self.storage_classes[pvc.storage_class]
        
        if storage_class.volume_binding_mode == VolumeBindingMode.WAIT_FOR_FIRST_CONSUMER:
            print(f"[Provisioner] Binding volume for PVC {pvc_key} on node {node_name}")
            return self._provision_volume(pvc_key)
        
        return None
    
    def delete_pvc(self, namespace: str, name: str) -> bool:
        """Delete PVC and handle volume reclaim"""
        pvc_key = f"{namespace}/{name}"
        
        if pvc_key not in self.pvcs:
            print(f"[Provisioner] PVC {pvc_key} not found")
            return False
        
        pvc = self.pvcs[pvc_key]
        
        # Handle bound volume
        if pvc_key in self.bindings:
            pv_name = self.bindings[pvc_key]
            pv = self.pvs[pv_name]
            
            print(f"[Provisioner] Handling reclaim for volume {pv_name}")
            
            if pv.reclaim_policy == ReclaimPolicy.DELETE:
                # Delete volume
                print(f"[Provisioner] Deleting volume {pv_name}")
                del self.pvs[pv_name]
            elif pv.reclaim_policy == ReclaimPolicy.RETAIN:
                # Retain volume but mark as released
                print(f"[Provisioner] Retaining volume {pv_name}")
                pv.reclaim_policy = ReclaimPolicy.RETAIN
            
            del self.bindings[pvc_key]
        
        # Delete PVC
        del self.pvcs[pvc_key]
        print(f"[Provisioner] Deleted PVC {pvc_key}")
        return True
    
    def expand_volume(self, pvc_key: str, new_size: str) -> bool:
        """Expand volume size"""
        if pvc_key not in self.pvcs:
            return False
        
        if pvc_key not in self.bindings:
            return False
        
        pvc = self.pvcs[pvc_key]
        storage_class = self.storage_classes[pvc.storage_class]
        
        if not storage_class.allow_volume_expansion:
            print(f"[Provisioner] Volume expansion not allowed for storage class {storage_class.name}")
            return False
        
        pv_name = self.bindings[pvc_key]
        pv = self.pvs[pv_name]
        
        print(f"[Provisioner] Expanding volume {pv_name} from {pv.capacity} to {new_size}")
        
        # Simulate expansion time
        time.sleep(2)
        
        # Update sizes
        pvc.size = new_size
        pv.capacity = new_size
        
        print(f"[Provisioner] Volume {pv_name} expanded successfully")
        return True
    
    def list_storage_classes(self) -> List[StorageClass]:
        """List available storage classes"""
        return list(self.storage_classes.values())
    
    def list_pvcs(self, namespace: str = None) -> List[PersistentVolumeClaim]:
        """List PVCs, optionally filtered by namespace"""
        if namespace:
            return [pvc for key, pvc in self.pvcs.items() if key.startswith(f"{namespace}/")]
        return list(self.pvcs.values())
    
    def list_pvs(self) -> List[PersistentVolume]:
        """List PVs"""
        return list(self.pvs.values())
    
    def get_provisioning_stats(self) -> Dict[str, Any]:
        """Get provisioning statistics"""
        total_capacity = 0
        storage_class_usage = {}
        
        for pv in self.pvs.values():
            # Parse capacity (simplified)
            capacity_str = pv.capacity.replace("Gi", "").replace("Ti", "000")
            capacity_gb = int(capacity_str)
            total_capacity += capacity_gb
            
            if pv.storage_class not in storage_class_usage:
                storage_class_usage[pv.storage_class] = {"count": 0, "capacity_gb": 0}
            
            storage_class_usage[pv.storage_class]["count"] += 1
            storage_class_usage[pv.storage_class]["capacity_gb"] += capacity_gb
        
        return {
            "total_pvcs": len(self.pvcs),
            "total_pvs": len(self.pvs),
            "total_capacity_gb": total_capacity,
            "storage_class_usage": storage_class_usage,
            "pending_pvcs": len([pvc for key, pvc in self.pvcs.items() if key not in self.bindings])
        }

def demonstrate_storage_provisioner():
    """Demonstrate storage provisioner functionality"""
    print("=== Storage Provisioner Demo ===")
    
    # Initialize provisioner
    provisioner = StorageProvisioner("demo.csi.example.com")
    
    # List storage classes
    print("\n1. Available storage classes...")
    storage_classes = provisioner.list_storage_classes()
    for sc in storage_classes:
        print(f"  {sc.name}: {sc.provisioner} ({sc.volume_binding_mode.value})")
    
    # Create PVCs
    print("\n2. Creating PVCs...")
    
    pvcs = [
        PersistentVolumeClaim(
            name="web-data",
            namespace="production",
            storage_class="fast-ssd",
            access_modes=["ReadWriteOnce"],
            size="10Gi"
        ),
        PersistentVolumeClaim(
            name="database-storage",
            namespace="production", 
            storage_class="standard",
            access_modes=["ReadWriteOnce"],
            size="50Gi"
        ),
        PersistentVolumeClaim(
            name="backup-storage",
            namespace="backup",
            storage_class="archive",
            access_modes=["ReadWriteOnce"],
            size="100Gi"
        )
    ]
    
    for pvc in pvcs:
        provisioner.create_pvc(pvc)
        time.sleep(0.5)
    
    # Simulate pod scheduling for WaitForFirstConsumer
    print("\n3. Simulating pod scheduling...")
    provisioner.bind_volume_on_scheduling("production/web-data", "node-1")
    
    # List PVCs and PVs
    print("\n4. Listing volumes...")
    pvcs_list = provisioner.list_pvcs()
    for pvc in pvcs_list:
        print(f"  PVC: {pvc.namespace}/{pvc.name} ({pvc.size}, {pvc.storage_class})")
    
    pvs_list = provisioner.list_pvs()
    for pv in pvs_list:
        print(f"  PV: {pv.name} ({pv.capacity}, {pv.storage_class})")
    
    # Expand volume
    print("\n5. Expanding volume...")
    provisioner.expand_volume("production/database-storage", "75Gi")
    
    # Show statistics
    print("\n6. Provisioning statistics...")
    stats = provisioner.get_provisioning_stats()
    print(f"  Total PVCs: {stats['total_pvcs']}")
    print(f"  Total PVs: {stats['total_pvs']}")
    print(f"  Total capacity: {stats['total_capacity_gb']}GB")
    print(f"  Pending PVCs: {stats['pending_pvcs']}")
    
    for sc_name, usage in stats['storage_class_usage'].items():
        print(f"  {sc_name}: {usage['count']} volumes, {usage['capacity_gb']}GB")
    
    # Cleanup
    print("\n7. Cleaning up...")
    for pvc in pvcs:
        provisioner.delete_pvc(pvc.namespace, pvc.name)
        time.sleep(0.2)
    
    print("\n=== Storage Provisioner Demo Complete ===")

if __name__ == "__main__":
    demonstrate_storage_provisioner()
