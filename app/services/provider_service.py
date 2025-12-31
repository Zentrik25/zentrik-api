"""
Provider service - business logic layer for providers.

This layer is STATELESS and contains ONLY business rules and validation.
NO database operations here - those are delegated to the repository.

Service layer responsibilities:
- Validate business rules
- Coordinate between multiple repositories if needed
- Transform data if needed
- Throw meaningful errors

This keeps business logic separate from data access and HTTP concerns.
"""
from typing import List, Optional
from app.repositories.provider_repository import ProviderRepository
from app.schemas.provider import ProviderCreate, ProviderUpdate


class ProviderService:
    """
    Provider service - handles business logic for provider operations.
    
    IMPORTANT: This class is STATELESS.
    - Each instance receives a repository (which has a session)
    - No state is stored between operations
    - All business rules are applied here
    """
    
    def __init__(self, repository: ProviderRepository):
        """
        Initialize service with repository.
        
        Args:
            repository: Provider repository for database operations
        """
        self.repository = repository

    def register_provider(self, data: ProviderCreate):
        """
        Register a new provider with business rule validation.
        
        Business rules:
        - Provider name cannot be empty or whitespace only
        - Sector cannot be empty or whitespace only
        
        Args:
            data: Validated provider data from API
            
        Returns:
            Created provider
            
        Raises:
            ValueError: If business rules are violated
            
        Example:
            provider = service.register_provider(
                ProviderCreate(name="City Clinic", sector="medical")
            )
        """
        # Business rule: Name must have actual content
        if not data.name.strip():
            raise ValueError("Provider name cannot be empty")
        
        # Business rule: Sector must be specified
        if not data.sector.strip():
            raise ValueError("Provider sector cannot be empty")
        
        # If all rules pass, delegate to repository
        return self.repository.create(data)

    def get_provider(self, provider_id: int):
        """
        Get a provider by ID with existence validation.
        
        Args:
            provider_id: Provider's database ID
            
        Returns:
            Provider entity
            
        Raises:
            ValueError: If provider not found
        """
        provider = self.repository.get_by_id(provider_id)
        if not provider:
            raise ValueError(f"Provider with ID {provider_id} not found")
        return provider

    def get_providers(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        sector: Optional[str] = None
    ):
        """
        Get all providers with optional filtering.
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            sector: Filter by sector (e.g., "medical", "real_estate")
            
        Returns:
            List of providers
            
        Note: No business rules to validate here, just pass through to repository.
        """
        return self.repository.list_all(skip=skip, limit=limit, sector=sector)

    def update_provider(self, provider_id: int, data: ProviderUpdate):
        """
        Update a provider with existence validation.
        
        Args:
            provider_id: Provider's database ID
            data: Fields to update
            
        Returns:
            Updated provider
            
        Raises:
            ValueError: If provider not found
            
        Note: Field-level validation is already handled by Pydantic schemas.
        """
        provider = self.repository.update(provider_id, data)
        if not provider:
            raise ValueError(f"Provider with ID {provider_id} not found")
        return provider

    def delete_provider(self, provider_id: int):
        """
        Delete a provider.
        
        Args:
            provider_id: Provider's database ID
            
        Returns:
            True if deleted
            
        Raises:
            ValueError: If provider not found
            
        WARNING: This is a hard delete. In production, consider:
        - Soft delete (set is_active=False)
        - Check for dependent bookings
        - Archive data before deletion
        """
        success = self.repository.delete(provider_id)
        if not success:
            raise ValueError(f"Provider with ID {provider_id} not found")
        return True