# Scripts Directory

This directory contains utility scripts for managing the Omen Invest application.

## Version Management

### `update_version.py`

A script to manage version updates across the entire application.

#### Usage

```bash
# Check current version
python3 scripts/update_version.py

# Update to a new version
python3 scripts/update_version.py 4.4.1
```

#### What it does

1. **Reads/Writes Version**: Manages the central `/VERSION` file
2. **Updates References**: Automatically updates version in:
   - `frontend/package.json` - Frontend package version
   - `frontend/src/App.tsx` - Sidebar version display
   - `backend/main.py` - Backend version references
   - `README.md` - Documentation version references
3. **Updates Changelog**: Adds new version entry to `CHANGELOG.md`

#### Version Format

Uses semantic versioning: `MAJOR.MINOR.PATCH` (e.g., `4.3.0`)

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

#### Examples

```bash
# Patch version (bug fixes)
python3 scripts/update_version.py 4.3.1

# Minor version (new features)
python3 scripts/update_version.py 4.4.1

# Major version (breaking changes)
python3 scripts/update_version.py 5.0.0
```

## Version Consistency

The script ensures all version references are kept in sync:

- ✅ Frontend package.json
- ✅ Frontend sidebar display
- ✅ Backend main application
- ✅ README documentation
- ✅ Changelog entries

## Manual Version Updates

If you need to update versions manually, see `/VERSION_USAGE.md` for a complete list of files that contain version references.
