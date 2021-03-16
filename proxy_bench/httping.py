from typing import NamedTuple, Tuple
import numpy as np
from loguru import logger

def extract_httping_run_result(stdout: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    
    """
    # Filter measurements from stdout
    lines = [str(l) for l in stdout if l.startswith(b'connected')]
    lines = [l[l.rfind('=')+1:].strip().rstrip(" ms\\n'") for l in lines]
    lines = list(map(lambda l: float(l), lines))
    
    # Ignore first result, this is often an outlier (httping specific)
    lines.pop(0)

    # Convert to numeric NumPy array
    times = np.array(lines)

    # Calculate run results
    stats = np.zeros(len(times))
    stats[0] = times.min()
    stats[1] = times.mean()
    stats[2] = times.max()
    stats[3] = times.std()

    return (times, stats)
