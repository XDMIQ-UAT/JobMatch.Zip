# JobMatch CLI - PyPI Publishing Guide

## Status: ✅ Ready for Publishing

Your package is fully configured and built successfully. All checks passed!

## What's Already Done

✅ **Package Configuration**
- `setup.py` with proper metadata
- `pyproject.toml` for modern Python packaging
- `MANIFEST.in` for package data
- Entry point: `jobmatch-cli` command

✅ **Build Files Created**
- Source distribution: `dist/jobmatch_cli-0.1.0.tar.gz`
- Wheel distribution: `dist/jobmatch_cli-0.1.0-py3-none-any.whl`
- Both validated with `twine check` ✓

✅ **GitHub Actions Workflow**
- `.github/workflows/publish-to-pypi.yml` configured
- Supports automated PyPI publishing on releases
- Uses trusted publishing (no manual credentials)

## Next Steps

### 1. Set Up PyPI Trusted Publishing

Before creating a release, configure trusted publishing (no API tokens needed):

1. **Go to PyPI**:
   - Visit https://pypi.org/ (or https://test.pypi.org/ for testing)
   - Register/login to your account

2. **Register the package name**:
   - Click "Your projects"
   - Click "Publishing" tab
   - Add a new "pending publisher"
   - Repository owner: `XDM-ZSBW`
   - Repository name: `jobmatch-ai`
   - Workflow name: `publish-to-pypi.yml`
   - Environment name: (leave blank)

### 2. Test Locally (Optional but Recommended)

Install the package locally to test:

```powershell
# Install in development mode
cd E:\JobFinder
pip install -e .

# Test the CLI
jobmatch-cli
```

### 3. Create GitHub Release

```powershell
# Make sure all changes are committed
git add .
git commit -m "chore: prepare v0.1.0 release"
git push

# Create and push tag
git tag -a v0.1.0 -m "Release v0.1.0: Initial JobMatch CLI"
git push origin v0.1.0
```

Then go to GitHub → Releases → Create new release:
- Tag: `v0.1.0`
- Title: `JobMatch CLI v0.1.0`
- Description: See template below
- Attach: `dist/jobmatch_cli-0.1.0-py3-none-any.whl`

**Release Description Template**:
```markdown
# JobMatch CLI v0.1.0

Terminal-based capability matching interface for JobMatch.zip paid beta users.

## Features
- 🎯 3-step capability assessment
- 💬 Interactive terminal interface
- 🔄 Session state persistence
- 📊 Real-time matching status
- ⭐ Session feedback system

## Installation

```bash
pip install jobmatch-cli
```

## Usage

```bash
# Set environment variables
export JOBMATCH_USER_ID="your-user-id"
export JOBMATCH_SESSION_ID="your-session-id"
export DATABASE_URL="postgresql://..."
export REDIS_HOST="localhost"

# Run CLI
jobmatch-cli
```

## What's New
- Initial release
- Core capability matching workflow
- Database and Redis integration
- Session management

## Requirements
- Python 3.8+
- PostgreSQL database
- Redis server
```

### 4. GitHub Actions Will Auto-Publish

Once you create the GitHub release:
1. GitHub Actions workflow triggers automatically
2. Builds the package
3. Publishes to PyPI (if trusted publishing is configured)
4. Uploads wheel to GitHub release assets

### 5. Verify on PyPI

After publishing:
- Check https://pypi.org/project/jobmatch-cli/
- Test installation: `pip install jobmatch-cli`

## Manual Publishing (Alternative)

If you prefer manual publishing or want to test first:

```powershell
# Test on TestPyPI first (recommended)
python -m twine upload --repository testpypi dist/*

# Then publish to real PyPI
python -m twine upload dist/*
```

**Note**: You'll need a PyPI API token for manual uploads. Get it from:
- https://pypi.org/manage/account/token/

## Updating the Package

For future releases:

```powershell
# 1. Update version in setup.py and pyproject.toml
# 2. Clean old builds
Remove-Item -Recurse -Force dist/

# 3. Rebuild
python -m build

# 4. Check
python -m twine check dist/*

# 5. Create new GitHub release with new tag (e.g., v0.2.0)
```

## Package URLs

- **PyPI**: https://pypi.org/project/jobmatch-cli/ (once published)
- **GitHub**: https://github.com/XDM-ZSBW/jobmatch-ai
- **Install**: `pip install jobmatch-cli`

## Troubleshooting

### Build Warnings
You may see deprecation warnings about:
- `project.license` format (cosmetic, doesn't affect functionality)
- License classifiers (cosmetic, doesn't affect functionality)

These don't prevent publishing but can be fixed in future releases.

### Trusted Publishing Fails
If automatic publishing fails:
1. Verify trusted publisher is configured on PyPI
2. Check GitHub Actions logs for errors
3. Use manual publishing as fallback

### Import Errors After Install
Make sure the package structure matches:
```
backend/
  └── jobmatch_cli.py  # Main CLI file
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/XDM-ZSBW/jobmatch-ai/issues
- Email: contact@jobmatch.zip

---

**Current Status**: ✅ Package built and validated. Ready for GitHub release!
