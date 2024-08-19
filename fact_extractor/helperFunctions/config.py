from pathlib import Path
from typing import List

import toml
from pydantic import BaseModel, Field

from helperFunctions.file_system import get_src_dir


class ExtractorUnpackConfig(BaseModel):
    blacklist: List[str] = Field(default_factory=list)
    data_folder: str = "/tmp/extractor"
    exclude: List[str] = Field(default_factory=list)


class ExpertSettings(BaseModel):
    statistics: bool = True
    unpack_threshold: float = 0.8
    header_overhead: int = 256
    compressed_file_types: List[str] = Field(default_factory=list)


class FactExtractorConfig(BaseModel):
    unpack: ExtractorUnpackConfig
    expert_settings: ExpertSettings


def load_config(config_file_name: str = 'main.toml') -> FactExtractorConfig:
    '''
    loads config of CONFIG_DIR/config_file_name
    Returns config object
    '''
    config_path = get_config_dir() / config_file_name
    if config_path.is_file():
        cfg_data = toml.loads(config_path.read_text())
        return FactExtractorConfig(**cfg_data)
    raise RuntimeError('Cannot load config')


def get_config_dir() -> Path:
    return Path(get_src_dir()) / 'config'
