from __future__ import annotations

from typing import Dict, Type

from pydantic import BaseSettings


class BaseConfig(BaseSettings):
    """ Base configuration class.

    This provides lazy loading of environment variable subgroups,
    allowing us to reference sub-configurations in an intuitive way
    and without having to either optionalize all attributes of a sub-
    configuration or force them to appear in the environment of
    services that don't require them.

    The `_subconfig` mapping is used to define the set of sub-
    configurations that are available on a 'parent' config class.
    The keys become attributes on the parent config instance; the
    values indicate the corresponding sub-config classes, which are
    instantiated (and their settings read from the environment and
    validated) upon first access.

    Note: while sub-configurations and their values are dereferenced
    in code using the usual dot-notation, the corresponding environment
    variables - and hence the `env_prefix`s - should use underscores
    in place of dots, so that environment variables may be used in
    shell commands/scripts.
    """

    _subconfig: Dict[str, Type[BaseConfig] | BaseConfig] = {}

    def __getattr__(self, name) -> BaseConfig:
        if name in self._subconfig:
            if not isinstance(self._subconfig[name], BaseConfig):
                self._subconfig[name] = (self._subconfig[name])()
            return self._subconfig[name]

        raise AttributeError

    class Config:
        env_file = '.env'
