### Requirements

- Python 3.9 or above
- `tabulate` python lib
- `yaml` python lib 
### How to run
```
python3.9 -m src.main
```

### Run results: 
Sample configuration:

todo: update yaml example

```yaml
QueuingModel:
  InputDistribution: # Erlang Distribution
    shape: 2 # Distribution shape - integer
    scale: 100 # Distribution rate - average interval between jobs arrival (millis)

  ProcessTimeDistribution: # Exponential Distribution
    scale: 200 # average job processing time (millis)

  serversNumber: 2
  queueSize: 5

  simulationDuration: 30000 # Duration of simulation (millis)
```
Sample result for the config (30 sec run):
```
---------------------------------  -------  -------------
Average job processing time        183.692  ms
Average time in queue              233.504  ms
Average queue size                 1.16794  jobs in queue
Average jobs number in the system  3.06298  jobs
Chance of system being idle           24.7  %
Chance of reject                      17.3  %
---------------------------------  -------  -------------
```