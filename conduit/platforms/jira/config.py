from pydantic import BaseModel

class JiraConfig(BaseModel):
    url: str
    api_token: str
