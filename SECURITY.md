# Security and privacy

Supported release line: 0.1.x. This project has a small maintenance team and no guaranteed response time.

For sensitive software vulnerabilities, use this repository's GitHub Security → Report a vulnerability feature when enabled. Do not post secrets, student information, exploit data or private notes in public issues. Ordinary non-sensitive defects may be filed publicly.

The reference server is a read-only, exact-route Python server that defaults to loopback. It has no authentication, role separation, TLS, student database, or upload endpoint. Teacher answer keys are open content. LAN mode requires explicit bind and allowed Host settings; it is not a multi-user school management security model. For public web use, publish the generated static files through a maintained HTTPS server.

Local notes are browser storage, accessible to people who use that browser profile and scripts allowed by the origin. Use separate profiles on shared computers, export personal notes and clear them when finished. Do not store identifiable student, family, health or safeguarding information in this app.
