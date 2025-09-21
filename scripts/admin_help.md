# 🔧 Administrative Scripts Usage Guide

## Overview

This guide shows how to use the administrative scripts with the new full-stack repository structure.

## 📁 Script Locations

- **Logs Clear Script**: `backend/admin/logs_clear.py`
- **Warehouse Clear Script**: `backend/admin/clear_warehouse.py`

## 🚀 Usage Examples

### From Root Directory

```bash
# Show log statistics
python3 backend/admin/logs_clear.py --stats

# Clear all logs
python3 backend/admin/logs_clear.py --clear-all

# Show warehouse statistics
python3 backend/admin/clear_warehouse.py --stats

# Clear all warehouse data
python3 backend/admin/clear_warehouse.py --clear-all
```

### From Backend Directory

```bash
cd backend

# Show log statistics
python3 admin/logs_clear.py --stats

# Clear all logs
python3 admin/logs_clear.py --clear-all

# Show warehouse statistics
python3 admin/clear_warehouse.py --stats

# Clear all warehouse data
python3 admin/clear_warehouse.py --clear-all
```

## 📊 Available Commands

### Logs Clear Script (`logs_clear.py`)

- `--stats` - Show log statistics
- `--clear-sessions` - Clear session logs only
- `--clear-total` - Clear total logs only
- `--clear-all` - Clear all logs
- `--backup-and-clear` - Create backup and clear all logs
- `--force` - Skip confirmation prompts

### Warehouse Clear Script (`clear_warehouse.py`)

- `--stats` - Show warehouse statistics
- `--clear-all` - Clear all warehouse data
- `--clear-ticker TICKER` - Clear data for specific ticker
- `--backup-and-clear` - Create backup and clear all data
- `--backup` - Create backup only
- `--restore BACKUP_FILE` - Restore from backup
- `--list-backups` - List available backups
- `--reset-metrics` - Reset warehouse metrics

## ⚠️ Important Notes

1. **Run from Root Directory**: Always run scripts from the project root directory
2. **Confirmation Prompts**: Most destructive operations require confirmation
3. **Backup First**: Consider creating backups before clearing data
4. **Path Updates**: Scripts now use the new directory structure:
   - Logs: `backend/logs/`
   - Warehouse: `database/warehouse/warehouse.sqlite`

## 🔄 Version 4.1.2 Changes

- Updated default paths to reflect new repository structure
- Updated usage examples in help text
- Added version information to script headers
- Maintained all existing functionality

---

*This guide is part of the Portfolio Analysis Tool v4.1.2 - Full-Stack Repository Restructure*
