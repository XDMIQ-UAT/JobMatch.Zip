# Setup SES configuration on VM for info@jobmatch.zip

param(
    [string]$VmName = "jobmatch-vm",
    [string]$Zone = "us-central1-a",
    [string]$FromEmail = "info@jobmatch.zip",
    [string]$SesRegion = "us-west-2"
)

Write-Host "🔧 Setting up SES configuration on VM..." -ForegroundColor Cyan
Write-Host ""

# Prompt for AWS credentials
Write-Host "Enter AWS SES credentials:" -ForegroundColor Yellow
$awsAccessKey = Read-Host "AWS Access Key ID"
$awsSecretKey = Read-Host "AWS Secret Access Key" -AsSecureString
$awsSecretPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($awsSecretKey)
)

Write-Host ""
Write-Host "📝 Updating .env file on VM..." -ForegroundColor Cyan

# Create update script
$updateScript = @"
cd /opt/jobmatch

# Remove existing SES config lines
sed -i '/^EMAIL_PROVIDER_MODE=/d' .env
sed -i '/^SES_FROM_EMAIL=/d' .env
sed -i '/^AWS_ACCESS_KEY_ID=/d' .env
sed -i '/^AWS_SECRET_ACCESS_KEY=/d' .env
sed -i '/^SES_REGION=/d' .env
sed -i '/^AWS_REGION=/d' .env

# Add new SES configuration
echo "" >> .env
echo "# Amazon SES Configuration" >> .env
echo "EMAIL_PROVIDER_MODE=ses" >> .env
echo "SES_FROM_EMAIL=$FromEmail" >> .env
echo "AWS_ACCESS_KEY_ID=$awsAccessKey" >> .env
echo "AWS_SECRET_ACCESS_KEY=$awsSecretPlain" >> .env
echo "SES_REGION=$SesRegion" >> .env
echo "AWS_REGION=$SesRegion" >> .env

echo "✅ Updated .env file"
cat .env | grep -E 'EMAIL_PROVIDER_MODE|SES_FROM_EMAIL|AWS_ACCESS_KEY_ID|SES_REGION' | sed 's/=.*/=***HIDDEN***/'
"@

gcloud compute ssh $VmName --zone=$Zone --command="$updateScript" 2>&1

Write-Host ""
Write-Host "🔄 Restarting application container..." -ForegroundColor Cyan
gcloud compute ssh $VmName --zone=$Zone --command="cd /opt/jobmatch && docker compose restart app" 2>&1 | Select-Object -Last 5

Write-Host ""
Write-Host "✅ SES configuration updated!" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  Next steps:" -ForegroundColor Yellow
Write-Host "  1. Verify $FromEmail in AWS SES Console" -ForegroundColor White
Write-Host "  2. Request production access if needed" -ForegroundColor White
Write-Host "  3. Test email sending from the application" -ForegroundColor White
Write-Host ""
Write-Host "📝 See docs/SES_TROUBLESHOOTING.md for troubleshooting" -ForegroundColor Cyan

