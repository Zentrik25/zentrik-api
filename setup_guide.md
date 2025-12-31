# Multi-Sector Front Desk Management API - Setup Guide

## 🎯 Architecture Overview

### STATELESS Design - Critical to Understand

This API is **completely stateless**:
- ✅ No session state maintained between requests
- ✅ Each request gets a fresh database session
- ✅ Sessions automatically close after each request
- ✅ Safe for horizontal scaling (run multiple instances)
- ✅ No race conditions or session conflicts
- ✅ Can be deployed to multiple servers behind a load balancer

**How it works:**
```
Request comes in 
→ FastAPI creates new DB session via get_db()
→ Request is processed
→ Session is automatically closed (even if error occurs)
→ Next request gets a completely new session
```

This avoids the common pitfall of maintaining database sessions across requests.

## Project Structure
```
backend/
├── app/
│   ├── __init__.py                    # Package marker
│   ├── main.py                        # Application entry point
│   ├── database.py                    # Database config (STATELESS)
│   ├── models/                        # ORM models (define schema only)
│   │   ├── __init__.py
│   │   ├── provider.py                # Provider model
│   │   └── booking.py                 # Booking model
│   ├── schemas/                       # Pydantic schemas (validation)
│   │   ├── __init__.py
│   │   ├── provider.py                # Provider request/response schemas
│   │   └── booking.py                 # Booking request/response schemas
│   ├── repositories/                  # Data access layer (database operations)
│   │   ├── __init__.py
│   │   ├── provider_repository.py     # Provider CRUD operations
│   │   └── booking_repository.py      # Booking CRUD operations
│   ├── services/                      # Business logic layer
│   │   ├── __init__.py
│   │   ├── provider_service.py        # Provider business rules
│   │   └── booking_service.py         # Booking business rules
│   └── api/                           # HTTP layer (routes)
│       ├── __init__.py
│       ├── provider_routes.py         # Provider endpoints
│       └── booking_routes.py          # Booking endpoints
├── requirements.txt                   # Python dependencies
├── docker-compose.yml                 # PostgreSQL container config
└── .env                              # Environment variables
```

### Layer Separation (Why This Matters)

Each layer has ONE job:

1. **Models** (`models/`) - Define database schema only
2. **Schemas** (`schemas/`) - Validate input/output data
3. **Repositories** (`repositories/`) - Execute database queries
4. **Services** (`services/`) - Enforce business rules
5. **Routes** (`api/`) - Handle HTTP requests/responses

This separation means:
- Easy to test (mock any layer)
- Easy to modify (change one layer without touching others)
- Easy to scale (can optimize each layer independently)
- No confusion about where code belongs

## Quick Start (5 minutes)

### 1. Create project structure
```bash
mkdir -p backend/app/{models,schemas,repositories,services,api}
cd backend
```

### 2. Create all __init__.py files
```bash
touch app/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/repositories/__init__.py
touch app/services/__init__.py
touch app/api/__init__.py
```

### 3. Copy all files from artifacts
Copy each file from the artifacts above into the correct location.

### 4. Create .env file
```bash
cp .env.example .env
```
Or manually create `.env`:
```
DATABASE_URL=postgresql://booking_user:booking_pass@localhost:5432/booking_db
```

### 5. Start PostgreSQL
```bash
docker-compose up -d
```

Wait for database to be ready:
```bash
docker-compose logs -f db
# Wait for: "database system is ready to accept connections"
# Press Ctrl+C to exit logs
```

### 6. Install dependencies
```bash
pip install -r requirements.txt
```

### 7. Run the API
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Test the API
Open browser: http://localhost:8000/docs

You'll see interactive API documentation (Swagger UI).

## API Endpoints

### Providers
- `POST /providers/` - Create provider
- `GET /providers/` - List providers (with filtering by sector)
- `GET /providers/{id}` - Get specific provider
- `PATCH /providers/{id}` - Update provider (partial update)
- `DELETE /providers/{id}` - Delete provider

### Bookings
- `POST /bookings/` - Create booking
- `GET /bookings/` - List bookings (with filtering by provider, status, dates)
- `GET /bookings/{id}` - Get specific booking
- `PATCH /bookings/{id}` - Update booking (partial update)
- `POST /bookings/{id}/cancel` - Cancel booking
- `DELETE /bookings/{id}` - Delete booking

## Testing with curl

### Create a Provider
```bash
curl -X POST "http://localhost:8000/providers/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "City Medical Clinic",
    "sector": "medical",
    "phone": "+1234567890",
    "email": "info@citymedical.com",
    "address": "123 Main St"
  }'
```

### List All Providers
```bash
curl "http://localhost:8000/providers/"
```

### Filter Providers by Sector
```bash
curl "http://localhost:8000/providers/?sector=medical"
```

### Create a Booking
```bash
curl -X POST "http://localhost:8000/bookings/" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_id": 1,
    "client_name": "John Doe",
    "client_phone": "+1234567890",
    "client_email": "john@example.com",
    "service_type": "consultation",
    "scheduled_at": "2025-01-15T10:00:00",
    "notes": "First visit"
  }'
```

### List Bookings for a Provider
```bash
curl "http://localhost:8000/bookings/?provider_id=1"
```

### Filter by Status
```bash
curl "http://localhost:8000/bookings/?status=pending"
```

### Filter by Date Range
```bash
curl "http://localhost:8000/bookings/?from_date=2025-01-01T00:00:00&to_date=2025-01-31T23:59:59"
```

### Update Booking Status
```bash
curl -X PATCH "http://localhost:8000/bookings/1" \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'
```

### Cancel a Booking
```bash
curl -X POST "http://localhost:8000/bookings/1/cancel"
```

## Database Design Features

### Current Schema

**Providers Table:**
- `id` - Primary key
- `name` - Business name
- `sector` - Industry (medical, real_estate, automotive, etc.)
- `phone`, `email`, `address` - Contact info
- `is_active` - Whether provider accepts bookings
- `created_at`, `updated_at` - Audit timestamps

**Bookings Table:**
- `id` - Primary key
- `provider_id` - Foreign key to providers
- `client_name`, `client_phone`, `client_email` - Client info
- `service_type` - Type of service
- `scheduled_at` - Appointment time
- `status` - pending, confirmed, completed, cancelled
- `notes` - Additional information
- `created_at`, `updated_at` - Audit timestamps

### Expandability Examples

The database is designed for easy expansion:

#### 1. Add fields to existing tables
```python
# In models/provider.py, add:
operating_hours = Column(JSON, nullable=True)
services_offered = Column(ARRAY(String), nullable=True)
rating = Column(Float, default=0.0)
```

#### 2. Add new tables
Create `app/models/staff.py`:
```python
class Staff(Base):
    __tablename__ = "staff"
    
    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey("providers.id"))
    name = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False)
    phone = Column(String(50))
```

Then create corresponding:
- Schema in `schemas/staff.py`
- Repository in `repositories/staff_repository.py`
- Service in `services/staff_service.py`
- Routes in `api/staff_routes.py`

#### 3. Common expansions for production

**Payments table:**
```python
class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), nullable=False)
    payment_method = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Reviews table:**
```python
class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Notifications table:**
```python
class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    type = Column(String(50), nullable=False)  # sms, email
    status = Column(String(50), nullable=False)  # sent, failed
    sent_at = Column(DateTime)
```

## Why This Architecture is Stateless

### Database Sessions (Most Important)
```python
# ❌ BAD: Session stored at module level (STATEFUL)
db = SessionLocal()  # Never do this!

# ✅ GOOD: Session created per request (STATELESS)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Repositories (Stateless)
```python
# Each repository gets a fresh session per request
class ProviderRepository:
    def __init__(self, db: Session):  # New session each time
        self.db = db
    
    def create(self, data):
        # Uses session, commits, done
        # No state stored in self
```

### Services (Stateless)
```python
# Each service gets a fresh repository per request
class ProviderService:
    def __init__(self, repository):  # New repository each time
        self.repository = repository
    
    def register_provider(self, data):
        # Validates, calls repository, returns
        # No state stored in self
```

### Routes (Stateless)
```python
# Each request gets fresh service via dependency injection
def create_provider(
    payload: ProviderCreate,
    service: ProviderService = Depends(get_provider_service)  # New each time
):
    return service.register_provider(payload)
```

### Benefits of This Design
1. **Horizontal scaling** - Run 10 instances behind a load balancer
2. **No race conditions** - Each request is isolated
3. **Automatic cleanup** - Sessions always close
4. **Testing friendly** - Easy to mock dependencies
5. **Production ready** - No session leaks or memory issues

## Production Checklist

### Must Do Before Production

- [ ] **Environment variables** - Move all config to environment variables
- [ ] **CORS origins** - Replace `allow_origins=["*"]` with specific domains
- [ ] **Database migrations** - Use Alembic instead of `create_all()`
- [ ] **Error tracking** - Add Sentry or similar
- [ ] **Logging** - Structured logging with correlation IDs
- [ ] **Health checks** - Monitor database connectivity
- [ ] **Rate limiting** - Prevent abuse
- [ ] **Authentication** - Add JWT tokens
- [ ] **HTTPS** - Always use HTTPS in production
- [ ] **Database backups** - Automated daily backups
- [ ] **Connection pooling** - Already configured in `database.py`

### Recommended Additions

- [ ] **API versioning** - `/v1/providers`, `/v2/providers`
- [ ] **Request validation** - Input sanitization
- [ ] **Response caching** - Redis for frequently accessed data
- [ ] **Pagination metadata** - Return total count, page info
- [ ] **API documentation** - Keep Swagger docs updated
- [ ] **Load testing** - Test with expected traffic
- [ ] **Monitoring** - Prometheus metrics
- [ ] **CI/CD pipeline** - Automated testing and deployment

## Next Steps

Pick ONE to implement next:

1. **Authentication (JWT)**
   - Add user registration/login
   - Protect endpoints with JWT tokens
   - Add role-based access control

2. **Alembic Migrations**
   - Replace `create_all()` with proper migrations
   - Track schema changes in version control
   - Enable safe production deployments

3. **Notifications**
   - SMS notifications for booking confirmations
   - Email reminders before appointments
   - Add notification preferences

4. **Payment Integration**
   - Add payment processing
   - Track payment status
   - Handle refunds

5. **Advanced Filtering**
   - Full-text search for providers
   - Complex date queries
   - Sort by multiple fields

## Troubleshooting

### Database connection fails
```bash
# Check if Postgres is running
docker-compose ps

# Check logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Import errors
```bash
# Ensure you're in backend/ directory
pwd
# Should show: /path/to/backend

# Check all __init__.py files exist
ls app/__init__.py app/models/__init__.py app/schemas/__init__.py
```

### Port already in use
```bash
# Change port
uvicorn app.main:app --reload --port 8001

# Or kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

### Database tables not created
```bash
# Check if init_db() is called in main.py
# Restart the API to recreate tables
```

### "No module named 'app'"
```bash
# Make sure you run uvicorn from backend/ directory
cd backend
uvicorn app.main:app --reload
```

## Common Questions

**Q: Why is there no session management?**
A: Each request gets a fresh database session. No need for session state because we're stateless.

**Q: Can I deploy this behind a load balancer?**
A: Yes! Because it's stateless, you can run multiple instances with no coordination needed.

**Q: How do I add a new field to a table?**
A: Add it to the model, add it to schemas, run Alembic migration (or restart with `create_all()`).

**Q: How do I add a new entity (e.g., Staff)?**
A: Create model, schema, repository, service, and routes following the same pattern as Provider.

**Q: Why separate repositories and services?**
A: Repositories handle database operations, services handle business logic. This separation makes testing and maintenance easier.