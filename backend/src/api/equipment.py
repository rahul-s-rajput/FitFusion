"""
Equipment Management API endpoints for FitFusion AI Workout App.
Handles user equipment inventory, specifications, and availability.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse
from uuid import UUID, uuid4
import logging

from ..models.equipment import (
    Equipment,
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentResponse,
    EquipmentCategory,
    EquipmentCondition
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/equipment", tags=["equipment"])


# Dependency for getting current user (placeholder - would integrate with auth system)
async def get_current_user_id() -> UUID:
    """Get current authenticated user ID - placeholder for auth integration"""
    return UUID('12345678-1234-5678-9012-123456789abc')


@router.get("/", response_model=List[EquipmentResponse])
async def get_user_equipment(
    user_id: UUID = Depends(get_current_user_id),
    category: Optional[EquipmentCategory] = Query(None, description="Filter by equipment category"),
    available_only: bool = Query(False, description="Only return available equipment"),
    condition: Optional[EquipmentCondition] = Query(None, description="Filter by equipment condition")
) -> List[EquipmentResponse]:
    """
    Get all equipment for the current user with optional filtering.
    
    Args:
        category: Filter by equipment category
        available_only: Only return equipment marked as available
        condition: Filter by equipment condition
        
    Returns:
        List[EquipmentResponse]: User's equipment inventory
    """
    try:
        logger.info(f"Fetching equipment for user {user_id}")
        
        # Mock equipment data - would come from database
        mock_equipment = [
            Equipment(
                id=uuid4(),
                user_id=user_id,
                name="Adjustable Dumbbells",
                category=EquipmentCategory.WEIGHTS,
                specifications={
                    "weight_range": "5-50 lbs",
                    "adjustment_type": "dial",
                    "material": "rubber_coated"
                },
                space_requirements={
                    "floor_space": "2x1 feet",
                    "storage_space": "compact"
                },
                noise_characteristics={
                    "noise_level": "low",
                    "noise_type": "metal_clanking"
                },
                condition=EquipmentCondition.EXCELLENT,
                is_available=True
            ),
            Equipment(
                id=uuid4(),
                user_id=user_id,
                name="Resistance Bands Set",
                category=EquipmentCategory.RESISTANCE,
                specifications={
                    "resistance_levels": "light, medium, heavy",
                    "band_count": 5,
                    "accessories": "door_anchor, handles, ankle_straps"
                },
                space_requirements={
                    "floor_space": "minimal",
                    "storage_space": "very_compact"
                },
                noise_characteristics={
                    "noise_level": "silent",
                    "noise_type": "none"
                },
                condition=EquipmentCondition.GOOD,
                is_available=True
            ),
            Equipment(
                id=uuid4(),
                user_id=user_id,
                name="Treadmill",
                category=EquipmentCategory.CARDIO,
                specifications={
                    "max_speed": "12 mph",
                    "incline_range": "0-15%",
                    "belt_size": "20x55 inches"
                },
                space_requirements={
                    "floor_space": "6x3 feet",
                    "ceiling_height": "8 feet"
                },
                noise_characteristics={
                    "noise_level": "moderate",
                    "noise_type": "motor_running"
                },
                condition=EquipmentCondition.NEEDS_REPAIR,
                is_available=False
            )
        ]
        
        # Apply filters
        filtered_equipment = mock_equipment
        
        if category:
            filtered_equipment = [eq for eq in filtered_equipment if eq.category == category]
        
        if available_only:
            filtered_equipment = [eq for eq in filtered_equipment if eq.is_available]
        
        if condition:
            filtered_equipment = [eq for eq in filtered_equipment if eq.condition == condition]
        
        # Convert to response format
        equipment_responses = [
            EquipmentResponse.from_equipment(eq) for eq in filtered_equipment
        ]
        
        logger.info(f"Successfully retrieved {len(equipment_responses)} equipment items for user {user_id}")
        return equipment_responses
        
    except Exception as e:
        logger.error(f"Error fetching equipment for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve equipment: {str(e)}"
        )


@router.post("/", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
async def add_equipment(
    equipment_data: EquipmentCreate,
    user_id: UUID = Depends(get_current_user_id)
) -> EquipmentResponse:
    """
    Add new equipment to user's inventory.
    
    Args:
        equipment_data: Equipment information to add
        
    Returns:
        EquipmentResponse: Created equipment item
    """
    try:
        logger.info(f"Adding equipment for user {user_id}: {equipment_data.name}")
        
        # Validate equipment data
        if not equipment_data.name or len(equipment_data.name.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Equipment name is required"
            )
        
        if len(equipment_data.name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Equipment name must be 100 characters or less"
            )
        
        # Create new equipment
        new_equipment = Equipment(
            id=uuid4(),
            user_id=user_id,
            name=equipment_data.name,
            category=equipment_data.category,
            specifications=equipment_data.specifications or {},
            space_requirements=equipment_data.space_requirements or {},
            noise_characteristics=equipment_data.noise_characteristics or {},
            condition=equipment_data.condition or EquipmentCondition.GOOD,
            is_available=equipment_data.is_available if equipment_data.is_available is not None else True
        )
        
        # This would save to database
        
        response = EquipmentResponse.from_equipment(new_equipment)
        logger.info(f"Successfully added equipment {new_equipment.id} for user {user_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding equipment for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add equipment: {str(e)}"
        )


@router.get("/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment_by_id(
    equipment_id: UUID,
    user_id: UUID = Depends(get_current_user_id)
) -> EquipmentResponse:
    """
    Get specific equipment item by ID.
    
    Args:
        equipment_id: ID of the equipment to retrieve
        
    Returns:
        EquipmentResponse: Equipment details
    """
    try:
        logger.info(f"Fetching equipment {equipment_id} for user {user_id}")
        
        # This would fetch from database
        # For now, return mock data
        mock_equipment = Equipment(
            id=equipment_id,
            user_id=user_id,
            name="Adjustable Dumbbells",
            category=EquipmentCategory.WEIGHTS,
            specifications={
                "weight_range": "5-50 lbs",
                "adjustment_type": "dial"
            },
            space_requirements={
                "floor_space": "2x1 feet"
            },
            noise_characteristics={
                "noise_level": "low"
            },
            condition=EquipmentCondition.EXCELLENT,
            is_available=True
        )
        
        response = EquipmentResponse.from_equipment(mock_equipment)
        logger.info(f"Successfully retrieved equipment {equipment_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error fetching equipment {equipment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment not found: {equipment_id}"
        )


@router.put("/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(
    equipment_id: UUID,
    equipment_update: EquipmentUpdate,
    user_id: UUID = Depends(get_current_user_id)
) -> EquipmentResponse:
    """
    Update existing equipment item.
    
    Args:
        equipment_id: ID of the equipment to update
        equipment_update: Updated equipment information
        
    Returns:
        EquipmentResponse: Updated equipment details
    """
    try:
        logger.info(f"Updating equipment {equipment_id} for user {user_id}")
        
        # Validate update data
        if equipment_update.name is not None:
            if not equipment_update.name or len(equipment_update.name.strip()) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Equipment name cannot be empty"
                )
            
            if len(equipment_update.name) > 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Equipment name must be 100 characters or less"
                )
        
        # This would fetch existing equipment from database and update it
        # For now, simulate update
        updated_equipment = Equipment(
            id=equipment_id,
            user_id=user_id,
            name=equipment_update.name or "Updated Equipment",
            category=equipment_update.category or EquipmentCategory.WEIGHTS,
            specifications=equipment_update.specifications or {},
            space_requirements=equipment_update.space_requirements or {},
            noise_characteristics=equipment_update.noise_characteristics or {},
            condition=equipment_update.condition or EquipmentCondition.GOOD,
            is_available=equipment_update.is_available if equipment_update.is_available is not None else True
        )
        
        response = EquipmentResponse.from_equipment(updated_equipment)
        logger.info(f"Successfully updated equipment {equipment_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating equipment {equipment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update equipment: {str(e)}"
        )


@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipment(
    equipment_id: UUID,
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Delete equipment item from user's inventory.
    
    Args:
        equipment_id: ID of the equipment to delete
    """
    try:
        logger.info(f"Deleting equipment {equipment_id} for user {user_id}")
        
        # This would delete from database
        # Also need to check if equipment is used in any active workouts
        
        logger.info(f"Successfully deleted equipment {equipment_id}")
        return None
        
    except Exception as e:
        logger.error(f"Error deleting equipment {equipment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete equipment: {str(e)}"
        )


@router.patch("/{equipment_id}/availability", response_model=EquipmentResponse)
async def update_equipment_availability(
    equipment_id: UUID,
    is_available: bool,
    user_id: UUID = Depends(get_current_user_id)
) -> EquipmentResponse:
    """
    Update equipment availability status.
    
    Args:
        equipment_id: ID of the equipment
        is_available: New availability status
        
    Returns:
        EquipmentResponse: Updated equipment with new availability
    """
    try:
        logger.info(f"Updating availability for equipment {equipment_id} to {is_available}")
        
        # This would update in database
        updated_equipment = Equipment(
            id=equipment_id,
            user_id=user_id,
            name="Equipment",
            category=EquipmentCategory.WEIGHTS,
            specifications={},
            space_requirements={},
            noise_characteristics={},
            condition=EquipmentCondition.GOOD,
            is_available=is_available
        )
        
        response = EquipmentResponse.from_equipment(updated_equipment)
        logger.info(f"Successfully updated availability for equipment {equipment_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error updating availability for equipment {equipment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update equipment availability: {str(e)}"
        )


@router.get("/categories/", response_model=List[str])
async def get_equipment_categories() -> List[str]:
    """
    Get all available equipment categories.
    
    Returns:
        List[str]: Available equipment categories
    """
    try:
        categories = [category.value for category in EquipmentCategory]
        logger.info(f"Retrieved {len(categories)} equipment categories")
        return categories
        
    except Exception as e:
        logger.error(f"Error fetching equipment categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve equipment categories: {str(e)}"
        )


@router.get("/suggestions/", response_model=List[Dict[str, Any]])
async def get_equipment_suggestions(
    user_id: UUID = Depends(get_current_user_id),
    budget: Optional[str] = Query(None, description="Budget range: low, medium, high"),
    space: Optional[str] = Query(None, description="Available space: small, medium, large"),
    goals: Optional[str] = Query(None, description="Comma-separated fitness goals")
) -> List[Dict[str, Any]]:
    """
    Get equipment suggestions based on user profile and constraints.
    
    Args:
        budget: Budget range for suggestions
        space: Available space constraint
        goals: Fitness goals for targeted suggestions
        
    Returns:
        List[Dict]: Equipment suggestions with rationale
    """
    try:
        logger.info(f"Getting equipment suggestions for user {user_id}")
        
        # This would integrate with Equipment Advisor agent
        suggestions = [
            {
                "name": "Resistance Bands Set",
                "category": "resistance",
                "price_range": "$20-40",
                "space_required": "minimal",
                "rationale": "Versatile, space-efficient, great for strength training",
                "priority": "high",
                "alternatives": ["Suspension Trainer", "Resistance Loops"]
            },
            {
                "name": "Adjustable Dumbbells",
                "category": "weights",
                "price_range": "$200-500",
                "space_required": "small",
                "rationale": "Replaces entire dumbbell set, progressive overload capability",
                "priority": "medium",
                "alternatives": ["Kettlebell Set", "Barbell with Plates"]
            },
            {
                "name": "Yoga Mat",
                "category": "flexibility",
                "price_range": "$15-50",
                "space_required": "minimal",
                "rationale": "Essential for floor exercises, stretching, and core work",
                "priority": "high",
                "alternatives": ["Exercise Mat", "Pilates Mat"]
            }
        ]
        
        # Filter suggestions based on parameters
        if budget == "low":
            suggestions = [s for s in suggestions if "$" in s["price_range"] and int(s["price_range"].split("-")[0].replace("$", "")) < 100]
        
        logger.info(f"Generated {len(suggestions)} equipment suggestions")
        return suggestions
        
    except Exception as e:
        logger.error(f"Error generating equipment suggestions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate equipment suggestions: {str(e)}"
        )


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint for equipment service"""
    return {"status": "healthy", "service": "equipment_api", "version": "1.0.0"}
