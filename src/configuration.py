import yaml

from src.distribution import Distribution, ErlangDistribution, ExponentialDistribution

CONFIG_ROOT_KEY = "QueuingModel"
INPUT_DISTRIBUTION_KEY = "InputDistribution"
PROCESS_TIME_DISTRIBUTION = "ProcessTimeDistribution"

SHAPE_KEY = "shape"
SCALE_KEY = "scale"
RATE_KEY = "rate"

SERVERS_NUMBER_KEY = "serversNumber"
QUEUE_SIZE_KEY = "queueSize"


class ConfigReader:

    def __init__(self, config_file_path) -> None:
        self.config_path = config_file_path
        self._config = None

    @property
    def input_distribution(self) -> Distribution:
        dist_config = self._get_config()[INPUT_DISTRIBUTION_KEY]
        shape = int(dist_config[SHAPE_KEY])
        scale = float(dist_config[SCALE_KEY])
        print("ErlangDistribution({},{})".format(shape, scale))
        return ErlangDistribution(shape, scale)

    @property
    def process_time_distribution(self) -> Distribution:
        dist_config = self._get_config()[PROCESS_TIME_DISTRIBUTION]
        scale = float(dist_config[SCALE_KEY])
        print("ExponentialDistribution({})".format(scale))
        return ExponentialDistribution(scale)

    @property
    def servers_number(self) -> int:
        return self._get_config()[SERVERS_NUMBER_KEY]

    @property
    def queue_size(self) -> int:
        return self._get_config()[QUEUE_SIZE_KEY]

    def _get_config(self) -> dict:
        if self._config is None:
            self._config = self._load_config()
        return self._config[CONFIG_ROOT_KEY]

    def _load_config(self):
        with open(self.config_path, 'r') as stream:
            return yaml.safe_load(stream)
