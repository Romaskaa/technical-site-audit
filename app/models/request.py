from pydantic import BaseModel

class AuditRequest(BaseModel):
    url: str
    depth: int = 3