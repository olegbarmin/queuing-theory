import os
from pathlib import Path

from src.configuration import ConfigReader
from src.job.jobs import JobGenerator, AtomicInteger, type_generation
from src.job.manager import ServerLoadManager
from src.job.queue import JobStorage
from src.model import QueuingSystem
from src.stats.eventbus import EventBus
from src.stats.stats import SimulationStatistics

if __name__ == '__main__':
    conf_path = os.path.join(str(Path(__file__).parent.parent.joinpath()), "conf.yaml")
    config = ConfigReader(conf_path)

    input_dist = config.input_distribution

    id_gen = AtomicInteger()
    job_generator = JobGenerator(id_gen.increment, type_generation)

    eventbus = EventBus()
    servers = config.gateways(eventbus)
    queue = JobStorage(config.queue_size)
    manager = ServerLoadManager(servers, queue, eventbus)
    stats = SimulationStatistics(queue, servers)
    eventbus.add(stats)

    system = QueuingSystem(input_dist, job_generator, config.simulation_duration, servers, manager, eventbus)
    system.run()

    table = stats.get_general_stats()
    print("------- General Stats -------")
    print(table)
