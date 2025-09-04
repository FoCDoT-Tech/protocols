#!/usr/bin/env python3
"""
OAuth 2.0 Client Application Simulation
Demonstrates OAuth client flows, token management, and API access
"""

import time
import random
import json
import hashlib
import base64
import secrets
import urllib.parse
from datetime import datetime, timedelta

class OAuthClient:
    def __init__(self, client_id, client_secret=None, redirect_uri=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.authorization_server = "https://auth.example.com"
        self.resource_server = "https://api.example.com"
        
        self.metrics = {
            'authorization_requests': 0,
            'token_requests': 0,
            'api_calls': 0,
            'token_refreshes': 0
        }
    
    def demonstrate_oauth_client_flows(self):
        """Demonstrate OAuth client-side flows"""
        print(f"=== OAuth 2.0 Client Application ===")
        print(f"Client ID: {self.client_id}")
        print(f"Authorization Server: {self.authorization_server}")
        print(f"Resource Server: {self.resource_server}")
        
        flows = [
            self.authorization_code_flow,
            self.pkce_flow,
            self.token_refresh_flow,
            self.api_access_demo
        ]
        
        results = []
        for flow in flows:
            result = flow()
            results.append(result)
            time.sleep(0.3)
        
        return results
    
    def authorization_code_flow(self):
        """Demonstrate Authorization Code Flow from client perspective"""
        print(f"\n🔐 Authorization Code Flow (Client Side)")
        
        # Step 1: Generate authorization URL
        state = secrets.token_urlsafe(16)
        auth_params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'read:profile read:email write:posts',
            'state': state
        }
        
        auth_url = f"{self.authorization_server}/authorize?" + urllib.parse.urlencode(auth_params)
        
        print(f"📤 Redirecting user to authorization server:")
        print(f"   URL: {auth_url[:80]}...")
        print(f"   State: {state}")
        print(f"   Scope: {auth_params['scope']}")
        
        self.metrics['authorization_requests'] += 1
        
        # Simulate user authorization and callback
        print(f"👤 User authorizes application...")
        time.sleep(0.5)
        
        # Step 2: Simulate callback with authorization code
        auth_code = f"auth_{secrets.token_urlsafe(16)}"
        callback_url = f"{self.redirect_uri}?code={auth_code}&state={state}"
        
        print(f"📨 Authorization callback received:")
        print(f"   Code: {auth_code}")
        print(f"   State: {state} (validated ✅)")
        
        # Step 3: Exchange code for tokens
        token_request = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri
        }
        
        print(f"📤 Exchanging code for tokens...")
        
        # Simulate token response
        tokens = self.simulate_token_response(token_request)
        
        if tokens:
            self.access_token = tokens['access_token']
            self.refresh_token = tokens['refresh_token']
            self.token_expires_at = datetime.now() + timedelta(seconds=tokens['expires_in'])
            
            print(f"✅ Tokens received:")
            print(f"   Access token: {self.access_token[:20]}...")
            print(f"   Refresh token: {self.refresh_token[:20]}...")
            print(f"   Expires in: {tokens['expires_in']} seconds")
            print(f"   Scope: {tokens['scope']}")
            
            self.metrics['token_requests'] += 1
            
            return {
                'flow': 'authorization_code',
                'status': 'success',
                'tokens': tokens
            }
        else:
            print(f"❌ Token exchange failed")
            return {
                'flow': 'authorization_code',
                'status': 'failed'
            }
    
    def pkce_flow(self):
        """Demonstrate PKCE flow for public clients"""
        print(f"\n🔒 PKCE Flow (Public Client)")
        
        # Generate PKCE parameters
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode('utf-8').rstrip('=')
        
        print(f"🔑 Generated PKCE parameters:")
        print(f"   Code verifier: {code_verifier[:20]}...")
        print(f"   Code challenge: {code_challenge[:20]}...")
        print(f"   Challenge method: S256")
        
        # Authorization request with PKCE
        state = secrets.token_urlsafe(16)
        auth_params = {
            'response_type': 'code',
            'client_id': 'mobile_app_789',
            'redirect_uri': 'com.example.app://oauth/callback',
            'scope': 'read:profile read:email',
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
            'state': state
        }
        
        auth_url = f"{self.authorization_server}/authorize?" + urllib.parse.urlencode(auth_params)
        
        print(f"📤 PKCE authorization request:")
        print(f"   URL: {auth_url[:80]}...")
        print(f"   Code challenge included: ✅")
        
        # Simulate callback
        auth_code = f"pkce_{secrets.token_urlsafe(16)}"
        print(f"📨 Authorization code received: {auth_code}")
        
        # Token exchange with code verifier
        token_request = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'client_id': 'mobile_app_789',
            'redirect_uri': 'com.example.app://oauth/callback',
            'code_verifier': code_verifier
        }
        
        print(f"📤 Token exchange with PKCE:")
        print(f"   Code verifier: {code_verifier[:20]}...")
        print(f"   No client secret (public client)")
        
        # Simulate token response
        tokens = self.simulate_token_response(token_request, pkce=True)
        
        if tokens:
            print(f"✅ PKCE verification successful")
            print(f"📤 Tokens issued: {tokens['access_token'][:20]}...")
            
            return {
                'flow': 'pkce',
                'status': 'success',
                'code_verifier': code_verifier,
                'tokens': tokens
            }
        else:
            print(f"❌ PKCE verification failed")
            return {
                'flow': 'pkce',
                'status': 'failed'
            }
    
    def token_refresh_flow(self):
        """Demonstrate token refresh"""
        print(f"\n🔄 Token Refresh Flow")
        
        if not self.refresh_token:
            print(f"❌ No refresh token available")
            return {'flow': 'refresh', 'status': 'failed', 'error': 'no_refresh_token'}
        
        print(f"⏰ Access token expires at: {self.token_expires_at}")
        print(f"🔄 Refreshing access token...")
        
        refresh_request = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'read:profile'  # Can request subset
        }
        
        print(f"📤 Refresh token request:")
        print(f"   Refresh token: {self.refresh_token[:20]}...")
        print(f"   Requested scope: {refresh_request['scope']}")
        
        # Simulate refresh response
        new_tokens = self.simulate_token_response(refresh_request, refresh=True)
        
        if new_tokens:
            old_token = self.access_token
            self.access_token = new_tokens['access_token']
            self.token_expires_at = datetime.now() + timedelta(seconds=new_tokens['expires_in'])
            
            print(f"✅ Token refreshed successfully:")
            print(f"   Old token: {old_token[:20]}... (invalidated)")
            print(f"   New token: {self.access_token[:20]}...")
            print(f"   New expiry: {self.token_expires_at}")
            
            self.metrics['token_refreshes'] += 1
            
            return {
                'flow': 'refresh',
                'status': 'success',
                'new_tokens': new_tokens
            }
        else:
            print(f"❌ Token refresh failed")
            return {
                'flow': 'refresh',
                'status': 'failed'
            }
    
    def api_access_demo(self):
        """Demonstrate API access with OAuth tokens"""
        print(f"\n🌐 API Access with OAuth Tokens")
        
        if not self.access_token:
            print(f"❌ No access token available")
            return {'demo': 'api_access', 'status': 'failed', 'error': 'no_token'}
        
        # API calls with different scopes
        api_calls = [
            {
                'endpoint': '/api/user/profile',
                'method': 'GET',
                'scope_required': 'read:profile',
                'description': 'Get user profile information'
            },
            {
                'endpoint': '/api/user/email',
                'method': 'GET',
                'scope_required': 'read:email',
                'description': 'Get user email address'
            },
            {
                'endpoint': '/api/posts',
                'method': 'POST',
                'scope_required': 'write:posts',
                'description': 'Create a new post'
            }
        ]
        
        results = []
        
        for api_call in api_calls:
            print(f"\n📡 API Call: {api_call['method']} {api_call['endpoint']}")
            print(f"   Description: {api_call['description']}")
            print(f"   Required scope: {api_call['scope_required']}")
            
            # Simulate API request with Bearer token
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            print(f"📤 Request headers:")
            print(f"   Authorization: Bearer {self.access_token[:20]}...")
            
            # Simulate API response
            response = self.simulate_api_response(api_call, headers)
            
            if response['status'] in [200, 201]:
                print(f"✅ API call successful:")
                print(f"   Status: {response['status']}")
                print(f"   Data: {json.dumps(response['data'], indent=2)[:100]}...")
            else:
                print(f"❌ API call failed:")
                print(f"   Status: {response['status']}")
                print(f"   Error: {response.get('error', 'Unknown error')}")
            
            results.append(response)
            self.metrics['api_calls'] += 1
            time.sleep(0.2)
        
        return {
            'demo': 'api_access',
            'status': 'success',
            'api_calls': len(results),
            'results': results
        }
    
    def simulate_token_response(self, request, pkce=False, refresh=False):
        """Simulate OAuth token response"""
        # Simulate network delay
        time.sleep(random.uniform(0.1, 0.3))
        
        if refresh:
            return {
                'access_token': f"at_{secrets.token_urlsafe(32)}",
                'token_type': 'Bearer',
                'expires_in': 3600,
                'scope': request['scope']
            }
        else:
            return {
                'access_token': f"at_{secrets.token_urlsafe(32)}",
                'token_type': 'Bearer',
                'expires_in': 3600,
                'refresh_token': f"rt_{secrets.token_urlsafe(32)}",
                'scope': request.get('scope', 'read:profile read:email')
            }
    
    def simulate_api_response(self, api_call, headers):
        """Simulate API response"""
        # Simulate network delay
        time.sleep(random.uniform(0.05, 0.15))
        
        # Check token format
        auth_header = headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return {
                'status': 401,
                'error': 'invalid_token',
                'message': 'Invalid authorization header'
            }
        
        # Simulate different responses based on endpoint
        if api_call['endpoint'] == '/api/user/profile':
            return {
                'status': 200,
                'data': {
                    'id': 'user123',
                    'name': 'Alice Johnson',
                    'username': 'alice',
                    'avatar_url': 'https://example.com/alice.jpg',
                    'created_at': '2020-01-15T10:30:00Z'
                }
            }
        elif api_call['endpoint'] == '/api/user/email':
            return {
                'status': 200,
                'data': {
                    'email': 'alice@example.com',
                    'verified': True,
                    'primary': True
                }
            }
        elif api_call['endpoint'] == '/api/posts':
            return {
                'status': 201,
                'data': {
                    'id': 'post_456',
                    'title': 'My OAuth Experience',
                    'content': 'OAuth 2.0 makes secure API access easy!',
                    'created_at': datetime.now().isoformat(),
                    'author': 'alice'
                }
            }
        else:
            return {
                'status': 404,
                'error': 'not_found',
                'message': 'Endpoint not found'
            }
    
    def demonstrate_security_best_practices(self):
        """Demonstrate OAuth security best practices"""
        print(f"\n=== OAuth Client Security Best Practices ===")
        
        practices = [
            {
                'practice': 'HTTPS Only',
                'description': 'Always use HTTPS for OAuth flows',
                'implementation': 'All URLs use https:// scheme'
            },
            {
                'practice': 'State Parameter',
                'description': 'Prevent CSRF attacks',
                'implementation': 'Random state value in auth requests'
            },
            {
                'practice': 'PKCE for Public Clients',
                'description': 'Protect against code interception',
                'implementation': 'SHA256 code challenge/verifier'
            },
            {
                'practice': 'Token Storage',
                'description': 'Secure token storage',
                'implementation': 'Encrypted storage, memory-only for web'
            },
            {
                'practice': 'Scope Minimization',
                'description': 'Request minimum required permissions',
                'implementation': 'Specific scopes, not wildcard access'
            },
            {
                'practice': 'Token Expiry Handling',
                'description': 'Graceful token refresh',
                'implementation': 'Automatic refresh before expiry'
            }
        ]
        
        for practice in practices:
            print(f"🔒 {practice['practice']}")
            print(f"   Description: {practice['description']}")
            print(f"   Implementation: {practice['implementation']}")
        
        return practices
    
    def analyze_token_lifecycle(self):
        """Analyze OAuth token lifecycle"""
        print(f"\n=== OAuth Token Lifecycle Analysis ===")
        
        if not self.access_token:
            print(f"❌ No active tokens to analyze")
            return None
        
        now = datetime.now()
        time_to_expiry = self.token_expires_at - now if self.token_expires_at else None
        
        lifecycle_info = {
            'access_token_length': len(self.access_token),
            'refresh_token_available': bool(self.refresh_token),
            'expires_at': self.token_expires_at.isoformat() if self.token_expires_at else None,
            'time_to_expiry_seconds': int(time_to_expiry.total_seconds()) if time_to_expiry else None,
            'should_refresh': time_to_expiry and time_to_expiry.total_seconds() < 300  # 5 minutes
        }
        
        print(f"Token Analysis:")
        print(f"  Access token length: {lifecycle_info['access_token_length']} characters")
        print(f"  Refresh token available: {lifecycle_info['refresh_token_available']}")
        print(f"  Expires at: {lifecycle_info['expires_at']}")
        print(f"  Time to expiry: {lifecycle_info['time_to_expiry_seconds']} seconds")
        print(f"  Should refresh soon: {lifecycle_info['should_refresh']}")
        
        return lifecycle_info
    
    def get_client_metrics(self):
        """Get OAuth client metrics"""
        return {
            'client_id': self.client_id,
            'authorization_requests': self.metrics['authorization_requests'],
            'token_requests': self.metrics['token_requests'],
            'api_calls': self.metrics['api_calls'],
            'token_refreshes': self.metrics['token_refreshes'],
            'has_active_token': bool(self.access_token),
            'has_refresh_token': bool(self.refresh_token)
        }

if __name__ == "__main__":
    # Create OAuth client
    oauth_client = OAuthClient(
        client_id='web_app_123',
        client_secret='secret_456',
        redirect_uri='https://webapp.example.com/callback'
    )
    
    # Demonstrate OAuth client flows
    flow_results = oauth_client.demonstrate_oauth_client_flows()
    
    # Demonstrate security best practices
    security_practices = oauth_client.demonstrate_security_best_practices()
    
    # Analyze token lifecycle
    lifecycle_analysis = oauth_client.analyze_token_lifecycle()
    
    # Get client metrics
    metrics = oauth_client.get_client_metrics()
    
    print(f"\n=== OAuth Client Summary ===")
    print(f"Client ID: {metrics['client_id']}")
    print(f"Authorization requests: {metrics['authorization_requests']}")
    print(f"Token requests: {metrics['token_requests']}")
    print(f"API calls: {metrics['api_calls']}")
    print(f"Token refreshes: {metrics['token_refreshes']}")
    print(f"Active token: {metrics['has_active_token']}")
    print(f"Security practices: {len(security_practices)}")
    print(f"OAuth 2.0 enables secure, delegated API access with robust client-side security")
