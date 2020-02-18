from enum import Enum
from datetime import date

from fastapi import Query


class MatchType(Enum):
    must = 'must'
    must_not = 'must_not'
    should = 'should'
    filter = 'filter'


class SortOrder(Enum):
    asc = 'asc'
    desc = 'desc'


class SearchParams:
    def __init__(
            self, *,
            match_type: MatchType = MatchType.must,
            output_fields: str = Query(None, description="Limit output to fields given in this comma-delimited list."),
            from_date: date = None,
            to_date: date = None,
            sort_field: str = None,
            sort_order: SortOrder = SortOrder.asc,
    ):
        self.match_type = match_type
        self.output_fields = output_fields
        self.from_date = from_date
        self.to_date = to_date
        self.sort_field = sort_field
        self.sort_order = sort_order
