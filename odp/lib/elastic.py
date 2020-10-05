from typing import List

from elasticsearch import Elasticsearch, ElasticsearchException, TransportError

from odp.api.models import Pagination
from odp.api.models.catalogue import QueryDSL, SearchHit, SearchResult, CatalogueRecord
from odp.lib.exceptions import ElasticsearchError


class ElasticClient:
    """ A client for the Elasticsearch metadata discovery catalogue """

    def __init__(
            self,
            server_url: str,
            indices: List[str],
    ):
        self.es_client = Elasticsearch([server_url])
        self.es_indices = indices

    def publish(self, record: CatalogueRecord) -> str:
        """ Publish a record to the catalogue, returning the name
        of the index to which the record was stored. """
        raise NotImplementedError

    def unpublish(self, record_id: str) -> None:
        """ Un-publish a record from the catalogue. The record is
        deleted from its index. """
        raise NotImplementedError

    def get(self, record_id: str) -> CatalogueRecord:
        """ Retrieve a record from the catalogue. """
        raise NotImplementedError

    def list(self, pagination: Pagination) -> List[CatalogueRecord]:
        """ Retrieve an unfiltered list of records from the catalogue. """
        raise NotImplementedError

    def query(self, query_dsl: QueryDSL, pagination: Pagination) -> SearchResult:
        """ Execute a search query across all indices. """
        try:
            response = self.es_client.search(
                index=','.join(self.es_indices),
                body={'query': query_dsl.query},
                from_=pagination.offset,
                size=pagination.limit,
            )
            return self._parse_response(response)

        except TransportError as e:
            status_code = e.status_code if type(e.status_code) is int else 503
            raise ElasticsearchError(status_code=status_code, error_detail=str(e))

        except ElasticsearchException as e:
            raise ElasticsearchError(status_code=400, error_detail=str(e))

    @staticmethod
    def _parse_response(r) -> SearchResult:
        return SearchResult(
            total_hits=(es_hits_dict := r.get('hits', {})).get('total', 0),
            max_score=es_hits_dict.get('max_score'),
            query_time=r.get('took'),
            hits=[SearchHit(
                score=hit['_score'],
                record=CatalogueRecord(
                    id=hit['_source']['record_id'],
                    doi=hit['_source'].get('doi'),
                    institution=hit['_source']['organization'],
                    collection=hit['_source']['collection'],
                    projects=hit['_source']['infrastructures'],
                    metadata=hit['_source']['metadata_json'],
                    published=True,
                )
            ) for hit in es_hits_dict.get('hits', [])],
        )
