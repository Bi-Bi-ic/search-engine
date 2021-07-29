from typing import Iterable, Union, Any

RepoResponse = Iterable[Union[str, Any]]

Created      = "CREATED"
Success      = "SUCCESS"
Uploaded     = "UPLOADED"
Deleted      = "DELETED"
NotFound     = "NOT_FOUND"
GetError     = "GET_ERROR"
CanNotCreate = "CAN_NOT_CREATE"
CannotGet = "CAN_NOT_GET"
CanNotUpdate = "CAN_NOT_UPDATE"
CanNotDelete = "CAN_NOT_DELETE"
CannotGetAll = "CAN_NOT_GET_ALL"
