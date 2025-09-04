#!/usr/bin/env python3
"""
IoT Device Simulation with MQTT
Smart home IoT devices communicating via MQTT.
"""

import time
import threading
import random
import json
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

from mqtt_broker import MQTTBroker, MQTTMessage, QoSLevel
from mqtt_client import MQTTClient, MQTTClientConfig

class DeviceType(Enum):
    TEMPERATURE_SENSOR = "temperature_sensor"
    HUMIDITY_SENSOR = "humidity_sensor"
    MOTION_DETECTOR = "motion_detector"
    SMART_LIGHT = "smart_light"
    SMART_THERMOSTAT = "smart_thermostat"
    DOOR_SENSOR = "door_sensor"

@dataclass
class SensorReading:
    device_id: str
    device_type: DeviceType
    value: float
    unit: str
    timestamp: float
    location: str

class IoTDevice:
    def __init__(self, device_id: str, device_type: DeviceType, location: str, broker: MQTTBroker):
        self.device_id = device_id
        self.device_type = device_type
        self.location = location
        self.broker = broker
        
        # MQTT client configuration
        config = MQTTClientConfig(
            client_id=device_id,
            clean_session=True,
            keep_alive=300,  # 5 minutes
            will_topic=f"devices/{device_id}/status",
            will_payload="offline",
            will_qos=QoSLevel.AT_LEAST_ONCE,
            will_retain=True
        )
        
        self.client = MQTTClient(config)
        self.running = False
        self.publish_interval = 30  # seconds
        
        # Device state
        self.state = {}
        self.last_reading = None
    
    def start(self):
        """Start the IoT device"""
        self.client.connect(self.broker)
        self.running = True
        
        # Publish online status
        self.client.publish(f"devices/{self.device_id}/status", "online", 
                           QoSLevel.AT_LEAST_ONCE, retain=True)
        
        # Start data publishing thread
        threading.Thread(target=self._publish_loop, daemon=True).start()
        
        print(f"🔌 IoT Device '{self.device_id}' ({self.device_type.value}) started in {self.location}")
    
    def stop(self):
        """Stop the IoT device"""
        self.running = False
        
        # Publish offline status
        if self.client.is_connected():
            self.client.publish(f"devices/{self.device_id}/status", "offline", 
                               QoSLevel.AT_LEAST_ONCE, retain=True)
            self.client.disconnect()
        
        print(f"🔌 IoT Device '{self.device_id}' stopped")
    
    def _publish_loop(self):
        """Main publishing loop"""
        while self.running:
            try:
                reading = self._generate_reading()
                if reading:
                    self._publish_reading(reading)
                
                time.sleep(self.publish_interval + random.uniform(-5, 5))
            except Exception as e:
                print(f"❌ Device {self.device_id} publish error: {e}")
    
    def _generate_reading(self) -> SensorReading:
        """Generate sensor reading based on device type"""
        timestamp = time.time()
        
        if self.device_type == DeviceType.TEMPERATURE_SENSOR:
            # Simulate temperature with some variation
            base_temp = 22.0
            variation = random.uniform(-3, 3)
            value = base_temp + variation
            return SensorReading(self.device_id, self.device_type, value, "°C", timestamp, self.location)
        
        elif self.device_type == DeviceType.HUMIDITY_SENSOR:
            # Simulate humidity
            base_humidity = 45.0
            variation = random.uniform(-10, 15)
            value = max(0, min(100, base_humidity + variation))
            return SensorReading(self.device_id, self.device_type, value, "%", timestamp, self.location)
        
        elif self.device_type == DeviceType.MOTION_DETECTOR:
            # Random motion detection
            if random.random() < 0.1:  # 10% chance of motion
                value = 1.0
            else:
                value = 0.0
            return SensorReading(self.device_id, self.device_type, value, "detected", timestamp, self.location)
        
        elif self.device_type == DeviceType.DOOR_SENSOR:
            # Random door state changes
            if random.random() < 0.05:  # 5% chance of state change
                current_state = self.state.get('door_open', False)
                value = 1.0 if not current_state else 0.0
                self.state['door_open'] = not current_state
            else:
                value = 1.0 if self.state.get('door_open', False) else 0.0
            return SensorReading(self.device_id, self.device_type, value, "open" if value else "closed", timestamp, self.location)
        
        return None
    
    def _publish_reading(self, reading: SensorReading):
        """Publish sensor reading to MQTT"""
        topic = f"sensors/{self.location}/{self.device_type.value}"
        
        # Create payload
        payload = {
            "device_id": reading.device_id,
            "value": reading.value,
            "unit": reading.unit,
            "timestamp": reading.timestamp,
            "location": reading.location
        }
        
        # Publish with retention for latest state
        self.client.publish(topic, json.dumps(payload), QoSLevel.AT_LEAST_ONCE, retain=True)
        
        # Store last reading
        self.last_reading = reading
        
        print(f"📊 {reading.device_id}: {reading.value}{reading.unit} → {topic}")

class SmartActuator:
    def __init__(self, device_id: str, device_type: DeviceType, location: str, broker: MQTTBroker):
        self.device_id = device_id
        self.device_type = device_type
        self.location = location
        self.broker = broker
        
        config = MQTTClientConfig(
            client_id=device_id,
            clean_session=False,  # Persistent session for actuators
            keep_alive=600,
            will_topic=f"devices/{device_id}/status",
            will_payload="offline",
            will_qos=QoSLevel.AT_LEAST_ONCE,
            will_retain=True
        )
        
        self.client = MQTTClient(config)
        self.state = {"power": False, "level": 0}
    
    def start(self):
        """Start the smart actuator"""
        self.client.connect(self.broker)
        
        # Subscribe to control commands
        control_topic = f"controls/{self.location}/{self.device_type.value}"
        self.client.subscribe(control_topic, QoSLevel.AT_LEAST_ONCE, self._handle_command)
        
        # Publish online status and initial state
        self.client.publish(f"devices/{self.device_id}/status", "online", 
                           QoSLevel.AT_LEAST_ONCE, retain=True)
        self._publish_state()
        
        print(f"🔌 Smart Actuator '{self.device_id}' ({self.device_type.value}) started in {self.location}")
    
    def stop(self):
        """Stop the smart actuator"""
        if self.client.is_connected():
            self.client.publish(f"devices/{self.device_id}/status", "offline", 
                               QoSLevel.AT_LEAST_ONCE, retain=True)
            self.client.disconnect()
        
        print(f"🔌 Smart Actuator '{self.device_id}' stopped")
    
    def _handle_command(self, message: MQTTMessage):
        """Handle control commands"""
        try:
            command = json.loads(message.payload)
            
            if self.device_type == DeviceType.SMART_LIGHT:
                if "power" in command:
                    self.state["power"] = command["power"]
                    print(f"💡 {self.device_id}: Light {'ON' if self.state['power'] else 'OFF'}")
                
                if "brightness" in command and self.state["power"]:
                    self.state["level"] = max(0, min(100, command["brightness"]))
                    print(f"🔆 {self.device_id}: Brightness set to {self.state['level']}%")
            
            elif self.device_type == DeviceType.SMART_THERMOSTAT:
                if "temperature" in command:
                    self.state["target_temp"] = command["temperature"]
                    print(f"🌡️  {self.device_id}: Target temperature set to {self.state['target_temp']}°C")
                
                if "mode" in command:
                    self.state["mode"] = command["mode"]
                    print(f"❄️  {self.device_id}: Mode set to {self.state['mode']}")
            
            # Publish updated state
            self._publish_state()
            
        except Exception as e:
            print(f"❌ Command handling error for {self.device_id}: {e}")
    
    def _publish_state(self):
        """Publish current device state"""
        state_topic = f"state/{self.location}/{self.device_type.value}"
        
        payload = {
            "device_id": self.device_id,
            "timestamp": time.time(),
            **self.state
        }
        
        self.client.publish(state_topic, json.dumps(payload), QoSLevel.AT_LEAST_ONCE, retain=True)

class HomeAutomationController:
    def __init__(self, broker: MQTTBroker):
        self.broker = broker
        
        config = MQTTClientConfig(
            client_id="home_automation_controller",
            clean_session=False,
            keep_alive=300
        )
        
        self.client = MQTTClient(config)
        self.rules = []
        self.sensor_data = {}
    
    def start(self):
        """Start the automation controller"""
        self.client.connect(self.broker)
        
        # Subscribe to all sensor data
        self.client.subscribe("sensors/+/+", QoSLevel.AT_LEAST_ONCE, self._handle_sensor_data)
        
        # Set up automation rules
        self._setup_automation_rules()
        
        print("🏠 Home Automation Controller started")
    
    def stop(self):
        """Stop the automation controller"""
        if self.client.is_connected():
            self.client.disconnect()
        
        print("🏠 Home Automation Controller stopped")
    
    def _handle_sensor_data(self, message: MQTTMessage):
        """Handle incoming sensor data"""
        try:
            data = json.loads(message.payload)
            sensor_key = f"{data['location']}_{message.topic.split('/')[-1]}"
            self.sensor_data[sensor_key] = data
            
            # Check automation rules
            self._check_automation_rules()
            
        except Exception as e:
            print(f"❌ Sensor data handling error: {e}")
    
    def _setup_automation_rules(self):
        """Set up automation rules"""
        # Rule 1: Turn on lights when motion detected
        def motion_light_rule():
            for key, data in self.sensor_data.items():
                if "motion_detector" in key and data.get("value", 0) == 1:
                    location = data["location"]
                    # Turn on light in the same location
                    command = {"power": True, "brightness": 80}
                    control_topic = f"controls/{location}/smart_light"
                    self.client.publish(control_topic, json.dumps(command), QoSLevel.AT_LEAST_ONCE)
                    print(f"🤖 Automation: Motion detected in {location}, turning on lights")
        
        # Rule 2: Adjust thermostat based on temperature
        def temperature_thermostat_rule():
            for key, data in self.sensor_data.items():
                if "temperature_sensor" in key:
                    temp = data.get("value", 22)
                    location = data["location"]
                    
                    if temp > 25:
                        # Too hot, turn on cooling
                        command = {"temperature": 22, "mode": "cool"}
                        control_topic = f"controls/{location}/smart_thermostat"
                        self.client.publish(control_topic, json.dumps(command), QoSLevel.AT_LEAST_ONCE)
                        print(f"🤖 Automation: High temperature in {location}, activating cooling")
                    elif temp < 18:
                        # Too cold, turn on heating
                        command = {"temperature": 22, "mode": "heat"}
                        control_topic = f"controls/{location}/smart_thermostat"
                        self.client.publish(control_topic, json.dumps(command), QoSLevel.AT_LEAST_ONCE)
                        print(f"🤖 Automation: Low temperature in {location}, activating heating")
        
        self.rules = [motion_light_rule, temperature_thermostat_rule]
    
    def _check_automation_rules(self):
        """Check and execute automation rules"""
        for rule in self.rules:
            try:
                rule()
            except Exception as e:
                print(f"❌ Automation rule error: {e}")

def demonstrate_iot_simulation():
    """Demonstrate IoT device simulation"""
    print("=== IoT Smart Home Simulation ===")
    
    # Create and start MQTT broker
    broker = MQTTBroker()
    broker.start()
    
    devices = []
    actuators = []
    
    try:
        # Create IoT sensors
        sensors = [
            IoTDevice("temp_living", DeviceType.TEMPERATURE_SENSOR, "living_room", broker),
            IoTDevice("temp_bedroom", DeviceType.TEMPERATURE_SENSOR, "bedroom", broker),
            IoTDevice("humid_bathroom", DeviceType.HUMIDITY_SENSOR, "bathroom", broker),
            IoTDevice("motion_entry", DeviceType.MOTION_DETECTOR, "entry", broker),
            IoTDevice("motion_living", DeviceType.MOTION_DETECTOR, "living_room", broker),
            IoTDevice("door_front", DeviceType.DOOR_SENSOR, "entry", broker)
        ]
        
        # Create smart actuators
        smart_devices = [
            SmartActuator("light_living", DeviceType.SMART_LIGHT, "living_room", broker),
            SmartActuator("light_bedroom", DeviceType.SMART_LIGHT, "bedroom", broker),
            SmartActuator("thermostat_main", DeviceType.SMART_THERMOSTAT, "living_room", broker)
        ]
        
        # Start all devices
        for sensor in sensors:
            sensor.start()
            devices.append(sensor)
        
        for actuator in smart_devices:
            actuator.start()
            actuators.append(actuator)
        
        # Start home automation controller
        controller = HomeAutomationController(broker)
        controller.start()
        
        print(f"\n🏠 Smart home with {len(devices)} sensors and {len(actuators)} actuators")
        
        # Let the simulation run
        print(f"\n⏱️  Running simulation for 30 seconds...")
        time.sleep(30)
        
        # Manual control commands
        print(f"\n🎮 Sending manual control commands...")
        
        # Create a control client
        control_config = MQTTClientConfig(client_id="mobile_app_control")
        control_client = MQTTClient(control_config)
        control_client.connect(broker)
        
        # Turn on bedroom light
        light_command = {"power": True, "brightness": 60}
        control_client.publish("controls/bedroom/smart_light", json.dumps(light_command), QoSLevel.AT_LEAST_ONCE)
        
        # Set thermostat
        thermostat_command = {"temperature": 24, "mode": "auto"}
        control_client.publish("controls/living_room/smart_thermostat", json.dumps(thermostat_command), QoSLevel.AT_LEAST_ONCE)
        
        time.sleep(2)
        
        # Display broker statistics
        print(f"\n📊 MQTT Broker Statistics:")
        stats = broker.get_broker_stats()
        print(f"   Connected clients: {stats['connected_clients']}")
        print(f"   Active subscriptions: {stats['active_subscriptions']}")
        print(f"   Retained messages: {stats['retained_messages']}")
        print(f"   Messages published: {stats['messages_published']}")
        print(f"   Messages delivered: {stats['messages_delivered']}")
        
        control_client.disconnect()
        controller.stop()
    
    finally:
        # Stop all devices
        for device in devices:
            device.stop()
        
        for actuator in actuators:
            actuator.stop()
        
        broker.stop()
    
    print("\n🎯 IoT Simulation demonstrates:")
    print("💡 MQTT-based IoT device communication")
    print("💡 Sensor data publishing with retention")
    print("💡 Smart actuator control via MQTT commands")
    print("💡 Home automation rules and triggers")
    print("💡 Last Will and Testament for device failures")

if __name__ == "__main__":
    demonstrate_iot_simulation()
