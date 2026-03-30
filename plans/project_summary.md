# Deribit Storage - Complete Project Plan

## Project Overview
A Python-based microservices application that:
1. Fetches BTC/USD and ETH/USD index prices from Deribit exchange every minute
2. Stores prices in PostgreSQL database with timestamps
3. Provides REST API with authentication to query stored data
4. Runs in Docker containers with CI/CD pipeline

## Architecture Summary

### System Components
1. **FastAPI Service** - REST API with authentication, rate limiting, and OpenAPI docs
2. **Celery Worker** - Periodic task scheduler for price fetching
3. **PostgreSQL** - Primary database for price history
4. **Redis** - Message broker for Celery
5. **Docker Containers** - Isolated deployment of all services

### Technology Stack
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic
- **Task Queue**: Celery with Redis broker
- **HTTP Client**: aiohttp
- **Database**: PostgreSQL 15 with asyncpg driver
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Authentication**: Client Credentials (Client ID + Secret)
- **Logging**: Structured JSON logging with structlog
- **Testing**: pytest with async support, pytest-cov for code coverage, pytest-mock

## Key Design Decisions

### 1. Microservices Architecture
**Decision**: Separate containers for API, Worker, Redis, and PostgreSQL
**Justification**:
- Independent scaling of components
- Better fault isolation
- Clear separation of concerns
- Easier maintenance and deployment

### 2. HTTP over WebSockets for Deribit
**Decision**: Use HTTP REST API instead of WebSockets
**Justification**:
- Simpler implementation for 1-minute polling
- No need for persistent connections
- Lower resource consumption
- Easier error handling and retry logic

### 3. PostgreSQL for Time-Series Data
**Decision**: Use PostgreSQL instead of time-series databases
**Justification**:
- ACID compliance for financial data
- Excellent performance with proper indexing
- Familiar tooling and ecosystem
- Support for complex queries if needed

### 4. Structured JSON Logging
**Decision**: Implement structured logging with JSON format
**Justification**:
- Machine-readable logs for aggregation
- Better debugging with context
- Easy integration with log collectors (ELK, Loki)
- Consistent format across services

### 5. Client Credentials Authentication
**Decision**: Use Client ID + Secret for API authentication
**Justification**:
- Simple yet secure for server-to-server communication
- Easy to implement and manage
- Suitable for programmatic access
- Can be extended to JWT if needed

## File Structure
```
deribit-storage/
├── src/
│   ├── api/                    # FastAPI application
│   │   ├── main.py            # FastAPI app instance
│   │   ├── routers/           # API endpoints
│   │   └── schemas/          # Pydantic models
│   ├── worker/                # Celery worker
│   │   ├── tasks.py           # Celery tasks
│   │   ├── deribit_client.py  # Deribit API client
│   ├── core/                  # Shared core functionality
│   │   ├── config.py          # Configuration
│   │   ├── database/
│   │   │   ├── connections.py        # Database connection
│   │   │   ├── models.py        # Database models
│   │   │   └── actions.py        # Database actions
│   │   ├── logging.py         # Logging setup
├── tests/                 # Test suite
├── docker/                    # Docker configuration
├── .github/workflows/        # GitHub Actions
├── migrations/               # Database migrations
├── .env.example              # Environment template
├── docker-compose.yml        # Local development
├── pyproject.toml           # Python project config
└── README.md                # Project documentation
```

## API Endpoints

### Authentication Required Endpoints
All endpoints require `X-Client-ID` and `X-Client-Secret` headers.

1. **GET /api/v1/prices**
   - Get all prices for a ticker
   - Query params: `ticker` (required), `limit`, `offset`
   - Response: `{ "data": [...], "pagination": {...} }`

2. **GET /api/v1/prices/latest**
   - Get latest price for a ticker
   - Query params: `ticker` (required)
   - Response: `{ "ticker": "...", "price": "...", "timestamp": ... }`

3. **GET /api/v1/prices/filter**
   - Get prices filtered by date range
   - Query params: `ticker` (required), `start_date`, `end_date`
   - Response: `{ "data": [...] }`

### Public Endpoints
1. **GET /health** - Service health check
2. **GET /docs** - Swagger UI documentation
3. **GET /redoc** - ReDoc documentation

## Database Schema

### Core Tables
1. **price_history** - Stores price data
   - `id` (UUID), `ticker` (VARCHAR), `price` (DECIMAL(20, 8))
   - `timestamp` (BIGINT - UNIX timestamp), `created_at` (TIMESTAMP WITH TIME ZONE)

### Authentication Note
- **Client credentials** stored in `.env` file (not database)
- Environment variables: `API_CLIENT_ID` and `API_CLIENT_SECRET`
- FastAPI middleware validates against environment variables
- No database table needed for authentication

## Container Architecture
- **api**: FastAPI application (port 8000)
- **worker**: Celery worker with beat scheduler
- **redis**: Message broker for Celery
- **postgres**: PostgreSQL database (port 5432)

## Development Workflow
1. Clone repository and set up environment
2. Configure environment variables (.env)
3. Start services with Docker Compose
4. Run database migrations
5. Start development server
6. Run tests and linting

## Production Deployment
1. Build Docker images
2. Configure environment variables
3. Deploy with Docker Compose or Kubernetes
4. Set up monitoring and alerting
5. Configure backups and disaster recovery

## Success Metrics
- **Reliability**: 99.9% uptime for price fetching
- **Performance**: < 100ms API response time (p95)
- **Accuracy**: 100% data integrity
- **Security**: No unauthorized access
- **Maintainability**: Comprehensive tests and documentation

## Risk Mitigation
1. **API Rate Limiting**: Implement retry with exponential backoff
2. **Database Failure**: Connection pooling and retry logic
3. **Service Outage**: Health checks and automatic restart
4. **Data Loss**: Regular backups and replication
5. **Security Breach**: Authentication, rate limiting, input validation
