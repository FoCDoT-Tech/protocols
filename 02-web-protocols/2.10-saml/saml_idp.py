#!/usr/bin/env python3
"""
SAML 2.0 Identity Provider (IdP) Simulation
Demonstrates SAML authentication, assertion generation, and SSO flows
"""

import time
import random
import json
import base64
import hashlib
import secrets
from datetime import datetime, timedelta
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as ET

class SAMLIdentityProvider:
    def __init__(self):
        self.entity_id = "https://idp.example.com"
        self.sso_endpoint = "https://idp.example.com/sso"
        self.slo_endpoint = "https://idp.example.com/slo"
        
        self.users = {
            'alice@example.com': {
                'password': 'password123',
                'name': 'Alice Johnson',
                'department': 'Engineering',
                'role': 'Senior Developer',
                'groups': ['developers', 'employees']
            },
            'bob@example.com': {
                'password': 'password456',
                'name': 'Bob Smith',
                'department': 'Sales',
                'role': 'Sales Manager',
                'groups': ['sales', 'managers', 'employees']
            }
        }
        
        self.service_providers = {
            'https://app1.example.com': {
                'name': 'Corporate App 1',
                'acs_url': 'https://app1.example.com/saml/acs',
                'certificate': 'sp1_cert_data'
            },
            'https://app2.example.com': {
                'name': 'Corporate App 2',
                'acs_url': 'https://app2.example.com/saml/acs',
                'certificate': 'sp2_cert_data'
            }
        }
        
        self.active_sessions = {}
        self.metrics = {
            'authentication_requests': 0,
            'assertions_issued': 0,
            'sso_sessions': 0,
            'logout_requests': 0
        }
    
    def demonstrate_saml_idp_flows(self):
        """Demonstrate SAML IdP flows and capabilities"""
        print(f"=== SAML 2.0 Identity Provider ===")
        print(f"Entity ID: {self.entity_id}")
        print(f"SSO Endpoint: {self.sso_endpoint}")
        print(f"SLO Endpoint: {self.slo_endpoint}")
        
        flows = [
            self.sp_initiated_sso,
            self.idp_initiated_sso,
            self.single_logout_flow,
            self.assertion_validation
        ]
        
        results = []
        for flow in flows:
            result = flow()
            results.append(result)
            time.sleep(0.3)
        
        return results
    
    def sp_initiated_sso(self):
        """Service Provider Initiated SSO Flow"""
        print(f"\n🔐 SP-Initiated SSO Flow")
        
        # Step 1: Receive AuthnRequest from SP
        authn_request = {
            'id': f"_req_{secrets.token_hex(16)}",
            'issuer': 'https://app1.example.com',
            'destination': self.sso_endpoint,
            'acs_url': 'https://app1.example.com/saml/acs',
            'name_id_format': 'urn:oasis:names:tc:SAML:2.0:nameid-format:persistent',
            'issue_instant': datetime.now().isoformat()
        }
        
        print(f"📨 Received AuthnRequest:")
        print(f"   Request ID: {authn_request['id']}")
        print(f"   Issuer: {authn_request['issuer']}")
        print(f"   ACS URL: {authn_request['acs_url']}")
        
        # Step 2: User Authentication
        print(f"\n👤 User Authentication:")
        username = 'alice@example.com'
        password = 'password123'
        
        if self.authenticate_user(username, password):
            print(f"✅ User authenticated: {username}")
            user_data = self.users[username]
            
            # Step 3: Generate SAML Assertion
            assertion = self.generate_saml_assertion(
                username,
                user_data,
                authn_request['issuer'],
                authn_request['id']
            )
            
            print(f"📤 SAML Assertion generated:")
            print(f"   Subject: {username}")
            print(f"   Audience: {authn_request['issuer']}")
            print(f"   Assertion ID: {assertion['id']}")
            
            # Step 4: Create SAML Response
            saml_response = self.create_saml_response(assertion, authn_request)
            
            print(f"📤 SAML Response created:")
            print(f"   Response ID: {saml_response['id']}")
            print(f"   Status: {saml_response['status']}")
            print(f"   Destination: {saml_response['destination']}")
            
            # Step 5: Create SSO Session
            session_id = self.create_sso_session(username, authn_request['issuer'])
            print(f"🔗 SSO Session created: {session_id}")
            
            self.metrics['authentication_requests'] += 1
            self.metrics['assertions_issued'] += 1
            self.metrics['sso_sessions'] += 1
            
            return {
                'flow': 'sp_initiated_sso',
                'status': 'success',
                'user': username,
                'assertion': assertion,
                'session_id': session_id
            }
        else:
            print(f"❌ Authentication failed")
            return {
                'flow': 'sp_initiated_sso',
                'status': 'failed',
                'error': 'authentication_failed'
            }
    
    def idp_initiated_sso(self):
        """Identity Provider Initiated SSO Flow"""
        print(f"\n🚀 IdP-Initiated SSO Flow")
        
        # User already authenticated at IdP
        username = 'bob@example.com'
        target_sp = 'https://app2.example.com'
        
        print(f"👤 User {username} accessing {target_sp}")
        print(f"🔐 User already authenticated at IdP")
        
        user_data = self.users[username]
        
        # Generate unsolicited assertion
        assertion = self.generate_saml_assertion(
            username,
            user_data,
            target_sp,
            None  # No InResponseTo for IdP-initiated
        )
        
        print(f"📤 Unsolicited SAML Assertion:")
        print(f"   Subject: {username}")
        print(f"   Audience: {target_sp}")
        print(f"   Assertion ID: {assertion['id']}")
        
        # Create SAML Response for IdP-initiated flow
        saml_response = {
            'id': f"_resp_{secrets.token_hex(16)}",
            'issue_instant': datetime.now().isoformat(),
            'destination': self.service_providers[target_sp]['acs_url'],
            'issuer': self.entity_id,
            'status': 'urn:oasis:names:tc:SAML:2.0:status:Success',
            'assertion': assertion
        }
        
        print(f"📤 IdP-Initiated SAML Response:")
        print(f"   Response ID: {saml_response['id']}")
        print(f"   Destination: {saml_response['destination']}")
        print(f"   No InResponseTo (unsolicited)")
        
        # Create SSO session
        session_id = self.create_sso_session(username, target_sp)
        print(f"🔗 SSO Session created: {session_id}")
        
        self.metrics['assertions_issued'] += 1
        self.metrics['sso_sessions'] += 1
        
        return {
            'flow': 'idp_initiated_sso',
            'status': 'success',
            'user': username,
            'target_sp': target_sp,
            'assertion': assertion,
            'session_id': session_id
        }
    
    def single_logout_flow(self):
        """Single Logout (SLO) Flow"""
        print(f"\n🚪 Single Logout (SLO) Flow")
        
        # Find active sessions
        if not self.active_sessions:
            print(f"❌ No active sessions to logout")
            return {'flow': 'single_logout', 'status': 'no_sessions'}
        
        # Select a session to logout
        session_id = list(self.active_sessions.keys())[0]
        session_data = self.active_sessions[session_id]
        
        print(f"🔍 Active session found:")
        print(f"   Session ID: {session_id}")
        print(f"   User: {session_data['user']}")
        print(f"   Service Providers: {len(session_data['service_providers'])}")
        
        # Generate LogoutRequest
        logout_request = {
            'id': f"_logout_{secrets.token_hex(16)}",
            'issue_instant': datetime.now().isoformat(),
            'issuer': self.entity_id,
            'name_id': session_data['user'],
            'session_index': session_id
        }
        
        print(f"📤 LogoutRequest generated:")
        print(f"   Request ID: {logout_request['id']}")
        print(f"   Name ID: {logout_request['name_id']}")
        print(f"   Session Index: {logout_request['session_index']}")
        
        # Send logout requests to all SPs
        logout_responses = []
        for sp_entity_id in session_data['service_providers']:
            print(f"📤 Sending LogoutRequest to {sp_entity_id}")
            
            # Simulate SP logout response
            logout_response = {
                'id': f"_logout_resp_{secrets.token_hex(8)}",
                'in_response_to': logout_request['id'],
                'issuer': sp_entity_id,
                'status': 'urn:oasis:names:tc:SAML:2.0:status:Success'
            }
            
            logout_responses.append(logout_response)
            print(f"📨 LogoutResponse from {sp_entity_id}: Success")
        
        # Terminate IdP session
        del self.active_sessions[session_id]
        print(f"🚪 IdP session terminated: {session_id}")
        
        self.metrics['logout_requests'] += 1
        
        return {
            'flow': 'single_logout',
            'status': 'success',
            'session_id': session_id,
            'logout_responses': logout_responses
        }
    
    def assertion_validation(self):
        """Demonstrate SAML assertion validation"""
        print(f"\n🔍 SAML Assertion Validation")
        
        # Create a sample assertion for validation
        username = 'alice@example.com'
        user_data = self.users[username]
        sp_entity_id = 'https://app1.example.com'
        
        assertion = self.generate_saml_assertion(username, user_data, sp_entity_id, None)
        
        print(f"📋 Validating SAML Assertion:")
        print(f"   Assertion ID: {assertion['id']}")
        print(f"   Subject: {assertion['subject']}")
        print(f"   Audience: {assertion['audience']}")
        
        # Validation checks
        validation_results = []
        
        # 1. Signature validation
        signature_valid = self.validate_assertion_signature(assertion)
        validation_results.append(('Signature', signature_valid))
        print(f"   ✅ Signature: {'Valid' if signature_valid else 'Invalid'}")
        
        # 2. Timestamp validation
        timestamp_valid = self.validate_assertion_timestamps(assertion)
        validation_results.append(('Timestamps', timestamp_valid))
        print(f"   ✅ Timestamps: {'Valid' if timestamp_valid else 'Invalid'}")
        
        # 3. Audience restriction
        audience_valid = self.validate_audience_restriction(assertion, sp_entity_id)
        validation_results.append(('Audience', audience_valid))
        print(f"   ✅ Audience: {'Valid' if audience_valid else 'Invalid'}")
        
        # 4. Replay protection
        replay_valid = self.validate_replay_protection(assertion)
        validation_results.append(('Replay Protection', replay_valid))
        print(f"   ✅ Replay Protection: {'Valid' if replay_valid else 'Invalid'}")
        
        overall_valid = all(result[1] for result in validation_results)
        print(f"📊 Overall Validation: {'✅ PASSED' if overall_valid else '❌ FAILED'}")
        
        return {
            'flow': 'assertion_validation',
            'assertion_id': assertion['id'],
            'validation_results': validation_results,
            'overall_valid': overall_valid
        }
    
    def authenticate_user(self, username, password):
        """Authenticate user credentials"""
        if username in self.users:
            return self.users[username]['password'] == password
        return False
    
    def generate_saml_assertion(self, username, user_data, audience, in_response_to):
        """Generate SAML assertion"""
        assertion_id = f"_assertion_{secrets.token_hex(16)}"
        issue_instant = datetime.now()
        not_before = issue_instant
        not_on_or_after = issue_instant + timedelta(hours=1)
        
        assertion = {
            'id': assertion_id,
            'version': '2.0',
            'issue_instant': issue_instant.isoformat(),
            'issuer': self.entity_id,
            'subject': username,
            'audience': audience,
            'in_response_to': in_response_to,
            'conditions': {
                'not_before': not_before.isoformat(),
                'not_on_or_after': not_on_or_after.isoformat(),
                'audience_restriction': [audience]
            },
            'authn_statement': {
                'authn_instant': issue_instant.isoformat(),
                'authn_context_class_ref': 'urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport'
            },
            'attribute_statement': {
                'attributes': [
                    {'name': 'Name', 'value': user_data['name']},
                    {'name': 'Department', 'value': user_data['department']},
                    {'name': 'Role', 'value': user_data['role']},
                    {'name': 'Groups', 'value': ','.join(user_data['groups'])}
                ]
            }
        }
        
        return assertion
    
    def create_saml_response(self, assertion, authn_request):
        """Create SAML Response"""
        response = {
            'id': f"_resp_{secrets.token_hex(16)}",
            'version': '2.0',
            'issue_instant': datetime.now().isoformat(),
            'destination': authn_request['acs_url'],
            'in_response_to': authn_request['id'],
            'issuer': self.entity_id,
            'status': 'urn:oasis:names:tc:SAML:2.0:status:Success',
            'assertion': assertion
        }
        
        return response
    
    def create_sso_session(self, username, sp_entity_id):
        """Create SSO session"""
        session_id = f"_session_{secrets.token_hex(16)}"
        
        self.active_sessions[session_id] = {
            'user': username,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'service_providers': [sp_entity_id]
        }
        
        return session_id
    
    def validate_assertion_signature(self, assertion):
        """Validate assertion digital signature"""
        # Simulate signature validation
        return True  # In real implementation, verify XML signature
    
    def validate_assertion_timestamps(self, assertion):
        """Validate assertion timestamps"""
        now = datetime.now()
        not_before = datetime.fromisoformat(assertion['conditions']['not_before'].replace('Z', '+00:00')).replace(tzinfo=None)
        not_on_or_after = datetime.fromisoformat(assertion['conditions']['not_on_or_after'].replace('Z', '+00:00')).replace(tzinfo=None)
        
        return not_before <= now <= not_on_or_after
    
    def validate_audience_restriction(self, assertion, expected_audience):
        """Validate audience restriction"""
        audience_restrictions = assertion['conditions']['audience_restriction']
        return expected_audience in audience_restrictions
    
    def validate_replay_protection(self, assertion):
        """Validate replay protection"""
        # In real implementation, check assertion ID against cache
        return True
    
    def generate_metadata(self):
        """Generate IdP metadata"""
        print(f"\n📋 SAML IdP Metadata Generation")
        
        metadata = {
            'entity_id': self.entity_id,
            'idp_sso_descriptor': {
                'want_authn_requests_signed': True,
                'single_sign_on_service': [
                    {
                        'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
                        'location': self.sso_endpoint
                    },
                    {
                        'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
                        'location': self.sso_endpoint
                    }
                ],
                'single_logout_service': [
                    {
                        'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
                        'location': self.slo_endpoint
                    }
                ],
                'name_id_formats': [
                    'urn:oasis:names:tc:SAML:2.0:nameid-format:persistent',
                    'urn:oasis:names:tc:SAML:2.0:nameid-format:transient'
                ]
            }
        }
        
        print(f"📤 IdP Metadata:")
        print(f"   Entity ID: {metadata['entity_id']}")
        print(f"   SSO Bindings: {len(metadata['idp_sso_descriptor']['single_sign_on_service'])}")
        print(f"   SLO Bindings: {len(metadata['idp_sso_descriptor']['single_logout_service'])}")
        print(f"   NameID Formats: {len(metadata['idp_sso_descriptor']['name_id_formats'])}")
        
        return metadata
    
    def get_idp_metrics(self):
        """Get IdP metrics"""
        active_sessions_count = len(self.active_sessions)
        registered_sps = len(self.service_providers)
        
        return {
            'authentication_requests': self.metrics['authentication_requests'],
            'assertions_issued': self.metrics['assertions_issued'],
            'sso_sessions': self.metrics['sso_sessions'],
            'logout_requests': self.metrics['logout_requests'],
            'active_sessions': active_sessions_count,
            'registered_service_providers': registered_sps,
            'registered_users': len(self.users)
        }

if __name__ == "__main__":
    # Create SAML IdP
    saml_idp = SAMLIdentityProvider()
    
    # Demonstrate SAML IdP flows
    flow_results = saml_idp.demonstrate_saml_idp_flows()
    
    # Generate metadata
    metadata = saml_idp.generate_metadata()
    
    # Get metrics
    metrics = saml_idp.get_idp_metrics()
    
    print(f"\n=== SAML IdP Summary ===")
    print(f"Authentication requests: {metrics['authentication_requests']}")
    print(f"Assertions issued: {metrics['assertions_issued']}")
    print(f"SSO sessions: {metrics['sso_sessions']}")
    print(f"Active sessions: {metrics['active_sessions']}")
    print(f"Registered SPs: {metrics['registered_service_providers']}")
    print(f"Registered users: {metrics['registered_users']}")
    print(f"SAML 2.0 enables secure, federated identity management with enterprise-grade SSO")
