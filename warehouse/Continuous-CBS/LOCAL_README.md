## Original Test in roadmap
```
# map and task input XML-files with all required information, config file is optional
./CCBS map.xml task.xml config.xml
```

```
./CCBS ./Examples/roadmap.xml ./Examples/roadmap_task.xml

cd /home/holly/ShareCode/warehouse/Continuous-CBS/
python3 visualize_roadmap.py /home/holly/ShareCode/warehouse/Continuous-CBS/Examples/roadmap.xml /home/holly/ShareCode/warehouse/Continuous-CBS/Examples/roadmap_task.xml /home/holly/ShareCode/warehouse/Continuous-CBS/Examples/roadmap_task_log.xml
```


## Test in warehouse roadmap(Jieshibang)
```
# Get data
cd /home/holly/ShareCode/warehouse/tools
python3 database_map2yaml_map.py

# enable_save_xml = True, save in execute path
# 执行目录下生成 roadmap.xml 和 roadmap_task.xml
cd /home/holly/ShareCode/warehouse/libMultiRobotPlanning/build
python3 ../tools/annotate_roadmap.py /home/holly/ShareCode/warehouse/tools/roadmap_data.yaml /home/holly/ShareCode/warehouse/tools/roadmap_data_annotated.yaml 

cd /home/holly/ShareCode/warehouse/Continuous-CBS
./CCBS /home/holly/ShareCode/warehouse/libMultiRobotPlanning/build/roadmap.xml /home/holly/ShareCode/warehouse/libMultiRobotPlanning/build/roadmap_task.xml config.xml robot123


cd /home/holly/ShareCode/warehouse/Continuous-CBS/
python3 visualize_roadmap.py /home/holly/ShareCode/warehouse/libMultiRobotPlanning/build/roadmap.xml /home/holly/ShareCode/warehouse/libMultiRobotPlanning/build/roadmap_task.xml /home/holly/ShareCode/warehouse/libMultiRobotPlanning/build/roadmap_task_log.xml --radius 0.66
```

## Test in warehouse roadmap(Qidu)
```
# Get data
cd /home/holly/ShareCode/warehouse/tools
python3 database_map2yaml_map.py

# enable_save_xml = True, save in execute path
# 输入目录下生成 roadmap.xml 和 roadmap_task.xml
cd /home/holly/ShareCode/warehouse/libMultiRobotPlanning/build

python3 ../tools/annotate_roadmap.py /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap_data.yaml roadmap_data_annotated.yaml 0.3

cd /home/holly/ShareCode/warehouse/Continuous-CBS
./CCBS /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap.xml /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap_task.xml config.xml robot123


cd /home/holly/ShareCode/warehouse/Continuous-CBS/
python3 visualize_roadmap.py /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap.xml /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap_task.xml /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap_task_log.xml
```

## 适配记录
1. 原来的node id 是顺序的，id 跟存储在vector的位置保持一致
valid_moves，存储的 neighbors 对应的 node id 也是跟存储在vector的位置保持一致

适配：
Node, gNode 添加 id_name，id 还是按照原来的跟存储在vector的位置保持一致，添加 id_name 与robot123的id/id_name 保持一致


TODO: 改为 unordered_map
std::vector<std::vector<int>> grid;
std::vector<gNode> nodes;

## TODO
1. 允许在起点/中途停车点延长等待时间 or 添加区域规则、限流