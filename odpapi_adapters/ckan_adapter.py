from typing import List
import re
import json
import os

from pydantic import BaseModel, UrlStr, UUID4
from requests import RequestException
from fastapi import HTTPException
import ckanapi

from odpapi.lib.adapter import ODPAPIAdapter
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
    ckan_url: UrlStr
    ckan_apikey: UUID4


class CKANAdapter(ODPAPIAdapter):

    def __init__(self, routes, **config):
        super().__init__(routes, **config)
        # ignore the config file and get the values from the environment
        config = {
            'ckan_url': os.environ.get('CKAN_URL'),
            'ckan_apikey': os.environ.get('CKAN_APIKEY'),
        }
        config = CKANAdapterConfig(**config)
        self.ckan_url = config.ckan_url
        self.ckan_apikey = config.ckan_apikey

    def _call_ckan(self, action, **kwargs):
        """
        Call a CKAN API action function.

        :param action: CKAN action function name
        :param kwargs: parameters to populate the data_dict for the action function
        :returns: the response dictionary / value returned from CKAN
        :raises HTTPException
        """
        try:
            with ckanapi.RemoteCKAN(self.ckan_url, apikey=self.ckan_apikey) as ckan:
                return ckan.call_action(action, data_dict=kwargs)

        except RequestException as e:
            raise HTTPException(status_code=503, detail="Error sending request to CKAN: {}".format(e))

        except ckanapi.ValidationError as e:
            raise HTTPException(status_code=400, detail=e.error_dict)

        except ckanapi.NotAuthorized as e:
            raise HTTPException(status_code=403, detail="Not authorized to access CKAN resource: {}".format(e))

        except ckanapi.NotFound as e:
            raise HTTPException(status_code=404, detail="CKAN resource not found: {}".format(e))

        except ckanapi.CKANAPIError as e:
            raise HTTPException(status_code=400, detail="CKAN error: {}".format(e))

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

    def list_institutions(self, pager: PagerParams) -> List[Institution]:
        return self._call_ckan(
            'organization_list',
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

    def get_institution(self, id_or_name: str) -> Institution:
        return self._call_ckan(
            'organization_show',
            id=id_or_name,
            include_datasets=False,
            include_dataset_count=False,
            include_extras=False,
            include_tags=False,
            include_groups=False,
            include_users=False,
            include_followers=False,
        )

    def add_institution(self, institution: InstitutionIn) -> InstitutionOut:
        return self._call_ckan(
            'organization_create',
            title=institution.title,
            description=institution.description,
            name=self._make_object_name(institution.title, 'organization'),
        )

    def update_institution(self, id_or_name: str, institution: InstitutionIn) -> InstitutionOut:
        # don't update the institution name as this may have unforeseen consequences
        return self._call_ckan(
            'organization_update',
            id=id_or_name,
            title=institution.title,
            description=institution.description,
        )

    def delete_institution(self, id_or_name: str) -> bool:
        self._call_ckan(
            'organization_delete',
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

    def _translate_to_ckan_record(self, metadata_record: MetadataRecordIn):
        """
        Convert a MetadataRecordIn object into a CKAN metadata record dict.
        """
        collection_name = metadata_record.collection
        if collection_name is None:
            institution_dict = self.get_institution(metadata_record.institution)
            collection_name = institution_dict['name'] + OBJECT_NAME_SUFFIXES['metadata_collection']
        return {
            'owner_org': metadata_record.institution,
            'metadata_collection_id': collection_name,
            'infrastructures': [{'id': inf_id} for inf_id in metadata_record.infrastructures],
            'metadata_standard_id': metadata_record.metadata_standard,
            'metadata_json': json.dumps(metadata_record.metadata),
        }

    def list_metadata_records(self, filter: MetadataRecordsFilter, pager: PagerParams) -> List[MetadataRecord]:
        ckan_record_list = self._call_ckan(
            'metadata_record_list',
            owner_org=filter.institution,
            infrastructure_id=filter.infrastructure,
            offset=pager.skip,
            limit=pager.limit,
            all_fields=True,
            deserialize_json=True,
        )
        return [self._translate_from_ckan_record(record) for record in ckan_record_list]

    def get_metadata_record(self, id_or_doi: str) -> MetadataRecord:
        ckan_record = self._call_ckan(
            'metadata_record_show',
            id=id_or_doi,
            deserialize_json=True,
        )
        return self._translate_from_ckan_record(ckan_record)

    def create_or_update_metadata_record(self, metadata_record: MetadataRecordIn) -> MetadataRecordOut:
        input_dict = self._translate_to_ckan_record(metadata_record)
        ckan_record = self._call_ckan(
            'metadata_record_create',
            deserialize_json=True,
            **input_dict,
        )

        if not ckan_record['validated']:
            # try to validate the record, for convenience
            try:
                validaton_result = self.validate_metadata_record(ckan_record['id'])
                ckan_record.update({
                    'validated': True,
                    'errors': validaton_result.errors,
                })
            except:
                pass

        return self._translate_from_ckan_record(ckan_record)

    def update_metadata_record(self, id_or_doi: str, metadata_record: MetadataRecordIn) -> MetadataRecordOut:
        input_dict = self._translate_to_ckan_record(metadata_record)
        ckan_record = self._call_ckan(
            'metadata_record_update',
            id=id_or_doi,
            deserialize_json=True,
            **input_dict,
        )

        if not ckan_record['validated']:
            # try to validate the record, for convenience
            try:
                validaton_result = self.validate_metadata_record(ckan_record['id'])
                ckan_record.update({
                    'validated': True,
                    'errors': validaton_result.errors,
                })
            except:
                pass

        return self._translate_from_ckan_record(ckan_record)

    def delete_metadata_record(self, id_or_doi: str) -> bool:
        self._call_ckan(
            'metadata_record_delete',
            id=id_or_doi,
        )
        return True

    def validate_metadata_record(self, id_or_doi: str) -> MetadataValidationResult:
        validation_activity_record = self._call_ckan(
            'metadata_record_validate',
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

    def set_workflow_state_of_metadata_record(self, id_or_doi: str, workflow_state: str) -> MetadataWorkflowResult:
        workflow_activity_record = self._call_ckan(
            'metadata_record_workflow_state_transition',
            id=id_or_doi,
            workflow_state_id=workflow_state,
        )
        workflow_errors = workflow_activity_record['data']['errors']

        return MetadataWorkflowResult(
            success=not workflow_errors,
            errors=workflow_errors,
        )

    # endregion Metadata
