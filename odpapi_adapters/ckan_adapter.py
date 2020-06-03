from typing import List, Dict, Any
import json
import logging

from pydantic import AnyHttpUrl
from requests import RequestException
from fastapi import HTTPException
import ckanapi
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_503_SERVICE_UNAVAILABLE

from odpapi.adapters import ODPAPIAdapter, ODPAPIAdapterConfig
from odpapi.models import Pagination
from odpapi.models.metadata import (
    MetadataRecord,
    MetadataRecordIn,
    MetadataValidationResult,
    MetadataWorkflowResult,
)

logger = logging.getLogger(__name__)


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
            raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Error sending request to CKAN: {}".format(e)) from e

        except ckanapi.ValidationError as e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                                detail="CKAN validation error: {}".format(e)) from e

        except ckanapi.NotAuthorized as e:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN,
                                detail="Not authorized to access CKAN resource: {}".format(e)) from e

        except ckanapi.NotFound as e:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                                detail="CKAN resource not found: {}".format(e)) from e

        except ckanapi.CKANAPIError as e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                                detail="CKAN error: {}".format(e)) from e

    @staticmethod
    def _translate_from_ckan_record(ckan_record):
        """
        Convert a CKAN metadata record dict into a MetadataRecord object.
        """
        return MetadataRecord(
            institution_key=ckan_record['owner_org'],
            collection_key=ckan_record['metadata_collection_id'],
            schema_key=ckan_record['metadata_standard_id'],
            metadata=ckan_record['metadata_json'],
            id=ckan_record['id'],
            pid=ckan_record['name'] if ckan_record['name'] != ckan_record['id'] else None,
            doi=ckan_record['doi'],
            validated=ckan_record['validated'],
            errors=ckan_record['errors'],
            state=ckan_record['workflow_state_id'],
        )

    @staticmethod
    def _translate_to_ckan_record(institution_key: str, metadata_record: MetadataRecordIn):
        """
        Convert a MetadataRecordIn object into a CKAN metadata record dict.
        """
        return {
            'owner_org': institution_key,
            'metadata_collection_id': metadata_record.collection_key,
            'metadata_standard_id': metadata_record.schema_key,
            'metadata_json': json.dumps(metadata_record.metadata),
            'doi': metadata_record.doi,
            'auto_assign_doi': metadata_record.auto_assign_doi,
        }

    def list_metadata_records(self,
                              institution_key: str,
                              pagination: Pagination,
                              access_token: str,
                              ) -> List[MetadataRecord]:
        ckan_record_list = self._call_ckan(
            'metadata_record_list',
            access_token,
            owner_org=institution_key,
            offset=pagination.offset,
            limit=pagination.limit,
            all_fields=True,
            deserialize_json=True,
        )
        return [self._translate_from_ckan_record(record) for record in ckan_record_list]

    def get_metadata_record(self,
                            institution_key: str,
                            record_id: str,
                            access_token: str,
                            ) -> MetadataRecord:
        ckan_record = self._call_ckan(
            'metadata_record_show',
            access_token,
            id=record_id,
            deserialize_json=True,
        )
        # check that the record has not been marked as deleted in CKAN, and
        # that it belongs to the given institution
        if ckan_record['state'] != 'active' or ckan_record['owner_org'] != institution_key:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="CKAN resource not found")

        return self._translate_from_ckan_record(ckan_record)

    def create_or_update_metadata_record(self,
                                         institution_key: str,
                                         metadata_record: MetadataRecordIn,
                                         access_token: str,
                                         ) -> MetadataRecord:
        input_dict = self._translate_to_ckan_record(institution_key, metadata_record)
        ckan_record = self._call_ckan(
            'metadata_record_create',
            access_token,
            deserialize_json=True,
            **input_dict,
        )
        record_id = ckan_record['id']
        self._annotate_metadata_record(record_id, metadata_record, access_token)

        if not ckan_record['validated']:
            # try to validate the record, for convenience
            try:
                validaton_result = self.validate_metadata_record(institution_key, record_id, access_token)
                ckan_record.update({
                    'validated': True,
                    'errors': validaton_result.errors,
                })
            except HTTPException as e:
                # note: this is a system error, not a validation error
                logger.warning(f"An error occurred while validating metadata record {record_id}: {e.detail}")

        return self._translate_from_ckan_record(ckan_record)

    def update_metadata_record(self,
                               institution_key: str,
                               record_id: str,
                               metadata_record: MetadataRecordIn,
                               access_token: str,
                               ) -> MetadataRecord:
        # make sure that the record we're updating belongs to the specified institution
        self.get_metadata_record(institution_key, record_id, access_token)

        input_dict = self._translate_to_ckan_record(institution_key, metadata_record)
        ckan_record = self._call_ckan(
            'metadata_record_update',
            access_token,
            id=record_id,
            deserialize_json=True,
            **input_dict,
        )
        self._annotate_metadata_record(record_id, metadata_record, access_token)

        if not ckan_record['validated']:
            # try to validate the record, for convenience
            try:
                validaton_result = self.validate_metadata_record(institution_key, record_id, access_token)
                ckan_record.update({
                    'validated': True,
                    'errors': validaton_result.errors,
                })
            except HTTPException as e:
                # note: this is a system error, not a validation error
                logger.warning(f"An error occurred while validating metadata record {record_id}: {e.detail}")

        return self._translate_from_ckan_record(ckan_record)

    def delete_metadata_record(self,
                               institution_key: str,
                               record_id: str,
                               access_token: str,
                               ) -> bool:
        # make sure that the record we're deleting belongs to the specified institution
        self.get_metadata_record(institution_key, record_id, access_token)

        self._call_ckan(
            'metadata_record_delete',
            access_token,
            id=record_id,
        )
        return True

    def validate_metadata_record(self,
                                 institution_key: str,
                                 record_id: str,
                                 access_token: str,
                                 ) -> MetadataValidationResult:
        # make sure that the record we're validating belongs to the specified institution
        self.get_metadata_record(institution_key, record_id, access_token)

        validation_activity_record = self._call_ckan(
            'metadata_record_validate',
            access_token,
            id=record_id,
        )
        validation_results = validation_activity_record['data']['results']
        validation_errors = {}
        for validation_result in validation_results:
            validation_errors.update(validation_result['errors'])

        return MetadataValidationResult(
            success=not validation_errors,
            errors=validation_errors,
        )

    def change_state_of_metadata_record(self,
                                        institution_key: str,
                                        record_id: str,
                                        state: str,
                                        access_token: str,
                                        ) -> MetadataWorkflowResult:
        # make sure that the record we're updating belongs to the specified institution
        self.get_metadata_record(institution_key, record_id, access_token)

        workflow_activity_record = self._call_ckan(
            'metadata_record_workflow_state_transition',
            access_token,
            id=record_id,
            workflow_state_id=state,
        )
        workflow_errors = workflow_activity_record['data']['errors']

        return MetadataWorkflowResult(
            success=not workflow_errors,
            errors=workflow_errors,
        )

    def _annotate_metadata_record(self,
                                  record_id: str,
                                  metadata_record: MetadataRecordIn,
                                  access_token: str,
                                  ) -> None:

        def annotate(key: str, value: Dict[str, Any]):
            try:
                self._call_ckan('metadata_record_workflow_annotation_create', access_token,
                                id=record_id, key=key, value=json.dumps(value))
            except HTTPException as e:
                err = None
                if e.status_code == 400:
                    # if we are doing a metadata record update, create annotation may fail with a 400 (duplicate),
                    # so we try updating the annotation
                    try:
                        self._call_ckan('metadata_record_workflow_annotation_update', access_token,
                                        id=record_id, key=key, value=json.dumps(value))
                    except HTTPException as e:
                        err = e.detail
                else:
                    err = e.detail

                if err:
                    logger.error(f'Error setting "{key}" annotation on metadata record {record_id}: {err}')

        annotate(
            key='terms_and_conditions',
            value={'accepted': metadata_record.terms_conditions_accepted},
        )
        annotate(
            key='data_agreement',
            value={'accepted': metadata_record.data_agreement_accepted, 'href': metadata_record.data_agreement_url},
        )
        annotate(
            key='capture_info',
            value={'capture_method': metadata_record.capture_method},
        )
