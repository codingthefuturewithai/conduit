from pydantic import BaseModel


class JiraConfig(BaseModel):
    url: str
    api_token: str
    email: str  # Email address associated with the API token
