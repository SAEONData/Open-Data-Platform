from typing import List

from elasticsearch import Elasticsearch, ElasticsearchException, TransportError
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE, HTTP_400_BAD_REQUEST

from odp.api.models import Pagination
from odp.api.models.search import QueryDSL, SearchHit, SearchResult


class ElasticClient:
    """ A client for the Elasticsearch metadata discovery catalogue """

    def __init__(
            self,
            server_url: str,
            indices: List[str],
    ):
        self.es_client = Elasticsearch([server_url])
        self.es_indices = indices

    @staticmethod
    def _parse_elastic_response(r) -> SearchResult:
        return SearchResult(
            total_hits=(es_hits_dict := r.get('hits', {})).get('total', 0),
            max_score=es_hits_dict.get('max_score', 0.0),
            query_time=r.get('took', 0),
            hits=[SearchHit(
                metadata=hit['_source']['metadata_json'],
                metadata_id=hit['_source']['record_id'],
                score=hit['_score'],
            ) for hit in es_hits_dict.get('hits', [])],
        )

    async def search_metadata(self, query_dsl: QueryDSL, pagination: Pagination) -> SearchResult:
        try:
            response = self.es_client.search(
                index=','.join(self.es_indices),
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
