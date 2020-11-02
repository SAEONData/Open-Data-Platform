from typing import Dict, Any, Optional

from pydantic import BaseModel, Field

from odp.api.models import KEY_REGEX


class WorkflowState(BaseModel):
    key: str = Field(..., regex=KEY_REGEX)
    name: str
    rules: Dict[str, Any]
    revert_key: Optional[str]
    publish: bool


class WorkflowTransition(BaseModel):
    from_key: Optional[str]
    to_key: str


class WorkflowAnnotation(BaseModel):
    key: str = Field(..., regex=KEY_REGEX)
    attributes: Dict[str, Any]
