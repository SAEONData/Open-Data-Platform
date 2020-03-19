from typing import List

from pydantic import AnyHttpUrl, validator
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE, HTTP_400_BAD_REQUEST
from elasticsearch import Elasticsearch, ElasticsearchException, TransportError

from odpapi.adapters import ODPAPIAdapter, ODPAPIAdapterConfig
from odpapi.models import Pagination
from odpapi.models.search import QueryDSL, SearchHit


class ElasticAdapterConfig(ODPAPIAdapterConfig):
    """
    Config for the Elastic adapter, populated from the environment.
    """
    ES_URL: AnyHttpUrl
    INDICES: List[str]

    @validator('ES_URL')
    def check_port(cls, v):
        if not v.port:
            raise ValueError("Port must be specified in the Elasticsearch URL")
        return v

    class Config:
        env_prefix = 'ELASTIC_ADAPTER.'


class ElasticAdapter(ODPAPIAdapter):

    def __init__(self, app, config: ElasticAdapterConfig):
        super().__init__(app, config)
        self.es_client = Elasticsearch([config.ES_URL])

    @staticmethod
    def _parse_elastic_response(r) -> List[SearchHit]:
        results = []
        for hit in r.get('hits', {}).get('hits', []):
            results += [SearchHit(
                metadata=hit['_source']['metadata_json'],
                institution=hit['_source']['organization'],
                collection=hit['_source']['collection'],
                id=hit['_source']['record_id'],
            )]
        return results

    async def search_metadata(self, query_dsl: QueryDSL, pagination: Pagination) -> List[SearchHit]:
        try:
            response = self.es_client.search(
                index=','.join(self.config.INDICES),
                body={'query': query_dsl.query},
                from_=pagination.offset,
                size=pagination.limit,
            )
            return self._parse_elastic_response(response)

        except TransportError as e:
            status_code = e.status_code if type(e.status_code) is int else HTTP_503_SERVICE_UNAVAILABLE
            raise HTTPException(status_code=status_code, detail=str(e))

        except ElasticsearchException as e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
