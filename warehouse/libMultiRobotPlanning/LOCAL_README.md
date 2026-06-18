## Test using roadmap
```
python3 ../tools/annotate_roadmap.py ../test/mapf_simple1_roadmap_to_annotate.yaml roadmap_data_annotated.yaml

./cbs_roadmap -i mapf_simple1_roadmap_annotated.yaml -o output.yaml

python3 ../example/visualize_roadmap.py mapf_simple1_roadmap_annotated.yaml output.yaml
```

## Show database map info
```
cd /home/holly/ShareCode/warehouse/tools
python3.10 show_database_map2.py
```

## Test using database map info(Jieshibang map)
```
cd /home/holly/ShareCode/warehouse/tools
python3 database_map2yaml_map.py

cd /home/holly/ShareCode/warehouse/libMultiRobotPlanning/build

python3 ../tools/annotate_roadmap.py /home/holly/ShareCode/warehouse/tools/roadmap_data.yaml roadmap_data_annotated.yaml 0.3

./cbs_roadmap -i /home/holly/ShareCode/warehouse/tools/roadmap_data_annotated.yaml -o /home/holly/ShareCode/warehouse/tools/output.yaml disappear-at-goal false

python3 ../example/visualize_roadmap.py /home/holly/ShareCode/warehouse/tools/roadmap_data_annotated.yaml /home/holly/ShareCode/warehouse/tools/output.yaml

# Calculate velocity
python3 ../example/calculate_velocity.py /home/holly/ShareCode/warehouse/tools/roadmap_data_annotated.yaml /home/holly/ShareCode/warehouse/tools/output.yaml /home/holly/ShareCode/warehouse/tools/output_velocity.yaml
```
## Test using database map info(Qidu map)
```
cd /home/holly/ShareCode/warehouse/tools
python3 database_map2yaml_map.py

cd /home/holly/ShareCode/warehouse/libMultiRobotPlanning/build

python3 ../tools/annotate_roadmap.py /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap_data.yaml roadmap_data_annotated.yaml 0.3

./cbs_roadmap -i /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap_data_annotated.yaml -o /home/holly/ShareCode/warehouse/data/warehouse_qidu/output.yaml disappear-at-goal false

python3 ../example/visualize_roadmap.py /home/holly/ShareCode/warehouse/data/warehouse_qidu/roadmap_data_annotated.yaml /home/holly/ShareCode/warehouse/data/warehouse_qidu/output.yaml
```


### 问题
1. 202（卸货点）， 0202（库位）; 203, 0203（库位） 坐标不同，区别是什么？
2. 实际中如何执行等待的逻辑？等待多长时间？ 等待实现方式： 只截取路径到达等待点的部分路径下发
3. 路径宽度，车需要掉头、旋转，考虑车体
4. 有些单向、有些双向（实际是部分有单双向）
5. 死锁问题的解决
6. 后退的路径，后退or旋转
 

## 待解决&验证的问题
1. robot的起点没在站点上而是任意位置；使用就近站点进行规划时，前往最近站点的时间对整体效果的影响评估
2. 改为实时规划运行的版本
3. 多任务同时到达同一个目标点
4. 如果一台机器由于避障、机器故障等原因长时间停在某个地方，如何把该点所在的边设置为不可通行
5. 速度计算考虑转弯（点到点之间是贝塞尔曲线）的情况
6. 其余未作业的机器所在位置标记为占用状态
7. **如果按照现在的算法，同时生成所有机器的路径，只要有一个机器update了路径，其余机器也应该同时update路径**， 但是现有机器是只有到某一个途经的站点请求一次update,而其余的可能没到点也不会做更新
8. 规划时间过长或者规划失败，添加超时退出

## TODO:
1. 为了适应实际的复杂场景，是否可以再在底层添加一层类似局部路径规划可绕障的路径规划？
2. 修改cost的计算方法，例如distance?


## 待确定问题
1. 路径的格式？日志里面的路径是PathCode和终点坐标？给出的格式：由station name + velocity 组成一组有序数据
2. 车端的避障逻辑是什么？或者说local planner 或者 controler 的策略是什么？

## 开发注意问题
1. 输入和输出数据来源分别从mqtt和ros话题获取或输出（分别用于实际成产环境和本地模拟测试），注意要做一个数据层的adapter以适应不同的数据来源
2. 注意触发机制
3. 地图和agent分开


## ROS2 test
控制规划：pure_pursuit, mpc
车辆模拟器: simple_planning_simulator

## 问题分析
1. CBS相关的算法
   1）车端需要实时响应路径的修改（有新任务请求时，所有未完成的agent都需要参与路径重新规划）TODO: 优化为基于现有路径正在执行的路径，只规划新请求（在时间协调上可能较难实现）
   2）等待完成一次规划的所有任务再继续下一次请求，这样会导致效率降低

   对于roadmap类型的地图，尤其是需要共享一条双向的路径情况，需要限制同一时间通过该条路径的车流量，不然计算量会随着agents的增加需要解决的conflicts也迅速增加。

2. Windowed MAPF solver resolves， 解决一段时间内的collision
