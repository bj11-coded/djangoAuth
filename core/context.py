from contextvars import ContextVar

_request_id : ContextVar[str] = ContextVar('request_id', default=None)

#  suppose Darpan (_request_id =  ac45)
#  token = set_reqiest_id(ac45) here in this function .set returns the token
def set_request_id(value: str ):
    return _request_id.set(value)


# resets the token after the request is over 
def reset_request_id(token) -> None:
    _request_id.reset(token)

# gets the request id from the context var
def get_request_id() -> str:
    return _request_id.get()


'''
suppose 
    darpan - GET /api/student/45
    aarti - GET /api/student/44
    suraj - GET /api/student/43
    sachin - GET /api/student/42
    +100 other request

FLow :
    Reuest (Darpan)  -->  Middleware   ---> View/Set   ---> Serailzer --> Database 

suppose something went wrong 
    - User requested student Data 
    - Database Query Execute 
    - Serailization Failed 
    - internal Server Error

After using ContextVar 
    - Darpan --> _request_id = acv34
    - Aarti --> _request_id = acv35
    - Suraj --> _request_id = acv36
    - Sachin --> _request_id = acv37

ContextVar stores a value for the current execution context.

'''