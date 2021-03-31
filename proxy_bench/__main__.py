import numpy as np
from . import containers, httping, utils, wrk
from copy import deepcopy
from docker import DockerClient
from loguru import logger
from pandas import DataFrame, ExcelWriter
from yaml import load, Loader
from click import command, argument, File


def expand_setup(setup, name):
    """
    
    """
    for section in setup.keys():
        for node in ['X', 'Y', 'Z']:
            if node not in setup[section]:
                logger.warning(f"Node '{node}' missing in section '{section}'.")

    # Only expand when multiple delays are specified for X.
    network = setup['network']
    x_delay = network['X']['delay']
    if type(network['X']['delay']) is not list:
        return [setup]

    length = len(x_delay)
    y_delay = utils.as_list_with_len(network['Y']['delay'], length)
    z_delay = utils.as_list_with_len(network['Z']['delay'], length)
    
    setups = []
    for delays in zip(x_delay, y_delay, z_delay):
        s = deepcopy(setup)
        s['network']['X']['delay'] = delays[0]
        s['network']['Y']['delay'] = delays[1]
        s['network']['Z']['delay'] = delays[2]

        setups.append(s)

    return setups
        

@command()
@argument("file", type=File('rb'))
def main(file: File):
    utils.configure_loguru()
    dc = DockerClient.from_env()

    # Load benchmark matrix
    matrix = load(file, Loader=Loader)
    client = matrix['client']
    output = matrix['output']
    runs_per_setup = matrix['runs-per-setup']
    defaults = matrix['defaults']

    # Setup the Docker network.
    tc = containers.create_tc_container(dc)
    net = containers.create_network(dc)

    # Results are written at the end.
    xlsx_sheets = {}

    for setup in matrix['setups']:
        setup_name = list(setup.keys())[0]
        logger.info(f"===== {setup_name} =====")

        setup = utils.merge(defaults, setup[setup_name])
        setups = expand_setup(setup, setup_name)

        for setup in setups:
            variant_times = DataFrame()
            variant_name = utils.add_delay_postfix(setup_name, setup)
            runs = range(1, runs_per_setup+1)

            for r in runs:
                try:
                    logger.info(f"===== {variant_name} ({r}/{runs_per_setup}) =====")
                    y, z = (None, None)

                    if 'Y' in setup['containers']:
                        y = containers.create_container('Y', setup, net, dc)

                    if 'Z' in setup['containers']:
                        z = containers.create_container('Z', setup, net, dc)

                    # An X node is mandatory.
                    x = containers.create_container('X', setup, net, dc)
                    
                    # Capture stdout until X completes.
                    logger.info(f"Waiting for container '{x.name}' (X) to finish.")
                    stdout = []
                    for line in x.attach(stream=True):
                        stdout.append(line)

                    # Process results
                    logger.info(f"Container '{x.name}' (X) finished. Processing results.")
                    
                    if client == "httping":
                        (times, stats) = httping.extract_httping_run_result(stdout)
                    elif client == "wrk":
                        (times, stats) = wrk.extract_wrk_run_result(stdout)
                    
                    variant_times[f'run{r}'] = times
                    variant_times[f'run{r}-stats'] = stats
                
                # Always perform cleanup
                finally:
                    if y is not None:
                        y.kill()

                    if z is not None:
                        z.kill()

            # Calculate variant-wide stats
            variant_stats = np.zeros(min(len(variant_times['run1']), 4))
            combined = np.array([])
            means = np.zeros(runs_per_setup)
            for (i, r) in enumerate(runs):
                means[i] = variant_times[f'run{r}-stats'][1]
                combined = np.append(combined, variant_times[f'run{r}'])
            
            variant_stats[0] = means.mean()
            variant_stats[1] = means.std()
            variant_stats[2] = combined.mean()
            variant_stats[3] = combined.std()

            # Add variant-wide stats to variant sheet
            variant_times['stats'] = variant_stats
            xlsx_sheets[variant_name] = variant_times

    # Write output to file
    logger.info("Writing output")
    with ExcelWriter(output) as w:
        for (name, df) in xlsx_sheets.items():
            df.to_excel(w, sheet_name=name)

    # Cleanup
    net.remove()
    tc.kill()


if __name__ == '__main__':
    main()