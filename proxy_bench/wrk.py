from typing import Tuple
import numpy as np
from loguru import logger

def extract_wrk_run_result(stdout: list) -> Tuple[np.ndarray, np.ndarray]:
    """
    
    """
    lines = []
    for line in stdout:
        lines.extend(line.splitlines())

    # Filter measurements from stdout
    lines = [str(l) for l in lines if l.startswith(b'Requests/sec:')]
    lines = [l[l.rfind(':')+1:].strip().rstrip("'") for l in lines]
    lines = list(map(lambda l: float(l), lines))
    
    # Convert to numeric NumPy array
    times = np.array(lines * 4)

    # Calculate run results
    stats = np.zeros(len(times))
    stats[0] = times.min()
    stats[1] = times.mean()
    stats[2] = times.max()
    stats[3] = times.std()

    return (times, stats)
