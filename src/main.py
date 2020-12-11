import os
from pathlib import Path
from typing import List, Dict

from src.configuration import ConfigReader
from src.job.jobs import JobGenerator, AtomicInteger, type_generation
from src.job.manager import ServerLoadManager
from src.job.queue import JobStorage
from src.job.server import ServerType, Server, GatewayServer
from src.model import QueuingSystem
from src.stats.eventbus import EventBus
from src.stats.stats import SimulationStatistics


def server_of(id_gen: AtomicInteger, server_type: ServerType, eventbus: EventBus, config: ConfigReader,
              managers: Dict[ServerType, ServerLoadManager] = None) -> List[Server]:
    if server_type == ServerType.GATEWAY and managers is None:
        raise Exception(f"Manager must be provided to create {server_type} server")

    server_config = config.server_config(server_type)
    if server_type == ServerType.GATEWAY:
        result = [GatewayServer(server_type, server_config["distribution"], id_gen.increment(), eventbus, managers)
                  for i in range(server_config["quantity"])]
    else:
        result = [Server(server_type, server_config["distribution"], id_gen.increment(), eventbus)
                  for i in range(server_config["quantity"])]

    return result


if __name__ == '__main__':
    conf_path = os.path.join(str(Path(__file__).parent.parent.joinpath()), "conf.yaml")
    config = ConfigReader(conf_path)

    input_dist = config.input_distribution

    id_gen = AtomicInteger()
    job_generator = JobGenerator(id_gen.increment, type_generation)

    server_id_gen = AtomicInteger()
    queue = JobStorage(config.queue_size)
    eventbus = EventBus()
    servers = {
        #  ServerType.PAYMENTS: server_of(server_id_gen, ServerType.PAYMENTS, eventbus, config),
        # ServerType.INVENTORY: server_of(server_id_gen, ServerType.INVENTORY, eventbus, config),
        # ServerType.SHIPMENT: server_of(server_id_gen, ServerType.SHIPMENT, eventbus, config),
    }

    server_managers = {t: ServerLoadManager(s, queue, eventbus) for t, s in servers.items()}
    gateways = server_of(server_id_gen, ServerType.GATEWAY, eventbus, config, server_managers)
    servers[ServerType.GATEWAY] = gateways
    server_managers[ServerType.GATEWAY] = ServerLoadManager(gateways, queue, eventbus)

    stats = SimulationStatistics(queue, servers)
    eventbus.add(stats)

    system = QueuingSystem(input_dist, job_generator, config.simulation_duration, server_managers, eventbus)
    system.run()

    table = stats.get_general_stats()
    print("------- General Stats -------")
    print(table)
