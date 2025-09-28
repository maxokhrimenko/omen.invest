# Portfolio Analysis Tool - Backend

## Overview

This is the backend component of the Portfolio Analysis Tool, providing financial analysis capabilities through a REST API built with FastAPI and clean architecture implementation.

## Architecture

The backend follows Clean Architecture principles with clear separation of concerns:

- **Domain Layer**: Core business logic and entities
- **Application Layer**: Use cases and business workflows  
- **Infrastructure Layer**: External systems and data access
- **Presentation Layer**: REST API controllers

## Quick Start

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# From the backend directory
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Or use the provided run script from the project root:
```bash
# From the project root
./local/run.sh backend
```

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/
```

## Directory Structure

```
backend/
├── src/                          # Source code
│   ├── domain/                   # Domain layer
│   │   ├── entities/             # Business entities
│   │   └── value_objects/        # Value objects
│   ├── application/              # Application layer
│   │   ├── use_cases/            # Business use cases
│   │   └── interfaces/           # Repository interfaces
│   ├── infrastructure/           # Infrastructure layer
│   │   ├── repositories/         # Data access
│   │   ├── logging/              # Logging system
│   │   ├── warehouse/            # Caching system
│   │   └── config/               # Configuration
│   └── presentation/             # Presentation layer
│       └── controllers/          # API Controllers
├── tests/                        # Test suite
├── admin/                        # Administrative tools
├── logs/                         # Application logs
├── input/                        # Input data files (moved to root)
├── api.py                        # FastAPI application entry point
└── requirements.txt              # Dependencies
```

## Configuration

### Environment Variables

- `WAREHOUSE_ENABLED`: Enable/disable warehouse caching (default: true)
- `WAREHOUSE_DB_PATH`: Path to warehouse database (default: ../database/warehouse/warehouse.sqlite)

### Logging

Logs are stored in the `logs/` directory:
- `logs/sessions/`: Session-specific logs
- `logs/total/`: All logs across sessions

## Features

- **Portfolio Analysis**: Financial metrics calculation
- **Ticker Analysis**: Individual stock analysis with dividend calculations
- **Warehouse Caching**: Performance improvement for repeated requests
- **Data Validation**: Missing data detection and reporting
- **Color-Coded Metrics**: Visual performance indicators
- **Logging**: Operation tracking

## Development

### Adding New Features

1. Follow Clean Architecture principles
2. Add new use cases in `src/application/use_cases/`
3. Implement repository interfaces in `src/infrastructure/repositories/`
4. Add tests for new functionality
5. Update documentation

### Code Quality

- Follow PEP 8 style guidelines
- Write tests
- Use type hints
- Document public APIs

## Documentation

- [Architecture Documentation](../docs/ARCHITECTURE.md)
- [AI Documentation](../docs/AI.MD)
- [Metrics Memorandum](../docs/METRICS_MEMORANDUM.md)

## API Endpoints

The backend provides a comprehensive REST API:

- **Portfolio Management**: Upload, retrieve, and clear portfolios
- **Analysis**: Portfolio analysis and individual ticker analysis
- **Comparison**: Ticker comparison functionality
- **Administration**: Warehouse management and statistics
- **Health Check**: Service health monitoring

### API Documentation

When running the application, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the backend directory
2. **Database Issues**: Check warehouse database path configuration
3. **Logging Issues**: Verify logs directory permissions

### Getting Help

- Check the logs in `logs/total/application.log`
- Review the architecture documentation
- Run tests to verify functionality

---

*This backend component is part of the full-stack Portfolio Analysis Tool v4.1.2*
