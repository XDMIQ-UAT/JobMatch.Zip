# Scripts Directory

Automation scripts for JobFinder development and operations.

## Infrastructure Agent (infra-agent.ps1)

**Primary tool for environment management.**

The Infrastructure Agent automates localhost environment lifecycle for pre-production verification. You **cannot trigger a production release** until the environment passes verification.

### Quick Start

```powershell
# Start environment
.\scripts\infra-agent.ps1 up

# Verify (REQUIRED before production release)
.\scripts\infra-agent.ps1 verify

# Check status
.\scripts\infra-agent.ps1 status

# Stop
.\scripts\infra-agent.ps1 down
```

### Available Actions

- `up` - Start all services with health checks
- `down` - Stop all services gracefully
- `status` - Check current state and service health
- `verify` - Run comprehensive verification tests (required for production)
- `restart` - Stop and restart environment
- `logs` - View live logs from all services
- `clean` - Remove all containers, volumes, and data

### Options

- `-Mode` - Environment mode: `dev` (default) or `prod-sim`
- `-Timeout` - Service startup timeout in seconds (default: 300)

### Examples

```powershell
# Start in production simulation mode
.\scripts\infra-agent.ps1 up -Mode prod-sim

# Extend timeout for slow systems
.\scripts\infra-agent.ps1 up -Timeout 600

# Quick verification check
.\scripts\infra-agent.ps1 verify
```

See [Infrastructure Agent Documentation](../docs/INFRA_AGENT.md) for complete guide.

## Convenience Aliases (infra-aliases.ps1)

Load shorter command aliases:

```powershell
# Load aliases in current session
. .\scripts\infra-aliases.ps1

# Now use shorter commands
infra-up
infra-status
infra-verify
infra-down
```

### Available Aliases

- `infra-up` → `.\scripts\infra-agent.ps1 up`
- `infra-down` → `.\scripts\infra-agent.ps1 down`
- `infra-status` → `.\scripts\infra-agent.ps1 status`
- `infra-verify` → `.\scripts\infra-agent.ps1 verify`
- `infra-restart` → `.\scripts\infra-agent.ps1 restart`
- `infra-logs` → `.\scripts\infra-agent.ps1 logs`
- `infra-clean` → `.\scripts\infra-agent.ps1 clean`

To load automatically, add to your PowerShell profile (`$PROFILE`):
```powershell
. E:\JobFinder\scripts\infra-aliases.ps1
```

## Other Scripts

### GCP CLI Wrapper (gcp-cli-wrapper.py)

Documented backdoor for technical access via Google Cloud CLI.

```bash
python scripts/gcp-cli-wrapper.py status
python scripts/gcp-cli-wrapper.py health
python scripts/gcp-cli-wrapper.py metrics
```

See [GCP CLI Backdoor Documentation](../docs/GCP_CLI_BACKDOOR.md).

### Development Start Scripts

Located in project root:
- `start-dev.ps1` (Windows)
- `start-dev.sh` (Linux/Mac)

These are simple wrappers - prefer using the Infrastructure Agent instead.

## Best Practices

1. **Always verify before production**: Run `infra-agent.ps1 verify` before any release
2. **Use Infrastructure Agent over manual Docker**: It handles health checks and state tracking
3. **Load aliases for daily use**: Source `infra-aliases.ps1` in your PowerShell profile
4. **Check status regularly**: Use `infra-status` to monitor environment health
5. **Clean weekly**: Run `infra-clean` to clear stale data

## Troubleshooting

### Script won't run
```powershell
# Check execution policy
Get-ExecutionPolicy

# If restricted, set to RemoteSigned
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Services fail to start
```powershell
# Check Docker is running
docker ps

# View detailed logs
.\scripts\infra-agent.ps1 logs

# Clean and restart
.\scripts\infra-agent.ps1 clean
.\scripts\infra-agent.ps1 up
```

### Port conflicts
```powershell
# Check what's using a port
Get-NetTCPConnection -LocalPort 8000

# Stop infrastructure properly
.\scripts\infra-agent.ps1 down
```

## Integration

The Infrastructure Agent integrates with:
- **Warp Workflows**: See `.warp/workflows/infra-agent.yaml`
- **Docker Compose**: Uses `docker-compose.dev.yml` and `docker-compose.yml`
- **CI/CD Pipelines**: Exit codes indicate pass/fail for automation
- **State Tracking**: Maintains state in `.warp/infra-state.json`

## Exit Codes

All scripts follow standard exit code conventions:
- `0` - Success
- `1` - Error/Failure

The `verify` action is designed for CI/CD integration:
```powershell
.\scripts\infra-agent.ps1 verify
if ($LASTEXITCODE -eq 0) {
    # Proceed with release
} else {
    # Block release
}
```

## Contributing

When adding new scripts:
1. Use PowerShell for Windows-specific automation
2. Use Python for cross-platform utilities
3. Add comprehensive help/documentation
4. Follow naming convention: `{purpose}-{action}.{ext}`
5. Update this README
