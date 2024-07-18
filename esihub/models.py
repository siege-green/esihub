from typing import Dict, Any, Optional

from pydantic import BaseModel, Field


class ESIHubRequestParams(BaseModel):
    method: str
    path: str
    query_params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = Field(default_factory=dict)


class ESIHubResponse(BaseModel):
    status: int
    headers: Dict[str, str]
    data: Any
