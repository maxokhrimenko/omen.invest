# Version Usage Documentation

This document tracks where version information is used throughout the Altidus application.

## Current Version
**4.4.3** - Portfolio Analysis & Visualization

## Version File Location
- **Central Version File**: `/VERSION` (root directory)
- **Version Format**: Semantic versioning (MAJOR.MINOR.PATCH)

## Version Usage Locations

### 1. Frontend (React Application)

#### Frontend Package Configuration
- **File**: `frontend/package.json`
- **Line**: 4
- **Usage**: `"version": "4.4.3"`
- **Purpose**: NPM package version for frontend application

#### Frontend Package Lock
- **File**: `frontend/package-lock.json`
- **Lines**: 3, 4, 9
- **Usage**: Version references in lockfile
- **Purpose**: Dependency version locking

#### Frontend Sidebar Display
- **File**: `frontend/src/App.tsx`
- **Lines**: 381-384
- **Usage**: Hardcoded version badge in sidebar
- **Code**:
  ```tsx
  <span className="inline-flex items-center justify-center px-2 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-800 whitespace-nowrap">
    v4.4.3
  </span>
  ```
- **Purpose**: User-visible version display in application sidebar

### 2. Backend (Python Application)

#### Backend Main Application
- **File**: `backend/main.py`
- **Lines**: 4, 84
- **Usage**: 
  - Docstring: `Version 4.4.3 - Advanced Portfolio Analysis & Visualization`
  - Print statement: `print("🚀 Starting Portfolio Analysis Tool v4.4.3...")`
- **Purpose**: Application startup version display and documentation

#### Backend API
- **File**: `backend/api.py`
- **Line**: 63
- **Usage**: `version="1.0.0"`
- **Purpose**: FastAPI application version (different from main app version)

### 3. Documentation

#### Main README
- **File**: `README.md`
- **Lines**: 5, 425
- **Usage**:
  - Header: `> **🚀 Version 4.4.3 - Advanced Portfolio Analysis & Visualization**`
  - Footer: `Current version: 4.4.3 - **Advanced Portfolio Analysis & Visualization**`
- **Purpose**: Documentation version display

#### Changelog
- **File**: `CHANGELOG.md`
- **Line**: 8
- **Usage**: `## [4.4.3] - 2025-09-22`
- **Purpose**: Version history tracking

### 4. Development Scripts

#### Local Development Runner
- **File**: `local/run.sh`
- **Usage**: May contain version references (needs verification)
- **Purpose**: Development environment version display

## Version Update Process

When updating the version, the following files need to be updated:

### Required Updates
1. **`/VERSION`** - Central version file (single source of truth)
2. **`frontend/package.json`** - Frontend package version
3. **`frontend/src/App.tsx`** - Sidebar version display
4. **`backend/main.py`** - Backend version references
5. **`README.md`** - Documentation version references
6. **`CHANGELOG.md`** - Version history entry

### Optional Updates
1. **`backend/api.py`** - API version (may remain independent)
2. **`frontend/package-lock.json`** - Will be updated automatically with `npm install`

## Version Consistency

### Current Status
- ✅ Frontend package.json: 4.4.3
- ✅ Frontend sidebar: 4.4.3
- ✅ Backend main.py: 4.4.3
- ✅ README.md: 4.4.3
- ✅ CHANGELOG.md: 4.4.3
- ⚠️ Backend API: 1.0.0 (different versioning scheme)

### Recommendations
1. **Centralize Version Management**: Use `/VERSION` file as single source of truth
2. **Automate Updates**: Create script to update all version references
3. **API Versioning**: Consider aligning API version with main application version
4. **Version Display**: Ensure all user-facing version displays are consistent

## Future Improvements

### Automated Version Management
- Create script to read from `/VERSION` and update all references
- Add version validation to CI/CD pipeline
- Implement semantic versioning enforcement

### Version Display Enhancements
- Add version to API health check endpoint
- Include version in application logs
- Add version to frontend footer or about page

### Documentation
- Keep this file updated when adding new version references
- Document version update process in development guidelines
- Add version compatibility matrix for API versions
