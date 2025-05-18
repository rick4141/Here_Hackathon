from pydantic import BaseModel
from typing import Optional

class PipelineRequest(BaseModel):
    pois_dir: str = "data/POIs"
    streets_dir: str = "data/STREETS_NAMING_ADDRESSING"
    output_dir: str = "output"
    test_mode: bool = False
    test_file: Optional[str] = None
    base_logdir: str = "logs"
