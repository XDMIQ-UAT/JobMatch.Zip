# How to Set Up SSL on VM Using PowerShell (Windows)

## Step-by-Step Instructions

### Step 1: Open PowerShell

1. Press `Windows Key + X`
2. Click "Windows PowerShell" or "Terminal"
3. Or search for "PowerShell" in the Start menu

### Step 2: Navigate to Your Project Folder

```powershell
cd E:\JobFinder
```

### Step 3: Set Your GCP Project ID (Optional but Recommended)

```powershell
$env:GCP_PROJECT_ID = "your-actual-project-id"
```

Replace `your-actual-project-id` with your real Google Cloud project ID.

**Example:**
```powershell
$env:GCP_PROJECT_ID = "my-jobfinder-project-12345"
```

### Step 4: Run the Script

```powershell
.\scripts\setup-vm-ssl-from-bundle.ps1
```

That's it! The script will:
- Extract the SSL bundle from `secrets\jobmatch.zip-ssl-bundle.zip`
- Upload certificates to your VM
- Configure Nginx for HTTPS
- Delete the SSL bundle when done

## What If You Get an Error?

### Error: "Execution Policy"

If you see an error about execution policy, run this first:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try running the script again.

### Error: "Cannot find VM"

Make sure your VM exists and you're using the correct name:

```powershell
# Check your VM name
gcloud compute instances list
```

If your VM has a different name, set it:

```powershell
$env:VM_NAME = "your-vm-name"
.\scripts\setup-vm-ssl-from-bundle.ps1
```

### Error: "SSL bundle not found"

Make sure the SSL bundle file exists:

```powershell
# Check if file exists
Test-Path secrets\jobmatch.zip-ssl-bundle.zip
```

If it doesn't exist, you need to put your SSL bundle there first.

## Complete Example

Here's everything in one go:

```powershell
# 1. Go to project folder
cd E:\JobFinder

# 2. Set your project ID
$env:GCP_PROJECT_ID = "my-project-id"

# 3. Run the script
.\scripts\setup-vm-ssl-from-bundle.ps1
```

## After Running

The script will tell you:
- ✅ If everything worked
- 🌐 Your HTTPS URL (https://jobmatch.zip)
- 🔍 How to test it

Test it with:
```powershell
curl -I https://jobmatch.zip
```

Or open in your browser: `https://jobmatch.zip`

