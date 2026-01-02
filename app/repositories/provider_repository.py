"""
Provider repository - data access layer for providers.

This layer is STATELESS and handles ONLY database operations.
NO business logic here - just CRUD operations.

Repository pattern benefits:
- Separates database concerns from business logic
- Makes testing easier (can mock repository)
- Centralizes all database queries in one place
- Makes it easy to switch database implementations
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.provider import Provider
from app.schemas.provider import ProviderCreate, ProviderUpdate


class ProviderRepository:
    """
    Provider repository - handles all database operations for providers.
    
    IMPORTANT: This class is STATELESS.
    - Each instance receives a fresh database session
    - No state is stored between operations
    - Thread-safe and concurrency-safe
    """
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy session (will be closed by FastAPI after request)
        """
        self.db = db

    def create(self, data: ProviderCreate) -> Provider:
        """
        Create a new provider in the database.
        
        Args:
            data: Validated provider data from API
            
        Returns:
            Created provider with auto-generated ID and timestamps
            
        Note: This commits the transaction immediately.
        """
        # Convert Pydantic schema to dict and create ORM model
        provider = Provider(**data.model_dump())
        
        # Add to session and commit
        self.db.add(provider)
        self.db.commit()  # Persist to database
        self.db.refresh(provider)  # Load generated fields (id, timestamps)
        
        return provider

    def get_by_id(self, provider_id: int) -> Optional[Provider]:
        """
        Retrieve a single provider by ID.
        
        Args:
            provider_id: Provider's database ID
            
        Returns:
            Provider if found, None otherwise
        """
        return self.db.query(Provider).filter(Provider.id == provider_id).first()

    def list_all(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        sector: Optional[str] = None
    ) -> List[Provider]:
        """
        List providers with optional filtering and pagination.
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            sector: Filter by sector (e.g., "medical", "real_estate")
            
        Returns:
            List of providers matching criteria
            
        Example:
            # Get first 10 medical providers
            providers = repo.list_all(skip=0, limit=10, sector="medical")
        """
        query = self.db.query(Provider)
        
        # Apply sector filter if provided
        if sector:
            query = query.filter(Provider.sector == sector)
        
        # Apply pagination and return results
        return query.offset(skip).limit(limit).all()

    def update(self, provider_id: int, data: ProviderUpdate) -> Optional[Provider]:
        """
        Update an existing provider.
        
        Args:
            provider_id: Provider's database ID
            data: Fields to update (only provided fields are updated)
            
        Returns:
            Updated provider if found, None otherwise
            
        Note: This uses PATCH semantics - only provided fields are updated.
        """
        # Find provider
        provider = self.get_by_id(provider_id)
        if not provider:
            return None
        
        # Get only the fields that were actually provided in the request
        # exclude_unset=True means we only get fields that were set by the client
        update_data = data.model_dump(exclude_unset=True)
        
        # Update each provided field
        for field, value in update_data.items():
            setattr(provider, field, value)
        
        # Commit changes
        self.db.commit()
        self.db.refresh(provider)
        
        return provider

    def delete(self, provider_id: int) -> bool:
        """
        Delete a provider from the database.
        
        Args:
            provider_id: Provider's database ID
            
        Returns:
            True if deleted, False if not found
            
        WARNING: This is a hard delete. Consider soft deletes in production
        by setting is_active=False instead.
        """
        provider = self.get_by_id(provider_id)
        if not provider:
            return False
        
        # Delete and commit
        self.db.delete(provider)
        self.db.commit()
        
        return True