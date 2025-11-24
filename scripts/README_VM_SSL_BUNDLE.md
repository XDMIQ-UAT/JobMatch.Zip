# VM SSL Setup from Bundle

This script configures HTTPS for `jobmatch.zip` on a GCP VM using an SSL bundle from the `/secrets` folder, then destroys the bundle after use. DNS should already point to the VM IP address.

## Prerequisites

1. **Google Cloud SDK** installed and authenticated
2. **GCP VM** running with Nginx installed
3. **DNS** already configured to point to VM IP address
4. **SSL Bundle** located at `secrets/jobmatch.zip-ssl-bundle.zip`

## Usage

### Linux/Mac (Bash)

```bash
export GCP_PROJECT_ID="your-project-id"  # Optional but recommended
export VM_NAME="jobmatch-vm"  # Optional: defaults to jobmatch-vm
export GCP_ZONE="us-central1-a"  # Optional: defaults to us-central1-a

chmod +x scripts/setup-vm-ssl-from-bundle.sh
./scripts/setup-vm-ssl-from-bundle.sh
```

### Windows (PowerShell)

```powershell
$env:GCP_PROJECT_ID = "your-project-id"  # Optional but recommended
$env:VM_NAME = "jobmatch-vm"  # Optional: defaults to jobmatch-vm
$env:GCP_ZONE = "us-central1-a"  # Optional: defaults to us-central1-a

.\scripts\setup-vm-ssl-from-bundle.ps1
```

## What It Does

1. **Extracts SSL Bundle**: Extracts the SSL certificate and private key from `secrets/jobmatch.zip-ssl-bundle.zip`
2. **Verifies Certificate**: Validates the certificate format (if openssl is available)
3. **Uploads to VM**: Uploads certificates to `/etc/nginx/ssl/jobmatch.zip/` on the VM
4. **Configures Nginx**: Sets up HTTPS with SSL certificates, HTTP to HTTPS redirect, and security headers
5. **Verifies DNS**: Optionally checks Cloud DNS configuration if GCP_PROJECT_ID is set
6. **Destroys SSL Bundle**: Removes the SSL bundle and temporary files as requested

## Environment Variables

- `GCP_PROJECT_ID` (optional): Your Google Cloud Project ID (used for DNS verification)
- `VM_NAME` (optional): VM instance name (defaults to `jobmatch-vm`)
- `GCP_ZONE` (optional): GCP zone (defaults to `us-central1-a`)
- `DOMAIN` (optional): Domain name (defaults to `jobmatch.zip`)
- `SSL_BUNDLE_PATH` (optional): Path to SSL bundle (defaults to `secrets/jobmatch.zip-ssl-bundle.zip`)

## SSL Bundle Format

The SSL bundle should be a ZIP file containing:
- `*.cert.pem` or `cert.pem` or `fullchain.pem` - Certificate file
- `private.key.pem` or `privkey.pem` or `*.key.pem` - Private key file
- `chain.pem` or `*.chain.pem` (optional) - Certificate chain file

## Important Notes

- **DNS Must Be Configured**: DNS should already point to the VM IP address before running this script
- **Nginx Required**: The VM must have Nginx installed and running
- **SSL Bundle Destruction**: The SSL bundle is permanently deleted after use as requested. Make sure you have a backup if needed
- **Development Use**: This is intended for development SSL setup on a VM

## Troubleshooting

### SSL Bundle Not Found
```
❌ SSL bundle not found: secrets/jobmatch.zip-ssl-bundle.zip
```
**Solution**: Ensure the SSL bundle exists at the specified path or set `SSL_BUNDLE_PATH` environment variable.

### VM Connection Failed
```
❌ Failed to connect to VM
```
**Solution**: 
1. Verify VM name: `gcloud compute instances list`
2. Check zone: `gcloud compute instances describe jobmatch-vm --zone=us-central1-a`
3. Ensure gcloud is authenticated: `gcloud auth login`

### Nginx Configuration Error
```
❌ Failed to configure Nginx
```
**Solution**: 
1. SSH into VM: `gcloud compute ssh jobmatch-vm --zone=us-central1-a`
2. Check Nginx config: `sudo nginx -t`
3. Verify certificate files: `ls -la /etc/nginx/ssl/jobmatch.zip/`
4. Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`

## Next Steps After Running

1. **Test HTTPS**: Verify HTTPS is working: `curl -I https://jobmatch.zip`
2. **Check Health**: Test health endpoint: `curl -I https://jobmatch.zip/health`
3. **Monitor Logs**: Check Nginx access logs: `gcloud compute ssh jobmatch-vm --zone=us-central1-a --command="sudo tail -f /var/log/nginx/access.log"`

