from pydantic import BaseModel, Field
import uuid

class LibraryName(BaseModel):
    name: str
    explanation: str = Field(..., alias="description")

    class Config:
        populate_by_name = True

class ResultItem(LibraryName):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    starred: bool = False