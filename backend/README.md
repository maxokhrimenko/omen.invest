# 🚀 Portfolio Analysis Tool - Backend

## Overview

This is the backend component of the Portfolio Analysis Tool, providing comprehensive financial analysis capabilities through a clean architecture implementation.

## 🏗️ Architecture

The backend follows Clean Architecture principles with clear separation of concerns:

- **Domain Layer**: Core business logic and entities
- **Application Layer**: Use cases and business workflows  
- **Infrastructure Layer**: External systems and data access
- **Presentation Layer**: CLI interface and controllers

## 🚀 Quick Start

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
python main.py
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

## 📁 Directory Structure

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
│       ├── cli/                  # CLI interface
│       └── controllers/          # Controllers
├── tests/                        # Test suite
├── admin/                        # Administrative tools
├── logs/                         # Application logs
├── input/                        # Input data files (moved to root)
├── main.py                       # Application entry point
└── requirements.txt              # Dependencies
```

## 🔧 Configuration

### Environment Variables

- `WAREHOUSE_ENABLED`: Enable/disable warehouse caching (default: true)
- `WAREHOUSE_DB_PATH`: Path to warehouse database (default: ../database/warehouse/warehouse.sqlite)

### Logging

Logs are stored in the `logs/` directory:
- `logs/sessions/`: Session-specific logs
- `logs/total/`: All logs across sessions

## 📊 Features

- **Portfolio Analysis**: Comprehensive financial metrics calculation
- **Ticker Analysis**: Individual stock analysis with dividend calculations
- **Warehouse Caching**: 100x+ performance improvement for repeated requests
- **Data Validation**: Missing data detection and reporting
- **Color-Coded Metrics**: Visual performance indicators
- **Comprehensive Logging**: Detailed operation tracking

## 🛠️ Development

### Adding New Features

1. Follow Clean Architecture principles
2. Add new use cases in `src/application/use_cases/`
3. Implement repository interfaces in `src/infrastructure/repositories/`
4. Add tests for new functionality
5. Update documentation

### Code Quality

- Follow PEP 8 style guidelines
- Write comprehensive tests
- Use type hints
- Document public APIs

## 📚 Documentation

- [Architecture Documentation](../docs/ARCHITECTURE.md)
- [AI Documentation](../docs/AI.MD)
- [Metrics Memorandum](../docs/METRICS_MEMORANDUM.md)

## 🔄 API Integration

The backend is designed to support future API integration:

- RESTful endpoints (planned)
- WebSocket support (planned)
- Authentication (planned)
- Rate limiting (planned)

## 🐛 Troubleshooting

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
