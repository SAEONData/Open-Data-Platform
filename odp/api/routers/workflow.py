from typing import List

from fastapi import APIRouter, Depends

from odp.api.dependencies.auth import Authorizer, AuthData
from odp.api.dependencies.ckan import get_ckan_client
from odp.api.models.auth import Role, Scope
from odp.api.models.workflow import WorkflowState, WorkflowTransition, WorkflowAnnotation
from odp.config import config
from odp.lib.ckan import CKANClient

router = APIRouter()


@router.get('/state/', response_model=List[WorkflowState])
async def list_workflow_states(
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(Authorizer(
            Scope.METADATA,
            *Role.all(),
            institution_key=config.ODP.ADMIN.INSTITUTION)),
):
    return ckan.list_workflow_states(auth_data.access_token)


@router.post('/state/', response_model=WorkflowState)
async def create_or_update_workflow_state(
        workflow_state: WorkflowState,
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(Authorizer(
            Scope.METADATA,
            Role.ADMIN,
            institution_key=config.ODP.ADMIN.INSTITUTION)),
):
    return ckan.create_or_update_workflow_state(workflow_state, auth_data.access_token)


@router.get('/transition/', response_model=List[WorkflowTransition])
async def list_workflow_transitions(
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(Authorizer(
            Scope.METADATA,
            *Role.all(),
            institution_key=config.ODP.ADMIN.INSTITUTION)),
):
    return ckan.list_workflow_transitions(auth_data.access_token)


@router.post('/transition/', response_model=WorkflowTransition)
async def create_or_update_workflow_transition(
        workflow_transition: WorkflowTransition,
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(Authorizer(
            Scope.METADATA,
            Role.ADMIN,
            institution_key=config.ODP.ADMIN.INSTITUTION)),
):
    return ckan.create_or_update_workflow_transition(workflow_transition, auth_data.access_token)


@router.get('/annotation/', response_model=List[WorkflowAnnotation])
async def list_workflow_annotations(
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(Authorizer(
            Scope.METADATA,
            *Role.all(),
            institution_key=config.ODP.ADMIN.INSTITUTION)),
):
    return ckan.list_workflow_annotations(auth_data.access_token)


@router.post('/annotation/', response_model=WorkflowAnnotation)
async def create_or_update_workflow_annotation(
        workflow_annotation: WorkflowAnnotation,
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(Authorizer(
            Scope.METADATA,
            Role.ADMIN,
            institution_key=config.ODP.ADMIN.INSTITUTION)),
):
    return ckan.create_or_update_workflow_annotation(workflow_annotation, auth_data.access_token)
