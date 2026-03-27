# Deribit HTTP Client Implementation Plan

## Overview
The Deribit client will fetch BTC/USD and ETH/USD index prices every minute using Deribit's public REST API.

## Deribit API Documentation
- **Base URL**: `https://www.deribit.com/api/v2`
- **Index Price Endpoint**: `GET /public/get_index_price`
- **Required Parameters**: `index_name` (e.g., "btc_usd", "eth_usd")
- **Response Format**: JSON with `result` object containing `index_price`

## Client Design

### 1. Client Requirements
- Fetch prices for both BTC/USD and ETH/USD
- Handle API rate limits (public API has limits)
- Implement retry logic with exponential backoff
- Async/await support for non-blocking I/O
- Comprehensive error handling
- Request/response logging

### 2. Technical Implementation

#### Dependencies
```python
# requirements/worker.txt
aiohttp>=3.9.0
asyncio
pydantic>=2.0.0
tenacity>=8.2.0  # for retry logic
structlog>=23.0.0  # for structured logging

# requirements/dev.txt (for testing)
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-mock>=3.10.0  # for mocking in tests
```

#### Client Class Structure
```python
class DeribitClient:
    """Async HTTP client for Deribit API."""
    
    def __init__(self, base_url: str = "https://www.deribit.com/api/v2"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = structlog.get_logger(__name__)
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def connect(self):
        """Create aiohttp session."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=10)
        )
    
    async def close(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
    )
    async def get_index_price(self, index_name: str) -> Decimal:
        """Fetch index price from Deribit API."""
        url = f"{self.base_url}/public/get_index_price"
        params = {"index_name": index_name}
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise DeribitAPIError(f"API returned {response.status}")
            
            data = await response.json()
            
            if "error" in data:
                error_msg = data["error"].get("message", "Unknown error")
                raise DeribitAPIError(f"Deribit error: {error_msg}")
            
            index_price = Decimal(str(data["result"]["index_price"]))
            return index_price
    
    async def get_btc_usd_price(self) -> Decimal:
        """Get BTC/USD index price."""
        return await self.get_index_price("btc_usd")
    
    async def get_eth_usd_price(self) -> Decimal:
        """Get ETH/USD index price."""
        return await self.get_index_price("eth_usd")
    
    async def get_all_prices(self) -> Dict[str, Decimal]:
        """Get both BTC and ETH prices concurrently."""
        btc_task = asyncio.create_task(self.get_btc_usd_price())
        eth_task = asyncio.create_task(self.get_eth_usd_price())
        
        btc_price, eth_price = await asyncio.gather(btc_task, eth_task)
        
        return {
            "btc_usd": btc_price,
            "eth_usd": eth_price
        }
```

### 3. Error Handling

#### Custom Exceptions
```python
class DeribitError(Exception):
    """Base exception for Deribit client errors."""
    pass

class DeribitAPIError(DeribitError):
    """Exception for API response errors."""
    pass

class DeribitConnectionError(DeribitError):
    """Exception for connection errors."""
    pass

class DeribitRateLimitError(DeribitError):
    """Exception for rate limit errors."""
    pass
```

#### Retry Logic
- **Max attempts**: 3
- **Exponential backoff**: 4s, 8s, 16s
- **Retry on**: Connection errors, timeouts, 5xx status codes
- **Do not retry on**: 4xx client errors (except 429 rate limit)

### 4. Configuration

#### Environment Variables
```bash
# .env
DERIBIT_BASE_URL=https://www.deribit.com/api/v2
DERIBIT_REQUEST_TIMEOUT=30
DERIBIT_MAX_RETRIES=3
DERIBIT_RETRY_DELAY_BASE=4
```

#### Pydantic Settings
```python
from pydantic_settings import BaseSettings

class DeribitSettings(BaseSettings):
    base_url: str = "https://www.deribit.com/api/v2"
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay_base: int = 4
    
    class Config:
        env_prefix = "DERIBIT_"  # Will read DERIBIT_BASE_URL, DERIBIT_REQUEST_TIMEOUT, etc.
```

### 5. Logging Strategy

#### Structured Logging
```python
import structlog

logger = structlog.get_logger()

# Log example
logger.info(
    "deribit_price_fetched",
    ticker="btc_usd",
    price=50000.50,
    response_time=0.15,
    attempt=1
)
```

#### Log Fields
- **ticker**: Cryptocurrency pair
- **price**: Fetched price
- **response_time**: API response time in seconds
- **attempt**: Retry attempt number
- **status**: Success/failure
- **error**: Error message if failed

### 6. Testing Strategy

#### Unit Tests (using pytest-mock)
```python
import pytest
from decimal import Decimal

class TestDeribitClient:
    @pytest.mark.asyncio
    async def test_get_index_price_success(self, mocker):
        """Test successful price fetch using pytest-mock."""
        mock_response = {
            "result": {"index_price": "50000.50"}
        }
        
        # Mock the aiohttp session
        mock_session = mocker.AsyncMock()
        mock_session.get.return_value.__aenter__.return_value.json = mocker.AsyncMock(
            return_value=mock_response
        )
        mock_session.get.return_value.__aenter__.return_value.status = 200
        
        # Patch the ClientSession
        mocker.patch("aiohttp.ClientSession", return_value=mock_session)
        
        client = DeribitClient()
        price = await client.get_index_price("btc_usd")
        
        assert price == Decimal("50000.50")
    
    @pytest.mark.asyncio
    async def test_get_index_price_api_error(self, mocker):
        """Test API error response using pytest-mock."""
        mock_response = {
            "error": {"message": "Invalid index name"}
        }
        
        # Mock the aiohttp session
        mock_session = mocker.AsyncMock()
        mock_session.get.return_value.__aenter__.return_value.json = mocker.AsyncMock(
            return_value=mock_response
        )
        mock_session.get.return_value.__aenter__.return_value.status = 200
        
        # Patch the ClientSession
        mocker.patch("aiohttp.ClientSession", return_value=mock_session)
        
        client = DeribitClient()
        
        with pytest.raises(DeribitAPIError):
            await client.get_index_price("invalid_ticker")
```

#### Integration Tests
- Test with real Deribit API (optional)
- Mock responses for CI/CD pipeline
- Test rate limiting behavior
- Test retry logic

### 7. Performance Considerations

#### Connection Pooling
- Reuse aiohttp session across requests
- Configure connection limits based on expected load
- Implement connection timeout and keep-alive

#### Concurrent Requests
- Use `asyncio.gather()` for parallel price fetching
- Implement semaphore for rate limiting
- Monitor response times and adjust timeouts

#### Caching Strategy
- Optional: Cache prices for short period (5-10 seconds)
- Reduce API calls during high-frequency access
- Implement cache invalidation on error

### 8. Monitoring & Metrics

#### Key Metrics to Track
1. **API response time** (p95, p99)
2. **Success/failure rate**
3. **Rate limit usage**
4. **Retry count distribution**
5. **Price volatility** (optional)

#### Health Checks
- Periodic API connectivity test
- Response time threshold alerts
- Price freshness monitoring

### 9. Integration with Celery

#### Task Definition
```python
from celery import Celery
from worker.deribit_client import DeribitClient
from worker.models import save_price_to_db

app = Celery("deribit_tasks")

@app.task
def fetch_and_store_prices():
    """Fetch prices from Deribit and store in database."""
    async def _fetch():
        async with DeribitClient() as client:
            prices = await client.get_all_prices()
            
            for ticker, price in prices.items():
                await save_price_to_db(ticker, price)
    
    # Run async function in sync context
    asyncio.run(_fetch())
```

#### Scheduled Task
```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    "fetch-prices-every-minute": {
        "task": "worker.tasks.fetch_and_store_prices",
        "schedule": crontab(minute="*"),  # Every minute
    },
}
```

### 10. Security Considerations

#### API Key Management
- Public API doesn't require authentication
- Future: Support authenticated endpoints if needed
- Store API keys in environment variables

#### Request Validation
- Validate index_name parameter
- Sanitize API responses
- Handle malformed JSON responses

#### Rate Limiting Compliance
- Respect Deribit's rate limits (public API: ~20 requests/second)
- Implement request throttling
- Monitor for 429 responses

### 11. Implementation Steps

#### Phase 1: Basic Client
1. Create DeribitClient class with aiohttp
2. Implement `get_index_price` method
3. Add error handling and retry logic
4. Write unit tests

#### Phase 2: Enhanced Features
1. Add concurrent price fetching
2. Implement structured logging
3. Add configuration via environment variables
4. Write integration tests

#### Phase 3: Production Ready
1. Add connection pooling
2. Implement health checks
3. Add monitoring metrics
4. Performance optimization

#### Phase 4: Integration
1. Integrate with Celery task
2. Add database storage
3. Implement scheduled execution
4. End-to-end testing

### 12. Deployment Considerations

#### Container Configuration
- Environment variables for configuration
- Resource limits (CPU, memory)
- Health check endpoints
- Log aggregation

#### Scaling Strategy
- Multiple Celery workers for high availability
- Load balancing for API requests
- Database connection pooling

### 13. Future Enhancements

#### WebSocket Support
- Real-time price updates
- Lower latency for price changes
- Reduced API call volume

#### Multiple Exchanges
- Extend to support other exchanges
- Price aggregation from multiple sources
- Arbitrage detection

#### Advanced Analytics
- Price prediction models
- Volatility analysis
- Trading signals

## Next Steps
1. Implement basic DeribitClient class
2. Add unit tests for price fetching
3. Integrate with Celery task scheduler
4. Add structured logging
5. Configure environment variables
6. Performance testing