from pydantic import BaseModel, UUID4


class InstitutionIn(BaseModel):
    title: str
    description: str = ''


class InstitutionOut(BaseModel):
    id: UUID4
    name: str
    state: str


class Institution(InstitutionIn, InstitutionOut):
    pass
