# Version Usage Documentation

This document tracks where version information is used throughout the Altidus application.

## Current Version
**4.5.3** - Advanced Risk Metrics & Enhanced Ticker Comparison

## Version File Location
- **Central Version File**: `/VERSION` (root directory)
- **Version Format**: Semantic versioning (MAJOR.MINOR.PATCH)

## Version Usage Locations

### 1. Frontend (React Application)

#### Frontend Package Configuration
- **File**: `frontend/package.json`
- **Line**: 4
- **Usage**: `"version": "4.5.3"`
- **Purpose**: NPM package version for frontend application

#### Frontend Package Lock
- **File**: `frontend/package-lock.json`
- **Lines**: 3, 4, 9
- **Usage**: Version references in lockfile
- **Purpose**: Dependency version locking

#### Frontend Sidebar Display
- **File**: `frontend/src/components/layout/Sidebar.tsx`
- **Lines**: 98-100
- **Usage**: Hardcoded version badge in sidebar
- **Code**:
  ```tsx
  <span className="inline-flex items-center justify-center px-2 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-800 whitespace-nowrap">
    alpha 4.5.3
  </span>
  ```
- **Purpose**: User-visible version display in application sidebar (alpha format)

### 2. Backend (Python Application)

#### Backend Main Application
- **File**: `backend/main.py`
- **Lines**: 4, 84
- **Usage**: 
  - Docstring: `Version 4.5.3 - Advanced Risk Metrics & Enhanced Ticker Comparison`
  - Print statement: `print("🚀 Starting Portfolio Analysis Tool v4.5.3...")`
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
  - Header: `> **🚀 Version 4.5.3 - Advanced Risk Metrics & Enhanced Ticker Comparison**`
  - Footer: `Current version: 4.5.3 - **Advanced Risk Metrics & Enhanced Ticker Comparison**`
- **Purpose**: Documentation version display

#### Changelog
- **File**: `CHANGELOG.md`
- **Line**: 8
- **Usage**: `## [4.5.3] - 2025-01-27`
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
3. **`frontend/src/App.tsx`** - Sidebar version display (alpha format)
4. **`backend/main.py`** - Backend version references
5. **`README.md`** - Documentation version references
6. **`CHANGELOG.md`** - Version history entry

### Optional Updates
1. **`backend/api.py`** - API version (may remain independent)
2. **`frontend/package-lock.json`** - Will be updated automatically with `npm install`

## Version Consistency

### Current Status
- ✅ Frontend package.json: 4.5.3
- ✅ Frontend sidebar: alpha 4.5.3
- ✅ Backend main.py: 4.5.3
- ✅ README.md: 4.5.3
- ✅ CHANGELOG.md: 4.5.3
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

---

## Documentation & Version Management Updates (v4.5.1)

### Overview
This release focuses on comprehensive documentation updates, version management improvements, and system maintenance to ensure all documentation reflects the current state of the application.

### Version Management Enhancements

#### Automated Version Updates
- **Enhanced Script**: Improved `scripts/update_version.py` with better file detection and error handling
- **Cross-Platform Compatibility**: Better compatibility across different operating systems
- **File Validation**: Enhanced file validation and error reporting
- **Error Recovery**: Improved error handling and recovery mechanisms

#### Version Synchronization
- **Centralized Management**: All version references now use `/VERSION` as single source of truth
- **Consistent Updates**: Automated script ensures all files are updated consistently
- **Platform Support**: Better cross-platform support for version updates
- **File Detection**: Enhanced file detection logic for version updates

### Documentation System Updates

#### Comprehensive Documentation Updates
- **AI.MD Updates**: Updated technical overview to reflect v4.5.1 architecture and current system capabilities
- **ARCHITECTURE.md Refinement**: Enhanced architecture documentation with current system features and design patterns
- **BACKEND.MD Enhancement**: Updated backend documentation with current API endpoints and service architecture
- **FRONTEND.MD Updates**: Enhanced frontend documentation with current component structure and features
- **METRICS.MD Clarification**: Improved metric explanations and threshold descriptions for different investment mandates
- **STYLE.MD Simplification**: Updated design system documentation with simplified language and improved clarity
- **structure.md Enhancement**: Updated repository structure documentation with current features and capabilities

#### Version Management Documentation
- **VERSION_USAGE.md Updates**: Updated version usage documentation with current version references
- **Version History**: Maintained comprehensive changelog with detailed version information
- **Cross-Reference Updates**: All internal links and references updated to current structure

### Technical Implementation

#### Version Update Script Enhancements
- **Better File Detection**: Improved detection of files that need version updates
- **Error Handling**: Enhanced error handling and recovery mechanisms
- **Platform Compatibility**: Better cross-platform support for version updates
- **File Validation**: Enhanced file validation and error reporting

#### Documentation Architecture
- **Centralized Version Management**: All documentation now references v4.5.1 consistently
- **Modular Documentation**: Each documentation file focuses on specific aspects of the system
- **Cross-Reference Updates**: All internal links and references updated to current structure
- **Version History**: Maintained comprehensive changelog with detailed version information

### Benefits

#### Developer Experience
- **Consistent Documentation**: All documentation now reflects current system state
- **Better Maintenance**: Easier to maintain and update documentation
- **Version Clarity**: Clear version management and update process
- **Code Quality**: Improved code organization and maintainability

#### System Reliability
- **Documentation Accuracy**: Ensures documentation matches actual system capabilities
- **Version Consistency**: Prevents version-related confusion and errors
- **Maintainability**: Easier to maintain and extend the system
- **Quality Assurance**: Better documentation quality and consistency

### Evidence
- `scripts/update_version.py` - Enhanced version update script
- `CHANGELOG.md` - Comprehensive version history and changes
- `docs/` - Updated documentation files across all components
