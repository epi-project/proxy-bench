from typing import NamedTuple, Tuple
import numpy as np
from loguru import logger

class RunResult(NamedTuple):
    mean: float
    std: float
    min: float
    max: float


def extract_httping_run_result(stdout: str) -> Tuple[np.ndarray, RunResult]:
    """
    
    """
    lines = stdout.splitlines()
    
    # Filter measurements from stdout
    lines = [str(l) for l in lines if l.startswith(b'connected')]
    lines = [l[l.rfind('=')+1:].strip().rstrip(" ms '") for l in lines]
    lines = list(map(lambda l: float(l), lines))
    
    # Ignore first result, this is often an outlier (httping specific)
    lines.pop(0)

    # Convert to numeric NumPy array
    times = np.array(lines)

    # Calculate run results
    run_result = RunResult(
        times.mean(),
        times.std(),
        times.min(),
        times.max(),
    )

    return (times, run_result)
