#!/usr/bin/env python3
"""
Version Update Script for Altidus Application

This script reads the version from the central VERSION file and updates
all version references throughout the application.

Usage:
    python scripts/update_version.py [new_version]
    
If no version is provided, it will read from VERSION file and display current version.
If a new version is provided, it will update VERSION file and all references.
"""

import os
import re
import sys
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Version file path
VERSION_FILE = PROJECT_ROOT / "VERSION"

# Files that contain version references
VERSION_FILES = {
    "frontend/package.json": {
        "pattern": r'"version":\s*"[^"]*"',
        "replacement": '"version": "{}"',
        "description": "Frontend package version"
    },
    "frontend/src/App.tsx": {
        "pattern": r'v\d+\.\d+\.\d+',
        "replacement": 'v{}',
        "description": "Frontend sidebar version display"
    },
    "backend/main.py": {
        "pattern": r'Version \d+\.\d+\.\d+',
        "replacement": 'Version {}',
        "description": "Backend main application version"
    },
    "backend/main.py": {
        "pattern": r'v\d+\.\d+\.\d+',
        "replacement": 'v{}',
        "description": "Backend startup message version"
    },
    "README.md": {
        "pattern": r'Version \d+\.\d+\.\d+',
        "replacement": 'Version {}',
        "description": "README version references"
    }
}

def read_version():
    """Read version from VERSION file."""
    try:
        with open(VERSION_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: VERSION file not found at {VERSION_FILE}")
        sys.exit(1)

def write_version(version):
    """Write version to VERSION file."""
    with open(VERSION_FILE, 'w') as f:
        f.write(version)

def update_file_version(file_path, version, pattern, replacement, description):
    """Update version in a specific file."""
    full_path = PROJECT_ROOT / file_path
    
    if not full_path.exists():
        print(f"Warning: {file_path} not found, skipping...")
        return False
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if pattern exists
        if not re.search(pattern, content):
            print(f"Warning: No version pattern found in {file_path}")
            return False
        
        # Replace version
        new_content = re.sub(pattern, replacement.format(version), content)
        
        if new_content != content:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Updated {file_path} - {description}")
            return True
        else:
            print(f"ℹ️  No changes needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def update_all_versions(version):
    """Update version in all tracked files."""
    print(f"Updating version to {version}...")
    print("=" * 50)
    
    updated_files = 0
    
    for file_path, config in VERSION_FILES.items():
        if update_file_version(file_path, version, config["pattern"], config["replacement"], config["description"]):
            updated_files += 1
    
    print("=" * 50)
    print(f"Updated {updated_files} files")
    
    # Update CHANGELOG.md with new version entry
    update_changelog(version)

def update_changelog(version):
    """Add new version entry to CHANGELOG.md."""
    changelog_path = PROJECT_ROOT / "CHANGELOG.md"
    
    if not changelog_path.exists():
        print("Warning: CHANGELOG.md not found, skipping...")
        return
    
    try:
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if version already exists
        if f"## [{version}]" in content:
            print("ℹ️  Version already exists in CHANGELOG.md")
            return
        
        # Add new version entry after the first line
        lines = content.split('\n')
        new_entry = [
            "",
            f"## [{version}] - {get_current_date()}",
            "",
            "### ✨ Added",
            "- [Add new features here]",
            "",
            "### 🔄 Changed", 
            "- [Add changes here]",
            "",
            "### 🐛 Fixed",
            "- [Add bug fixes here]",
            ""
        ]
        
        # Insert after the first line (title)
        lines[1:1] = new_entry
        
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print("✅ Updated CHANGELOG.md with new version entry")
        
    except Exception as e:
        print(f"Error updating CHANGELOG.md: {e}")

def get_current_date():
    """Get current date in YYYY-MM-DD format."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")

def validate_version(version):
    """Validate version format (semantic versioning)."""
    pattern = r'^\d+\.\d+\.\d+$'
    if not re.match(pattern, version):
        print(f"Error: Invalid version format '{version}'. Expected format: MAJOR.MINOR.PATCH (e.g., 1.0.0)")
        return False
    return True

def main():
    """Main function."""
    if len(sys.argv) > 1:
        new_version = sys.argv[1]
        
        if not validate_version(new_version):
            sys.exit(1)
        
        print(f"Updating version from {read_version()} to {new_version}")
        write_version(new_version)
        update_all_versions(new_version)
        print(f"\n🎉 Version successfully updated to {new_version}")
        
    else:
        current_version = read_version()
        print(f"Current version: {current_version}")
        print("\nTo update version, run:")
        print(f"python scripts/update_version.py <new_version>")
        print("\nExample:")
        print(f"python scripts/update_version.py 4.4.3")

if __name__ == "__main__":
    main()
