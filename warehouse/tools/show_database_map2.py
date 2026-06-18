#!/usr/bin/python3
"""
Show the warehouse paths and stations data
author: Tam Fowun
data: 2023-09-04
"""

import time
# import sqlite3
import argparse
import mysql.connector
import matplotlib
from matplotlib.patches import Circle, FancyArrow, Rectangle, Arrow
import matplotlib.pyplot as plt
from matplotlib import animation
import matplotlib.animation as manimation
import numpy as np

EnableJieshibang = False
EnableQidu = True


Colors = ['orange', 'blue', 'green']
DatabaseName = ""
MapStationName = ""
MapPathName = ""
FloorNum = ""
XMax = 100
XMin = -100
YMax = 100
YMin = -100
OnlyStation = True # False # Whether only show station info

if EnableJieshibang:
    DatabaseName = "warehouse_map"
    MapStationName = "map_station"
    MapPathName = "map_path"
    FloorNum = "2F"
    XMax = 80
    XMin = -80
    YMax = 80
    YMin = -80
if EnableQidu:
    DatabaseName = "warehouse_qidu"
    MapStationName = "mpp_station"
    MapPathName = "mpp_path"
    FloorNum = "qidu"
    XMax = 120
    XMin = -120
    YMax = 120
    YMin = -120


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("host", help="database host")
    # parser.add_argument("user", help="database user")
    # parser.add_argument("password", help="database password")
    # parser.add_argument("database_name", help="database name")
    
    # args = parser.parse_args()

    conn = mysql.connector.connect(
        host='localhost',
        user='holly',
        password='aa',
        charset='utf8',
        database=DatabaseName,
        buffered=True)
    

    # Read Map
    cur = conn.cursor()
    # TODO:https://stackoverflow.com/questions/51493860/mysql-connector-with-python-getting-data-by-field-name
    # cur = conn.cursor(MySQLdb.cursors.DictCursor) # Can  access the values by field names instead indexes.
    # cur.execute(sql语句)
    result = cur.execute("select * from " + MapStationName)
    result_list = cur.fetchall() # get information

    des = cur.description
    # print("table keywords:")
    # print(des)

    # plt.ion()
    # plt.figure()

    # todo: calculate the maximun and minimun
    aspect = (XMax - XMin) / (YMax - YMin)
    radius = 0.05
    fig = plt.figure(frameon=False, figsize=(4 * aspect, 4))
    ax = fig.add_subplot(111, aspect='equal')
    fig.subplots_adjust(left=0,right=1,bottom=0,top=1, wspace=None, hspace=None)

    # plt.xlim(XMin - radius, XMax + radius)
    # plt.ylim(YMin - radius, YMax + radius)
    print("XMax:", XMax, "XMin:", XMin, "YMax:", YMax, "YMin:", YMin)
    plt.xlim(55, 65)
    plt.ylim(10, 70)

    # patches = []
    # artists = []
    vertices = dict()
    vertice_names = dict()

    print("selected map code:", FloorNum)

    ## station
    station_dict = {}
    for item in result_list:
        station_code = item[0]
        station_name = item[1]
        map_code = item[2]

        # position
        x0 = item[5]
        y0 = item[6]
        # print("position:", x0, y0)

        # angle
        orientation_x = item[8]
        orientation_y = item[9]
        orientation_z = item[10]
        orientation_w = item[11]

        # character
        is_pass_point = item[21]
        counter = 0
        if FloorNum == map_code:
            # if 1:
            if "P" in station_name or "S" in station_name:
                continue
            else:
                if counter % 4 == 0:
                    # print(">>>>> station")
                    # print("Get node:", station_name)
                    station = {station_code: [x0, y0]}
                    station_dict.update(station)
                    # if item[21] == 1:
                    #     plt.scatter(x0, y0, s = 20, color = '#ff7f0e',
                    #         marker='o',label = station_name)
                    # else:
                    #     plt.scatter(x0, y0, s = 20, color = 'k',
                    #             marker='o',label = station_name)

                    vertices[station_name] = Circle((x0, y0), radius, facecolor=Colors[counter%len(Colors)], edgecolor='black')
                    vertices[station_name].original_face_color = Colors[counter%len(Colors)]
                    # patches.append(vertices[station_name])

                    # https://matplotlib.org/stable/users/explain/text/text_intro.html
                    vertice_names[station_name] = ax.text(x0, y0, station_name, fontsize=6)
                    vertice_names[station_name].set_horizontalalignment('center')
                    vertice_names[station_name].set_verticalalignment('center')
                    # artists.append(vertice_names[station_name])

                    ax.add_patch(vertices[station_name])
                    ax.add_artist(vertice_names[station_name])

                # plt.gca().add_patch(vertices[station_name]) # gca() means Get Current Axis
                # plt.gca().add_artist(vertice_names[station_name])
                
                counter += 1
    
    
    if not OnlyStation:
        ## path
        result = cur.execute("select * from " + MapPathName)
        result_list = cur.fetchall() # get information
        for item in result_list:
            path_code = item[0]
            path_name = item[1]
            map_code = item[2]
            start_station = item[3]
            end_station = item[4]
            path_length = item[5]
            type = item[6]
            bezier_conf = item[7]
            maximum_velocity = item[8]
            cost = item[9]
            obs_area = item[10]
            status = item[11]
            driving_angle = item[13]

            if FloorNum == map_code:
                if (("P" in start_station) or ("P" in end_station)) or (("S" in start_station) or ("S" in end_station)):
                    continue
                else:
                    # print(">>>>> arrow")
                    x_begin = station_dict[start_station][0]
                    y_begin = station_dict[start_station][1]
                    x_end = station_dict[end_station][0]
                    y_end = station_dict[end_station][1]
                    print("Find a path:", path_code, " with station:", start_station, end_station)
                    print("station:", x_begin, y_begin, x_end, y_end)
                    plt.arrow(x_begin, y_begin, x_end - x_begin, y_end - y_begin,
                                length_includes_head=True,     # 增加的长度包含箭头部分
                                head_width = 0.3, head_length =0.2, fc="red", ec="black",linestyle='-',linewidth=0.3)
            
                    # plt.show()
                    # time.sleep(0.001)
                    # plt.pause(0.001)
    

    # plt.show()
    plt.pause(100000)
    # plt.close

    # close 
    cur.close()
    # close connection
    conn.close()


if __name__ == "__main__":
    main()