from .repositories import *

def status_as_string(status):
    switcher={
        Created:        "Created",
        Success:        "Success",
        Uploaded:       "Uploaded",
        Deleted:        "Deleted",
        NotFound:       "Not Found",
        GetError:       "Get Error",
        CanNotCreate:   "Can not Create",
        CannotGet:      "Can not Get",
        CanNotUpdate:   "Can not Update",
        CanNotDelete:   "Can not Delete",
        CannotGetAll:   "Can not Get All",
    }

    return switcher.get(status, "")

def status_as_bool(status):
    switcher={
        Created:        True,
        Success:        True,
        Uploaded:       True,
        Deleted:        True,
        NotFound:       False,
        GetError:       False,
        CanNotCreate:   False,
        CannotGet:      False,
        CanNotUpdate:   False,
        CanNotDelete:   False,
        CannotGetAll:   False,
    }

    return switcher.get(status, False)