# Database Design for Deribit Storage

## Database Choice: PostgreSQL 15
**Justification**: PostgreSQL provides ACID compliance, excellent performance for time-series data with proper indexing, and robust support for financial applications.

## Schema Design

### 1. Price History Table (`price_history`)
Stores historical price data fetched from Deribit.

```sql
CREATE TABLE price_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(20) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    timestamp BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_ticker CHECK (ticker IN ('btc_usd', 'eth_usd')),
    CONSTRAINT positive_price CHECK (price > 0),
    CONSTRAINT valid_timestamp CHECK (timestamp > 0)
);

-- Indexes for performance optimization
CREATE INDEX idx_price_history_ticker_timestamp 
ON price_history(ticker, timestamp DESC);

CREATE INDEX idx_price_history_timestamp 
ON price_history(timestamp DESC);

CREATE INDEX idx_price_history_created_at 
ON price_history(created_at DESC);
```

**Fields Description**:
- `id`: Unique identifier (UUID)
- `ticker`: Cryptocurrency pair (btc_usd or eth_usd)
- `price`: Index price from Deribit with 8 decimal places
- `timestamp`: UNIX timestamp when price was recorded
- `created_at`: When the record was inserted in the database

### 2. Authentication Note
**Important**: API authentication credentials (Client ID and Client Secret) will be stored in environment variables (`.env` file), not in the database. This simplifies the architecture and aligns with the 12-factor app methodology.

**Reasoning**:
- Single client configuration (no need for multiple clients in database)
- Simpler deployment and management
- Credentials can be rotated without database changes
- Environment variables are the standard for configuration in containerized applications

### 3. Task Logs Table (`task_logs`) - Optional
For monitoring Celery task executions and debugging.

```sql
CREATE TABLE task_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    parameters JSONB,
    result JSONB,
    
    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('PENDING', 'STARTED', 'SUCCESS', 'FAILURE', 'RETRY'))
);

-- Indexes for task monitoring
CREATE INDEX idx_task_logs_task_name 
ON task_logs(task_name);

CREATE INDEX idx_task_logs_started_at 
ON task_logs(started_at DESC);

CREATE INDEX idx_task_logs_status 
ON task_logs(status);
```

## SQLAlchemy Models

### PriceHistory Model
```python
from sqlalchemy import Column, String, Numeric, BigInteger, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String(20), nullable=False)
    price = Column(Numeric(20, 8), nullable=False)
    timestamp = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint("ticker IN ('btc_usd', 'eth_usd')", name="valid_ticker"),
        CheckConstraint("price > 0", name="positive_price"),
        CheckConstraint("timestamp > 0", name="valid_timestamp"),
    )
```

### Note: No APIClient Model Needed
Authentication credentials are managed via environment variables, not database tables. The FastAPI application will validate client credentials against values stored in the `.env` file.

## Migration Strategy

### Using Alembic for Database Migrations
1. Initialize Alembic in the project
2. Create initial migration for core tables
3. Set up automatic migration generation on model changes
4. Include migration scripts in version control

### Migration File Structure
```
migrations/
├── versions/
│   ├── 001_initial_schema.py
│   ├── 002_add_task_logs.py
│   └── ...
├── env.py
└── alembic.ini
```

## Performance Considerations

### 1. Partitioning Strategy
For high-volume data (millions of records), consider partitioning by:
- **Time-based partitioning**: Monthly or weekly partitions
- **Ticker-based partitioning**: Separate partitions for BTC and ETH

### 2. Query Optimization
- Use composite indexes for common query patterns
- Implement materialized views for aggregated data
- Consider TimescaleDB extension for time-series optimization

### 3. Connection Pooling
- Use `asyncpg` driver for async support
- Configure connection pool size based on expected load
- Implement connection health checks

## Data Retention Policy

### Default Policy
- Keep all price history indefinitely
- Optional: Implement automated cleanup for old data
- Consider archiving to cold storage after certain period

### Retention Configuration
```python
# Configuration options
DATA_RETENTION_DAYS = 365  # Keep data for 1 year
ARCHIVE_AFTER_DAYS = 30    # Move to archive after 30 days
```

## Backup Strategy

### Regular Backups
1. **Daily full backups** using `pg_dump`
2. **WAL archiving** for point-in-time recovery
3. **Automated backup verification**

### Disaster Recovery
1. **Multi-region replication** for high availability
2. **Automated failover** procedures
3. **Regular recovery testing**

## Security Considerations

### 1. Data Encryption
- **At-rest encryption** using PostgreSQL TDE
- **In-transit encryption** using TLS 1.3
- **Column-level encryption** for sensitive data

### 2. Access Control
- **Principle of least privilege** for database users
- **Role-based access control** (RBAC)
- **Audit logging** for all database operations

### 3. Injection Prevention
- **Parameterized queries** exclusively
- **SQLAlchemy ORM** with proper escaping
- **Input validation** at application layer

## Monitoring & Maintenance

### Key Metrics to Monitor
1. **Database connections** (active, idle, waiting)
2. **Query performance** (slow queries, index usage)
3. **Storage growth** (table sizes, index sizes)
4. **Replication lag** (if using replication)

### Maintenance Tasks
1. **Regular vacuum** and analyze operations
2. **Index rebuild** for fragmented indexes
3. **Statistics update** for query planner
4. **Connection pool** health checks

## Implementation Steps

### Phase 1: Initial Setup
1. Create PostgreSQL database
2. Install SQLAlchemy and asyncpg
3. Define base models
4. Create Alembic migration setup

### Phase 2: Core Implementation
1. Implement PriceHistory model and CRUD operations
2. Create database connection pool
3. Add connection health checks
4. Implement database migration setup with Alembic

### Phase 3: Optimization
1. Add indexes based on query patterns
2. Implement connection pooling
3. Add query performance monitoring
4. Set up database backup procedures

### Phase 4: Production Readiness
1. Implement database migration automation
2. Add monitoring and alerting
3. Set up backup and recovery procedures
4. Performance testing and tuning