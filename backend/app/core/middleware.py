from app.logger import logger
import cProfile
import os
from datetime import datetime

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

PROFILER_DIR = "profiler/"


class ProfileMiddleware(BaseHTTPMiddleware):

  def __init__(
    self,
    app,
    some_attribute: str = "",
  ):
    super().__init__(app)
    self.some_attribute = some_attribute

  def save_profiler_stats(self, pr: cProfile.Profile, file_name: str):
    stats_file = os.path.join(PROFILER_DIR, file_name)
    pr.dump_stats(stats_file)

  def generate_file_name(self, request: Request) -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    path = "_".join(request.url.path.split("/"))
    return f"{timestamp}_{path}.prof"
  
  async def dispatch(self, request: Request, call_next):
    if request.query_params.get("profile", False):
      os.makedirs(PROFILER_DIR, exist_ok=True)
      file_name = self.generate_file_name(request)
      pr = cProfile.Profile()
      pr.enable()
      response = await call_next(request)
      pr.disable()
      self.save_profiler_stats(pr, file_name)
      return response
    return await call_next(request)
