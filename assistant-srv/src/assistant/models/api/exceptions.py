from typing import Optional

from fastapi import HTTPException, status


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str, headers: Optional[dict[str, str]] = None):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(HTTPException):
    def __init__(self, detail: str, headers: Optional[dict[str, str]] = None):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, headers=headers)


class NotFoundException(HTTPException):
    def __init__(self, detail: str, headers: Optional[dict[str, str]] = None):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, headers=headers)


class InternalServerErrorException(HTTPException):
    def __init__(self, detail: str, headers: Optional[dict[str, str]] = None):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail, headers=headers)


class BadRequestException(HTTPException):
    def __init__(self, detail: str, headers: Optional[dict[str, str]] = None):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, headers=headers)


class ConflictException(HTTPException):
    def __init__(self, detail: str, headers: Optional[dict[str, str]] = None):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail, headers=headers)
