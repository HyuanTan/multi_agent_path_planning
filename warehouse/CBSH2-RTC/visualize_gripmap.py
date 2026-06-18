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
 

Colors = ['orange', 'blue', 'green']
Interval = 1
FreeLand = 0
Obstacle = 255

class Animation:
  def __init__(self, map, task, schedules, radius):
    self.map = map
    self.task = task
    self.schedules = schedules
    self.radius = radius

    # find boundary
    self.map_width = self.map["size"]["width"]
    self.map_height = self.map["size"]["height"]
    xmin = -self.map_width
    ymin = -self.map_height
    xmax = self.map_width
    ymax = self.map_height

    aspect = (xmax - xmin) / (ymax - ymin)
    self.fig = plt.figure(frameon=False, figsize=(4 * aspect, 4))
    self.ax = self.fig.add_subplot(111, aspect='equal')
    self.fig.subplots_adjust(left=0,right=1,bottom=0,top=1, wspace=None, hspace=None)

    self.patches = []
    self.artists = []
    self.agents = dict()
    self.agent_names = dict()

    plt.imshow(map["map"])
    # plt.show()

    # create agents:
    self.T = 0
    # draw goals first
    counter = 0
    for agent_name in self.schedules:
      v = self.task[agent_name]["goal"]
      self.patches.append(Rectangle((v[0] - radius, v[1] - radius), 2*radius, 2*radius, facecolor=Colors[counter%len(Colors)], edgecolor='black', alpha=0.5))
      '''
      v = self.task[agent_name]["start"]
      self.agents[agent_name] = Circle((v[0], v[1]), radius, facecolor=Colors[counter%len(Colors)], edgecolor='black', alpha=0.5)
      self.agents[agent_name].original_face_color = Colors[counter%len(Colors)]
      self.patches.append(self.agents[agent_name])
      '''
      counter = counter + 1
    
    counter = 0
    for key, value in self.schedules.items():
      name = key
      v = self.task[name]["start"]
      self.agents[name] = Circle((v[0], v[1]), radius, facecolor=Colors[counter%len(Colors)], edgecolor='black')
      self.agents[name].original_face_color = Colors[counter%len(Colors)]
      self.patches.append(self.agents[name])
      self.T = max(self.T, len(value))
      self.agent_names[name] = self.ax.text(v[0], v[1], name.replace('Agent', ''))
      self.agent_names[name].set_horizontalalignment('center')
      self.agent_names[name].set_verticalalignment('center')
      self.artists.append(self.agent_names[name])
      counter = counter + 1

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
        if np.linalg.norm(pos1 - pos2) == 0.0:
          d1.set_facecolor('red')
          d2.set_facecolor('red')
          print("COLLISION! (agent-agent) ({}, {})".format(i, j))
    ''' Have some problem
    # check drive-obstacle collisions
    for i in range(0, len(agents_array)):
      d1 = agents_array[i]
      pos1 = np.array(d1.center)
      if (self.map["map"][int(pos1[0]), int(pos1[1])] == Obstacle):
        d1.set_facecolor('red')
        print("COLLISION! (agent-obstacle) {}-({},{})".format(i, int(pos1[0]), int(pos1[1])))
    '''
         
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

def get_map(file_path):
  # For Nathan's benchmark
  f = open(file_path,"r")
  lines = f.readlines()
  lines_num = range(0, len(lines))
  map_height = 0
  map_width = 0
  map_dict = {}
  map = [[]]
  get_map_height = False
  get_map_width = False
  get_ready = False
  for index, data in zip(lines_num, lines):
    # print(index, data)
    if index == 1 and "height" in data:
      map_height = int((data.split(" "))[-1])
      get_map_height = True
      print("map_height:", map_height)
    if index == 2 and "width" in data:
      map_width = int((data.split(" "))[-1])
      get_map_width = True
      print("map_width:", map_width)

    if(get_map_height and get_map_width and not get_ready):
      # map = np.zeros((map_height, map_width), dtype=int)
      # map = np.full((map_height, map_width), np.inf, dtype=int)
      map = np.full((map_height, map_width), -1, dtype=int)
      map_size = {"height": map_height, "width": map_width}
      map_dict.update({"size": map_size})
      get_ready = True
    # else:
    #   print("Can not get width and height, please check the data")
    #   break

    if index > 3:
      row_index = index - 4
      column = range(0, get_map_width-1)
      column_index = 0
      # print("...........row_index:", row_index)
      for element in data:
      # for column_index, element in zip(column, data):
        if element == ".": # free land, sign as 0
          map[row_index, column_index] = FreeLand
          # print("Get . in ", column_index)
        elif element == "@": # obstacle, sign as 255
          map[row_index, column_index] = Obstacle
          # print("Get @ in ", column_index)
        elif element == "T": # Tree, sign as 255
          map[row_index, column_index] = Obstacle
        else:
          pass
          # print("Get ", element, " in ", column_index, " please check")

        column_index = column_index + 1
  map_dict.update({"map": map})

   
  # img_path = os.path.dirname(file_path) + "/" + "gripmap.png"
  # matplotlib.image.imsave(img_path, map)
  # plt.imsave(img_path, map)
  # https://pillow.readthedocs.io/en/stable/reference/Image.html
  # img = Image.fromarray(map, mode="L")
  # img.save(img_path)

  with open(os.path.dirname(file_path) + "/" + "gripmap.txt", 'w') as f:
    csv.writer(f, delimiter=' ').writerows(map)
  return map_dict

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
      element = element.replace("(", "")
      element = element.replace(")", "")
      element_list = element.split(",") # (y,x)
      # path_dict = {"v": [int(element_list[0]), int(element_list[1])], "t": t}
      path_dict = {"v": [int(element_list[1]), int(element_list[0])], "t": t} # (x,y)
      path_list.append(path_dict)
      t = t + 1

    schedules.update({agent_name: path_list})
  # print(schedules)
  return schedules


def get_task(file_path):
  f = open(file_path,"r")
  lines = f.readlines()
  task = {}
  lines_num = range(0, len(lines))
  angent_num = 0
  for index, data in zip(lines_num, lines):
    if index > 0:
      agent_dict = {}
      data_list = data.split("\t")
      agent_name = "Agent" + str(angent_num)
      angent_num = angent_num + 1
      agent_dict.update({"start": [float(data_list[4]), float(data_list[5])]}) # start(x,y):4,5   goal(x,y):6,7
      agent_dict.update({"goal": [float(data_list[6]), float(data_list[7])]})
      task.update({agent_name: agent_dict})
  # print(task) 
  return task


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("map", help="input file containing map")
  parser.add_argument("task", help="input file containing task")
  parser.add_argument("schedule", help="schedule for agents")
  parser.add_argument('--video', dest='video', default=None, help="output video file (or leave empty to show on screen)")
  parser.add_argument("--speed", type=int, default=1, help="speedup-factor")
  parser.add_argument("--radius", type=float, default=0.3, help="radius of robot")
  args = parser.parse_args()

  map = get_map(args.map)
  schedules = get_schedule(args.schedule)
  task = get_task(args.task)
  
  # plt.imshow(map["map"])
  # plt.show()

  animation = Animation(map, task, schedules, args.radius)

  if args.video:
    animation.save(args.video, args.speed)
  else:
    animation.show()

if __name__ == "__main__":
  main()
  
