from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional

class TagRead(BaseModel):
    tag_code: str = Field(..., min_length=1)
    timestamp: str

class TagsPayload(BaseModel):
    module_loto_code: str
    tags: Dict[Literal["CARD","LOTO"], List[TagRead]]

class StatusAlertItem(BaseModel):
    name: str
    lastname: str
    message: str

class StatusPayload(BaseModel):
    module_loto_code: str
    status: Literal["ok", "alert", "error"]
    alerts: Optional[List[StatusAlertItem]] = None
    message: Optional[str] = None

class LwtPayload(BaseModel):
    module_loto_code: str
    status: Literal["online", "offline", "error"]
