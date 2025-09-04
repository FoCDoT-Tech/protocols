# SAML 2.0 - Security Assertion Markup Language

## Definition
SAML (Security Assertion Markup Language) 2.0 is an XML-based open standard for exchanging authentication and authorization data between parties, particularly between an identity provider and a service provider. It enables single sign-on (SSO) and identity federation across different domains and organizations.

## RFCs and Standards
- **SAML 2.0 Core**: Defines assertions, protocols, and bindings (OASIS, March 2005)
- **SAML 2.0 Profiles**: Defines specific use cases and flows
- **SAML 2.0 Bindings**: HTTP POST, HTTP Redirect, HTTP Artifact, SOAP
- **SAML 2.0 Metadata**: Describes SAML entities and their capabilities
- **SAML 2.0 Conformance**: Testing and interoperability requirements

## Real-World Engineering Scenario
Consider a large enterprise with multiple cloud applications (Salesforce, Office 365, AWS Console) where employees need seamless access without multiple logins. SAML 2.0 enables centralized authentication through Active Directory, allowing users to authenticate once and access all authorized applications through federated identity management.

## Key Features

### Core Components
- **Identity Provider (IdP)**: Authenticates users and issues assertions
- **Service Provider (SP)**: Consumes assertions and provides services
- **Assertions**: XML documents containing authentication/authorization statements
- **Protocols**: Request/response patterns for assertion exchange
- **Bindings**: Transport mechanisms for SAML messages

### Authentication Flows
- **SP-Initiated SSO**: Service provider initiates authentication
- **IdP-Initiated SSO**: Identity provider initiates authentication
- **Single Logout (SLO)**: Coordinated logout across all services
- **Artifact Resolution**: Indirect assertion retrieval for security

### Security Features
- **XML Digital Signatures**: Message integrity and authenticity
- **XML Encryption**: Confidentiality of sensitive assertion data
- **Replay Protection**: Timestamp and ID-based attack prevention
- **Audience Restriction**: Limit assertion usage to intended recipients

## Code Examples

### SAML Assertion Structure
```xml
<saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                ID="_8e8dc5f69a98cc4c1ff3427e5ce34606fd672f91e6"
                Version="2.0"
                IssueInstant="2024-01-15T10:30:00Z">
  <saml:Issuer>https://idp.example.com</saml:Issuer>
  <saml:Subject>
    <saml:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent">
      alice@example.com
    </saml:NameID>
  </saml:Subject>
  <saml:AuthnStatement AuthnInstant="2024-01-15T10:30:00Z">
    <saml:AuthnContext>
      <saml:AuthnContextClassRef>
        urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport
      </saml:AuthnContextClassRef>
    </saml:AuthnContext>
  </saml:AuthnStatement>
</saml:Assertion>
```

### SAML Authentication Request
```xml
<samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                    ID="_8e8dc5f69a98cc4c1ff3427e5ce34606fd672f91e6"
                    Version="2.0"
                    IssueInstant="2024-01-15T10:30:00Z"
                    Destination="https://idp.example.com/sso">
  <saml:Issuer xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
    https://sp.example.com
  </saml:Issuer>
  <samlp:NameIDPolicy Format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent"/>
</samlp:AuthnRequest>
```

## SAML vs OAuth Comparison

| Aspect | SAML 2.0 | OAuth 2.0 |
|--------|----------|-----------|
| **Primary Use** | Authentication & SSO | Authorization & API access |
| **Format** | XML | JSON/Form data |
| **Complexity** | High | Medium |
| **Enterprise Adoption** | Very High | High |
| **Mobile Support** | Limited | Excellent |
| **Token Format** | XML Assertions | Bearer tokens |

## Performance Characteristics
- **Authentication latency**: 300-800ms (XML processing overhead)
- **Assertion size**: 2-8KB (XML verbosity)
- **Signature verification**: 10-50ms (RSA/DSA operations)
- **Scalability**: Excellent (stateless assertions)
- **Caching**: Effective (metadata and certificates)

## Use Cases
- **Enterprise SSO**: Single sign-on across corporate applications
- **Identity Federation**: Cross-domain authentication
- **Cloud Integration**: SaaS application authentication
- **Government Systems**: High-security federated identity
- **Educational Institutions**: Student/faculty access management

## Security Considerations
- **Certificate Management**: Proper PKI infrastructure required
- **Assertion Encryption**: Protect sensitive user attributes
- **Replay Attack Prevention**: Implement proper timestamp validation
- **XML Security**: Validate against XML signature wrapping attacks
- **Metadata Security**: Secure exchange and validation of entity metadata

## Run Instructions

Execute the SAML demonstrations:

```bash
# Run SAML identity provider simulation
python3 saml_idp.py

# Run SAML service provider simulation
python3 saml_sp.py

# Run SAML federation and SSO flows
python3 saml_federation.py

# Generate protocol diagrams
python3 render_diagram.py

# Run all tests
make test
```

SAML 2.0 provides robust, enterprise-grade identity federation with strong security guarantees, enabling seamless single sign-on across complex organizational boundaries.
