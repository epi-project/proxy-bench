from . import containers, httping, utils
from docker import DockerClient
from loguru import logger
from pandas import DataFrame, ExcelWriter
from sys import stdout
from yaml import load, Loader

RUNS=5

def load_bench_matrix():
    """..."""
    with open("matrix.yml") as f:
        matrix = load(f, Loader=Loader)

    return matrix

def configure_loguru():
    """..."""
    logger.remove(0)
    logger.add(
        stdout, 
        colorize=True, 
        format=
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )

if __name__ == '__main__':
    """..."""
    configure_loguru()

    matrix = load_bench_matrix()
    defaults = matrix['defaults']

    dc = DockerClient.from_env()

    # Prepare network
    tc = containers.create_tc_container(dc)
    net = containers.create_network(dc)

    # Prepare output
    xlsx_sheets = {}

    for setup in matrix['setups']:
        name = list(setup.keys())[0]
        config = utils.merge(defaults, setup[name])

        raw_times = DataFrame({f'run{r}': [] for r in range(1, RUNS+1)})

        for r in range(1, RUNS+1):
            logger.info(f"===== {name} ({r}/{RUNS}) =====")

            z = containers.create_container('Z', config, net, dc)
            y = containers.create_container('Y', config, net, dc)
            x = containers.create_container('X', config, net, dc)
            
            # Wait until the X container finishes
            logger.info(f"Waiting for container '{x.name}' (X) to finish.")
            x.wait()

            logger.info(f"Container '{x.name}' (X) finished.")
            
            logger.info("Processing results.")
            (times, run_result) = httping.extract_httping_run_result(x.logs())
            
            raw_times[f'run{r}'] = times

            logger.info("Finished processing results.")

            logger.info("Cleaning up containers")
            x.remove()

            if y is not None:
                y.kill()
                y.remove()

            z.kill()
            z.remove()
            logger.info("Finished cleaning up containers")

        logger.info("Writing output")
        xlsx_sheets[name] = raw_times

    # Write output to file
    with ExcelWriter("results.xlsx") as w:
        for (name, df) in xlsx_sheets.items():
            df.to_excel(w, sheet_name=name)

    # Cleanup
    net.remove()
    tc.kill()
