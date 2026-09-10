# Service Health

A service is considered healthy when the service is running
and its required dependencies are available.

For a payment service, database connectivity must be checked
before performing remediation.

If the service is unhealthy but database connectivity is healthy,
the service may be restarted.

After a restart, service health must be validated.