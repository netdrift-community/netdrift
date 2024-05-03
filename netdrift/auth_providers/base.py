"""Base logic for all AuthProviders."""

from os import environ

from netdrift import exceptions


class AuthProviderBase:
    """Base logic implementation for all AuthProviders.

    If you need to create a new AuthProvider, you should ideally house the code
    inside a separate file and map it inside the implementations dict found in the
    __init__.py file.
    """

    def get_auth_credentials() -> dict:
        """Generic method implemented in all AuthProviders.

        This method should always return a dict of values that can be
        passed into the ncclient manager.connect() method. Some examples include:
            - username
            - password
            - key_filename
            - hostkey_verify
            - look_for_keys
            - ssh_config
        """
        raise NotImplementedError

    def set_auth_credentials() -> dict:
        """Generic method implemented in all AuthProviders.

        This method should handle any logic to store credentials
        for example, in a database or in a key/value store.
        """
        raise NotImplementedError


class AuthProviderEnvironmentVariable:
    """Implementation for env based AuthProviders.

    Note this provider shouldn't be used directly, but used for lower level
    implementation with env based AuthProvider implementations. For examples, see
    AuthProviderSSH.
    """

    def get_env(env_key: str) -> str:
        """Retrieve a specific environment variable.

        Args:
            env_key:        Name of the environment variable to get.
        """
        env_variable = environ.get(env_key)
        if not env_variable:
            raise exceptions.NetdriftAuthProviderError(
                f"Unable to find environment variable set as '{env_key}'."
            )

        return env_variable

    def set_env(env_key: str, env_value: str) -> None:
        """Set a specific environment variable.

        Args:
            env_key:        Name of the environment variable to set.
            env_value:      Value of the environment variable to set.
        """
        environ[env_key] = env_value
