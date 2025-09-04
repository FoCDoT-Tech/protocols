#!/usr/bin/env python3
"""
SAML 2.0 Service Provider (SP) Simulation
Demonstrates SAML service provider flows, assertion consumption, and SSO integration
"""

import time
import random
import json
import base64
import hashlib
import secrets
from datetime import datetime, timedelta
import urllib.parse

class SAMLServiceProvider:
    def __init__(self, entity_id, idp_entity_id):
        self.entity_id = entity_id
        self.idp_entity_id = idp_entity_id
        self.acs_url = f"{entity_id}/saml/acs"
        self.sls_url = f"{entity_id}/saml/sls"
        
        self.idp_sso_url = "https://idp.example.com/sso"
        self.idp_slo_url = "https://idp.example.com/slo"
        
        self.user_sessions = {}
        self.pending_requests = {}
        
        self.metrics = {
            'authn_requests_sent': 0,
            'assertions_received': 0,
            'sso_logins': 0,
            'logout_requests': 0
        }
    
    def demonstrate_saml_sp_flows(self):
        """Demonstrate SAML SP flows and capabilities"""
        print(f"=== SAML 2.0 Service Provider ===")
        print(f"Entity ID: {self.entity_id}")
        print(f"ACS URL: {self.acs_url}")
        print(f"IdP Entity ID: {self.idp_entity_id}")
        
        flows = [
            self.initiate_sso_flow,
            self.process_saml_response,
            self.handle_logout_request,
            self.assertion_consumption
        ]
        
        results = []
        for flow in flows:
            result = flow()
            results.append(result)
            time.sleep(0.3)
        
        return results
    
    def initiate_sso_flow(self):
        """Initiate SP-initiated SSO flow"""
        print(f"\n🚀 SP-Initiated SSO Flow")
        
        # User tries to access protected resource
        protected_resource = "/dashboard"
        user_ip = "192.168.1.100"
        
        print(f"👤 User accessing protected resource: {protected_resource}")
        print(f"🔒 Authentication required - redirecting to IdP")
        
        # Generate AuthnRequest
        authn_request = self.generate_authn_request()
        
        print(f"📤 AuthnRequest generated:")
        print(f"   Request ID: {authn_request['id']}")
        print(f"   Destination: {authn_request['destination']}")
        print(f"   ACS URL: {authn_request['assertion_consumer_service_url']}")
        print(f"   NameID Format: {authn_request['name_id_policy']['format']}")
        
        # Store pending request
        self.pending_requests[authn_request['id']] = {
            'request': authn_request,
            'original_url': protected_resource,
            'user_ip': user_ip,
            'timestamp': datetime.now()
        }
        
        # Create redirect URL
        redirect_url = self.create_sso_redirect_url(authn_request)
        
        print(f"🔄 Redirecting user to IdP:")
        print(f"   URL: {redirect_url[:80]}...")
        print(f"   Method: HTTP Redirect (GET)")
        
        self.metrics['authn_requests_sent'] += 1
        
        return {
            'flow': 'initiate_sso',
            'status': 'success',
            'authn_request': authn_request,
            'redirect_url': redirect_url
        }
    
    def process_saml_response(self):
        """Process SAML Response from IdP"""
        print(f"\n📨 Processing SAML Response")
        
        # Simulate receiving SAML Response
        saml_response = self.simulate_saml_response()
        
        print(f"📨 SAML Response received:")
        print(f"   Response ID: {saml_response['id']}")
        print(f"   InResponseTo: {saml_response['in_response_to']}")
        print(f"   Status: {saml_response['status']}")
        print(f"   Issuer: {saml_response['issuer']}")
        
        # Validate SAML Response
        validation_result = self.validate_saml_response(saml_response)
        
        if validation_result['valid']:
            print(f"✅ SAML Response validation successful")
            
            # Extract assertion
            assertion = saml_response['assertion']
            print(f"📋 Processing assertion:")
            print(f"   Assertion ID: {assertion['id']}")
            print(f"   Subject: {assertion['subject']}")
            print(f"   Audience: {assertion['audience']}")
            
            # Create user session
            session_result = self.create_user_session(assertion)
            
            print(f"🔗 User session created:")
            print(f"   Session ID: {session_result['session_id']}")
            print(f"   User: {session_result['user']}")
            print(f"   Attributes: {len(session_result['attributes'])} attributes")
            
            # Redirect to original resource
            original_request = self.pending_requests.get(saml_response['in_response_to'])
            if original_request:
                original_url = original_request['original_url']
                print(f"🔄 Redirecting to original resource: {original_url}")
                del self.pending_requests[saml_response['in_response_to']]
            
            self.metrics['assertions_received'] += 1
            self.metrics['sso_logins'] += 1
            
            return {
                'flow': 'process_saml_response',
                'status': 'success',
                'session': session_result,
                'original_url': original_url if original_request else None
            }
        else:
            print(f"❌ SAML Response validation failed:")
            for error in validation_result['errors']:
                print(f"   • {error}")
            
            return {
                'flow': 'process_saml_response',
                'status': 'failed',
                'errors': validation_result['errors']
            }
    
    def handle_logout_request(self):
        """Handle logout request from IdP"""
        print(f"\n🚪 Handling Logout Request")
        
        # Simulate receiving LogoutRequest
        logout_request = {
            'id': f"_logout_{secrets.token_hex(16)}",
            'issue_instant': datetime.now().isoformat(),
            'destination': self.sls_url,
            'issuer': self.idp_entity_id,
            'name_id': 'alice@example.com',
            'session_index': list(self.user_sessions.keys())[0] if self.user_sessions else 'session_123'
        }
        
        print(f"📨 LogoutRequest received:")
        print(f"   Request ID: {logout_request['id']}")
        print(f"   Issuer: {logout_request['issuer']}")
        print(f"   Name ID: {logout_request['name_id']}")
        print(f"   Session Index: {logout_request['session_index']}")
        
        # Find and terminate user session
        session_terminated = False
        for session_id, session_data in list(self.user_sessions.items()):
            if session_data['user'] == logout_request['name_id']:
                print(f"🔍 Found user session: {session_id}")
                del self.user_sessions[session_id]
                session_terminated = True
                print(f"🚪 Session terminated: {session_id}")
                break
        
        if not session_terminated:
            print(f"⚠️ No active session found for user")
        
        # Generate LogoutResponse
        logout_response = {
            'id': f"_logout_resp_{secrets.token_hex(16)}",
            'issue_instant': datetime.now().isoformat(),
            'destination': self.idp_slo_url,
            'in_response_to': logout_request['id'],
            'issuer': self.entity_id,
            'status': 'urn:oasis:names:tc:SAML:2.0:status:Success'
        }
        
        print(f"📤 LogoutResponse sent:")
        print(f"   Response ID: {logout_response['id']}")
        print(f"   InResponseTo: {logout_response['in_response_to']}")
        print(f"   Status: Success")
        
        self.metrics['logout_requests'] += 1
        
        return {
            'flow': 'handle_logout',
            'status': 'success',
            'session_terminated': session_terminated,
            'logout_response': logout_response
        }
    
    def assertion_consumption(self):
        """Demonstrate assertion consumption and attribute extraction"""
        print(f"\n🔍 SAML Assertion Consumption")
        
        # Create sample assertion for demonstration
        sample_assertion = {
            'id': f"_assertion_{secrets.token_hex(16)}",
            'version': '2.0',
            'issue_instant': datetime.now().isoformat(),
            'issuer': self.idp_entity_id,
            'subject': 'bob@example.com',
            'audience': self.entity_id,
            'conditions': {
                'not_before': datetime.now().isoformat(),
                'not_on_or_after': (datetime.now() + timedelta(hours=1)).isoformat(),
                'audience_restriction': [self.entity_id]
            },
            'authn_statement': {
                'authn_instant': datetime.now().isoformat(),
                'authn_context_class_ref': 'urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport'
            },
            'attribute_statement': {
                'attributes': [
                    {'name': 'Name', 'value': 'Bob Smith'},
                    {'name': 'Email', 'value': 'bob@example.com'},
                    {'name': 'Department', 'value': 'Sales'},
                    {'name': 'Role', 'value': 'Sales Manager'},
                    {'name': 'Groups', 'value': 'sales,managers,employees'},
                    {'name': 'EmployeeID', 'value': 'EMP001234'}
                ]
            }
        }
        
        print(f"📋 Consuming SAML Assertion:")
        print(f"   Assertion ID: {sample_assertion['id']}")
        print(f"   Subject: {sample_assertion['subject']}")
        print(f"   Issuer: {sample_assertion['issuer']}")
        
        # Extract user attributes
        attributes = self.extract_user_attributes(sample_assertion)
        
        print(f"👤 Extracted User Attributes:")
        for attr_name, attr_value in attributes.items():
            print(f"   {attr_name}: {attr_value}")
        
        # Apply attribute mapping
        mapped_attributes = self.apply_attribute_mapping(attributes)
        
        print(f"🔄 Mapped Attributes (for application):")
        for attr_name, attr_value in mapped_attributes.items():
            print(f"   {attr_name}: {attr_value}")
        
        # Determine user permissions
        permissions = self.determine_user_permissions(mapped_attributes)
        
        print(f"🔐 Determined Permissions:")
        for permission in permissions:
            print(f"   • {permission}")
        
        return {
            'flow': 'assertion_consumption',
            'status': 'success',
            'attributes': attributes,
            'mapped_attributes': mapped_attributes,
            'permissions': permissions
        }
    
    def generate_authn_request(self):
        """Generate SAML AuthnRequest"""
        request_id = f"_req_{secrets.token_hex(16)}"
        
        authn_request = {
            'id': request_id,
            'version': '2.0',
            'issue_instant': datetime.now().isoformat(),
            'destination': self.idp_sso_url,
            'assertion_consumer_service_url': self.acs_url,
            'issuer': self.entity_id,
            'name_id_policy': {
                'format': 'urn:oasis:names:tc:SAML:2.0:nameid-format:persistent',
                'allow_create': True
            },
            'requested_authn_context': {
                'comparison': 'minimum',
                'authn_context_class_ref': 'urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport'
            }
        }
        
        return authn_request
    
    def create_sso_redirect_url(self, authn_request):
        """Create SSO redirect URL"""
        # In real implementation, this would be base64-encoded XML
        saml_request = base64.b64encode(json.dumps(authn_request).encode()).decode()
        
        params = {
            'SAMLRequest': saml_request,
            'RelayState': '/dashboard'  # Original resource
        }
        
        redirect_url = f"{self.idp_sso_url}?{urllib.parse.urlencode(params)}"
        return redirect_url
    
    def simulate_saml_response(self):
        """Simulate SAML Response from IdP"""
        # Find a pending request to respond to
        if self.pending_requests:
            request_id = list(self.pending_requests.keys())[0]
        else:
            request_id = f"_req_{secrets.token_hex(16)}"
        
        saml_response = {
            'id': f"_resp_{secrets.token_hex(16)}",
            'version': '2.0',
            'issue_instant': datetime.now().isoformat(),
            'destination': self.acs_url,
            'in_response_to': request_id,
            'issuer': self.idp_entity_id,
            'status': 'urn:oasis:names:tc:SAML:2.0:status:Success',
            'assertion': {
                'id': f"_assertion_{secrets.token_hex(16)}",
                'version': '2.0',
                'issue_instant': datetime.now().isoformat(),
                'issuer': self.idp_entity_id,
                'subject': 'alice@example.com',
                'audience': self.entity_id,
                'conditions': {
                    'not_before': datetime.now().isoformat(),
                    'not_on_or_after': (datetime.now() + timedelta(hours=1)).isoformat(),
                    'audience_restriction': [self.entity_id]
                },
                'authn_statement': {
                    'authn_instant': datetime.now().isoformat(),
                    'authn_context_class_ref': 'urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport'
                },
                'attribute_statement': {
                    'attributes': [
                        {'name': 'Name', 'value': 'Alice Johnson'},
                        {'name': 'Email', 'value': 'alice@example.com'},
                        {'name': 'Department', 'value': 'Engineering'},
                        {'name': 'Role', 'value': 'Senior Developer'}
                    ]
                }
            }
        }
        
        return saml_response
    
    def validate_saml_response(self, saml_response):
        """Validate SAML Response"""
        errors = []
        
        # Check issuer
        if saml_response['issuer'] != self.idp_entity_id:
            errors.append(f"Invalid issuer: {saml_response['issuer']}")
        
        # Check destination
        if saml_response['destination'] != self.acs_url:
            errors.append(f"Invalid destination: {saml_response['destination']}")
        
        # Check status
        if saml_response['status'] != 'urn:oasis:names:tc:SAML:2.0:status:Success':
            errors.append(f"Non-success status: {saml_response['status']}")
        
        # Validate assertion
        assertion = saml_response['assertion']
        
        # Check audience restriction
        if self.entity_id not in assertion['conditions']['audience_restriction']:
            errors.append(f"Invalid audience restriction")
        
        # Check timestamps
        now = datetime.now()
        not_before = datetime.fromisoformat(assertion['conditions']['not_before'].replace('Z', '+00:00')).replace(tzinfo=None)
        not_on_or_after = datetime.fromisoformat(assertion['conditions']['not_on_or_after'].replace('Z', '+00:00')).replace(tzinfo=None)
        
        if not (not_before <= now <= not_on_or_after):
            errors.append(f"Assertion timestamp validation failed")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def create_user_session(self, assertion):
        """Create user session from assertion"""
        session_id = f"_session_{secrets.token_hex(16)}"
        
        # Extract attributes
        attributes = self.extract_user_attributes(assertion)
        
        session_data = {
            'user': assertion['subject'],
            'assertion_id': assertion['id'],
            'created_at': datetime.now(),
            'expires_at': datetime.fromisoformat(assertion['conditions']['not_on_or_after'].replace('Z', '+00:00')).replace(tzinfo=None),
            'attributes': attributes,
            'idp_entity_id': assertion['issuer']
        }
        
        self.user_sessions[session_id] = session_data
        
        return {
            'session_id': session_id,
            'user': assertion['subject'],
            'attributes': attributes
        }
    
    def extract_user_attributes(self, assertion):
        """Extract user attributes from assertion"""
        attributes = {}
        
        if 'attribute_statement' in assertion:
            for attr in assertion['attribute_statement']['attributes']:
                attributes[attr['name']] = attr['value']
        
        return attributes
    
    def apply_attribute_mapping(self, attributes):
        """Apply attribute mapping for application"""
        # Map SAML attributes to application attributes
        mapping = {
            'Name': 'display_name',
            'Email': 'email',
            'Department': 'department',
            'Role': 'job_title',
            'Groups': 'groups',
            'EmployeeID': 'employee_id'
        }
        
        mapped_attributes = {}
        for saml_attr, app_attr in mapping.items():
            if saml_attr in attributes:
                mapped_attributes[app_attr] = attributes[saml_attr]
        
        return mapped_attributes
    
    def determine_user_permissions(self, attributes):
        """Determine user permissions based on attributes"""
        permissions = ['read']  # Default permission
        
        # Role-based permissions
        role = attributes.get('job_title', '').lower()
        if 'manager' in role:
            permissions.extend(['write', 'approve'])
        elif 'developer' in role:
            permissions.extend(['write', 'deploy'])
        elif 'admin' in role:
            permissions.extend(['write', 'admin', 'delete'])
        
        # Group-based permissions
        groups = attributes.get('groups', '').lower().split(',')
        if 'administrators' in groups:
            permissions.append('admin')
        if 'developers' in groups:
            permissions.append('debug')
        
        return list(set(permissions))  # Remove duplicates
    
    def get_sp_metrics(self):
        """Get SP metrics"""
        active_sessions = len(self.user_sessions)
        pending_requests = len(self.pending_requests)
        
        return {
            'authn_requests_sent': self.metrics['authn_requests_sent'],
            'assertions_received': self.metrics['assertions_received'],
            'sso_logins': self.metrics['sso_logins'],
            'logout_requests': self.metrics['logout_requests'],
            'active_sessions': active_sessions,
            'pending_requests': pending_requests
        }

if __name__ == "__main__":
    # Create SAML SP
    saml_sp = SAMLServiceProvider(
        entity_id='https://app1.example.com',
        idp_entity_id='https://idp.example.com'
    )
    
    # Demonstrate SAML SP flows
    flow_results = saml_sp.demonstrate_saml_sp_flows()
    
    # Get metrics
    metrics = saml_sp.get_sp_metrics()
    
    print(f"\n=== SAML SP Summary ===")
    print(f"Entity ID: {saml_sp.entity_id}")
    print(f"AuthnRequests sent: {metrics['authn_requests_sent']}")
    print(f"Assertions received: {metrics['assertions_received']}")
    print(f"SSO logins: {metrics['sso_logins']}")
    print(f"Active sessions: {metrics['active_sessions']}")
    print(f"Pending requests: {metrics['pending_requests']}")
    print(f"SAML 2.0 SP enables secure SSO integration with enterprise identity providers")
