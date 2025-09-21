# 🏗️ Repository Structure - Full-Stack Portfolio Analysis Tool

## Overview

This document outlines the new repository structure designed to support a full-stack application with backend, frontend, and database components. The current backend-only structure is being reorganized to accommodate future frontend development while maintaining all existing functionality.

## 🎯 Design Principles

- **Separation of Concerns**: Clear boundaries between backend, frontend, and database
- **Scalability**: Structure supports independent development and deployment
- **Maintainability**: Clean organization with logical grouping
- **Backward Compatibility**: Existing backend functionality preserved
- **Future-Ready**: Prepared for frontend and additional services

## 📁 New Repository Structure

```
omen.invest/
├── 📁 backend/                          # Backend API and Services
│   ├── 📁 src/                          # Backend source code
│   │   ├── 📁 domain/                   # Domain layer (Clean Architecture)
│   │   │   ├── 📁 entities/             # Business entities
│   │   │   │   ├── __init__.py
│   │   │   │   ├── portfolio.py
│   │   │   │   ├── position.py
│   │   │   │   └── ticker.py
│   │   │   ├── 📁 value_objects/        # Immutable value types
│   │   │   │   ├── __init__.py
│   │   │   │   ├── date_range.py
│   │   │   │   ├── money.py
│   │   │   │   └── percentage.py
│   │   │   └── __init__.py
│   │   ├── 📁 application/              # Application layer
│   │   │   ├── 📁 use_cases/            # Business use cases
│   │   │   │   ├── __init__.py
│   │   │   │   ├── analyze_portfolio.py
│   │   │   │   ├── analyze_ticker.py
│   │   │   │   ├── compare_tickers.py
│   │   │   │   └── load_portfolio.py
│   │   │   ├── 📁 interfaces/           # Repository interfaces
│   │   │   │   ├── __init__.py
│   │   │   │   ├── metrics_color_service.py
│   │   │   │   └── repositories.py
│   │   │   └── __init__.py
│   │   ├── 📁 infrastructure/           # Infrastructure layer
│   │   │   ├── 📁 config/               # Configuration management
│   │   │   │   ├── __init__.py
│   │   │   │   └── warehouse_config.py
│   │   │   ├── 📁 logging/              # Logging system
│   │   │   │   ├── __init__.py
│   │   │   │   ├── decorators.py
│   │   │   │   └── logger_service.py
│   │   │   ├── 📁 repositories/         # Data access implementations
│   │   │   │   ├── __init__.py
│   │   │   │   ├── csv_portfolio_repository.py
│   │   │   │   ├── warehouse_market_repository.py
│   │   │   │   └── yfinance_market_repository.py
│   │   │   ├── 📁 warehouse/            # Warehouse system
│   │   │   │   ├── __init__.py
│   │   │   │   ├── trading_day_service.py
│   │   │   │   └── warehouse_service.py
│   │   │   ├── color_metrics_service.py
│   │   │   └── table_formatter.py
│   │   ├── 📁 presentation/             # Presentation layer
│   │   │   ├── 📁 cli/                  # CLI interface
│   │   │   │   ├── __init__.py
│   │   │   │   └── menu.py
│   │   │   ├── 📁 controllers/          # Application controllers
│   │   │   │   ├── __init__.py
│   │   │   │   └── portfolio_controller.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── 📁 tests/                        # Backend tests
│   │   ├── 📁 unit/                     # Unit tests
│   │   │   ├── __init__.py
│   │   │   ├── test_entities.py
│   │   │   └── test_value_objects.py
│   │   ├── 📁 integration/              # Integration tests
│   │   │   ├── __init__.py
│   │   │   └── test_portfolio_analysis.py
│   │   └── __init__.py
│   ├── 📁 admin/                        # Administrative tools
│   │   ├── __init__.py
│   │   ├── clear_warehouse.py
│   │   └── logs_clear.py
│   ├── 📁 logs/                         # Backend logs
│   │   ├── 📁 sessions/                 # Session-specific logs
│   │   └── 📁 total/                    # All logs across sessions
│   ├── 📁 input/                        # Input data files (moved to root)
│   ├── main.py                          # Backend entry point
│   ├── requirements.txt                 # Backend dependencies
│   └── README.md                        # Backend documentation
├── 📁 frontend/                         # Frontend Application (Future)
│   ├── 📁 src/                          # Frontend source code
│   │   ├── 📁 components/               # React/Vue components
│   │   ├── 📁 pages/                    # Application pages
│   │   ├── 📁 services/                 # API services
│   │   ├── 📁 utils/                    # Utility functions
│   │   ├── 📁 assets/                   # Static assets
│   │   └── index.html                   # Main HTML file
│   ├── 📁 public/                       # Public static files
│   ├── 📁 tests/                        # Frontend tests
│   ├── package.json                     # Frontend dependencies
│   ├── package-lock.json               # Lock file
│   ├── vite.config.js                  # Build configuration
│   └── README.md                        # Frontend documentation
├── 📁 database/                         # Database and Data Storage
│   ├── 📁 warehouse/                    # SQLite warehouse database
│   │   ├── 📁 backups/                  # Database backups
│   │   │   └── warehouse_backup_20250921_172152.sqlite
│   │   └── warehouse.sqlite             # Main database file
│   ├── 📁 migrations/                   # Database migrations (Future)
│   ├── 📁 seeds/                        # Database seeds (Future)
│   └── README.md                        # Database documentation
├── 📁 shared/                           # Shared Resources
│   ├── 📁 types/                        # Shared TypeScript types
│   ├── 📁 schemas/                      # API schemas and contracts
│   ├── 📁 utils/                        # Shared utility functions
│   └── 📁 constants/                    # Shared constants
├── 📁 docs/                             # Documentation
│   ├── AI.MD                            # AI/LLM documentation
│   ├── ARCHITECTURE.md                  # Technical architecture
│   ├── METRICS_MEMORANDUM.md           # Financial metrics definitions
│   ├── structure.md                     # This file
│   └── README.md                        # Main project documentation
├── 📁 scripts/                          # Build and deployment scripts
│   ├── 📁 build/                        # Build scripts
│   ├── 📁 deploy/                       # Deployment scripts
│   └── 📁 dev/                          # Development scripts
├── 📁 input/                            # Input data files
│   ├── full.csv
│   └── test.csv
├── 📁 config/                           # Configuration files
│   ├── docker-compose.yml               # Docker configuration
│   ├── .env.example                     # Environment variables template
│   └── .gitignore                       # Git ignore rules
├── 📁 .github/                          # GitHub workflows (Future)
│   └── 📁 workflows/                    # CI/CD pipelines
├── .gitignore                           # Root gitignore
├── README.md                            # Main project README
├── CHANGELOG.md                         # Version history
└── LICENSE                              # Project license
```

## 🔄 Migration Strategy

### Phase 1: Backend Restructuring (Current)
- Move all existing backend code to `backend/` directory
- Update import paths to reflect new structure
- Ensure all functionality remains intact
- Update documentation references

### Phase 2: Frontend Preparation (Future)
- Create `frontend/` directory structure
- Set up build tools and dependencies
- Implement API integration layer

### Phase 3: Database Enhancement (Future)
- Move database files to `database/` directory
- Add migration system
- Implement backup strategies

### Phase 4: Shared Resources (Future)
- Create shared types and schemas
- Implement common utilities
- Set up API contracts

## 📋 Directory Responsibilities

### Backend (`/backend/`)
- **Purpose**: API services, business logic, and data processing
- **Technology**: Python with Clean Architecture
- **Entry Point**: `backend/main.py`
- **Dependencies**: `backend/requirements.txt`

### Frontend (`/frontend/`)
- **Purpose**: User interface and client-side application
- **Technology**: Modern web framework (React/Vue/Angular)
- **Entry Point**: `frontend/src/index.html`
- **Dependencies**: `frontend/package.json`

### Database (`/database/`)
- **Purpose**: Data storage, migrations, and backups
- **Technology**: SQLite (current), PostgreSQL (future)
- **Location**: `database/warehouse/`
- **Management**: Migration scripts and backup tools

### Shared (`/shared/`)
- **Purpose**: Common types, schemas, and utilities
- **Technology**: TypeScript/JavaScript
- **Usage**: Both frontend and backend
- **Maintenance**: Versioned and synchronized

### Documentation (`/docs/`)
- **Purpose**: Technical documentation and guides
- **Format**: Markdown files
- **Audience**: Developers and stakeholders
- **Maintenance**: Updated with code changes

## 🔧 Configuration Changes

### Import Path Updates
All Python imports will be updated to reflect the new structure:

```python
# Old imports
from src.presentation.cli.menu import MainMenu
from src.infrastructure.repositories.csv_portfolio_repository import CsvPortfolioRepository

# New imports
from backend.src.presentation.cli.menu import MainMenu
from backend.src.infrastructure.repositories.csv_portfolio_repository import CsvPortfolioRepository
```

### Path Configuration
- Update `sys.path.insert()` in `main.py`
- Modify relative imports throughout the codebase
- Update test discovery paths
- Adjust logging file paths

### Environment Variables
- `BACKEND_ROOT`: Path to backend directory
- `DATABASE_PATH`: Path to database files
- `LOG_PATH`: Path to log files
- `FRONTEND_URL`: Frontend application URL

## 🚀 Benefits of New Structure

### Development Benefits
- **Clear Separation**: Backend and frontend can be developed independently
- **Scalability**: Easy to add new services or components
- **Maintainability**: Logical organization makes code easier to find and modify
- **Team Collaboration**: Different teams can work on different parts

### Deployment Benefits
- **Independent Deployment**: Backend and frontend can be deployed separately
- **Containerization**: Each component can be containerized independently
- **Load Balancing**: Frontend and backend can be scaled independently
- **Monitoring**: Component-specific monitoring and logging

### Future Benefits
- **Microservices Ready**: Structure supports breaking into microservices
- **API-First**: Clear API boundaries between components
- **Testing**: Component-specific testing strategies
- **Documentation**: Clear documentation boundaries

## 📝 Implementation Notes

### File Moves Required
1. Move `src/` → `backend/src/`
2. Move `tests/` → `backend/tests/`
3. Move `admin/` → `backend/admin/`
4. Move `logs/` → `backend/logs/`
5. Move `input/` → `backend/input/`
6. Move `warehouse/` → `database/warehouse/`
7. Move `main.py` → `backend/main.py`
8. Move `requirements.txt` → `backend/requirements.txt`

### Import Updates Required
- Update all relative imports in Python files
- Modify `sys.path` configuration
- Update test discovery paths
- Adjust file path references in configuration

### Documentation Updates Required
- Update all file path references in documentation
- Modify README files to reflect new structure
- Update architecture diagrams
- Adjust development setup instructions

---

*This structure document reflects the reorganization for version 4.1.2 of the Portfolio Analysis Tool, transitioning from a backend-only application to a full-stack service.*
