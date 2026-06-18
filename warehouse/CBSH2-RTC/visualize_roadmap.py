#!/usr/bin/env python3
import yaml
import matplotlib
from matplotlib.patches import Circle, FancyArrow, Rectangle, Arrow
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
from matplotlib import image
import matplotlib.animation as manimation
import argparse
import math
import sys
import os
from PIL import Image
import csv
from lxml import etree # https://lxml.de/tutorial.html
 
Colors = ['orange', 'blue', 'green']
Interval = 10
FreeLand = 0
Obstacle = 255

# find boundary
xmin = 9999999.99999
ymin = 9999999.99999
xmax = -9999999.99999
ymax = -9999999.99999

# xmin = -50
# ymin = -50
# xmax = 50
# ymax = 50

class Animation:
  def __init__(self, map, schedules, radius):
    self.map = map
    self.schedules = schedules
    self.radius = radius

    aspect = (xmax - xmin) / (ymax - ymin)
    print("xmin, ymin, xmax, ymax", xmin, ymin, xmax, ymax)
    self.fig = plt.figure(frameon=False, figsize=(4 * aspect, 4))
    self.ax = self.fig.add_subplot(111, aspect='equal')
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
      self.patches.append(FancyArrow(start[0], start[1], goal[0] - start[0], goal[1] - start[1], width=0.05, length_includes_head=True))#, head_width=0))

    # create agents:
    self.T = 0
    # draw goals first
    counter = 0
    # for agent_name in self.schedules:
    for task in self.map["agents"]:
      agent_name = task["name"]
      v = map["roadmap"]["vertices"][task["goal"]]
      self.patches.append(Rectangle((v[0] - radius, v[1] - radius), 2*radius, 2*radius, facecolor=Colors[counter%len(Colors)], edgecolor='black', alpha=0.5))
      
      v = map["roadmap"]["vertices"][task["start"]]
      self.agents[agent_name] = Circle((v[0], v[1]), radius, facecolor=Colors[counter%len(Colors)], edgecolor='black', alpha=0.5)
      self.agents[agent_name].original_face_color = Colors[counter%len(Colors)]
      self.patches.append(self.agents[agent_name])
      
      self.agent_names[agent_name] = self.ax.text(v[0], v[1], agent_name.replace('agent', ''))
      self.agent_names[agent_name].set_horizontalalignment('center')
      self.agent_names[agent_name].set_verticalalignment('center')
      self.artists.append(self.agent_names[agent_name])
      counter = counter + 1

    for key, value in self.schedules.items():
      self.T = max(self.T, len(value))
    
    print("T:", self.T)
    print("start show.........")
    self.anim = animation.FuncAnimation(self.fig, self.animate_func,
                               init_func=self.init_func,
                               frames=int(self.T) * Interval,
                               interval=100,
                               blit=True)

  def save(self, file_name, speed):
    self.anim.save(
      file_name,
      "ffmpeg",
      fps=10 * speed,
      dpi=200),
      # savefig_kwargs={"pad_inches": 0, "bbox_inches": "tight"})

  def show(self):
    plt.show()

  def init_func(self):
    for p in self.patches:
      self.ax.add_patch(p)
    for a in self.artists:
      self.ax.add_artist(a)
    
    return self.patches + self.artists

  def animate_func(self, i):
    # print("animate_func:", i)
    for agent_name, path in self.schedules.items():
      pos = self.getState(i / Interval, path)
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
        # if np.linalg.norm(pos1 - pos2) < 2 * self.radius:
        if np.linalg.norm(pos1 - pos2) < self.radius:
        # if np.linalg.norm(pos1 - pos2) == 0.0:
          d1.set_facecolor('red')
          d2.set_facecolor('red')
          print("COLLISION! (agent-agent) ({}, {})".format(i, j))
         
    return self.patches + self.artists


  def getState(self, t, d):
    idx = 0
    while idx < len(d) and d[idx]["t"] < t:
      idx += 1
    if idx == 0:
      return np.array(d[0]["v"])
    elif idx < len(d):
      posLast = np.array(d[idx-1]["v"])
      posNext = np.array(d[idx]["v"])
    else:
      return np.array(d[-1]["v"])
    dt = d[idx]["t"] - d[idx-1]["t"]
    t = (t - d[idx-1]["t"]) / dt

    pos = (posNext - posLast) * t + posLast
    return pos

# https://lxml.de/api/lxml.etree._Element-class.html
def get_map_from_xml(file_path):
  global xmin
  global ymin
  global xmax
  global ymax

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
              x = float(data_ij[0])
              y = float(data_ij[1])
              vertices_dict.update({node_id: [x, y]})
              if(x < xmin): xmin = x
              if(x > xmax): xmax = x 
              if(y < ymin): ymin = y
              if(y > ymax): ymax = y

        elif((element.tag).find('edge') > -1):
          edge = []
          edge.append(element.get("source"))
          edge.append(element.get("target"))
          edges_list.append(edge)
      # print("edges_list:", edges_list)
      # print("vertices_dict:", vertices_dict)
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

      start_id = data.get("start_id") # robot123
      goal_id = data.get("goal_id")
      agent_id = data.get("agent_id")
     
      agent = {"goal": goal_id, "start": start_id, "name": agent_id}
      agents_list.append(agent)
  agents = {"agents": agents_list}
  map.update(agents)
  return map
  
def get_schedule(file_path):
  f = open(file_path,"r")
  lines = f.readlines()
  schedules = {}
  for data in lines:
    agent_name = ((data.split(":"))[0]).replace(" ", "")
    path_string = (data.split(":"))[-1]
    path_string_list = path_string.split("->")[:-1] # Removing newline character
    path_list = []
    t = 0
    for element in path_string_list:
      element = element.split("(")[-1]
      # element = element.replace("(", "")
      element = element.replace(")", "")
      element_list = element.split(",") # (y,x)
      path_dict = {"v": [float(element_list[0]), float(element_list[1])], "t": t}
      path_list.append(path_dict)
      t = t + 1

    schedules.update({agent_name: path_list})
  # print(schedules)
  return schedules

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("map", help="input file containing map")
  parser.add_argument("task", help="input file containing task")
  parser.add_argument("schedule", help="schedule for agents")
  parser.add_argument('--video', dest='video', default=None, help="output video file (or leave empty to show on screen)")
  parser.add_argument("--speed", type=int, default=1, help="speedup-factor")
  parser.add_argument("--radius", type=float, default=0.3, help="radius of robot")
  args = parser.parse_args()

  map = get_map_from_xml(args.map)
  map = get_tasks_from_xml(args.task, map)
  schedules = get_schedule(args.schedule)
 
  # plt.imshow(map["map"])
  # plt.show()

  animation = Animation(map, schedules, args.radius)

  if args.video:
    animation.save(args.video, args.speed)
  else:
    animation.show()

if __name__ == "__main__":
  main()
  
