from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional


@dataclass
class JobRequest:
    command: str
    job_name: Optional[str] = None
    num_nodes: int = 1
    num_tasks: int = 1
    cpus_per_task: int = 1
    gpus_per_task: int = 0
    wall_time: Optional[int] = None
    working_directory: Optional[str] = None
    environment: Dict[str, str] = field(default_factory=dict)
    output_file: Optional[str] = None
    error_file: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
