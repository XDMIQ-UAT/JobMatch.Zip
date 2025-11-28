# JobMatch CLI - Quick Setup Reference

## 🚀 Current Status
✅ Package built and validated  
✅ Distribution files ready  
✅ GitHub Actions configured  

## 📦 One-Command Test Install

```powershell
cd E:\JobFinder
pip install -e .
```

Then test it:
```powershell
$env:JOBMATCH_USER_ID="test-user"
$env:JOBMATCH_SESSION_ID="test-session"
$env:DATABASE_URL="postgresql://user:pass@localhost/jobmatch"
$env:REDIS_HOST="localhost"

jobmatch-cli
```

## 🏷️ Release to GitHub (3 commands)

```powershell
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
# Then create release on GitHub web interface
```

## 🌐 PyPI Setup (One-Time)

1. Go to https://pypi.org/manage/account/publishing/
2. Add pending publisher:
   - Owner: `XDM-ZSBW`
   - Repo: `jobmatch-ai`
   - Workflow: `publish-to-pypi.yml`

## 📤 Manual Publish (Alternative)

```powershell
# Test first
python -m twine upload --repository testpypi dist/*

# Then real PyPI
python -m twine upload dist/*
```

## 🔄 Update Package

```powershell
# 1. Edit version in setup.py and pyproject.toml
# 2. Clean and rebuild
Remove-Item -Recurse -Force dist/
python -m build
python -m twine check dist/*
# 3. Create new GitHub release
```

## 📋 Files Structure

```
E:\JobFinder\
├── backend\
│   └── jobmatch_cli.py        # Main CLI (already exists)
├── setup.py                    # Package config ✓
├── pyproject.toml              # Modern config ✓
├── MANIFEST.in                 # Package data ✓
├── dist\
│   ├── jobmatch_cli-0.1.0.tar.gz           ✓
│   └── jobmatch_cli-0.1.0-py3-none-any.whl ✓
└── .github\workflows\
    └── publish-to-pypi.yml     # Auto-publish ✓
```

## 🎯 What Users Will Do

After you publish to PyPI:

```bash
pip install jobmatch-cli
jobmatch-cli  # Ready to use!
```

## 📚 Full Documentation

See `docs/PYPI_SETUP.md` for complete guide.

## ⚡ Next Action

**Choose one**:
- Test locally: `pip install -e .`
- Publish to PyPI: Set up trusted publishing → Create GitHub release
- Manual publish: `twine upload dist/*`

---

**Package**: `jobmatch-cli`  
**Version**: `0.1.0`  
**Status**: ✅ Ready  
**Install**: `pip install jobmatch-cli` (after publishing)
