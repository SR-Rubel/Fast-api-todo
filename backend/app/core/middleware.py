import cProfile
import os
from datetime import datetime

from fastapi import Request
# from pyinstrument import Profiler
# from pyinstrument.renderers.html import HTMLRenderer
# from pyinstrument.renderers.speedscope import SpeedscopeRenderer
from starlette.middleware.base import BaseHTTPMiddleware

PROFILER_DIR = "profiler/"


async def profile_middleware(request: Request, call_next):
  os.makedirs(PROFILER_DIR, exist_ok=True)
  file_name = generate_file_name(request)
  pr = cProfile.Profile()
  pr.enable()
  response = await call_next(request)
  pr.disable()
  save_profiler_stats(pr, file_name)
  return response


def generate_file_name(request: Request) -> str:
  timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
  path = "_".join(request.url.path.split("/"))
  return f"{timestamp}_{path}.prof"


def save_profiler_stats(pr: cProfile.Profile, file_name: str):
  stats_file = os.path.join(PROFILER_DIR, file_name)
  pr.dump_stats(stats_file)


# class PyinstrumentMiddleware(BaseHTTPMiddleware):
#   """Profile the current request
#   Taken from https://pyinstrument.readthedocs.io/en/latest/guide.html#profile-a-web-request-in-fastapi
#   with small improvements.
#   """

#   def __init__(
#     self,
#     app,
#     some_attribute: str = "",
#   ):
#     super().__init__(app)
#     self.some_attribute = some_attribute

#   async def dispatch(self, request: Request, call_next):
#     profile_type_to_ext = {"html": "html", "speedscope": "speedscope.json"}
#     profile_type_to_renderer = {
#       "html": HTMLRenderer,
#       "speedscope": SpeedscopeRenderer,
#     }
#     if request.query_params.get("profile", False):
#       profile_type = request.query_params.get("profile_format", "speedscope")

#       with Profiler(interval=0.001) as profiler:
#         response = await call_next(request)
#       extension = profile_type_to_ext[profile_type]
#       renderer = profile_type_to_renderer[profile_type]()
#       with open(f"profile.{extension}", "w") as out:
#         out.write(profiler.output(renderer=renderer))
#       return response
#     return await call_next(request)