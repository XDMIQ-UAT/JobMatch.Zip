# Secret Management with Google Secret Manager

## Overview

**🐱 CRITICAL: This project uses Google Secret Manager for ALL secrets in production.**

Never store secrets in:
- `.env` files committed to git
- Plain text configuration files
- Code or comments
- CI/CD pipelines (except as Secret Manager references)

**Violation = Kittens at risk 🙀**

---

## Architecture

### Development (Local)
- Secrets loaded from `.env` file
- File is gitignored and never committed
- Use `backend/.env.example` as template

### Production (GCP VM / Cloud Run)
- Secrets loaded from Google Secret Manager
- Automatic loading when `NODE_ENV=production`
- VM service account has access via IAM

---

## Setup Process

### 1. Enable Secret Manager API

```bash
gcloud services enable secretmanager.googleapis.com \
  --project=futurelink-private-112912460
```

### 2. Run the Setup Script

From your local machine:

```bash
# Make script executable
chmod +x scripts/setup-secrets.sh

# Run setup
bash scripts/setup-secrets.sh
```

This script will:
- Enable Secret Manager API
- Create secrets with generated values (JWT_SECRET, DATABASE_URL)
- Set up IAM permissions for VM service account
- Provide command for adding OpenAI API key

### 3. Add Your OpenAI API Key

**IMPORTANT**: The setup script creates a placeholder. You must add your actual key:

```bash
echo -n 'sk-proj-YOUR_ACTUAL_KEY_HERE' | gcloud secrets create jobmatch-openai-key \
  --project=futurelink-private-112912460 \
  --replication-policy='automatic' \
  --data-file=-
```

If the secret already exists, update it:

```bash
echo -n 'sk-proj-YOUR_ACTUAL_KEY_HERE' | gcloud secrets versions add jobmatch-openai-key \
  --project=futurelink-private-112912460 \
  --data-file=-
```

### 4. Verify Secrets

List all secrets:

```bash
gcloud secrets list --project=futurelink-private-112912460
```

View secret metadata (not the actual value):

```bash
gcloud secrets describe jobmatch-jwt-secret \
  --project=futurelink-private-112912460
```

Access a secret value (for verification):

```bash
gcloud secrets versions access latest \
  --secret=jobmatch-jwt-secret \
  --project=futurelink-private-112912460
```

---

## Secret Names

The following secrets are used:

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `jobmatch-jwt-secret` | JWT signing key | `base64-encoded-random-string` |
| `jobmatch-database-url` | PostgreSQL connection string | `postgresql://user@host:5432/db` |
| `jobmatch-openai-key` | OpenAI API key | `sk-proj-...` |

---

## Code Integration

### Backend Configuration

The backend automatically loads secrets based on `NODE_ENV`:

```typescript
// backend/src/config/secrets.ts
import { getSecrets } from './config/secrets';

async function initialize() {
  // Automatically loads from Secret Manager if NODE_ENV=production
  // Otherwise loads from .env file
  const secrets = await getSecrets();
  
  // secrets.JWT_SECRET
  // secrets.DATABASE_URL
  // secrets.OPENAI_API_KEY
}
```

### Usage Example

```typescript
import { getSecrets } from './config/secrets';

// In your Express app initialization
app.listen(PORT, async () => {
  const secrets = await getSecrets();
  
  // Use secrets
  jwt.sign(payload, secrets.JWT_SECRET);
  // Database already uses secrets.DATABASE_URL
  // OpenAI client uses secrets.OPENAI_API_KEY
});
```

---

## Updating Secrets

### Update JWT Secret

```bash
NEW_SECRET=$(openssl rand -base64 32)
echo -n "$NEW_SECRET" | gcloud secrets versions add jobmatch-jwt-secret \
  --project=futurelink-private-112912460 \
  --data-file=-
```

### Update Database URL

```bash
echo -n 'postgresql://user:pass@host:5432/db' | gcloud secrets versions add jobmatch-database-url \
  --project=futurelink-private-112912460 \
  --data-file=-
```

### Update OpenAI Key

```bash
echo -n 'sk-proj-NEW_KEY' | gcloud secrets versions add jobmatch-openai-key \
  --project=futurelink-private-112912460 \
  --data-file=-
```

After updating secrets, restart services:

```bash
# On VM
pm2 restart all
```

---

## IAM Permissions

### VM Service Account Access

The VM's default compute service account needs the `secretAccessor` role:

```bash
# Get project number
PROJECT_NUMBER=$(gcloud projects describe futurelink-private-112912460 \
  --format="value(projectNumber)")

# Service account email
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# Grant access to all secrets
for SECRET in jobmatch-jwt-secret jobmatch-database-url jobmatch-openai-key; do
  gcloud secrets add-iam-policy-binding $SECRET \
    --project=futurelink-private-112912460 \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"
done
```

### Cloud Run Service Account

For Cloud Run deployment:

```bash
# Create service account
gcloud iam service-accounts create jobmatch-cloudrun \
  --project=futurelink-private-112912460 \
  --display-name="JobMatch Cloud Run Service Account"

# Grant Secret Manager access
for SECRET in jobmatch-jwt-secret jobmatch-database-url jobmatch-openai-key; do
  gcloud secrets add-iam-policy-binding $SECRET \
    --project=futurelink-private-112912460 \
    --member="serviceAccount:jobmatch-cloudrun@futurelink-private-112912460.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
done
```

---

## Security Best Practices

### ✅ DO

- Use Secret Manager for all production secrets
- Rotate secrets regularly (every 90 days)
- Use different secrets for dev/staging/prod
- Monitor secret access via Cloud Logging
- Delete old secret versions after rotation
- Use least-privilege IAM roles

### ❌ DON'T

- Store secrets in `.env` files on production
- Commit secrets to git
- Log secret values
- Share secrets via email/Slack
- Use the same secrets across environments
- Give broad IAM permissions

---

## Troubleshooting

### Error: "Failed to load secrets from Secret Manager"

**Solution 1**: Check Secret Manager API is enabled

```bash
gcloud services enable secretmanager.googleapis.com \
  --project=futurelink-private-112912460
```

**Solution 2**: Verify secrets exist

```bash
gcloud secrets list --project=futurelink-private-112912460
```

**Solution 3**: Check IAM permissions

```bash
gcloud secrets get-iam-policy jobmatch-jwt-secret \
  --project=futurelink-private-112912460
```

### Error: "Secret {name} is empty"

The secret was created but has no value. Add a version:

```bash
echo -n 'your-secret-value' | gcloud secrets versions add SECRET_NAME \
  --project=futurelink-private-112912460 \
  --data-file=-
```

### Error: "Permission denied"

VM service account doesn't have access. Grant it:

```bash
gcloud secrets add-iam-policy-binding SECRET_NAME \
  --project=futurelink-private-112912460 \
  --member="serviceAccount:COMPUTE_SA" \
  --role="roles/secretmanager.secretAccessor"
```

---

## Monitoring & Auditing

### View Secret Access Logs

```bash
gcloud logging read \
  'protoPayload.methodName="google.cloud.secretmanager.v1.SecretManagerService.AccessSecretVersion"' \
  --project=futurelink-private-112912460 \
  --limit=50 \
  --format=json
```

### Set Up Alerts

Create alerting policy for unexpected secret access:

```bash
# Via Google Cloud Console:
# Monitoring > Alerting > Create Policy
# Metric: Secret Manager Secret Access
# Condition: Access from unexpected IP or service account
```

---

## Cost

Google Secret Manager pricing (as of 2025):

- **Secret versions**: $0.06 per month per active version
- **Access operations**: $0.03 per 10,000 operations

For this project (3 secrets):
- **Storage**: ~$0.18/month
- **Access**: ~$0.03/month (assuming 10K accesses)
- **Total**: ~$0.21/month

Negligible compared to the security benefits!

---

## Migration from .env Files

If you previously had `.env` files on the VM:

### 1. Backup existing secrets

```bash
cd ~/jobmatch-ai/backend
cat .env | grep -E '(JWT_SECRET|DATABASE_URL|OPENAI_API_KEY)' > secrets-backup.txt
```

### 2. Add to Secret Manager

```bash
# Extract and add each secret
JWT_SECRET=$(grep JWT_SECRET secrets-backup.txt | cut -d'=' -f2)
echo -n "$JWT_SECRET" | gcloud secrets versions add jobmatch-jwt-secret \
  --project=futurelink-private-112912460 \
  --data-file=-

# Repeat for other secrets...
```

### 3. Remove secrets from .env

```bash
sed -i '/JWT_SECRET=/d' .env
sed -i '/DATABASE_URL=/d' .env
sed -i '/OPENAI_API_KEY=/d' .env
```

### 4. Update NODE_ENV

```bash
echo "NODE_ENV=production" >> .env
```

### 5. Restart services

```bash
pm2 restart all
```

---

## Additional Resources

- [Google Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Best Practices for Secrets](https://cloud.google.com/secret-manager/docs/best-practices)
- [Secret Manager Client Libraries](https://cloud.google.com/secret-manager/docs/reference/libraries)

---

**Remember**: Protecting secrets = Protecting kittens 🐱💖

Last updated: 2025-10-25
