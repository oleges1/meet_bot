import os

TOKEN = os.getenv("TOKEN")
PROXY_URL = os.getenv("PROXY_URL")
PROXY_LOGIN = os.getenv("PROXY_LOGIN")
PROXY_PASS = os.getenv("PROXY_URL")

(   ACTION
    , LIST_OF_MEETINGS
    , LOCATION
    , LOCATION_NAME
    , LOCATION_ADDED
    , WORKSPACE
    , WORKSPACE_ADDED
    , MEETING
    , MEETING_USERS
    , MEETING_WORKSPACE
    , MEETING_LOCATION
    , MEETING_START
    , MEETING_END
    , MEETING_ADDED
    ) = range(14)

end_command = "/done"