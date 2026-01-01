from pydantic import BaseModel

class NewsRequest(BaseModel):
    query: str
    limit: int