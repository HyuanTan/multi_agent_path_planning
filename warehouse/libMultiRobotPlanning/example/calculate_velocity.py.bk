#!/usr/bin/env python3
import yaml
import numpy as np
import argparse
import math
import copy

class VelocityCalculator:
  def __init__(self, map, schedule, out_file):
    self.map = map
    self.schedule = schedule
    self.time_interval = 10 # time:60s
    self.normal_speed = 1.0 # m/s

    # new_schedule = self.calculate_velocity(self.map, self.schedule, self.time_interval)
    new_schedule = self.calculate_velocity2(self.map, self.schedule, self.normal_speed)
    with open(out_file, 'w') as f:
      yaml.dump(new_schedule, f)
  
  # Set a regular time_interval to calculate speed
  def calculate_velocity(self, map, schedule, time_interval):
    v_dict = map["roadmap"]["vertices"]
    for agent_name in schedule["schedule"]:
      agent = schedule["schedule"][agent_name]
      distance = 0.0
      speed = 0.0
      for d, idx in zip(agent, range(0, len(agent))):
        if idx == 0:
          continue
        elif idx < len(agent):
          posLast = np.array(v_dict[agent[idx-1]["v"]])
          posNext = np.array(v_dict[agent[idx]["v"]])
          distance = math.sqrt(math.pow(posNext[0]-posLast[0], 2) + math.pow(posNext[1]-posLast[1], 2))
          speed = round(distance / time_interval, 2)
          print("distance:", distance, "speed:", speed)
          schedule["schedule"][agent_name][idx-1].update({"s": speed})
      # the final point
      schedule["schedule"][agent_name][-1].update({"s": 0.0})
    return schedule
  
  # SET A comman speed , calculate time_interval
  def calculate_velocity2(self, map, schedule, normal_speed):
    v_dict = map["roadmap"]["vertices"]
    
    t_length = []
    for agent_name in schedule["schedule"]:
      agent = schedule["schedule"][agent_name]
      t_length.append(len(agent))
    
    t_number = np.max(t_length)
    diastance_array = np.zeros((len(t_length), t_number))

    for agent_name, agen_idx in zip(schedule["schedule"], range(0, len(schedule["schedule"]))):
      agent = schedule["schedule"][agent_name]
      distance = 0.0
      for d, idx in zip(agent, range(0, len(agent))):
        if idx == 0:
          continue
        elif idx < len(agent):
          posLast = np.array(v_dict[agent[idx-1]["v"]])
          posNext = np.array(v_dict[agent[idx]["v"]])
          distance = math.sqrt(math.pow(posNext[0]-posLast[0], 2) + math.pow(posNext[1]-posLast[1], 2))
          diastance_array[agen_idx, idx-1] = distance
    # find the max/min distance in t
    diastance_max_min = np.zeros((2, t_number))
    diastance_max_min[1, :] = 99999999.99

    for i in range(0, t_number):
      max = np.max(diastance_array[:, i])
      diastance_max_min[0,i] = max
      for data in diastance_array[:, i]:
        if data > 0 and data < diastance_max_min[1,i]:
          diastance_max_min[1,i] = data
    
    # time_interval
    time_interval_array = []
    for i in range(0, t_number):
      distance_tmp = (diastance_max_min[0,i] + diastance_max_min[1,i]) / 2.0
      time_interval_array.append(round(distance_tmp / normal_speed, 2))
    
    for agent_name, agen_idx in zip(schedule["schedule"], range(0, len(schedule["schedule"]))):
      agent = schedule["schedule"][agent_name]
      speed = 0.0
      for d, idx in zip(agent, range(0, len(agent))):
        if idx == 0:
          continue
        elif idx < len(agent):
          speed = round(diastance_array[agen_idx, idx-1] / time_interval_array[idx-1], 2)
          schedule["schedule"][agent_name][idx-1].update({"s": float(speed)})
      # the final point
      schedule["schedule"][agent_name][-1].update({"s": 0.0})
    return schedule

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("map", help="input file containing map")
  parser.add_argument("schedule", help="schedule for agents")
  parser.add_argument("out", help="schedule with velocity for agents")
  args = parser.parse_args()

  with open(args.map) as map_file:
    map = yaml.safe_load(map_file)

  if "roadmap" not in map:
    print("Not a roadmap file!")
    exit()
    
  with open(args.schedule) as states_file:
    schedule = yaml.safe_load(states_file)
  
  out_file = args.out
  
  calculator = VelocityCalculator(map, schedule, out_file)


if __name__ == "__main__":
  main()