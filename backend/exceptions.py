from fastapi import HTTPException, status


class InvalidToken(Exception):
    """Raised when a token is invalid or has been tampered with."""

    pass


class AuthenticationError(HTTPException):
    """Base class for authentication-related errors."""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class InvalidStateError(AuthenticationError):
    """Raised when the OAuth state is invalid."""

    def __init__(self):
        super().__init__(detail="Invalid state")


class UserCreationError(HTTPException):
    """Raised when there's an error creating or updating a user."""

    def __init__(self, detail: str = "Error processing user data"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )


class OAuthError(HTTPException):
    """Raised when there's an error in the OAuth process."""

    def __init__(self, detail: str = "OAuth error"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InternalServerError(HTTPException):
    """Raised for unexpected internal server errors."""

    def __init__(self, detail: str = "An unexpected error occurred"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )
