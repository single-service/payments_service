from functools import lru_cache
from string import Template

from pydantic import BaseSettings


class CommonConfig(BaseSettings):
    ciflags: Template = Template("ciflags_$cip_id")


@lru_cache
def get_all_keys() -> CommonConfig:
    return CommonConfig()


all_keys: CommonConfig = get_all_keys()
