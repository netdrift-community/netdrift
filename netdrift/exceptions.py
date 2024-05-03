from fastapi import status

from netdrift.models.mongo import PyObjectId
from netdrift.enums import APIExceptionCodes


class NetdriftBaseException(Exception):
    """Generic Netdrift exception implementation."""

    def __init__(
        self,
        code: int,
        reason: str,
        message: str,
        status: int | None = None,
        reference_error: str | None = None,
    ):
        """All netdrift exceptions should inherit the base exception.

        Args:
            code:               Application specific error code defined in the Netdrift API.
            reason:             Simplified explanation of the error for a human.
            message:            More detailed explanation of the error.
            status:             HTTP error code.
            reference_error:    URI of error if applicable.
        """
        self.code = code
        self.reason = reason
        self.message = str(message)
        self.status = status
        self.reference_error = reference_error

        super().__init__(
            self.message,
        )

    def json(self) -> dict:
        """Error formatting for JSON type response."""
        return {
            "code": self.code,
            "reason": self.reason,
            "message": self.message,
            "status": self.status,
            "reference_error": self.reference_error,
        }


class NetdriftXMLParserError(NetdriftBaseException):
    """Raised when an XML parsing error occurs."""

    def __init__(self, detail: str):
        super().__init__(
            code=APIExceptionCodes.XML_PARSER_ERROR,
            reason="XML formatting error has occured.",
            message=detail,
            status=status.HTTP_400_BAD_REQUEST,
        )


class NetdriftFullIntentConfigNotFoundError(NetdriftBaseException):
    """Raised when a FullIntentConfig is not found in the database."""

    def __init__(self, id: PyObjectId):
        super().__init__(
            code=APIExceptionCodes.FULL_INTENT_CONFIG_NOT_FOUND,
            reason=f"FullIntentConfig '{id}' not found.",
            message=self.__doc__,
            status=status.HTTP_400_BAD_REQUEST,
        )


class NetdriftPartialIntentConfigNotFoundError(NetdriftBaseException):
    """Raised when a PartialIntentConfig is not found in the database."""

    def __init__(self, id: PyObjectId):
        super().__init__(
            code=APIExceptionCodes.PARTIAL_INTENT_CONFIG_NOT_FOUND,
            reason=f"PartialIntentConfig '{id}' not found.",
            message=self.__doc__,
            status=status.HTTP_400_BAD_REQUEST,
        )


class NetdriftFullIntentConfigAlreadyExistError(NetdriftBaseException):
    """Raised when a FullIntentConfig already exist in the database."""

    def __init__(self):
        super().__init__(
            code=APIExceptionCodes.FULL_INTENT_CONFIG_ALREADY_EXIST,
            reason="FullIntentConfig already exist.",
            message=self.__doc__,
            status=status.HTTP_400_BAD_REQUEST,
        )


class NetdriftPartialIntentConfigAlreadyExistError(NetdriftBaseException):
    """Raised when a PartialIntentConfig already exist in the database."""

    def __init__(self):
        super().__init__(
            code=APIExceptionCodes.PARTIAL_INTENT_CONFIG_ALREADY_EXIST,
            reason="PartialIntentConfig already exist.",
            message=self.__doc__,
            status=status.HTTP_400_BAD_REQUEST,
        )


class NetdriftPartialIntentConfigFilterAlreadyExistError(NetdriftBaseException):
    """Raised when a PartialIntentConfig filter already exist in the database."""

    def __init__(self):
        super().__init__(
            code=APIExceptionCodes.PARTIAL_INTENT_CONFIG_FILTER_ALREADY_EXIST,
            reason="PartialIntentConfig filter already exist.",
            message=self.__doc__,
            status=status.HTTP_400_BAD_REQUEST,
        )


class NetdriftIntentGroupAlreadyExistError(NetdriftBaseException):
    """Raised when an IntentGroup already exist in the database."""

    def __init__(self):
        super().__init__(
            code=APIExceptionCodes.INTENT_GROUP_ALREADY_EXIST,
            reason="IntentConfig already exist.",
            message=self.__doc__,
            status=status.HTTP_400_BAD_REQUEST,
        )


class NetdriftFullIntentConfigUpdateError(NetdriftBaseException):
    """Raised when a FullIntentConfigUpdate has a generic error."""

    def __init__(
        self, message: str, reason: str = "Unable to update FullIntentConfig."
    ):
        super().__init__(
            code=APIExceptionCodes.FULL_INTENT_CONFIG_UPDATE_FAILED,
            reason=reason,
            message=message,
            status=status.HTTP_400_BAD_REQUEST,
        )


class NetdriftPartialIntentConfigUpdateError(NetdriftBaseException):
    """Raised when a PartialIntentConfigUpdate has a generic error."""

    def __init__(
        self, message: str, reason: str = "Unable to update PartialIntentConfig."
    ):
        super().__init__(
            code=APIExceptionCodes.PARTIAL_INTENT_CONFIG_UPDATE_FAILED,
            reason=reason,
            message=message,
            status=status.HTTP_400_BAD_REQUEST,
        )


class NetdriftIntentConfigAPILockError(NetdriftBaseException):
    """Raised when a FullIntentConfig or PartialIntentConfig netdrift_managed attribute is changed from 'True' to 'False' via the API."""

    def __init__(self):
        super().__init__(
            code=APIExceptionCodes.INTENT_CONFIG_API_LOCK,
            reason="netdrift_managed attribute can not be changed via the API because this will break the discovery logic.",
            message=self.__doc__,
            status=status.HTTP_400_BAD_REQUEST,
        )


class NetdriftIntentConfigHostnameLockError(NetdriftBaseException):
    """Raised when a FullIntentConfig or PartialIntentConfig hostname attribute is changed. This attribute should never be changed."""

    def __init__(self):
        super().__init__(
            code=APIExceptionCodes.INTENT_CONFIG_HOSTNAME_LOCK,
            reason="hostname attribute can not be changed on an Intent because this will break logic in code.",
            message=self.__doc__,
            status=status.HTTP_400_BAD_REQUEST,
        )


class NetdriftIntentGroupNotFoundError(NetdriftBaseException):
    """Raised when a IntentGroup is not found in the database."""

    def __init__(self, id: PyObjectId):
        super().__init__(
            code=APIExceptionCodes.INTENT_GROUP_NOT_FOUND,
            reason=f"IntentGroup '{id}' not found.",
            message=self.__doc__,
            status=status.HTTP_400_BAD_REQUEST,
        )


class NetdriftIntentGroupHostnameManagedError(NetdriftBaseException):
    """Raised when a common IntentGroup (no hostname attribute) tries to inherit a PartialIntentConfig or IntentGroup which is managed via a hostname."""

    def __init__(self):
        super().__init__(
            code=APIExceptionCodes.INTENT_GROUP_HOSTNAME_MANAGED,
            reason="IntentGroups without hostname attribute can not inherit PartialIntentConfig or IntentGroup objects which is managed via a hostname.",
            message=self.__doc__,
            status=status.HTTP_400_BAD_REQUEST,
        )


class NetdriftIntentGroupHostnameMismatchError(NetdriftBaseException):
    """Raised when an IntentGroup managed with hostname attribute tries to inherit a PartialIntentConfig or IntentGroup where the hostname doesn't match."""

    def __init__(self):
        super().__init__(
            code=APIExceptionCodes.INTENT_GROUP_HOSTNAME_MISMATCH,
            reason="IntentGroups managed with hostname attribute must only inherit PartialIntentConfig or IntentGroup objects with the same hostname attribute.",
            message=self.__doc__,
            status=status.HTTP_400_BAD_REQUEST,
        )


class NetdriftIntentGroupIntentRecursionError(NetdriftBaseException):
    """Raised when an IntentGroup manages a specific PartialIntentConfig at the root level which is trying to also be managed by an inherited group."""

    def __init__(self):
        super().__init__(
            code=APIExceptionCodes.INTENT_GROUP_POTENTIAL_RECURSION,
            reason="IntentGroups can not inherit other groups that manage the same PartialIntentConfig and/or IntentGroup managed by other resources.",
            message=self.__doc__,
            status=status.HTTP_400_BAD_REQUEST,
        )


class NetdriftIntentGroupIntentDuplicationError(NetdriftBaseException):
    """Raised when an IntentGroup has duplicated PartialIntentConfig ids either directly or indirectly via group inheritance."""

    def __init__(self):
        super().__init__(
            code=APIExceptionCodes.INTENT_GROUP_DUPLICATION,
            reason="An existing Intent has been found either directly or indirectly via an inherited group. You can not manage the same Intent from multiple resources.",
            message=self.__doc__,
            status=status.HTTP_400_BAD_REQUEST,
        )


class NetdriftAuthProviderError(NetdriftBaseException):
    """Raised when logic implemented in an AuthProvider has failed/caught an error."""

    def __init__(self, reason: str):
        super().__init__(
            code=APIExceptionCodes.AUTH_PROVIDER_LOGIC_ERROR,
            reason=reason,
            message=self.__doc__,
            status=status.HTTP_400_BAD_REQUEST,
        )


class NetdriftNotImplementedError(NetdriftBaseException):
    """Raised when the specific logic/endpoint has not been fully implemented."""

    def __init__(self):
        super().__init__(
            code=APIExceptionCodes.NOT_IMPLEMENTED_ERROR,
            reason="This endpoint/logic is currently not implemented.",
            message=self.__doc__,
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )
