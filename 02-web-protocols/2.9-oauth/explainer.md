# OAuth 2.0 - Open Authorization Framework

## Definition
OAuth 2.0 is an authorization framework that enables applications to obtain limited access to user accounts on an HTTP service. It works by delegating user authentication to the service that hosts the user account and authorizing third-party applications to access the user account.

## RFCs and Standards
- **RFC 6749**: The OAuth 2.0 Authorization Framework (October 2012)
- **RFC 6750**: The OAuth 2.0 Authorization Framework: Bearer Token Usage
- **RFC 7636**: Proof Key for Code Exchange by OAuth Public Clients (PKCE)
- **RFC 8252**: OAuth 2.0 for Native Apps
- **OpenID Connect Core 1.0**: Identity layer on top of OAuth 2.0

## Real-World Engineering Scenario
Consider a modern e-commerce platform where users want to sign in using their Google account and grant a mobile shopping app access to their profile information without sharing their Google password. OAuth 2.0 enables secure, delegated authorization through standardized flows while maintaining user privacy and security.

## Key Features

### Authorization Flows
- **Authorization Code Flow**: Most secure for web applications
- **Implicit Flow**: For single-page applications (deprecated)
- **Client Credentials Flow**: For machine-to-machine communication
- **Resource Owner Password Credentials**: For trusted applications
- **PKCE Extension**: Enhanced security for public clients

### Security Features
- **Token-based authentication**: No password sharing
- **Scope-based permissions**: Granular access control
- **Short-lived access tokens**: Reduced exposure window
- **Refresh tokens**: Seamless token renewal
- **State parameter**: CSRF protection

### Modern Extensions
- **OpenID Connect**: Identity layer for authentication
- **JWT tokens**: Self-contained, stateless tokens
- **Device Authorization Grant**: For input-constrained devices
- **Token introspection**: Real-time token validation

## Code Examples

### Authorization Code Flow
```python
# Step 1: Redirect user to authorization server
auth_url = "https://auth.example.com/oauth/authorize"
params = {
    "response_type": "code",
    "client_id": "your_client_id",
    "redirect_uri": "https://yourapp.com/callback",
    "scope": "read:profile read:email",
    "state": "random_state_value"
}

# Step 2: Exchange authorization code for access token
token_url = "https://auth.example.com/oauth/token"
token_data = {
    "grant_type": "authorization_code",
    "code": "received_auth_code",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "redirect_uri": "https://yourapp.com/callback"
}
```

### PKCE Flow (Enhanced Security)
```python
# Generate PKCE parameters
code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode()).digest()
).decode('utf-8').rstrip('=')

# Authorization request with PKCE
auth_params = {
    "response_type": "code",
    "client_id": "your_client_id",
    "code_challenge": code_challenge,
    "code_challenge_method": "S256",
    "scope": "openid profile email"
}
```

## OAuth vs Traditional Authentication

| Aspect | Traditional Auth | OAuth 2.0 |
|--------|------------------|-----------|
| **Password Sharing** | Required | Never shared |
| **Access Granularity** | All-or-nothing | Scope-based |
| **Token Lifecycle** | Session-based | Configurable expiry |
| **Third-party Access** | Difficult | Native support |
| **Security Model** | Credential-based | Token-based |

## Performance Characteristics
- **Authorization latency**: 200-500ms (network dependent)
- **Token validation**: <10ms (local validation with JWT)
- **Refresh overhead**: 100-300ms (periodic background refresh)
- **Scalability**: Excellent (stateless tokens, distributed validation)

## Use Cases
- **Social login**: Sign in with Google, Facebook, GitHub
- **API access delegation**: Third-party app accessing user data
- **Microservices authorization**: Service-to-service authentication
- **Mobile app security**: Secure token-based authentication
- **Enterprise SSO**: Single sign-on across applications

## Security Considerations
- **Always use HTTPS**: Prevent token interception
- **Implement PKCE**: Protect against code interception
- **Validate redirect URIs**: Prevent authorization code injection
- **Use short-lived tokens**: Minimize exposure window
- **Implement proper logout**: Revoke tokens on sign-out

## Run Instructions

Execute the OAuth demonstrations:

```bash
# Run OAuth authorization server simulation
python3 oauth_server.py

# Run OAuth client application simulation
python3 oauth_client.py

# Run OAuth security analysis
python3 oauth_security.py

# Generate protocol diagrams
python3 render_diagram.py

# Run all tests
make test
```

OAuth 2.0 provides secure, standardized authorization for modern applications while maintaining user privacy and enabling seamless third-party integrations.
