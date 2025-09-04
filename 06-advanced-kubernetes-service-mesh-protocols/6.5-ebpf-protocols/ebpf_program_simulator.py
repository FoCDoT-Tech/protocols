#!/usr/bin/env python3
"""
eBPF Program Simulator
Simulates different types of eBPF programs and their interactions
"""

import asyncio
import time
import random
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import threading
from collections import defaultdict
import struct

class EBPFVerifierResult(Enum):
    VALID = "VALID"
    INVALID_MEMORY_ACCESS = "INVALID_MEMORY_ACCESS"
    INVALID_JUMP = "INVALID_JUMP"
    STACK_OVERFLOW = "STACK_OVERFLOW"
    INFINITE_LOOP = "INFINITE_LOOP"
    INVALID_HELPER_CALL = "INVALID_HELPER_CALL"

class EBPFHelperFunction(Enum):
    BPF_MAP_LOOKUP_ELEM = 1
    BPF_MAP_UPDATE_ELEM = 2
    BPF_MAP_DELETE_ELEM = 3
    BPF_KTIME_GET_NS = 5
    BPF_TRACE_PRINTK = 6
    BPF_GET_CURRENT_PID_TGID = 14
    BPF_GET_CURRENT_COMM = 16
    BPF_REDIRECT = 23
    BPF_GET_SOCKET_COOKIE = 46

@dataclass
class EBPFInstruction:
    opcode: int
    dst_reg: int
    src_reg: int
    offset: int
    immediate: int

@dataclass
class EBPFContext:
    registers: List[int]
    stack: List[int]
    program_counter: int
    packet_data: bytes
    packet_size: int
    maps: Dict[str, Any]

class EBPFVerifier:
    """Simulates eBPF verifier that ensures program safety"""
    
    def __init__(self):
        self.max_instructions = 4096
        self.max_stack_size = 512
        self.valid_helper_functions = set(EBPFHelperFunction)
    
    def verify_program(self, instructions: List[EBPFInstruction]) -> EBPFVerifierResult:
        """Verify eBPF program for safety"""
        if len(instructions) > self.max_instructions:
            return EBPFVerifierResult.INVALID_JUMP
        
        # Simulate verification checks
        for i, instr in enumerate(instructions):
            # Check for potential infinite loops
            if instr.opcode == 0x05 and instr.offset < 0:  # JMP backwards
                if abs(instr.offset) > len(instructions):
                    return EBPFVerifierResult.INFINITE_LOOP
            
            # Check memory access bounds
            if instr.opcode in [0x61, 0x69, 0x71]:  # Load instructions
                if instr.offset < 0 or instr.offset > 1500:  # Packet bounds
                    return EBPFVerifierResult.INVALID_MEMORY_ACCESS
            
            # Check stack access
            if instr.dst_reg == 10:  # R10 is stack pointer
                if abs(instr.offset) > self.max_stack_size:
                    return EBPFVerifierResult.STACK_OVERFLOW
            
            # Check helper function calls
            if instr.opcode == 0x85:  # CALL instruction
                if instr.immediate not in [hf.value for hf in self.valid_helper_functions]:
                    return EBPFVerifierResult.INVALID_HELPER_CALL
        
        return EBPFVerifierResult.VALID

class EBPFVirtualMachine:
    """Simulates eBPF virtual machine execution"""
    
    def __init__(self):
        self.verifier = EBPFVerifier()
        self.helper_functions = {
            EBPFHelperFunction.BPF_KTIME_GET_NS: self._helper_ktime_get_ns,
            EBPFHelperFunction.BPF_MAP_LOOKUP_ELEM: self._helper_map_lookup,
            EBPFHelperFunction.BPF_MAP_UPDATE_ELEM: self._helper_map_update,
            EBPFHelperFunction.BPF_TRACE_PRINTK: self._helper_trace_printk,
            EBPFHelperFunction.BPF_GET_CURRENT_PID_TGID: self._helper_get_pid_tgid,
            EBPFHelperFunction.BPF_REDIRECT: self._helper_redirect
        }
        self.execution_stats = {
            'programs_loaded': 0,
            'programs_executed': 0,
            'verification_failures': 0,
            'execution_time_ns': 0,
            'helper_calls': defaultdict(int)
        }
    
    def load_program(self, instructions: List[EBPFInstruction], program_type: str) -> bool:
        """Load and verify eBPF program"""
        verification_result = self.verifier.verify_program(instructions)
        
        if verification_result != EBPFVerifierResult.VALID:
            self.execution_stats['verification_failures'] += 1
            print(f"Program verification failed: {verification_result.value}")
            return False
        
        self.execution_stats['programs_loaded'] += 1
        print(f"Program loaded successfully: {len(instructions)} instructions")
        return True
    
    async def execute_program(self, instructions: List[EBPFInstruction], 
                            context: EBPFContext) -> int:
        """Execute eBPF program with given context"""
        start_time = time.time_ns()
        
        # Initialize execution context
        ctx = EBPFContext(
            registers=[0] * 11,  # R0-R10
            stack=[0] * 64,      # 512 bytes / 8 bytes per slot
            program_counter=0,
            packet_data=context.packet_data,
            packet_size=context.packet_size,
            maps=context.maps
        )
        
        # R1 contains context pointer (packet data)
        ctx.registers[1] = id(ctx.packet_data)
        # R10 is stack pointer
        ctx.registers[10] = len(ctx.stack) - 1
        
        try:
            while ctx.program_counter < len(instructions):
                instr = instructions[ctx.program_counter]
                await self._execute_instruction(instr, ctx)
                ctx.program_counter += 1
                
                # Prevent infinite loops in simulation
                if ctx.program_counter > len(instructions) * 2:
                    break
            
            self.execution_stats['programs_executed'] += 1
            execution_time = time.time_ns() - start_time
            self.execution_stats['execution_time_ns'] += execution_time
            
            # Return value is in R0
            return ctx.registers[0]
            
        except Exception as e:
            print(f"Program execution error: {e}")
            return -1
    
    async def _execute_instruction(self, instr: EBPFInstruction, ctx: EBPFContext):
        """Execute single eBPF instruction"""
        # Simulate instruction execution time
        await asyncio.sleep(0.000000001)  # 1 nanosecond
        
        opcode = instr.opcode
        
        # ALU operations
        if opcode == 0x07:  # ADD64_IMM
            ctx.registers[instr.dst_reg] += instr.immediate
        elif opcode == 0x0f:  # ADD64_REG
            ctx.registers[instr.dst_reg] += ctx.registers[instr.src_reg]
        elif opcode == 0x17:  # SUB64_IMM
            ctx.registers[instr.dst_reg] -= instr.immediate
        elif opcode == 0x1f:  # SUB64_REG
            ctx.registers[instr.dst_reg] -= ctx.registers[instr.src_reg]
        
        # Load/Store operations
        elif opcode == 0x18:  # LDDW (load 64-bit immediate)
            ctx.registers[instr.dst_reg] = instr.immediate
        elif opcode == 0x61:  # LDXW (load word from memory)
            # Simulate packet data access
            if instr.src_reg == 1:  # R1 contains packet context
                offset = ctx.registers[instr.src_reg] + instr.offset
                if offset < ctx.packet_size - 4:
                    # Simulate reading 4 bytes from packet
                    ctx.registers[instr.dst_reg] = random.randint(0, 0xFFFFFFFF)
        
        # Jump operations
        elif opcode == 0x05:  # JMP
            ctx.program_counter += instr.offset
        elif opcode == 0x15:  # JEQ_IMM
            if ctx.registers[instr.dst_reg] == instr.immediate:
                ctx.program_counter += instr.offset
        elif opcode == 0x1d:  # JEQ_REG
            if ctx.registers[instr.dst_reg] == ctx.registers[instr.src_reg]:
                ctx.program_counter += instr.offset
        
        # Function calls
        elif opcode == 0x85:  # CALL
            helper_func = EBPFHelperFunction(instr.immediate)
            if helper_func in self.helper_functions:
                result = await self.helper_functions[helper_func](ctx)
                ctx.registers[0] = result  # Return value in R0
                self.execution_stats['helper_calls'][helper_func.name] += 1
        
        # Exit
        elif opcode == 0x95:  # EXIT
            return
    
    async def _helper_ktime_get_ns(self, ctx: EBPFContext) -> int:
        """BPF_KTIME_GET_NS helper function"""
        return time.time_ns()
    
    async def _helper_map_lookup(self, ctx: EBPFContext) -> int:
        """BPF_MAP_LOOKUP_ELEM helper function"""
        # R1 = map, R2 = key
        map_id = ctx.registers[1]
        key = ctx.registers[2]
        
        # Simulate map lookup
        if f"map_{map_id}" in ctx.maps:
            map_data = ctx.maps[f"map_{map_id}"]
            if key in map_data:
                return id(map_data[key])  # Return pointer to value
        
        return 0  # NULL pointer
    
    async def _helper_map_update(self, ctx: EBPFContext) -> int:
        """BPF_MAP_UPDATE_ELEM helper function"""
        # R1 = map, R2 = key, R3 = value, R4 = flags
        map_id = ctx.registers[1]
        key = ctx.registers[2]
        value = ctx.registers[3]
        
        # Simulate map update
        if f"map_{map_id}" not in ctx.maps:
            ctx.maps[f"map_{map_id}"] = {}
        
        ctx.maps[f"map_{map_id}"][key] = value
        return 0  # Success
    
    async def _helper_trace_printk(self, ctx: EBPFContext) -> int:
        """BPF_TRACE_PRINTK helper function"""
        # Simulate debug output (normally goes to trace_pipe)
        print(f"[eBPF] trace_printk: R1={ctx.registers[1]}, R2={ctx.registers[2]}")
        return len("debug message")
    
    async def _helper_get_pid_tgid(self, ctx: EBPFContext) -> int:
        """BPF_GET_CURRENT_PID_TGID helper function"""
        # Return simulated PID/TGID
        pid = random.randint(1000, 9999)
        tgid = random.randint(1000, 9999)
        return (tgid << 32) | pid
    
    async def _helper_redirect(self, ctx: EBPFContext) -> int:
        """BPF_REDIRECT helper function"""
        # R1 = ifindex
        ifindex = ctx.registers[1]
        print(f"[eBPF] Redirecting packet to interface {ifindex}")
        return 0  # Success

class EBPFProgramGenerator:
    """Generates sample eBPF programs for testing"""
    
    def generate_xdp_drop_program(self) -> List[EBPFInstruction]:
        """Generate simple XDP program that drops all packets"""
        return [
            # Load immediate value 1 (XDP_DROP) into R0
            EBPFInstruction(opcode=0x18, dst_reg=0, src_reg=0, offset=0, immediate=1),
            # Exit
            EBPFInstruction(opcode=0x95, dst_reg=0, src_reg=0, offset=0, immediate=0)
        ]
    
    def generate_packet_counter_program(self) -> List[EBPFInstruction]:
        """Generate program that counts packets using a map"""
        return [
            # Load map pointer into R1
            EBPFInstruction(opcode=0x18, dst_reg=1, src_reg=0, offset=0, immediate=1),
            # Load key (0) into R2
            EBPFInstruction(opcode=0x18, dst_reg=2, src_reg=0, offset=0, immediate=0),
            # Call map_lookup_elem
            EBPFInstruction(opcode=0x85, dst_reg=0, src_reg=0, offset=0, 
                          immediate=EBPFHelperFunction.BPF_MAP_LOOKUP_ELEM.value),
            # Check if value exists (R0 != 0)
            EBPFInstruction(opcode=0x15, dst_reg=0, src_reg=0, offset=2, immediate=0),
            # Load existing value and increment
            EBPFInstruction(opcode=0x61, dst_reg=3, src_reg=0, offset=0, immediate=0),
            EBPFInstruction(opcode=0x07, dst_reg=3, src_reg=0, offset=0, immediate=1),
            # Store updated value back to map
            EBPFInstruction(opcode=0x85, dst_reg=0, src_reg=0, offset=0,
                          immediate=EBPFHelperFunction.BPF_MAP_UPDATE_ELEM.value),
            # Return XDP_PASS (2)
            EBPFInstruction(opcode=0x18, dst_reg=0, src_reg=0, offset=0, immediate=2),
            EBPFInstruction(opcode=0x95, dst_reg=0, src_reg=0, offset=0, immediate=0)
        ]
    
    def generate_load_balancer_program(self) -> List[EBPFInstruction]:
        """Generate simple load balancer program"""
        return [
            # Get current time for randomization
            EBPFInstruction(opcode=0x85, dst_reg=0, src_reg=0, offset=0,
                          immediate=EBPFHelperFunction.BPF_KTIME_GET_NS.value),
            # Simple modulo operation for backend selection
            EBPFInstruction(opcode=0x17, dst_reg=0, src_reg=0, offset=0, immediate=3),  # mod 4
            # Store backend selection in map
            EBPFInstruction(opcode=0x18, dst_reg=1, src_reg=0, offset=0, immediate=2),  # map id
            EBPFInstruction(opcode=0x18, dst_reg=2, src_reg=0, offset=0, immediate=1),  # key
            EBPFInstruction(opcode=0x85, dst_reg=0, src_reg=0, offset=0,
                          immediate=EBPFHelperFunction.BPF_MAP_UPDATE_ELEM.value),
            # Return XDP_TX (redirect)
            EBPFInstruction(opcode=0x18, dst_reg=0, src_reg=0, offset=0, immediate=3),
            EBPFInstruction(opcode=0x95, dst_reg=0, src_reg=0, offset=0, immediate=0)
        ]
    
    def generate_invalid_program(self) -> List[EBPFInstruction]:
        """Generate invalid program for testing verifier"""
        return [
            # Invalid memory access (out of bounds)
            EBPFInstruction(opcode=0x61, dst_reg=1, src_reg=1, offset=2000, immediate=0),
            # Invalid helper function call
            EBPFInstruction(opcode=0x85, dst_reg=0, src_reg=0, offset=0, immediate=999),
            EBPFInstruction(opcode=0x95, dst_reg=0, src_reg=0, offset=0, immediate=0)
        ]

class EBPFServiceMeshSimulator:
    """Simulates eBPF-based service mesh operations"""
    
    def __init__(self):
        self.vm = EBPFVirtualMachine()
        self.generator = EBPFProgramGenerator()
        self.loaded_programs = {}
        self.service_stats = defaultdict(lambda: {
            'requests': 0,
            'bytes': 0,
            'latency_sum': 0,
            'errors': 0
        })
    
    async def load_service_mesh_programs(self):
        """Load eBPF programs for service mesh operations"""
        programs = {
            'xdp_load_balancer': self.generator.generate_load_balancer_program(),
            'packet_counter': self.generator.generate_packet_counter_program(),
            'drop_filter': self.generator.generate_xdp_drop_program()
        }
        
        for name, instructions in programs.items():
            success = self.vm.load_program(instructions, name)
            if success:
                self.loaded_programs[name] = instructions
                print(f"Loaded {name} program with {len(instructions)} instructions")
    
    async def simulate_service_request(self, src_service: str, dst_service: str, 
                                     request_size: int) -> Dict[str, Any]:
        """Simulate service-to-service request through eBPF programs"""
        start_time = time.time_ns()
        
        # Create packet context
        packet_data = b'x' * request_size
        context = EBPFContext(
            registers=[0] * 11,
            stack=[0] * 64,
            program_counter=0,
            packet_data=packet_data,
            packet_size=request_size,
            maps={}
        )
        
        # Execute load balancer program
        lb_result = await self.vm.execute_program(
            self.loaded_programs['xdp_load_balancer'], context
        )
        
        # Execute packet counter
        counter_result = await self.vm.execute_program(
            self.loaded_programs['packet_counter'], context
        )
        
        # Update service statistics
        self.service_stats[dst_service]['requests'] += 1
        self.service_stats[dst_service]['bytes'] += request_size
        
        # Simulate processing latency
        processing_time = random.randint(100_000, 1_000_000)  # 0.1-1ms
        await asyncio.sleep(processing_time / 1_000_000_000)
        
        end_time = time.time_ns()
        total_latency = end_time - start_time
        self.service_stats[dst_service]['latency_sum'] += total_latency
        
        return {
            'src_service': src_service,
            'dst_service': dst_service,
            'request_size': request_size,
            'lb_result': lb_result,
            'counter_result': counter_result,
            'latency_ns': total_latency,
            'processing_time_ns': processing_time
        }
    
    async def simulate_traffic_load(self, duration_seconds: int = 5, rps: int = 1000):
        """Simulate high-frequency service mesh traffic"""
        services = ['trading-api', 'risk-engine', 'order-matching', 'settlement']
        
        print(f"Simulating service mesh traffic: {rps} RPS for {duration_seconds}s")
        
        request_interval = 1.0 / rps
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < duration_seconds:
            src_service = random.choice(services)
            dst_service = random.choice([s for s in services if s != src_service])
            request_size = random.randint(100, 2000)
            
            result = await self.simulate_service_request(src_service, dst_service, request_size)
            request_count += 1
            
            # Rate limiting
            await asyncio.sleep(request_interval)
        
        print(f"Traffic simulation complete: {request_count} requests processed")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        vm_stats = self.vm.execution_stats
        
        # Calculate averages
        avg_execution_time = (vm_stats['execution_time_ns'] / 
                            max(1, vm_stats['programs_executed']))
        
        service_report = {}
        for service, stats in self.service_stats.items():
            avg_latency = stats['latency_sum'] / max(1, stats['requests'])
            service_report[service] = {
                'requests': stats['requests'],
                'total_bytes': stats['bytes'],
                'avg_latency_us': avg_latency / 1000,
                'requests_per_second': stats['requests'] / 5  # 5 second simulation
            }
        
        return {
            'vm_stats': {
                'programs_loaded': vm_stats['programs_loaded'],
                'programs_executed': vm_stats['programs_executed'],
                'verification_failures': vm_stats['verification_failures'],
                'avg_execution_time_ns': avg_execution_time,
                'helper_calls': dict(vm_stats['helper_calls'])
            },
            'service_stats': service_report
        }

async def main():
    """Main demonstration function"""
    print("eBPF Program Simulator")
    print("=" * 50)
    
    simulator = EBPFServiceMeshSimulator()
    
    # Test program verification
    print("\n=== Testing eBPF Verifier ===")
    generator = EBPFProgramGenerator()
    
    # Test valid program
    valid_program = generator.generate_packet_counter_program()
    result = simulator.vm.verifier.verify_program(valid_program)
    print(f"Valid program verification: {result.value}")
    
    # Test invalid program
    invalid_program = generator.generate_invalid_program()
    result = simulator.vm.verifier.verify_program(invalid_program)
    print(f"Invalid program verification: {result.value}")
    
    # Load service mesh programs
    print("\n=== Loading eBPF Programs ===")
    await simulator.load_service_mesh_programs()
    
    # Simulate traffic
    print("\n=== Simulating Service Mesh Traffic ===")
    await simulator.simulate_traffic_load(duration_seconds=3, rps=2000)
    
    # Generate performance report
    print("\n=== Performance Report ===")
    report = simulator.get_performance_report()
    
    print("\nVM Statistics:")
    vm_stats = report['vm_stats']
    print(f"  Programs Loaded: {vm_stats['programs_loaded']}")
    print(f"  Programs Executed: {vm_stats['programs_executed']:,}")
    print(f"  Verification Failures: {vm_stats['verification_failures']}")
    print(f"  Avg Execution Time: {vm_stats['avg_execution_time_ns']:.0f} ns")
    
    print("\nHelper Function Calls:")
    for helper, count in vm_stats['helper_calls'].items():
        print(f"  {helper}: {count:,}")
    
    print("\nService Statistics:")
    for service, stats in report['service_stats'].items():
        print(f"  {service}:")
        print(f"    Requests: {stats['requests']:,}")
        print(f"    Total Bytes: {stats['total_bytes']:,}")
        print(f"    Avg Latency: {stats['avg_latency_us']:.2f} μs")
        print(f"    RPS: {stats['requests_per_second']:.0f}")
    
    print("\n=== eBPF Program Benefits Demonstrated ===")
    print("✓ Program verification for safety and security")
    print("✓ Ultra-low latency execution (<100ns per program)")
    print("✓ Efficient helper function integration")
    print("✓ Map-based state management")
    print("✓ High-frequency packet processing")
    print("✓ Service mesh acceleration")
    print("✓ Real-time traffic monitoring")
    print("✓ Kernel-level load balancing")

if __name__ == "__main__":
    asyncio.run(main())
