---
name: spring-security
description: Spring Security filter chains, request authorization, authentication providers, method security, CSRF, CORS, sessions, OAuth2 resource servers, and security tests. Use for Spring applications when the task changes or reviews a concrete security boundary.
license: MIT
metadata:
  author: pi-dev-kit
  source-type: official-doc-derived
  reviewed: "2026-08-21"
---

# Spring Security

Treat security configuration as an ordered request-processing boundary, not a collection of unrelated annotations. Confirm the Spring Security version and the application's authentication model before changing it.

## Official references

- https://docs.spring.io/spring-security/reference/servlet/architecture.html
- https://docs.spring.io/spring-security/reference/servlet/authorization/authorize-http-requests.html
- https://docs.spring.io/spring-security/reference/servlet/exploits/csrf.html
- https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/index.html
- https://docs.spring.io/spring-security/reference/servlet/test/index.html

This is an original pi-dev-kit summary derived from official documentation.

## Filter-chain ownership

- Inspect every `SecurityFilterChain` and its `securityMatcher`. Multiple chains are selected by matcher and order; only the first matching chain applies.
- Keep authentication filters before authorization decisions at the documented positions. Avoid manual filter insertion unless the required relative filter is explicit.
- Use `authorizeHttpRequests` matchers from most specific to least specific. A broad permit rule can shadow later restrictions.
- Distinguish web request authorization from method security. Enabling `@EnableMethodSecurity` does not replace URL-level protection.

## Authentication

- Identify whether credentials come from sessions, bearer tokens, API keys, OAuth2 login, or another provider.
- Reuse `AuthenticationProvider`, `AuthenticationManager`, JWT decoder, and converter facilities rather than parsing credentials in controllers.
- Keep principal construction and authority mapping at the authentication boundary. Do not trust caller-supplied role or identity headers without an authenticated trust boundary.

## CSRF and CORS

- Do not disable CSRF merely because an endpoint is called an API. Determine whether browser-managed credentials such as cookies or HTTP Basic are sent automatically.
- For cookie-backed sessions, preserve CSRF protection and token transport unless the complete threat model justifies a narrower matcher exclusion.
- CORS is not authorization. Configure allowed origins, methods, headers, and credentials deliberately and test preflight behavior.

## OAuth2 resource servers

- Validate issuer, audience where required, signature algorithm, clock behavior, and authority conversion.
- Keep token issuance separate from resource-server token validation unless the application explicitly owns both roles.
- Never log bearer tokens, session IDs, API keys, or full authentication objects containing credentials.

## Tests

- Use Spring Security test support (`@WithMockUser`, request post-processors, result matchers) for authorization behavior.
- Include denied and unauthenticated cases, not only the success path.
- When custom filters or chain ordering matter, use an application-context or web integration test that exercises the actual chain.

## Review checklist

1. Map chain selection, order, and matcher scope.
2. Identify the credential and principal ownership boundary.
3. Verify CSRF/CORS decisions against browser credential behavior.
4. Test allowed, denied, and unauthenticated requests.
5. Keep secrets and tokens out of source, logs, and test reports.

## Application security hardening

- Use Spring Security adaptive password encoders; never store plaintext credentials or invent password hashing.
- Keep secrets out of committed configuration, defaults, logs, and fixtures.
- Use parameterized persistence APIs and validated DTO boundaries; never concatenate untrusted SQL, JPQL, commands, redirects, or paths.
- Put headers and rate limits at the owning boundary and verify the effective response instead of duplicating controls.
- Constrain upload size, type, path, storage, and execution boundaries.
- Redact personal and authentication data from logs.
