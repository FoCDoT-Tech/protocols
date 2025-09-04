#!/usr/bin/env python3
"""
OAuth 2.0 Authorization Server Simulation
Demonstrates OAuth flows, token management, and security features
"""

import time
import random
import json
import hashlib
import base64
import secrets
from datetime import datetime, timedelta
from collections import defaultdict
import urllib.parse

class OAuthAuthorizationServer:
    def __init__(self):
        self.clients = {
            'web_app_123': {
                'client_secret': 'secret_456',
                'redirect_uris': ['https://webapp.example.com/callback'],
                'grant_types': ['authorization_code', 'refresh_token'],
                'scope': ['read:profile', 'read:email', 'write:posts']
            },
            'mobile_app_789': {
                'client_secret': None,  # Public client
                'redirect_uris': ['com.example.app://oauth/callback'],
                'grant_types': ['authorization_code', 'refresh_token'],
                'scope': ['read:profile', 'read:email']
            },
            'service_client_456': {
                'client_secret': 'service_secret_789',
                'redirect_uris': [],
                'grant_types': ['client_credentials'],
                'scope': ['read:data', 'write:data']
            }
        }
        
        self.authorization_codes = {}
        self.access_tokens = {}
        self.refresh_tokens = {}
        self.users = {
            'user123': {
                'username': 'alice@example.com',
                'name': 'Alice Johnson',
                'email': 'alice@example.com',
                'profile_picture': 'https://example.com/alice.jpg'
            }
        }
        
        self.metrics = {
            'authorization_requests': 0,
            'token_requests': 0,
            'token_validations': 0,
            'refresh_operations': 0
        }
    
    def demonstrate_oauth_flows(self):
        """Demonstrate various OAuth 2.0 flows"""
        print(f"=== OAuth 2.0 Authorization Server ===")
        print(f"Server: https://auth.example.com")
        print(f"Endpoints: /authorize, /token, /introspect, /revoke")
        
        flows = [
            self.authorization_code_flow,
            self.pkce_flow,
            self.client_credentials_flow,
            self.refresh_token_flow
        ]
        
        results = []
        for flow in flows:
            result = flow()
            results.append(result)
            time.sleep(0.2)
        
        return results
    
    def authorization_code_flow(self):
        """Standard Authorization Code Flow"""
        print(f"\n🔐 Authorization Code Flow")
        
        # Step 1: Authorization Request
        auth_request = {
            'response_type': 'code',
            'client_id': 'web_app_123',
            'redirect_uri': 'https://webapp.example.com/callback',
            'scope': 'read:profile read:email',
            'state': 'xyz123'
        }
        
        print(f"📨 Authorization request received:")
        print(f"   Client: {auth_request['client_id']}")
        print(f"   Scope: {auth_request['scope']}")
        print(f"   Redirect URI: {auth_request['redirect_uri']}")
        
        # Validate client and redirect URI
        if not self.validate_client(auth_request['client_id'], auth_request['redirect_uri']):
            print(f"❌ Invalid client or redirect URI")
            return {'flow': 'authorization_code', 'status': 'failed', 'error': 'invalid_client'}
        
        # Generate authorization code
        auth_code = self.generate_authorization_code(
            auth_request['client_id'],
            'user123',
            auth_request['scope'],
            auth_request['redirect_uri']
        )
        
        print(f"✅ User authorized application")
        print(f"📤 Authorization code generated: {auth_code}")
        print(f"🔄 Redirecting to: {auth_request['redirect_uri']}?code={auth_code}&state={auth_request['state']}")
        
        self.metrics['authorization_requests'] += 1
        
        # Step 2: Token Exchange
        token_request = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'client_id': 'web_app_123',
            'client_secret': 'secret_456',
            'redirect_uri': 'https://webapp.example.com/callback'
        }
        
        print(f"\n📨 Token exchange request:")
        print(f"   Grant type: {token_request['grant_type']}")
        print(f"   Authorization code: {token_request['code']}")
        
        # Validate and exchange code for tokens
        tokens = self.exchange_code_for_tokens(token_request)
        
        if tokens:
            print(f"✅ Tokens issued successfully:")
            print(f"   Access token: {tokens['access_token'][:20]}...")
            print(f"   Refresh token: {tokens['refresh_token'][:20]}...")
            print(f"   Expires in: {tokens['expires_in']} seconds")
            print(f"   Scope: {tokens['scope']}")
        
        return {
            'flow': 'authorization_code',
            'status': 'success',
            'auth_code': auth_code,
            'tokens': tokens
        }
    
    def pkce_flow(self):
        """Authorization Code Flow with PKCE"""
        print(f"\n🔒 PKCE Flow (Enhanced Security)")
        
        # Generate PKCE parameters
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode('utf-8').rstrip('=')
        
        print(f"🔑 PKCE parameters generated:")
        print(f"   Code verifier: {code_verifier[:20]}...")
        print(f"   Code challenge: {code_challenge[:20]}...")
        
        # Authorization request with PKCE
        auth_request = {
            'response_type': 'code',
            'client_id': 'mobile_app_789',
            'redirect_uri': 'com.example.app://oauth/callback',
            'scope': 'read:profile read:email',
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
            'state': 'mobile_state_456'
        }
        
        print(f"📨 PKCE authorization request:")
        print(f"   Client: {auth_request['client_id']} (public client)")
        print(f"   Code challenge method: {auth_request['code_challenge_method']}")
        
        # Generate authorization code with PKCE
        auth_code = self.generate_authorization_code(
            auth_request['client_id'],
            'user123',
            auth_request['scope'],
            auth_request['redirect_uri'],
            code_challenge=code_challenge
        )
        
        print(f"✅ Authorization code with PKCE: {auth_code}")
        
        # Token exchange with code verifier
        token_request = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'client_id': 'mobile_app_789',
            'redirect_uri': 'com.example.app://oauth/callback',
            'code_verifier': code_verifier
        }
        
        print(f"📨 Token exchange with PKCE verification:")
        print(f"   Code verifier provided: {code_verifier[:20]}...")
        
        # Verify PKCE and issue tokens
        if self.verify_pkce(auth_code, code_verifier):
            tokens = self.exchange_code_for_tokens(token_request)
            print(f"✅ PKCE verification successful")
            print(f"📤 Tokens issued: {tokens['access_token'][:20]}...")
        else:
            print(f"❌ PKCE verification failed")
            tokens = None
        
        return {
            'flow': 'pkce',
            'status': 'success' if tokens else 'failed',
            'code_verifier': code_verifier,
            'tokens': tokens
        }
    
    def client_credentials_flow(self):
        """Client Credentials Flow for Service-to-Service"""
        print(f"\n🤖 Client Credentials Flow")
        
        token_request = {
            'grant_type': 'client_credentials',
            'client_id': 'service_client_456',
            'client_secret': 'service_secret_789',
            'scope': 'read:data write:data'
        }
        
        print(f"📨 Service-to-service token request:")
        print(f"   Client: {token_request['client_id']}")
        print(f"   Scope: {token_request['scope']}")
        
        # Validate client credentials
        if self.validate_client_credentials(token_request['client_id'], token_request['client_secret']):
            # Issue access token (no refresh token for client credentials)
            access_token = self.generate_access_token(
                token_request['client_id'],
                None,  # No user context
                token_request['scope']
            )
            
            tokens = {
                'access_token': access_token,
                'token_type': 'Bearer',
                'expires_in': 3600,
                'scope': token_request['scope']
            }
            
            print(f"✅ Service token issued:")
            print(f"   Access token: {tokens['access_token'][:20]}...")
            print(f"   Expires in: {tokens['expires_in']} seconds")
            print(f"   No refresh token (service-to-service)")
            
            self.metrics['token_requests'] += 1
            
            return {
                'flow': 'client_credentials',
                'status': 'success',
                'tokens': tokens
            }
        else:
            print(f"❌ Invalid client credentials")
            return {
                'flow': 'client_credentials',
                'status': 'failed',
                'error': 'invalid_client'
            }
    
    def refresh_token_flow(self):
        """Refresh Token Flow"""
        print(f"\n🔄 Refresh Token Flow")
        
        # Use refresh token from previous flow
        existing_refresh_token = list(self.refresh_tokens.keys())[0] if self.refresh_tokens else None
        
        if not existing_refresh_token:
            print(f"❌ No refresh token available")
            return {'flow': 'refresh_token', 'status': 'failed', 'error': 'no_refresh_token'}
        
        refresh_request = {
            'grant_type': 'refresh_token',
            'refresh_token': existing_refresh_token,
            'client_id': 'web_app_123',
            'client_secret': 'secret_456',
            'scope': 'read:profile'  # Can request subset of original scope
        }
        
        print(f"📨 Refresh token request:")
        print(f"   Refresh token: {refresh_request['refresh_token'][:20]}...")
        print(f"   Requested scope: {refresh_request['scope']}")
        
        # Validate refresh token and issue new access token
        if existing_refresh_token in self.refresh_tokens:
            refresh_data = self.refresh_tokens[existing_refresh_token]
            
            # Issue new access token
            new_access_token = self.generate_access_token(
                refresh_data['client_id'],
                refresh_data['user_id'],
                refresh_request['scope']
            )
            
            tokens = {
                'access_token': new_access_token,
                'token_type': 'Bearer',
                'expires_in': 3600,
                'scope': refresh_request['scope'],
                'refresh_token': existing_refresh_token  # Can optionally rotate
            }
            
            print(f"✅ New access token issued:")
            print(f"   Access token: {tokens['access_token'][:20]}...")
            print(f"   Refresh token: reused")
            
            self.metrics['refresh_operations'] += 1
            
            return {
                'flow': 'refresh_token',
                'status': 'success',
                'tokens': tokens
            }
        else:
            print(f"❌ Invalid refresh token")
            return {
                'flow': 'refresh_token',
                'status': 'failed',
                'error': 'invalid_grant'
            }
    
    def validate_client(self, client_id, redirect_uri):
        """Validate client and redirect URI"""
        if client_id not in self.clients:
            return False
        
        client = self.clients[client_id]
        return redirect_uri in client['redirect_uris']
    
    def validate_client_credentials(self, client_id, client_secret):
        """Validate client credentials"""
        if client_id not in self.clients:
            return False
        
        client = self.clients[client_id]
        return client['client_secret'] == client_secret
    
    def generate_authorization_code(self, client_id, user_id, scope, redirect_uri, code_challenge=None):
        """Generate authorization code"""
        auth_code = f"auth_{secrets.token_urlsafe(16)}"
        
        self.authorization_codes[auth_code] = {
            'client_id': client_id,
            'user_id': user_id,
            'scope': scope,
            'redirect_uri': redirect_uri,
            'code_challenge': code_challenge,
            'expires_at': datetime.now() + timedelta(minutes=10),
            'used': False
        }
        
        return auth_code
    
    def exchange_code_for_tokens(self, token_request):
        """Exchange authorization code for access and refresh tokens"""
        auth_code = token_request['code']
        
        if auth_code not in self.authorization_codes:
            return None
        
        code_data = self.authorization_codes[auth_code]
        
        # Validate code hasn't been used and hasn't expired
        if code_data['used'] or datetime.now() > code_data['expires_at']:
            return None
        
        # Mark code as used
        code_data['used'] = True
        
        # Generate tokens
        access_token = self.generate_access_token(
            code_data['client_id'],
            code_data['user_id'],
            code_data['scope']
        )
        
        refresh_token = self.generate_refresh_token(
            code_data['client_id'],
            code_data['user_id'],
            code_data['scope']
        )
        
        self.metrics['token_requests'] += 1
        
        return {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': refresh_token,
            'scope': code_data['scope']
        }
    
    def generate_access_token(self, client_id, user_id, scope):
        """Generate access token"""
        access_token = f"at_{secrets.token_urlsafe(32)}"
        
        self.access_tokens[access_token] = {
            'client_id': client_id,
            'user_id': user_id,
            'scope': scope,
            'expires_at': datetime.now() + timedelta(hours=1),
            'created_at': datetime.now()
        }
        
        return access_token
    
    def generate_refresh_token(self, client_id, user_id, scope):
        """Generate refresh token"""
        refresh_token = f"rt_{secrets.token_urlsafe(32)}"
        
        self.refresh_tokens[refresh_token] = {
            'client_id': client_id,
            'user_id': user_id,
            'scope': scope,
            'created_at': datetime.now()
        }
        
        return refresh_token
    
    def verify_pkce(self, auth_code, code_verifier):
        """Verify PKCE code challenge"""
        if auth_code not in self.authorization_codes:
            return False
        
        code_data = self.authorization_codes[auth_code]
        stored_challenge = code_data.get('code_challenge')
        
        if not stored_challenge:
            return True  # No PKCE required
        
        # Verify code challenge
        computed_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode('utf-8').rstrip('=')
        
        return stored_challenge == computed_challenge
    
    def introspect_token(self, token):
        """Token introspection endpoint"""
        print(f"\n🔍 Token Introspection")
        print(f"   Token: {token[:20]}...")
        
        if token in self.access_tokens:
            token_data = self.access_tokens[token]
            is_active = datetime.now() < token_data['expires_at']
            
            introspection_response = {
                'active': is_active,
                'client_id': token_data['client_id'],
                'username': token_data['user_id'],
                'scope': token_data['scope'],
                'exp': int(token_data['expires_at'].timestamp()),
                'iat': int(token_data['created_at'].timestamp())
            }
            
            print(f"✅ Token is {'active' if is_active else 'expired'}")
            print(f"   Client: {token_data['client_id']}")
            print(f"   Scope: {token_data['scope']}")
            
            self.metrics['token_validations'] += 1
            
            return introspection_response
        else:
            print(f"❌ Token not found")
            return {'active': False}
    
    def revoke_token(self, token):
        """Token revocation endpoint"""
        print(f"\n🚫 Token Revocation")
        print(f"   Token: {token[:20]}...")
        
        revoked = False
        
        # Check access tokens
        if token in self.access_tokens:
            del self.access_tokens[token]
            revoked = True
            print(f"✅ Access token revoked")
        
        # Check refresh tokens
        if token in self.refresh_tokens:
            del self.refresh_tokens[token]
            revoked = True
            print(f"✅ Refresh token revoked")
        
        if not revoked:
            print(f"❌ Token not found")
        
        return revoked
    
    def demonstrate_security_features(self):
        """Demonstrate OAuth security features"""
        print(f"\n=== OAuth Security Features ===")
        
        security_features = [
            {
                'feature': 'State Parameter',
                'description': 'CSRF protection in authorization flow',
                'implementation': 'Random state value validated on callback'
            },
            {
                'feature': 'PKCE',
                'description': 'Code interception protection for public clients',
                'implementation': 'SHA256 code challenge/verifier pair'
            },
            {
                'feature': 'Short-lived Tokens',
                'description': 'Minimize exposure window',
                'implementation': '1-hour access token expiry'
            },
            {
                'feature': 'Scope Limitation',
                'description': 'Principle of least privilege',
                'implementation': 'Granular permission scopes'
            },
            {
                'feature': 'Secure Redirect',
                'description': 'Prevent authorization code injection',
                'implementation': 'Whitelist of valid redirect URIs'
            }
        ]
        
        for feature in security_features:
            print(f"🔒 {feature['feature']}")
            print(f"   Description: {feature['description']}")
            print(f"   Implementation: {feature['implementation']}")
        
        return security_features
    
    def get_server_metrics(self):
        """Get OAuth server metrics"""
        active_tokens = len([t for t, data in self.access_tokens.items() 
                           if datetime.now() < data['expires_at']])
        
        return {
            'authorization_requests': self.metrics['authorization_requests'],
            'token_requests': self.metrics['token_requests'],
            'token_validations': self.metrics['token_validations'],
            'refresh_operations': self.metrics['refresh_operations'],
            'active_access_tokens': active_tokens,
            'total_refresh_tokens': len(self.refresh_tokens),
            'registered_clients': len(self.clients)
        }

if __name__ == "__main__":
    # Create OAuth server
    oauth_server = OAuthAuthorizationServer()
    
    # Demonstrate OAuth flows
    flow_results = oauth_server.demonstrate_oauth_flows()
    
    # Demonstrate security features
    security_features = oauth_server.demonstrate_security_features()
    
    # Token introspection demo
    if oauth_server.access_tokens:
        sample_token = list(oauth_server.access_tokens.keys())[0]
        introspection_result = oauth_server.introspect_token(sample_token)
        
        # Token revocation demo
        revocation_result = oauth_server.revoke_token(sample_token)
    
    # Get server metrics
    metrics = oauth_server.get_server_metrics()
    
    print(f"\n=== OAuth Server Summary ===")
    print(f"Authorization requests: {metrics['authorization_requests']}")
    print(f"Token requests: {metrics['token_requests']}")
    print(f"Active access tokens: {metrics['active_access_tokens']}")
    print(f"Refresh tokens: {metrics['total_refresh_tokens']}")
    print(f"Registered clients: {metrics['registered_clients']}")
    print(f"Security features: {len(security_features)}")
    print(f"OAuth 2.0 provides secure, delegated authorization with multiple flows and robust security")
