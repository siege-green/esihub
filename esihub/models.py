from typing import Any, Dict, Optional

from pydantic import BaseModel


class ESIRequestParams(BaseModel):
    method: str
    path: str
    character_id: Optional[int] = None


class ESICharacter(BaseModel):
    character_id: int
    name: str
    corporation_id: int
    alliance_id: Optional[int] = None
    birthday: str
    security_status: float
    race_id: int
    ancestry_id: Optional[int] = None
    bloodline_id: int


class ESICorporation(BaseModel):
    corporation_id: int
    name: str
    ticker: str
    member_count: int
    ceo_id: int
    alliance_id: Optional[int] = None
    description: str
    tax_rate: float
    creator_id: int
    url: Optional[str] = None


class ESIAlliance(BaseModel):
    alliance_id: int
    name: str
    ticker: str
    creator_corporation_id: int
    creator_id: int
    date_founded: str
    executor_corporation_id: Optional[int] = None


class ESIAsset(BaseModel):
    item_id: int
    type_id: int
    quantity: int
    location_id: int
    location_type: str
    is_singleton: bool


class ESIWallet(BaseModel):
    balance: float


class ESISkillQueue(BaseModel):
    skill_id: int
    finished_level: int
    queue_position: int
    start_date: Optional[str] = None
    finish_date: Optional[str] = None
    level_start_sp: Optional[int] = None
    level_end_sp: Optional[int] = None
    training_start_sp: Optional[int] = None


class ESIResponse(BaseModel):
    data: Dict[str, Any]
    expires: str
    last_modified: Optional[str] = None
