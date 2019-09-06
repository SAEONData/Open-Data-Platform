from typing import List
import re
import json
import os

from pydantic import BaseModel, UrlStr
from requests import RequestException
from fastapi import HTTPException
import ckanapi
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_503_SERVICE_UNAVAILABLE

from odpapi.lib.adapters import ODPAPIAdapter
from odpapi.lib.common import PagerParams
from odpapi.lib.metadata import MetadataRecordsFilter, DOI_REGEX
from odpapi.models.institution import (
    Institution,
    InstitutionIn,
    InstitutionOut,
)
from odpapi.models.metadata import (
    MetadataRecord,
    MetadataRecordIn,
    MetadataRecordOut,
    MetadataValidationResult,
    MetadataWorkflowResult,
)


OBJECT_NAME_SUFFIXES = {
    'organization': '',
    'metadata_collection': '-metadata',
    'infrastructure': '-infrastructure',
}


class CKANAdapterConfig(BaseModel):
    ckan_url: UrlStr = None
    use_apikey: bool = False


class CKANAdapter(ODPAPIAdapter):

    def __init__(self, app, routes, **config):
        super().__init__(app, routes, **config)
        config = CKANAdapterConfig(**config)
        # the environment variable CKAN_URL will override the local config
        self.ckan_url = os.getenv('CKAN_URL') or config.ckan_url
        self.use_apikey = config.use_apikey

    def _call_ckan(self, action, access_token, **kwargs):
        """
        Call a CKAN API action function.

        For certain development/internal scenarios:
        A CKAN API key may be provided instead of an access token if the CKANAdapter's ``config.use_apikey``
        option has been set to ``True``. Note: this will only work if the ``security.no_access_token_validation``
        config option has also been set to ``True``.

        :param action: CKAN action function name
        :param access_token: the access token string to be forwarded to CKAN in the Authorization header
        :param kwargs: parameters to populate the data_dict for the action function
        :returns: the response dictionary / value returned from CKAN
        :raises HTTPException
        """
        if self.use_apikey:
            authorization_header = access_token
        else:
            authorization_header = 'Bearer ' + access_token
        try:
            with ckanapi.RemoteCKAN(self.ckan_url) as ckan:
                return ckan.call_action(action, data_dict=kwargs, apikey=authorization_header)

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
    def _make_object_name(title: str, object_type: str):
        """
        Generate a name for a CKAN object. This may be suffixed according to the object
        type, to prevent name collisions between different types of CKAN group object.
        """
        suffix = OBJECT_NAME_SUFFIXES.get(object_type, '')
        name = title.lower() + suffix
        return re.sub(r'[^a-z0-9_-]+', '-', name)

    # region Institutions

    def list_institutions(self, pager: PagerParams, access_token: str) -> List[Institution]:
        return self._call_ckan(
            'organization_list',
            access_token,
            offset=pager.skip,
            limit=pager.limit,
            all_fields=True,
            include_datasets=False,
            include_dataset_count=False,
            include_extras=False,
            include_tags=False,
            include_groups=False,
            include_users=False,
            include_followers=False,
        )

    def get_institution(self, id_or_name: str, access_token: str) -> Institution:
        return self._call_ckan(
            'organization_show',
            access_token,
            id=id_or_name,
            include_datasets=False,
            include_dataset_count=False,
            include_extras=False,
            include_tags=False,
            include_groups=False,
            include_users=False,
            include_followers=False,
        )

    def add_institution(self, institution: InstitutionIn, access_token: str) -> InstitutionOut:
        return self._call_ckan(
            'organization_create',
            access_token,
            title=institution.title,
            description=institution.description,
            name=self._make_object_name(institution.title, 'organization'),
        )

    def update_institution(self, id_or_name: str, institution: InstitutionIn, access_token: str) -> InstitutionOut:
        # don't update the institution name as this may have unforeseen consequences
        return self._call_ckan(
            'organization_update',
            access_token,
            id=id_or_name,
            title=institution.title,
            description=institution.description,
        )

    def delete_institution(self, id_or_name: str, access_token: str) -> bool:
        self._call_ckan(
            'organization_delete',
            access_token,
            id=id_or_name,
        )
        return True

    # endregion Institutions

    # region Metadata

    @staticmethod
    def _translate_from_ckan_record(ckan_record):
        """
        Convert a CKAN metadata record dict into a MetadataRecord object.
        """
        return MetadataRecord(
            institution=ckan_record['owner_org'],
            metadata_standard=ckan_record['metadata_standard_id'],
            metadata=ckan_record['metadata_json'],
            infrastructures=[inf_dict['id'] for inf_dict in ckan_record['infrastructures']],
            id=ckan_record['id'],
            doi=ckan_record['name'] if re.match(DOI_REGEX, ckan_record['name']) else None,
            state=ckan_record['state'],
            errors=ckan_record['errors'],
            validated=ckan_record['validated'],
            workflow_state=ckan_record['workflow_state_id'],
        )

    def _translate_to_ckan_record(self, metadata_record: MetadataRecordIn, access_token: str):
        """
        Convert a MetadataRecordIn object into a CKAN metadata record dict.
        """
        collection_name = metadata_record.collection
        if collection_name is None:
            institution_dict = self.get_institution(metadata_record.institution, access_token)
            collection_name = institution_dict['name'] + OBJECT_NAME_SUFFIXES['metadata_collection']
        return {
            'owner_org': metadata_record.institution,
            'metadata_collection_id': collection_name,
            'infrastructures': [{'id': inf_id} for inf_id in metadata_record.infrastructures],
            'metadata_standard_id': metadata_record.metadata_standard,
            'metadata_json': json.dumps(metadata_record.metadata),
        }

    def list_metadata_records(self, filter: MetadataRecordsFilter, pager: PagerParams, access_token: str) -> List[MetadataRecord]:
        ckan_record_list = self._call_ckan(
            'metadata_record_list',
            access_token,
            owner_org=filter.institution,
            infrastructure_id=filter.infrastructure,
            offset=pager.skip,
            limit=pager.limit,
            all_fields=True,
            deserialize_json=True,
        )
        return [self._translate_from_ckan_record(record) for record in ckan_record_list]

    def get_metadata_record(self, id_or_doi: str, access_token: str) -> MetadataRecord:
        ckan_record = self._call_ckan(
            'metadata_record_show',
            access_token,
            id=id_or_doi,
            deserialize_json=True,
        )
        return self._translate_from_ckan_record(ckan_record)

    def create_or_update_metadata_record(self, metadata_record: MetadataRecordIn, access_token: str) -> MetadataRecordOut:
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

    def update_metadata_record(self, id_or_doi: str, metadata_record: MetadataRecordIn, access_token: str) -> MetadataRecordOut:
        input_dict = self._translate_to_ckan_record(metadata_record, access_token)
        ckan_record = self._call_ckan(
            'metadata_record_update',
            access_token,
            id=id_or_doi,
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

    def delete_metadata_record(self, id_or_doi: str, access_token: str) -> bool:
        self._call_ckan(
            'metadata_record_delete',
            access_token,
            id=id_or_doi,
        )
        return True

    def validate_metadata_record(self, id_or_doi: str, access_token: str) -> MetadataValidationResult:
        validation_activity_record = self._call_ckan(
            'metadata_record_validate',
            access_token,
            id=id_or_doi,
        )
        validation_results = validation_activity_record['data']['results']
        validation_errors = {}
        for validation_result in validation_results:
            validation_errors.update(validation_result['errors'])

        return MetadataValidationResult(
            success=not validation_errors,
            errors=validation_errors,
        )

    def set_workflow_state_of_metadata_record(self, id_or_doi: str, workflow_state: str, access_token: str) -> MetadataWorkflowResult:
        workflow_activity_record = self._call_ckan(
            'metadata_record_workflow_state_transition',
            access_token,
            id=id_or_doi,
            workflow_state_id=workflow_state,
        )
        workflow_errors = workflow_activity_record['data']['errors']

        return MetadataWorkflowResult(
            success=not workflow_errors,
            errors=workflow_errors,
        )

    # endregion Metadata
