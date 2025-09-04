#!/usr/bin/env python3
"""
OAuth 2.0 Security Analysis and Threat Mitigation
Demonstrates OAuth security vulnerabilities and protection mechanisms
"""

import time
import random
import json
import hashlib
import base64
import secrets
import urllib.parse
from datetime import datetime, timedelta

class OAuthSecurityAnalyzer:
    def __init__(self):
        self.vulnerabilities = []
        self.mitigations = []
        self.security_tests = []
        
    def demonstrate_oauth_security(self):
        """Demonstrate OAuth security analysis"""
        print(f"=== OAuth 2.0 Security Analysis ===")
        print(f"Analyzing common vulnerabilities and protection mechanisms")
        
        analyses = [
            self.analyze_authorization_code_interception,
            self.analyze_csrf_attacks,
            self.analyze_token_leakage,
            self.analyze_scope_escalation,
            self.demonstrate_pkce_protection,
            self.demonstrate_state_parameter_protection
        ]
        
        results = []
        for analysis in analyses:
            result = analysis()
            results.append(result)
            time.sleep(0.2)
        
        return results
    
    def analyze_authorization_code_interception(self):
        """Analyze authorization code interception vulnerability"""
        print(f"\n🚨 Vulnerability: Authorization Code Interception")
        
        vulnerability = {
            'name': 'Authorization Code Interception',
            'description': 'Attacker intercepts authorization code in redirect',
            'impact': 'High - Can obtain access tokens',
            'attack_vector': 'Network sniffing, malicious apps, browser history'
        }
        
        print(f"📋 Vulnerability Analysis:")
        print(f"   Name: {vulnerability['name']}")
        print(f"   Impact: {vulnerability['impact']}")
        print(f"   Vector: {vulnerability['attack_vector']}")
        
        # Simulate vulnerable scenario
        print(f"\n⚠️ Vulnerable Scenario:")
        auth_code = "auth_123456"
        redirect_url = f"http://app.example.com/callback?code={auth_code}"
        print(f"   Insecure redirect: {redirect_url}")
        print(f"   ❌ HTTP (not HTTPS) - code visible in logs")
        print(f"   ❌ No PKCE - code can be replayed")
        
        # Mitigation strategies
        mitigations = [
            "Use HTTPS for all OAuth flows",
            "Implement PKCE for public clients",
            "Short authorization code lifetime (10 minutes)",
            "One-time use authorization codes",
            "Validate redirect URI exactly"
        ]
        
        print(f"\n🛡️ Mitigations:")
        for i, mitigation in enumerate(mitigations, 1):
            print(f"   {i}. {mitigation}")
        
        self.vulnerabilities.append(vulnerability)
        self.mitigations.extend(mitigations)
        
        return {
            'vulnerability': vulnerability,
            'mitigations': mitigations,
            'severity': 'high'
        }
    
    def analyze_csrf_attacks(self):
        """Analyze CSRF attacks in OAuth flows"""
        print(f"\n🚨 Vulnerability: Cross-Site Request Forgery (CSRF)")
        
        vulnerability = {
            'name': 'OAuth CSRF Attack',
            'description': 'Attacker tricks user into authorizing malicious app',
            'impact': 'Medium - Unauthorized account linking',
            'attack_vector': 'Malicious websites, email links'
        }
        
        print(f"📋 Vulnerability Analysis:")
        print(f"   Name: {vulnerability['name']}")
        print(f"   Impact: {vulnerability['impact']}")
        print(f"   Vector: {vulnerability['attack_vector']}")
        
        # Simulate CSRF attack
        print(f"\n⚠️ CSRF Attack Scenario:")
        malicious_auth_url = "https://auth.example.com/authorize?response_type=code&client_id=attacker_app&redirect_uri=https://attacker.com/callback"
        print(f"   Malicious link: {malicious_auth_url[:80]}...")
        print(f"   ❌ No state parameter - CSRF possible")
        print(f"   ❌ User unknowingly authorizes attacker's app")
        
        # State parameter protection
        print(f"\n🛡️ State Parameter Protection:")
        state = secrets.token_urlsafe(32)
        secure_auth_url = f"https://auth.example.com/authorize?response_type=code&client_id=legitimate_app&state={state}&redirect_uri=https://app.com/callback"
        print(f"   Secure URL with state: {secure_auth_url[:80]}...")
        print(f"   ✅ State parameter: {state[:20]}...")
        print(f"   ✅ CSRF protection enabled")
        
        mitigations = [
            "Always include state parameter",
            "Validate state on callback",
            "Use cryptographically secure random state",
            "Bind state to user session",
            "Implement proper logout"
        ]
        
        print(f"\n🛡️ CSRF Mitigations:")
        for i, mitigation in enumerate(mitigations, 1):
            print(f"   {i}. {mitigation}")
        
        return {
            'vulnerability': vulnerability,
            'mitigations': mitigations,
            'severity': 'medium',
            'state_example': state
        }
    
    def analyze_token_leakage(self):
        """Analyze token leakage vulnerabilities"""
        print(f"\n🚨 Vulnerability: Token Leakage")
        
        vulnerability = {
            'name': 'Access Token Leakage',
            'description': 'Tokens exposed through various channels',
            'impact': 'High - Direct API access compromise',
            'attack_vector': 'Browser history, logs, referrer headers, XSS'
        }
        
        print(f"📋 Vulnerability Analysis:")
        print(f"   Name: {vulnerability['name']}")
        print(f"   Impact: {vulnerability['impact']}")
        print(f"   Vector: {vulnerability['attack_vector']}")
        
        # Token leakage scenarios
        leakage_scenarios = [
            {
                'scenario': 'URL Fragment Leakage',
                'example': 'https://app.com/callback#access_token=abc123&token_type=bearer',
                'risk': 'Browser history, referrer headers'
            },
            {
                'scenario': 'JavaScript Console Logging',
                'example': 'console.log("Token:", accessToken)',
                'risk': 'Developer tools, debugging'
            },
            {
                'scenario': 'Local Storage',
                'example': 'localStorage.setItem("token", accessToken)',
                'risk': 'XSS attacks, browser inspection'
            }
        ]
        
        print(f"\n⚠️ Token Leakage Scenarios:")
        for scenario in leakage_scenarios:
            print(f"   {scenario['scenario']}:")
            print(f"     Example: {scenario['example']}")
            print(f"     Risk: {scenario['risk']}")
        
        # Protection mechanisms
        protections = [
            "Use Authorization Code flow (not Implicit)",
            "Store tokens in secure, httpOnly cookies",
            "Implement short token lifetimes",
            "Use refresh tokens for long-term access",
            "Implement proper token revocation",
            "Avoid logging sensitive data"
        ]
        
        print(f"\n🛡️ Token Protection:")
        for i, protection in enumerate(protections, 1):
            print(f"   {i}. {protection}")
        
        return {
            'vulnerability': vulnerability,
            'scenarios': leakage_scenarios,
            'protections': protections,
            'severity': 'high'
        }
    
    def analyze_scope_escalation(self):
        """Analyze scope escalation attacks"""
        print(f"\n🚨 Vulnerability: Scope Escalation")
        
        vulnerability = {
            'name': 'OAuth Scope Escalation',
            'description': 'Obtaining broader permissions than intended',
            'impact': 'Medium - Unauthorized data access',
            'attack_vector': 'Scope manipulation, privilege escalation'
        }
        
        print(f"📋 Vulnerability Analysis:")
        print(f"   Name: {vulnerability['name']}")
        print(f"   Impact: {vulnerability['impact']}")
        
        # Scope escalation example
        print(f"\n⚠️ Scope Escalation Example:")
        requested_scope = "read:profile"
        granted_scope = "read:profile read:email write:posts admin:users"
        
        print(f"   Requested scope: {requested_scope}")
        print(f"   Granted scope: {granted_scope}")
        print(f"   ❌ Server granted more permissions than requested")
        print(f"   ❌ Client didn't validate granted scope")
        
        # Scope validation
        print(f"\n🛡️ Scope Validation:")
        print(f"   ✅ Server validates requested scopes against client permissions")
        print(f"   ✅ Client validates granted scopes match request")
        print(f"   ✅ Implement principle of least privilege")
        
        mitigations = [
            "Validate all requested scopes",
            "Implement scope hierarchy",
            "Client-side scope validation",
            "Audit scope grants regularly",
            "Use fine-grained permissions"
        ]
        
        print(f"\n🛡️ Scope Protection:")
        for i, mitigation in enumerate(mitigations, 1):
            print(f"   {i}. {mitigation}")
        
        return {
            'vulnerability': vulnerability,
            'example': {
                'requested': requested_scope,
                'granted': granted_scope
            },
            'mitigations': mitigations,
            'severity': 'medium'
        }
    
    def demonstrate_pkce_protection(self):
        """Demonstrate PKCE protection mechanism"""
        print(f"\n🛡️ PKCE Protection Demonstration")
        
        # Generate PKCE parameters
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode('utf-8').rstrip('=')
        
        print(f"🔐 PKCE Parameters:")
        print(f"   Code verifier: {code_verifier[:30]}...")
        print(f"   Code challenge: {code_challenge[:30]}...")
        print(f"   Challenge method: S256")
        
        # Simulate attack without PKCE
        print(f"\n⚠️ Attack Without PKCE:")
        intercepted_code = "auth_intercepted_123"
        print(f"   1. Attacker intercepts authorization code: {intercepted_code}")
        print(f"   2. Attacker exchanges code for tokens")
        print(f"   3. ❌ Attack succeeds - no additional verification")
        
        # Simulate protection with PKCE
        print(f"\n🛡️ Protection With PKCE:")
        print(f"   1. Attacker intercepts authorization code: {intercepted_code}")
        print(f"   2. Attacker attempts token exchange")
        print(f"   3. Server requires code verifier")
        print(f"   4. ✅ Attack fails - attacker doesn't have code verifier")
        
        # PKCE verification simulation
        print(f"\n🔍 PKCE Verification Process:")
        
        # Correct verification
        computed_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode('utf-8').rstrip('=')
        
        verification_success = computed_challenge == code_challenge
        print(f"   Stored challenge: {code_challenge[:30]}...")
        print(f"   Computed challenge: {computed_challenge[:30]}...")
        print(f"   Verification result: {'✅ SUCCESS' if verification_success else '❌ FAILED'}")
        
        return {
            'protection': 'PKCE',
            'code_verifier': code_verifier,
            'code_challenge': code_challenge,
            'verification_success': verification_success,
            'attack_prevented': True
        }
    
    def demonstrate_state_parameter_protection(self):
        """Demonstrate state parameter CSRF protection"""
        print(f"\n🛡️ State Parameter CSRF Protection")
        
        # Generate secure state
        client_state = secrets.token_urlsafe(32)
        session_binding = f"user_session_{random.randint(1000, 9999)}"
        
        print(f"🔐 State Parameter Generation:")
        print(f"   Client state: {client_state[:30]}...")
        print(f"   Session binding: {session_binding}")
        
        # Simulate CSRF attack attempt
        print(f"\n⚠️ CSRF Attack Attempt:")
        attacker_state = "attacker_controlled_state"
        print(f"   1. Attacker crafts malicious authorization URL")
        print(f"   2. Attacker state: {attacker_state}")
        print(f"   3. User clicks malicious link")
        
        # State validation
        print(f"\n🔍 State Validation:")
        received_state = client_state  # Legitimate callback
        validation_success = received_state == client_state
        
        print(f"   Expected state: {client_state[:30]}...")
        print(f"   Received state: {received_state[:30]}...")
        print(f"   Validation result: {'✅ SUCCESS' if validation_success else '❌ FAILED'}")
        
        # CSRF attack with wrong state
        print(f"\n🚨 CSRF Attack Validation:")
        attacker_received_state = attacker_state
        csrf_validation = attacker_received_state == client_state
        
        print(f"   Expected state: {client_state[:30]}...")
        print(f"   Attacker state: {attacker_received_state}")
        print(f"   Validation result: {'✅ SUCCESS' if csrf_validation else '❌ FAILED (CSRF blocked)'}")
        
        return {
            'protection': 'State Parameter',
            'client_state': client_state,
            'legitimate_validation': validation_success,
            'csrf_blocked': not csrf_validation,
            'session_binding': session_binding
        }
    
    def security_checklist(self):
        """Generate OAuth security checklist"""
        print(f"\n=== OAuth 2.0 Security Checklist ===")
        
        checklist = [
            {
                'category': 'Transport Security',
                'items': [
                    'Use HTTPS for all OAuth endpoints',
                    'Validate SSL certificates',
                    'Implement certificate pinning',
                    'Use secure redirect URIs'
                ]
            },
            {
                'category': 'Authorization Flow',
                'items': [
                    'Implement PKCE for public clients',
                    'Use state parameter for CSRF protection',
                    'Validate redirect URIs exactly',
                    'Short authorization code lifetime'
                ]
            },
            {
                'category': 'Token Management',
                'items': [
                    'Use short-lived access tokens',
                    'Implement refresh token rotation',
                    'Secure token storage',
                    'Proper token revocation'
                ]
            },
            {
                'category': 'Scope and Permissions',
                'items': [
                    'Implement principle of least privilege',
                    'Validate requested scopes',
                    'Use fine-grained permissions',
                    'Regular scope audits'
                ]
            },
            {
                'category': 'Client Security',
                'items': [
                    'Secure client secret storage',
                    'Validate server responses',
                    'Implement proper error handling',
                    'Regular security updates'
                ]
            }
        ]
        
        for category in checklist:
            print(f"\n🔒 {category['category']}:")
            for item in category['items']:
                print(f"   ✓ {item}")
        
        return checklist
    
    def analyze_security_metrics(self):
        """Analyze OAuth security metrics"""
        print(f"\n=== OAuth Security Metrics ===")
        
        # Simulate security metrics
        metrics = {
            'vulnerabilities_identified': len(self.vulnerabilities),
            'mitigations_implemented': len(set(self.mitigations)),
            'security_score': 85,  # Out of 100
            'pkce_adoption': 95,   # Percentage
            'https_usage': 98,     # Percentage
            'token_lifetime_avg': 3600,  # Seconds
            'failed_auth_attempts': 12,
            'suspicious_redirects': 3
        }
        
        print(f"Security Assessment:")
        print(f"  Vulnerabilities identified: {metrics['vulnerabilities_identified']}")
        print(f"  Mitigations available: {metrics['mitigations_implemented']}")
        print(f"  Security score: {metrics['security_score']}/100")
        print(f"  PKCE adoption: {metrics['pkce_adoption']}%")
        print(f"  HTTPS usage: {metrics['https_usage']}%")
        print(f"  Avg token lifetime: {metrics['token_lifetime_avg']}s")
        print(f"  Failed auth attempts: {metrics['failed_auth_attempts']}")
        print(f"  Suspicious redirects: {metrics['suspicious_redirects']}")
        
        return metrics

if __name__ == "__main__":
    # Create security analyzer
    security_analyzer = OAuthSecurityAnalyzer()
    
    # Demonstrate OAuth security analysis
    security_results = security_analyzer.demonstrate_oauth_security()
    
    # Generate security checklist
    checklist = security_analyzer.security_checklist()
    
    # Analyze security metrics
    metrics = security_analyzer.analyze_security_metrics()
    
    print(f"\n=== OAuth Security Summary ===")
    print(f"Vulnerabilities analyzed: {len(security_results)}")
    print(f"Security checklist items: {sum(len(cat['items']) for cat in checklist)}")
    print(f"Overall security score: {metrics['security_score']}/100")
    print(f"PKCE protection: {'✅ Enabled' if metrics['pkce_adoption'] > 90 else '⚠️ Needs improvement'}")
    print(f"OAuth 2.0 security requires comprehensive protection against multiple attack vectors")
