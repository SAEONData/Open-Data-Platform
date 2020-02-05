from typing import List
import json

from pydantic import AnyHttpUrl
from requests import RequestException
from fastapi import HTTPException
import ckanapi
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_503_SERVICE_UNAVAILABLE

from odpapi.adapters import ODPAPIAdapter, ODPAPIAdapterConfig
from odpapi.models import PagerParams
from odpapi.models.metadata import (
    MetadataRecord,
    MetadataRecordIn,
    MetadataValidationResult,
    MetadataWorkflowResult,
)


class CKANAdapterConfig(ODPAPIAdapterConfig):
    """
    Config for the CKAN adapter, populated from the environment.
    """
    CKAN_URL: AnyHttpUrl

    class Config:
        env_prefix = 'CKAN_ADAPTER.'


class CKANAdapter(ODPAPIAdapter):

    def _call_ckan(self, action, access_token, **kwargs):
        """
        Call a CKAN API action function.

        For development/internal usage:
        If the NO_AUTH environment variable has been set to ``True``, we assume that the access_token
        parameter contains a CKAN API key instead of an access token.

        :param action: CKAN action function name
        :param access_token: the access token string to be forwarded to CKAN in the Authorization header
        :param kwargs: parameters to populate the data_dict for the action function
        :returns: the response dictionary / value returned from CKAN
        :raises HTTPException
        """
        if self.app_config.NO_AUTH:
            authorization_header = access_token  # assume it's a CKAN API key
        else:
            authorization_header = 'Bearer ' + access_token
        try:
            with ckanapi.RemoteCKAN(self.config.CKAN_URL) as ckan:
                return ckan.call_action(action, data_dict=kwargs, apikey=authorization_header,
                                        requests_kwargs={'verify': self.app_config.SERVER_ENV != 'development'})

        except RequestException as e:
            raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE, detail="Error sending request to CKAN: {}".format(e))

        except ckanapi.ValidationError as e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=e.error_dict)

        except ckanapi.NotAuthorized as e:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authorized to access CKAN resource: {}".format(e))

        except ckanapi.NotFound as e:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="CKAN resource not found: {}".format(e))

        except ckanapi.CKANAPIError as e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="CKAN error: {}".format(e))

    @staticmethod
    def _translate_from_ckan_record(ckan_record):
        """
        Convert a CKAN metadata record dict into a MetadataRecord object.
        """
        return MetadataRecord(
            institution=ckan_record['owner_org'],
            collection=ckan_record['metadata_collection_id'],
            metadata_standard=ckan_record['metadata_standard_id'],
            metadata=ckan_record['metadata_json'],
            id=ckan_record['id'],
            pid=ckan_record['name'] if ckan_record['name'] != ckan_record['id'] else None,
            doi=ckan_record['doi'],
            state=ckan_record['state'],
            errors=ckan_record['errors'],
            validated=ckan_record['validated'],
            workflow_state=ckan_record['workflow_state_id'],
        )

    def _translate_to_ckan_record(self, metadata_record: MetadataRecordIn, access_token: str):
        """
        Convert a MetadataRecordIn object into a CKAN metadata record dict.
        """
        return {
            'owner_org': metadata_record.institution,
            'metadata_collection_id': metadata_record.collection,
            'metadata_standard_id': metadata_record.metadata_standard,
            'metadata_json': json.dumps(metadata_record.metadata),
            'doi': metadata_record.doi,
            'auto_assign_doi': metadata_record.auto_assign_doi,
        }

    def list_metadata_records(self, institution_key: str, pager: PagerParams, access_token: str) -> List[MetadataRecord]:
        ckan_record_list = self._call_ckan(
            'metadata_record_list',
            access_token,
            owner_org=institution_key,
            offset=pager.skip,
            limit=pager.limit,
            all_fields=True,
            deserialize_json=True,
        )
        return [self._translate_from_ckan_record(record) for record in ckan_record_list]

    def get_metadata_record(self, id: str, access_token: str) -> MetadataRecord:
        ckan_record = self._call_ckan(
            'metadata_record_show',
            access_token,
            id=id,
            deserialize_json=True,
        )
        return self._translate_from_ckan_record(ckan_record)

    def create_or_update_metadata_record(self, metadata_record: MetadataRecordIn, access_token: str) -> MetadataRecord:
        input_dict = self._translate_to_ckan_record(metadata_record, access_token)
        ckan_record = self._call_ckan(
            'metadata_record_create',
            access_token,
            deserialize_json=True,
            **input_dict,
        )

        if not ckan_record['validated']:
            # try to validate the record, for convenience
            try:
                validaton_result = self.validate_metadata_record(ckan_record['id'], access_token)
                ckan_record.update({
                    'validated': True,
                    'errors': validaton_result.errors,
                })
            except:
                pass

        return self._translate_from_ckan_record(ckan_record)

    def update_metadata_record(self, id: str, metadata_record: MetadataRecordIn, access_token: str) -> MetadataRecord:
        input_dict = self._translate_to_ckan_record(metadata_record, access_token)
        ckan_record = self._call_ckan(
            'metadata_record_update',
            access_token,
            id=id,
            deserialize_json=True,
            **input_dict,
        )

        if not ckan_record['validated']:
            # try to validate the record, for convenience
            try:
                validaton_result = self.validate_metadata_record(ckan_record['id'], access_token)
                ckan_record.update({
                    'validated': True,
                    'errors': validaton_result.errors,
                })
            except:
                pass

        return self._translate_from_ckan_record(ckan_record)

    def delete_metadata_record(self, id: str, access_token: str) -> bool:
        self._call_ckan(
            'metadata_record_delete',
            access_token,
            id=id,
        )
        return True

    def validate_metadata_record(self, id: str, access_token: str) -> MetadataValidationResult:
        validation_activity_record = self._call_ckan(
            'metadata_record_validate',
            access_token,
            id=id,
        )
        validation_results = validation_activity_record['data']['results']
        validation_errors = {}
        for validation_result in validation_results:
            validation_errors.update(validation_result['errors'])

        return MetadataValidationResult(
            success=not validation_errors,
            errors=validation_errors,
        )

    def set_workflow_state_of_metadata_record(self, id: str, workflow_state: str, access_token: str) -> MetadataWorkflowResult:
        workflow_activity_record = self._call_ckan(
            'metadata_record_workflow_state_transition',
            access_token,
            id=id,
            workflow_state_id=workflow_state,
        )
        workflow_errors = workflow_activity_record['data']['errors']

        return MetadataWorkflowResult(
            success=not workflow_errors,
            errors=workflow_errors,
        )
