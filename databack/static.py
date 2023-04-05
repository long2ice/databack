from starlette.exceptions import HTTPException
from starlette.staticfiles import StaticFiles
from starlette.status import HTTP_404_NOT_FOUND


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            response = await super().get_response(path, scope)
        except HTTPException as e:
            if e.status_code == HTTP_404_NOT_FOUND:
                response = await super().get_response("index.html", scope)
            else:
                raise
        return response
