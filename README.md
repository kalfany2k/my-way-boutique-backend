````markdown
# MWB Backend

Backend API for MWB (My Wedding Boutique) e-commerce platform.

## Tech Stack

-   FastAPI
-   PostgreSQL
-   SQLAlchemy ORM
-   JWT Authentication
-   Redis for caching

## Setup & Installation

1. Clone the repository:
    ```bash
    git clone git@github.com:yourusername/mwb-backend.git
    cd mwb-backend
    ```
````

2. Create and activate virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    # or
    .\venv\Scripts\activate  # Windows
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up environment variables:

    ```bash
    cp .env.example .env
    # Edit .env with your configuration
    ```

5. Run migrations:

    ```bash
    alembic upgrade head
    ```

6. Start development server:
    ```bash
    uvicorn app.main:app --reload
    ```

## Development Guidelines

### Branch Naming

-   `feature/`: For new features
-   `bugfix/`: For bug fixes
-   `hotfix/`: For urgent production fixes
-   `release/`: For release preparations

### Commit Convention

```
type(scope): description

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Run migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### API Documentation

-   Swagger UI: http://localhost:8000/docs
-   ReDoc: http://localhost:8000/redoc

## Testing

```bash
pytest tests/
```

```

```
