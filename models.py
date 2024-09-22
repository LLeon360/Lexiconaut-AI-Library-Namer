from pydantic import BaseModel, Field

class LibraryName(BaseModel):
    name: str
    explanation: str = Field(..., alias="description")

    class Config:
        populate_by_name = True

class ResultItem(LibraryName):
    starred: bool = False