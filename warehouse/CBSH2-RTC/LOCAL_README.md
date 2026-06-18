## Data
benchmarks: https://movingai.com/benchmarks/mapf/index.html

Game benchmarks: https://movingai.com/benchmarks/grids.html
formats: https://movingai.com/benchmarks/formats.html

flatland-challenge,Simplified Railway System:
https://www.aicrowd.com/challenges/flatland-challenge
https://gitlab.aicrowd.com/flatland/baselines/blob/master/torch_training/Getting_Started_Training.md


load data(Instance.cpp):
Currently only works for undirected unweighted 4-neighbor grids


To change it to roadmap, you only need to rewrite the variables and functions in the instance class that relate to maps. This should not demand an extensive amount of work. Additionally, please disable the rectangle reasoning technique, as it is not suitable for general roadmaps.

## Visualize GripMap
```
cd /mnt/hgfs/Code/warehouse/CBSH2-RTC
python3 visualize_gripmap.py /home/holly/ShareCode/warehouse/CBSH2-RTC/random-32-32-20.map /home/holly/ShareCode/warehouse/CBSH2-RTC/random-32-32-20-random-1.scen /home/holly/ShareCode/warehouse/CBSH2-RTC/paths.txt
```

## Test on road map
```
./cbs -f roadmap -m /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap.xml -a /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap_task.xml -o /home/holly/ShareCode/warehouse/data/warehouse_qidu/CBSH2-RTC.csv --outputPaths=/home/holly/ShareCode/warehouse/data/warehouse_qidu/paths.txt -k 30 -t 60 --heuristics=WDG --prioritizingConflicts=true --bypass=true --disjointSplitting=false --rectangleReasoning=None --corridorReasoning=GC --mutexReasoning=false --targetReasoning=true --restart=1 --sipp=false -s 2



./cbs -f roadmap -m /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap.xml -a /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap_task.xml -o /home/holly/ShareCode/warehouse/data/warehouse_qidu/CBSH2-RTC.csv --outputPaths=/home/holly/ShareCode/warehouse/data/warehouse_qidu/paths.txt -t 20 --heuristics=CG --prioritizingConflicts=true --bypass=true --disjointSplitting=false --rectangleReasoning=None --corridorReasoning=None --mutexReasoning=false --targetReasoning=true --restart=1 --sipp=false -s 2

### Get Optimal result
./cbs -f roadmap -m /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap.xml -a /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap_task.xml -o /home/holly/ShareCode/warehouse/data/warehouse_qidu/CBSH2-RTC.csv --outputPaths=/home/holly/ShareCode/warehouse/data/warehouse_qidu/paths.txt -t 20 --heuristics=WDG --prioritizingConflicts=true --bypass=true --disjointSplitting=true --rectangleReasoning=None --corridorReasoning=None --mutexReasoning=false --targetReasoning=true --restart=1 --sipp=false -s 2


### Get Optimal result --- Can deal with more same direction conflict(有些多余的路径段)
./cbs -f roadmap -m /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap.xml -a /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap_task.xml -o /home/holly/ShareCode/warehouse/data/warehouse_qidu/CBSH2-RTC.csv --outputPaths=/home/holly/ShareCode/warehouse/data/warehouse_qidu/paths.txt -t 20 --heuristics=WDG --prioritizingConflicts=true --bypass=true --disjointSplitting=true --rectangleReasoning=None --corridorReasoning=None --mutexReasoning=true --targetReasoning=true --restart=1 --sipp=false -s 2

### Get Optimal result --- Can deal with more same direction conflict
./cbs -f roadmap -m /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap.xml -a /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap_task.xml -o /home/holly/ShareCode/warehouse/data/warehouse_qidu/CBSH2-RTC.csv --outputPaths=/home/holly/ShareCode/warehouse/data/warehouse_qidu/paths.txt -t 20 --heuristics=CG --prioritizingConflicts=true --bypass=true --disjointSplitting=true --rectangleReasoning=None --corridorReasoning=None --mutexReasoning=true --targetReasoning=true --restart=1 --sipp=false -s 2

### Get Optimal result --- Can deal with more same direction conflict
./cbs -f roadmap -m /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap.xml -a /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap_task.xml -o /home/holly/ShareCode/warehouse/data/warehouse_qidu/CBSH2-RTC.csv --outputPaths=/home/holly/ShareCode/warehouse/data/warehouse_qidu/paths.txt -t 20 --heuristics=DG --prioritizingConflicts=true --bypass=true --disjointSplitting=true --rectangleReasoning=None --corridorReasoning=None --mutexReasoning=true --targetReasoning=true --restart=1 --sipp=false -s 2

### Get Optimal result
./cbs -f roadmap -m /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap.xml -a /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap_task.xml -o /home/holly/ShareCode/warehouse/data/warehouse_qidu/CBSH2-RTC.csv --outputPaths=/home/holly/ShareCode/warehouse/data/warehouse_qidu/paths.txt -t 20 --heuristics=WDG --prioritizingConflicts=true --bypass=true --disjointSplitting=true --rectangleReasoning=None --corridorReasoning=None --mutexReasoning=false --targetReasoning=true --restart=1 --sipp=true -s 2

### Get Optimal result, mutexReasoning=true is faster
./cbs -f roadmap -m /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap.xml -a /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap_task.xml -o /home/holly/ShareCode/warehouse/data/warehouse_qidu/CBSH2-RTC.csv --outputPaths=/home/holly/ShareCode/warehouse/data/warehouse_qidu/paths.txt -t 20 --heuristics=WDG --prioritizingConflicts=true --bypass=true --disjointSplitting=true --rectangleReasoning=None --corridorReasoning=None --mutexReasoning=true --targetReasoning=true --restart=1 --sipp=true -s 2

# core dumped: corridorReasoning=PC/GC/Disjoint, the rest timeout
./cbs -f roadmap -m /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap.xml -a /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap_task.xml -o /home/holly/ShareCode/warehouse/data/warehouse_qidu/CBSH2-RTC.csv --outputPaths=/home/holly/ShareCode/warehouse/data/warehouse_qidu/paths.txt -t 20 --heuristics=DG --prioritizingConflicts=true --bypass=true --disjointSplitting=true --rectangleReasoning=None --corridorReasoning=STC --mutexReasoning=true --targetReasoning=true --restart=1 --sipp=false -s 2


./cbs -f roadmap -m /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap.xml -a /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap_task.xml -o /home/holly/ShareCode/warehouse/data/warehouse_qidu/CBSH2-RTC.csv --outputPaths=/home/holly/ShareCode/warehouse/data/warehouse_qidu/paths.txt -t 20 --heuristics=WDG --prioritizingConflicts=true --bypass=true --disjointSplitting=true --rectangleReasoning=None --corridorReasoning=GC --mutexReasoning=true --targetReasoning=true --restart=1 --sipp=false -s 2

```

## Visualize Roadmap
```
cd /mnt/hgfs/Code/warehouse/CBSH2-RTC
python3 visualize_roadmap.py /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap.xml /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap_task.xml /home/holly/ShareCode/warehouse/data/warehouse_qidu/paths.txt
```

## TODO:

1. SpaceTimeAStar::getTravelTime while using corridorReasoning, **the agent cannot stay at its start location**