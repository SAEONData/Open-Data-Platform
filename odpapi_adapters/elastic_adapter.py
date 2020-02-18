from typing import List, Dict

import requests
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE, HTTP_422_UNPROCESSABLE_ENTITY
from pydantic import AnyHttpUrl, BaseModel

from odpapi.adapters import ODPAPIAdapter, ODPAPIAdapterConfig
from odpapi.models import PagerParams
from odpapi.models.search import SearchParams


class ElasticAdapterConfig(ODPAPIAdapterConfig):
    """
    Config for the Elastic adapter, populated from the environment.
    """
    ES_AGENT_URL: AnyHttpUrl
    SEARCH_INDEXES: List[str]

    class Config:
        env_prefix = 'ELASTIC_ADAPTER.'


class ElasticAdapter(ODPAPIAdapter):

    class SearchResult(BaseModel):
        success: bool
        msg: str = ''
        error: str = ''
        result_length: int = 0
        results: List[Dict] = []

    async def search_metadata(self, search_params: SearchParams, pager_params: PagerParams, **search_terms) -> List[Dict]:
        results = []
        params = search_terms
        params.update({
            'match': search_params.match_type.value,
            'fields': search_params.output_fields,
            'from': search_params.from_date.strftime('%Y-%m-%d') if search_params.from_date else None,
            'to': search_params.to_date.strftime('%Y-%m-%d') if search_params.to_date else None,
            'sort': search_params.sort_field,
            'sortorder': search_params.sort_order.value,
            'start': pager_params.skip + 1,  # search agent 'start' is a 1-based record position
            'size': pager_params.limit,
        })
        try:
            for index in self.config.SEARCH_INDEXES:
                params['index'] = index
                r = requests.get(self.config.ES_AGENT_URL + '/search',
                                 params=params,
                                 timeout=None if self.app_config.SERVER_ENV == 'development' else 30,
                                 headers={'Accept': 'application/json'})
                r.raise_for_status()
                result = self.SearchResult(**r.json())
                if result.success:
                    results += result.results
                else:
                    raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail=result.msg or result.error)

            return results

        except requests.HTTPError as e:
            try:
                error_detail = e.response.json()
            except ValueError:
                error_detail = e.response.reason
            raise HTTPException(status_code=e.response.status_code, detail=error_detail)

        except requests.RequestException as e:
            raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
