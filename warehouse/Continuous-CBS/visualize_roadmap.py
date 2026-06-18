#!/usr/bin/env python3
import yaml
import matplotlib
# matplotlib.use("Agg")
from matplotlib.patches import Circle, FancyArrow, Rectangle, Arrow, ConnectionPatch, PathPatch
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
import matplotlib.animation as manimation
import argparse
import math
from lxml import etree # https://lxml.de/tutorial.html
from matplotlib.patheffects import withStroke
import plotly.tools as tls
import matplotlib.patheffects as path_effects
from enum import Enum
import time

'''
Update:
1. 优化路径、车体、目标点等的显示
2. 添加支持显示没有任务的车
'''

# 'green' -- charge or parking 
Colors = ['orange', 'blue', 'red', 'yellow', 'purple']
enable_robot123 = True
step_interval = 2 # 10 # 5 #10

class TaskStatus(Enum):
  NO_TASK = 0
  HAS_TASK = 1

# 自定义的带透明度的阴影效果类
class AlphaStroke(path_effects.AbstractPathEffect):
  def __init__(self, linewidth=1, foreground='black', alpha=1.0):
    self.linewidth = linewidth
    self.foreground = foreground
    self.alpha = alpha

  def draw_path(self, renderer, gc, tpath, affine, rgbFace=None):
    gc0 = renderer.new_gc()
    gc0.set_linewidth(self.linewidth)
    gc0.set_foreground(self.foreground)
    gc0.set_alpha(self.alpha)
    gc0.set_capstyle(gc.get_capstyle())
    gc0.set_joinstyle(gc.get_joinstyle())
    renderer.draw_path(gc0, tpath, affine, rgbFace)
    gc0.restore()

class Animation:
  def __init__(self, map, schedule, radius):

    # self.map = yaml.safe_load(map)
    # self.schedule = yaml.safe_load(schedule)

    self.map = map
    self.schedule = schedule

    self.radius = radius
    radius_goal = radius + 0.15

    # find boundary
    all_pos = np.array(list(map["roadmap"]["vertices"].values()))
    xmin = np.min(all_pos[:, 0])
    ymin = np.min(all_pos[:, 1])
    xmax = np.max(all_pos[:, 0])
    ymax = np.max(all_pos[:, 1])

    aspect = (xmax - xmin) / (ymax - ymin)

    self.fig = plt.figure(frameon=False, figsize=(4 * aspect, 4))
    self.ax = self.fig.add_subplot(111, aspect='equal')
    self.ax.axis('off')
    self.fig.subplots_adjust(left=0,right=1,bottom=0,top=1, wspace=None, hspace=None)

    self.patches = []
    self.artists = []
    self.agents = dict()
    self.agent_names = dict()

    plt.xlim(xmin - radius, xmax + radius)
    plt.ylim(ymin - radius, ymax + radius)

    v_dict = map["roadmap"]["vertices"]
    for edge in map["roadmap"]["edges"]:
      start = v_dict[edge[0]]
      goal = v_dict[edge[1]]
      # self.patches.append(FancyArrow(start[0], start[1], goal[0] - start[0], goal[1] - start[1], width=0.05, length_includes_head=True))#, head_width=0))
      
      # 创建一个 ConnectionPatch
      con = ConnectionPatch(xyA=(start[0], start[1]), xyB=(goal[0], goal[1]), coordsA="data", coordsB="data",
                            axesA=self.ax, axesB=self.ax, color="black")
      # 添加阴影效果
      con.set_path_effects([withStroke(linewidth=12, foreground="orange", alpha=0.5)])
      # con.set_path_effects([AlphaStroke(linewidth=12, foreground='orange', alpha=0.2)])
      self.patches.append(con)

    # create agents:
    self.T = 0
    # draw goals first
    for d, i in zip(map["agents"], range(0, len(map["agents"]))):
      if "goal" in d:
        goals = [d["goal"]]
      if "potentialGoals" in d:
        goals = [goal for goal in d["potentialGoals"]]
      for goal in goals:
        v = v_dict[goal]
        if(d["status"] == TaskStatus.HAS_TASK):
          # self.patches.append(Rectangle((v[0] - radius, v[1] - radius), 2*radius, 2*radius, facecolor=Colors[i%len(Colors)], edgecolor='black', alpha=0.5))
          self.patches.append(Rectangle((v[0] - radius_goal, v[1] - radius_goal), 2*radius_goal, 2*radius_goal, facecolor=Colors[i%len(Colors)], edgecolor='black', alpha=0.5))
        else:
          self.patches.append(Rectangle((v[0] - radius_goal, v[1] - radius_goal), 2*radius_goal, 2*radius_goal, facecolor="green", edgecolor='black', alpha=0.5))

    for d, i in zip(map["agents"], range(0, len(map["agents"]))):
      status = d["status"]
      name = d["name"]
      v = v_dict[d["start"]]
      self.agents[name] = Circle((v[0], v[1]), radius, facecolor=Colors[i%len(Colors)], edgecolor='black')
      self.agents[name].original_face_color = Colors[i%len(Colors)]
      self.patches.append(self.agents[name])
      # print("-------------------agent name", name)
      # print(schedule["schedule"][name][-1]["t"])

      if(status == TaskStatus.HAS_TASK):
        if enable_robot123:
          # self.T = max(self.T, schedule["schedule"][name][-1]["t"])
          self.T = max(self.T, schedule["total_duration"][name])
        else:
          self.T = max(self.T, schedule["schedule"][name][-1]["t"])
      self.agent_names[name] = self.ax.text(v[0], v[1], name.replace('agent', ''))
      self.agent_names[name].set_horizontalalignment('center')
      self.agent_names[name].set_verticalalignment('center')
      self.artists.append(self.agent_names[name])

    if enable_robot123:
      print("...............self.T:", self.T)
      self.anim = animation.FuncAnimation(self.fig, self.animate_func,# 每帧调用的动画函数，通常用于更新图形数据
                                init_func=self.init_func,# 初始化函数，只在动画开始前调用一次
                                # frames=math.ceil(self.T) * 10,
                                # frames=int(self.T * step_interval),# 动画的总帧数。可以是一个整数，表示帧的数量，也可以是一个可迭代对象
                                frames=int(self.T+1) * step_interval,
                                interval=40, # 帧之间的时间间隔，以毫秒为单位, 20帧/秒
                                blit=True)
    else:
      self.anim = animation.FuncAnimation(self.fig, self.animate_func,
                                init_func=self.init_func,
                                frames=int(self.T+1) * 10,
                                interval=100,
                                blit=True)

  def save(self, file_name, speed):
    '''
    self.anim.save(
      file_name,
      "ffmpeg",
      fps=10 * speed,
      dpi=200),
      # savefig_kwargs={"pad_inches": 0, "bbox_inches": "tight"})
    '''
    # self.anim.save(
    #   file_name + ".gif",
    #   "imagemagick",
    #   fps=10 * speed)

    # writer = animation.FFMpegWriter(fps=10 * speed)
    # self.anim.save(
    #     file_name + ".avi",
    #     writer=writer,
    #     dpi=200)

    # Ensure ffmpeg is installed in your system
    writer = animation.FFMpegWriter(fps=10 * speed)
    self.anim.save(
        file_name + ".mp4",
        writer=writer,
        dpi=300)

  def show(self):
    plt.show()

    # plotly_fig = tls.mpl_to_plotly(self.fig)
    # plotly_fig.show()

  def init_func(self):
    for p in self.patches:
      self.ax.add_patch(p)
    for a in self.artists:
      self.ax.add_artist(a)
    return self.patches + self.artists

  def animate_func(self, i):
    # if(i == 0):
      # time.sleep(10) # 用于记录视频前的准备
    print("animate_func:", i)
    for agent_name in self.schedule["schedule"]:
      agent = self.schedule["schedule"][agent_name]
      pos = []
      if enable_robot123:
        pos = self.getState(i / step_interval, agent) 
      else:
        pos = self.getState(i / 10, agent) # Setp 0.1, 0.2.....
      p = (pos[0], pos[1])
      self.agents[agent_name].center = p
      self.agent_names[agent_name].set_position(p)

    # reset all colors
    for _,agent in self.agents.items():
      agent.set_facecolor(agent.original_face_color)

    # check drive-drive collisions
    agents_array = [agent for _,agent in self.agents.items()]
    for i in range(0, len(agents_array)):
      for j in range(i+1, len(agents_array)):
        d1 = agents_array[i]
        d2 = agents_array[j]
        pos1 = np.array(d1.center)
        pos2 = np.array(d2.center)
        if np.linalg.norm(pos1 - pos2) < 2 * self.radius:
          d1.set_facecolor('red')
          d2.set_facecolor('red')
          print("COLLISION! (agent-agent) ({}, {})".format(i, j))

    return self.patches + self.artists

    # check drive-drive collisions
    agents_array = [agent for _,agent in self.agents.items()]
    for i in range(0, len(agents_array)):
      for j in range(i+1, len(agents_array)):
        d1 = agents_array[i]
        d2 = agents_array[j]
        pos1 = np.array(d1.center)
        pos2 = np.array(d2.center)
        if np.linalg.norm(pos1 - pos2) < 2 * self.radius:
          d1.set_facecolor('red')
          d2.set_facecolor('red')
          print("COLLISION! (agent-agent) ({}, {})".format(i, j))

    return self.patches + self.artists


  def getState(self, t, d):
    v_dict = self.map["roadmap"]["vertices"]   
    pos = []
    if enable_robot123:
      idx = 0
      while idx < len(d) and d[idx]["d"] < t:
      # while idx < len(d) and (d[idx]["d"] < t or d[idx]["d"] == t):
        idx += 1
      if idx == 0:
        return np.array(v_dict[d[0]["v"]])
      elif idx < len(d):
        posLast = np.array(v_dict[d[idx-1]["v"]])
        posNext = np.array(v_dict[d[idx]["v"]])
      else:
        return np.array(v_dict[d[-1]["v"]])

      dt = d[idx]["d"] - d[idx-1]["d"]
      t = (t - d[idx-1]["d"]) / dt
      # print("t:", t)
      pos = (posNext - posLast) * t + posLast
    else:
      idx = 0
      while idx < len(d) and d[idx]["t"] < t:
        idx += 1
      if idx == 0:
        return np.array(v_dict[d[0]["v"]])
      elif idx < len(d):
        posLast = np.array(v_dict[d[idx-1]["v"]])
        posNext = np.array(v_dict[d[idx]["v"]])
      else:
        return np.array(v_dict[d[-1]["v"]])

      dt = d[idx]["t"] - d[idx-1]["t"]
      t = (t - d[idx-1]["t"]) / dt
      pos = (posNext - posLast) * t + posLast

    return pos

 

def get_schedule_from_xml(file_path):
  print("Get schedule from file:", file_path)
  schedules = {}
  schedule = {}
  tree = etree.parse(file_path)
  root = tree.getroot()
  total_duration_dict = {}
  for data in root:
    # print("data.tag:", data.tag)
    if(data.tag == "log"):
      for agent in data:
        if(agent.tag == "agent"):
          # agent_id = "agent" + agent.get("number")
          agent_id = agent.get("number")
          print("agent_id:", agent_id)
          for path in agent:
            if(path.tag == "path"):
              total_duration_dict.update({agent_id: float(path.get("duration"))})
              path_list = []
              cumulated_duration = 0.0
              for section in path:
                path_list.append({"v": section.get("start_id_name"), "t": int(section.get("number")), "d": cumulated_duration})
                cumulated_duration = cumulated_duration + float(section.get("duration"))
              path_list.append({"v": path[-1].get("goal_id_name"), "t": int(path[-1].get("number")), "d": cumulated_duration}) # Add gold
                
              schedule.update({agent_id: path_list})
      schedules.update({"schedule": schedule})
      schedules.update({"total_duration": total_duration_dict})
    print(schedules)
  return schedules

# https://lxml.de/api/lxml.etree._Element-class.html
def get_map_from_xml(file_path):
  print("Get roadmap from file:", file_path)
  map = {}
  vertices_dict = {}
  edges_list = []
  tree = etree.parse(file_path)
  root = tree.getroot()
  
  for data in root:
    print("data.tag:", data.tag)
    if((data.tag).find('graph') > -1):
      for element in data:
        if((element.tag).find('node') > -1):
          node_id = element.get("id")
          for node_data in element:
            if((node_data.tag).find('data') > -1):
              # print("data text:", node_data.text)
              data_ij = (node_data.text).split(",")
              vertices_dict.update({node_id: [float(data_ij[0]), float(data_ij[1])]})
        elif((element.tag).find('edge') > -1):
          edge = []
          edge.append(element.get("source"))
          edge.append(element.get("target"))
          edges_list.append(edge)
      # print("edges_list:", edges_list)
      print("vertices_dict:", vertices_dict)
      roadmap = {}
      roadmap.update({"vertices": vertices_dict})
      roadmap.update({"edges": edges_list})
      map.update({"roadmap": roadmap})
  return map

def get_tasks_from_xml(file_path, map):
  print("Get tasks from file:", file_path)
  agents = {}
  agents_list = []
  tree = etree.parse(file_path)
  root = tree.getroot()
  for data in root:
    # print("data.tag:", data.tag)
    if(data.tag == 'agent'):
      start_id = goal_id = agent_id = ""
      status = TaskStatus.HAS_TASK
      if(enable_robot123):
        start_id = data.get("start_id") # robot123
        goal_id = data.get("goal_id")
        agent_id = data.get("agent_id")
        if(start_id == goal_id):
          status = TaskStatus.NO_TASK
          print("NO_TASK agent:", agent_id)
      else:
        start_id = "n" + data.get("start_id") # Original
        goal_id = "n" + data.get("goal_id")
        agent_id = str(len(agents_list))
        if(start_id == goal_id):
          status = TaskStatus.NO_TASK
          print("NO_TASK agent:", agent_id)
      
      agent = {"goal": goal_id, "start": start_id, "name": agent_id, "status": status}
      agents_list.append(agent)
  agents = {"agents": agents_list}
  map.update(agents)
  return map

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("map", help="input file containing map")
  parser.add_argument("task", help="input file containing task")
  parser.add_argument("schedule", help="schedule for agents")
  parser.add_argument('--video', dest='video', default=None, help="output video file (or leave empty to show on screen)")
  parser.add_argument("--speed", type=int, default=1, help="speedup-factor")
  parser.add_argument("--radius", type=float, default=0.3, help="radius of robot")
  args = parser.parse_args()

  # with open(args.map) as map_file:
  #   map = yaml.safe_load(map_file)
  map = get_map_from_xml(args.map)
  # print("---------------------map1:", map)
  map = get_tasks_from_xml(args.task, map)
  # print("---------------------map2:", map)


  if "roadmap" not in map:
    print("Not a roadmap file!")
    exit()
    
  schedules = get_schedule_from_xml(args.schedule)
  # print("-------------schedules:", schedules["schedule"])

  animation = Animation(map, schedules, args.radius)

  if args.video:
    # animation.save(args.video, args.speed)
    animation.save(args.video, args.speed)
  else:
    animation.show()

if __name__ == "__main__":
  main()
  
