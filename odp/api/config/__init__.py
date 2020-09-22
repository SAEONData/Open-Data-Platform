from typing import List, Union, Literal, Dict, Type

from pydantic import BaseSettings, constr, AnyHttpUrl, PostgresDsn

from odp.api.config.catalogue import CatalogueConfig
from odp.api.config.datacite import DataciteConfig
from odp.api.models import KEY_REGEX
from odp.api.models.env import ServerEnv


class Config(BaseSettings):
    """ Environment variables used by the ODP admin and public APIs """

    # deployment environment
    SERVER_ENV: ServerEnv

    # (optional) URL path prefix at which the API is mounted, e.g. `/api`
    PATH_PREFIX: constr(regex=r'^(/\w+)*$') = ''

    # (optional) JSON-encoded list of allowed CORS origins; `["*"]` to allow any origin
    ALLOW_ORIGINS: List[Union[Literal['*'], AnyHttpUrl]] = []

    # URL of the ODP accounts database
    DATABASE_URL: PostgresDsn

    # institution key of the institution that owns the platform
    ADMIN_INSTITUTION: constr(regex=KEY_REGEX)

    # URL of the ODP admin API
    ADMIN_API_URL: AnyHttpUrl

    # URL of the Hydra admin API
    HYDRA_ADMIN_URL: AnyHttpUrl

    # URL of the CKAN metadata management server
    CKAN_URL: AnyHttpUrl

    _extras: Dict[str, Union[Type[BaseSettings], BaseSettings]] = {
        'CATALOGUE': CatalogueConfig,
        'DATACITE': DataciteConfig,
    }

    def __getattr__(self, name) -> BaseSettings:
        """ Provides lazy loading of environment variable subgroups.

        This allows us to reference an additional settings instance in an
        intuitive way (using the dotted form as defined by the ``env_prefix``
        of the settings class), without having to either optionalize all its
        attributes or force them to appear in the environment of services that
        don't require them.
        """
        if name in self._extras:
            if not isinstance(self._extras[name], BaseSettings):
                self._extras[name] = (self._extras[name])()
            return self._extras[name]

        raise AttributeError
