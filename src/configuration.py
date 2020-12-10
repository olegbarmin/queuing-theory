import yaml

from src.distribution import Distribution, ExponentialDistribution, GammaDistribution

CONFIG_ROOT_KEY = "QueuingModel"
INPUT_DISTRIBUTION_KEY = "InputDistribution"
PROCESS_TIME_DISTRIBUTION = "ProcessTimeDistribution"

SHAPE_KEY = "shape"
SCALE_KEY = "scale"
RATE_KEY = "rate"

SERVERS_NUMBER_KEY = "serversNumber"
QUEUE_SIZE_KEY = "queueSize"
SIMULATION_DURATION_KEY = "simulationDuration"


class ConfigReader:

    def __init__(self, config_file_path) -> None:
        self.config_path = config_file_path
        self._config = None

    @property
    def input_distribution(self) -> Distribution:
        dist_config = self._get_config()[INPUT_DISTRIBUTION_KEY]
        shape = float(dist_config[SHAPE_KEY])
        scale = float(dist_config[SCALE_KEY])
        return GammaDistribution(shape, scale)

    @property
    def process_time_distribution(self) -> Distribution:
        dist_config = self._get_config()[PROCESS_TIME_DISTRIBUTION]
        scale = float(dist_config[SCALE_KEY])
        return ExponentialDistribution(scale)

    @property
    def servers_number(self) -> int:
        return self._get_config()[SERVERS_NUMBER_KEY]

    @property
    def queue_size(self) -> int:
        return self._get_config()[QUEUE_SIZE_KEY]

    @property
    def simulation_duration(self) -> int:
        return int(self._get_config()[SIMULATION_DURATION_KEY])

    def _get_config(self) -> dict:
        if self._config is None:
            self._config = self._load_config()
        return self._config[CONFIG_ROOT_KEY]

    def _load_config(self):
        with open(self.config_path, 'r') as stream:
            config = yaml.safe_load(stream)
            print("Loaded config:\n--------\n{}".format(yaml.dump(config)))
            print("--------")
            return config
