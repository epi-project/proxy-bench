from docker import DockerClient
from docker.types import IPAMConfig, IPAMPool, Mount, containers
from docker.models.containers import Container
from docker.models.networks import Network
from docker.types.services import Privileges
from loguru import logger


TC_CONTAINER_NAME="docker-tc"
PROXY_BENCH_NET_NAME="proxy_bench_net"


def create_tc_container(dc: DockerClient) -> Container:
    """

    
    """
    containers = dc.containers.list()
    for container in containers:
        if container.name == TC_CONTAINER_NAME:
            logger.info(f"Container '{TC_CONTAINER_NAME}' already exists, skipping creation.")
            return container

    docker_sock = Mount("/var/run/docker.sock", "/var/run/docker.sock", type="bind")
    docker_tc = Mount("/var/docker-tc", "/var/docker-tc", type="bind")

    tc_container = dc.containers.run(
        name=TC_CONTAINER_NAME,
        network="host",
        auto_remove=True,
        detach=True,
        privileged=True,
        mounts=[docker_sock, docker_tc],
        image="lukaszlach/docker-tc",
    )

    logger.info(f"Created '{TC_CONTAINER_NAME}' container.")
    return tc_container


def create_container(name, config, net: Network, dc: DockerClient) -> Container:
    """

    """
    if name not in config['containers']:
        return None

    image = config['containers'][name]["image"]
    command = config['containers'][name].get("command", [])
    cpu = float(config['resources'][name]['cpu'])
    ram = config['resources'][name]['ram']
    ip = config['network'][name]['ip']
    delay = config['network'][name]['delay']
  
    container = dc.containers.create(
        image=image,
        command=command,
        privileged=True,
        nano_cpus=int(cpu * 1000000000),
        mem_limit=ram,
        labels={
            "com.docker-tc.enabled": "1",
            "com.docker-tc.delay": delay
        }
    )

    net.connect(container, ipv4_address=ip)

    networks = dc.networks.list()
    for network in networks:
        if network.name == "bridge":
            network.disconnect(container)

    container.start()

    logger.info(f"Created '{name}' container (CPU: {cpu}, RAM: {ram}, packet delay: {delay}).")

    return container


def create_network(dc: DockerClient) -> Network:
    """


    """
    networks = dc.networks.list()
    for network in networks:
        if network.name == PROXY_BENCH_NET_NAME:
            logger.info(f"Network '{PROXY_BENCH_NET_NAME}' already exists, skipping creation.")
            return network

    ipam_pool = IPAMPool(
        subnet="172.0.10.0/24",
        gateway="172.0.10.1"
    )

    ipam_config = IPAMConfig(
        pool_configs=[ipam_pool]
    )

    network = dc.networks.create(
        name=PROXY_BENCH_NET_NAME,
        driver="bridge",
        ipam=ipam_config
    )

    logger.info(f"Created '{PROXY_BENCH_NET_NAME}' network.")
    return network
