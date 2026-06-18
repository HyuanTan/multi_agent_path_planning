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
import matplotlib.pyplot as plt
import numpy as np

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
        database='warehouse_map',
        buffered=True)
    

    # Read Map
    cur = conn.cursor()
    # cur.execute(sql语句)
    result = cur.execute("select * from map_station")
    result_list = cur.fetchall() # get information

    des = cur.description
    print("table keywords:")
    print(des)

    plt.ion()
    plt.figure()
    print("table content:")

    select_map_code = "2F"
    print("selected map code:", select_map_code)

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

        if select_map_code == map_code:
            station = {station_code: [x0, y0]}
            station_dict.update(station)
            if item[21] == 1:
                plt.scatter(x0, y0, s = 20, color = '#ff7f0e',
                    marker='o',label = station_name)
            else:
                plt.scatter(x0, y0, s = 20, color = 'k',
                        marker='o',label = station_name)
    

    ## path
    result = cur.execute("select * from map_path")
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

        if select_map_code == map_code:
            
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
            plt.pause(0.001)

    plt.pause(10)
    # plt.close

    # close 
    cur.close()
    # close connection
    conn.close()


if __name__ == "__main__":
    main()