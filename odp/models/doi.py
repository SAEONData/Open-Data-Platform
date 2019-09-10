from pydantic import BaseModel, Schema

from ..lib.metadata import DOI_REGEX


class NewDOI(BaseModel):
    doi: str = Schema(None, regex=DOI_REGEX)
