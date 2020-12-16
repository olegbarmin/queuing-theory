import os
from pathlib import Path

from src.configuration import ConfigReader
from src.job.jobs import JobGenerator, AtomicInteger, type_generation
from src.job.manager import ServerLoadManager
from src.job.server import ServerType, Server, GatewayServer
from src.model import QueuingSystem
from src.stats.eventbus import EventBus
from src.stats.server_stats import GatewayStatistics
from src.stats.system_stats import SimulationStatistics


def manager_of(id_gen: AtomicInteger, server_type: ServerType, eventbus: EventBus, config: ConfigReader,
               server_build_func=lambda t, d, _id, eb: Server(t, d, _id, eb)) -> ServerLoadManager:
    if server_type == ServerType.GATEWAY and managers is None:
        raise Exception(f"Manager must be provided to create {server_type} server")

    server_config = config.server_config(server_type)
    servers = [server_build_func(server_type, server_config["distribution"], id_gen.increment(), eventbus)
               for i in range(server_config["quantity"])]
    return ServerLoadManager(servers, server_config["queueSize"], eventbus)


if __name__ == '__main__':
    conf_path = os.path.join(str(Path(__file__).parent.parent.joinpath()), "conf.yaml")
    config = ConfigReader(conf_path)

    input_dist = config.input_distribution

    id_gen = AtomicInteger()
    job_generator = JobGenerator(id_gen.increment, type_generation)

    server_id_gen = AtomicInteger()
    eventbus = EventBus()
    managers = {}
    for t in config.server_types:
        if t != ServerType.GATEWAY:
            managers[t] = manager_of(server_id_gen, t, eventbus, config)

    gateway_manager = manager_of(server_id_gen, ServerType.GATEWAY, eventbus, config,
                                 lambda t, d, i, eb: GatewayServer(t, d, i, eb, managers))
    gateway_manager.stats = GatewayStatistics(gateway_manager.queue, gateway_manager.servers)
    managers[ServerType.GATEWAY] = gateway_manager

    stats = SimulationStatistics(managers)
    eventbus.add(stats)

    system = QueuingSystem(input_dist, job_generator, config.simulation_duration, managers, eventbus)
    system.run()
    stats.print_stats()
