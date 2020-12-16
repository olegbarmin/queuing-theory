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

```yaml
QueuingModel:
QueuingModel:
  InputDistribution: # Exponential Distribution
    scale: 100 # average interval between jobs arrival (millis)

  Servers:
    Gateway: # Gamma Distribution for request processing time
      shape: 1 # Distribution shape
      scale: 100 # Distribution scale
      quantity: 3
      queueSize: 10
    Payments:
      shape: 2 # Distribution shape
      scale: 2000 # Distribution scale
      quantity: 3
      queueSize: 10
    Inventory:
      shape: 1 # Distribution shape
      scale: 100 # Distribution scale
      quantity: 3
      queueSize: 3
    Shipment:
      shape: 2 # Distribution shape
      scale: 500 # Distribution scale
      quantity: 1
      queueSize: 3

  simulationDuration: 60000 # Duration of simulation (millis)
```
Sample result for the config (30 sec run):
```
-------------------- System Statistics --------------------
---------------------------------  ------  ----
Average jobs number in the system  14.421  jobs
Chance of system being idle         0.58   %
Chance of reject                   11.86   %
---------------------------------  ------  ----
-------------------- ServerType.PAYMENTS --------------------
---------------------------  -------  -------------
Average job processing time  4666.09  ms
Average time in queue        12975.1  ms
Average queue size           7.30851  jobs in queue
---------------------------  -------  -------------
-------------------- ServerType.INVENTORY --------------------
---------------------------  --------  -------------
Average job processing time   102.807  ms
Average time in queue         25.8333  ms
Average queue size           0.037037  jobs in queue
---------------------------  --------  -------------
-------------------- ServerType.SHIPMENT --------------------
---------------------------  -------  -------------
Average job processing time  874.098  ms
Average time in queue         1231.3  ms
Average queue size           1.27869  jobs in queue
---------------------------  -------  -------------
-------------------- ServerType.GATEWAY --------------------
---------------------------  ---------  -------------
Average job processing time     102.17  ms
Average time in queue            27.25  ms
Average queue size           0.0756014  jobs in queue
---------------------------  ---------  -------------
```