"""Recurring Task API routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from uuid import UUID
from datetime import datetime
from ..models.database import get_session
from ..models.user import User
from ..schemas.recurring import (
    RecurringTaskTemplateCreate,
    RecurringTaskTemplateUpdate,
    RecurringTaskTemplateResponse
)
from ..controllers.recurring_task_controller import (
    get_recurring_task_controller,
    RecurringTaskController
)
from ..api.dependencies import get_current_user


router = APIRouter(prefix="/recurring-tasks", tags=["recurring-tasks"])


@router.post("/", response_model=RecurringTaskTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_recurring_task_template(
    template_data: RecurringTaskTemplateCreate,
    current_user: User = Depends(get_current_user),
    controller: RecurringTaskController = Depends(get_recurring_task_controller),
    session: Session = Depends(get_session)
):
    """Create a new recurring task template."""
    return await controller.create_recurring_task_template(
        user_id=current_user.id,
        template_data=template_data,
        session=session
    )


@router.get("/{template_id}", response_model=RecurringTaskTemplateResponse)
async def get_recurring_task_template(
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    controller: RecurringTaskController = Depends(get_recurring_task_controller),
    session: Session = Depends(get_session)
):
    """Get a specific recurring task template."""
    return await controller.get_recurring_task_template(
        template_id=template_id,
        user_id=current_user.id,
        session=session
    )


@router.get("/", response_model=List[RecurringTaskTemplateResponse])
async def get_user_recurring_task_templates(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    controller: RecurringTaskController = Depends(get_recurring_task_controller),
    session: Session = Depends(get_session)
):
    """Get all recurring task templates for the user."""
    return await controller.get_user_recurring_task_templates(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        session=session
    )


@router.put("/{template_id}", response_model=RecurringTaskTemplateResponse)
async def update_recurring_task_template(
    template_id: UUID,
    update_data: RecurringTaskTemplateUpdate,
    current_user: User = Depends(get_current_user),
    controller: RecurringTaskController = Depends(get_recurring_task_controller),
    session: Session = Depends(get_session)
):
    """Update a recurring task template."""
    return await controller.update_recurring_task_template(
        template_id=template_id,
        user_id=current_user.id,
        update_data=update_data,
        session=session
    )


@router.patch("/{template_id}", response_model=RecurringTaskTemplateResponse)
async def partially_update_recurring_task_template(
    template_id: UUID,
    update_data: RecurringTaskTemplateUpdate,
    current_user: User = Depends(get_current_user),
    controller: RecurringTaskController = Depends(get_recurring_task_controller),
    session: Session = Depends(get_session)
):
    """Partially update a recurring task template."""
    return await controller.update_recurring_task_template(
        template_id=template_id,
        user_id=current_user.id,
        update_data=update_data,
        session=session
    )


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recurring_task_template(
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    controller: RecurringTaskController = Depends(get_recurring_task_controller),
    session: Session = Depends(get_session)
):
    """Delete (deactivate) a recurring task template."""
    success = await controller.delete_recurring_task_template(
        template_id=template_id,
        user_id=current_user.id,
        session=session
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring task template not found"
        )
    
    return


@router.post("/{template_id}/generate-instances", status_code=status.HTTP_204_NO_CONTENT)
async def generate_task_instances_from_template(
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    controller: RecurringTaskController = Depends(get_recurring_task_controller),
    session: Session = Depends(get_session)
):
    """Generate task instances from a recurring template."""
    success = await controller.generate_task_instances_from_template(
        template_id=template_id,
        user_id=current_user.id,
        session=session
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring task template not found"
        )
    
    return


@router.get("/{template_id}/instances", response_model=List[TaskResponse])
async def get_task_instances_from_template(
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    controller: RecurringTaskController = Depends(get_recurring_task_controller),
    session: Session = Depends(get_session)
):
    """Get all task instances generated from a recurring template."""
    return await controller.get_task_instances_from_template(
        template_id=template_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        session=session
    )


@router.get("/active-today", response_model=List[RecurringTaskTemplateResponse])
async def get_active_recurring_tasks_today(
    current_user: User = Depends(get_current_user),
    controller: RecurringTaskController = Depends(get_recurring_task_controller),
    session: Session = Depends(get_session)
):
    """Get all recurring task templates that are active today."""
    return await controller.get_active_recurring_tasks_today(
        user_id=current_user.id,
        session=session
    )


@router.get("/stats", response_model=dict)
async def get_recurring_task_stats(
    current_user: User = Depends(get_current_user),
    controller: RecurringTaskController = Depends(get_recurring_task_controller),
    session: Session = Depends(get_session)
):
    """Get statistics about recurring tasks for the user."""
    return await controller.get_recurring_task_stats(
        user_id=current_user.id,
        session=session
    )