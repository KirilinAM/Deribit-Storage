# Deribit Storage

Cryptocurrency price tracking from Deribit exchange with REST API.

## Overview

Deribit Storage is a Python-based application that:
1. Fetches BTC/USD and ETH/USD index prices from Deribit exchange every minute
2. Stores prices in PostgreSQL database with timestamps
3. Provides REST API with authentication to query stored data
4. Runs in Docker containers with CI/CD pipeline

## Features

- **Real-time price fetching**: BTC/USD and ETH/USD prices every minute
- **REST API**: FastAPI with OpenAPI/Swagger documentation
- **Authentication**: Client credentials authentication
- **Rate limiting**: Configurable rate limiting per client
- **Structured logging**: JSON logging with structlog
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Task queue**: Celery with Redis broker for periodic tasks
- **Containerized**: Docker Compose for easy deployment
- **CI/CD**: GitHub Actions for automated testing and deployment

## Architecture

The application uses a microservices architecture with 4 containers:
1. **FastAPI** - REST API service (port 8000)
2. **Celery Worker** - Periodic price fetching (every minute)
3. **Redis** - Message broker for Celery
4. **PostgreSQL** - Database for price history

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Git

### 1. Clone the repository

```bash
git clone <repository-url>
cd deribit-storage
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start with Docker Compose

```bash
docker-compose up -d
```

### 4. Access the application

- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- ReDoc Documentation: http://localhost:8000/redoc

## API Endpoints

All endpoints require authentication via `X-Client-ID` and `X-Client-Secret` headers.

### GET /api/v1/prices
Get all prices for a ticker with pagination.

**Query Parameters:**
- `ticker` (required): Cryptocurrency pair (btc_usd or eth_usd)
- `limit` (optional): Number of results per page (default: 100)
- `offset` (optional): Pagination offset (default: 0)

### GET /api/v1/prices/latest
Get the latest price for a ticker.

**Query Parameters:**
- `ticker` (required): Cryptocurrency pair (btc_usd or eth_usd)

### GET /api/v1/prices/filter
Get prices filtered by date range.

**Query Parameters:**
- `ticker` (required): Cryptocurrency pair (btc_usd or eth_usd)
- `start_date` (optional): Start date (UNIX timestamp or ISO format)
- `end_date` (optional): End date (UNIX timestamp or ISO format)

### GET /health
Health check endpoint.

## Development

### Set up development environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run database migrations
alembic upgrade head

# Run tests
pytest

# Start development server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Start Celery worker (in separate terminal)
celery -A src.worker.tasks worker --loglevel=info
```

### Project Structure

```
deribit-storage/
├── src/
│   ├── api/                    # FastAPI application
│   │   ├── main.py            # FastAPI app instance
│   │   ├── routers/           # API endpoints
│   │   ├── dependencies/      # FastAPI dependencies
│   │   ├── middleware/        # Custom middleware
│   │   └── schemas/           # Pydantic models
│   ├── worker/                # Celery worker
│   │   ├── tasks.py           # Celery tasks
│   │   ├── deribit_client.py  # Deribit API client
│   │   └── models.py          # SQLAlchemy models
│   ├── core/                  # Shared core functionality
│   │   ├── config.py          # Configuration
│   │   ├── database.py        # Database connection
│   │   ├── logging.py         # Logging setup
│   │   └── security.py        # Security utilities
│   └── tests/                 # Test suite
├── docker/                    # Docker configuration
├── .github/workflows/        # GitHub Actions
├── migrations/               # Database migrations
├── .env.example              # Environment template
├── docker-compose.yml        # Local development
├── pyproject.toml           # Python project config
└── README.md                # Project documentation
```

## Design Decisions

### Technology Choices

1. **FastAPI**: Chosen for its excellent performance, automatic OpenAPI documentation, and async support.
2. **PostgreSQL**: Selected for ACID compliance and excellent performance with time-series data.
3. **Celery**: Used for robust task scheduling with built-in retry mechanisms.
4. **aiohttp**: Async HTTP client for non-blocking API calls to Deribit.
5. **SQLAlchemy 2.0**: Modern ORM with async support and type hints.
6. **Pydantic**: Data validation and settings management.
7. **Structlog**: Structured JSON logging for better log aggregation.
8. **Tenacity**: Retry logic with exponential backoff for API calls.

### Architecture Decisions

1. **Microservices**: Separate containers for API, worker, Redis, and PostgreSQL for independent scaling.
2. **Environment-based authentication**: Client credentials stored in environment variables (not database) for simplicity.
3. **Structured logging**: JSON format for machine-readable logs and better integration with log collectors.
4. **Containerization**: Docker Compose for consistent development and production environments.
5. **HTTP over WebSockets**: HTTP REST API used for Deribit instead of WebSockets for simpler 1-minute polling.

## Deployment

### Docker Compose

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Considerations

1. **Environment variables**: Set production values in `.env` file or container environment.
2. **Database backups**: Configure regular PostgreSQL backups.
3. **Monitoring**: Set up monitoring for application metrics and logs.
4. **Security**: Use HTTPS in production, rotate credentials regularly.
5. **Scaling**: Adjust container resources based on load.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest src/tests/test_api.py -v
```

## License

MIT License - see LICENSE file for details.

## Contact

Author: kirilinartem@yandex.ru