# Quick Start - Backend Server

## Start the Server

### Option 1: Simple Script (Recommended)
```powershell
cd backend
.\start.ps1
```

### Option 2: Direct Command
```powershell
cd backend
$env:PYTHONPATH='E:\JobFinder'
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Option 3: From Project Root
```powershell
.\scripts\start-backend-only.ps1
```

## Test SEO Endpoint

Once server is running:
```powershell
curl http://localhost:8000/api/seo/status
```

## Troubleshooting

### If server won't start:
1. Make sure you're in the `backend` directory
2. Set `PYTHONPATH` to project root: `$env:PYTHONPATH='E:\JobFinder'`
3. Check for Python errors in the output

### If you see database errors:
- The SEO endpoints don't require database access
- Try the test server: `python test_seo_server.py`

### Common Issues:
- **Port 8000 already in use**: Stop other processes or change port
- **Import errors**: Make sure `PYTHONPATH` is set correctly
- **Credentials not found**: Check `.env` file exists in project root

## URLs

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health
- **SEO Status**: http://localhost:8000/api/seo/status

