#!/usr/bin/python3
"""
Show the warehouse paths and stations data
author: Tam Fowun
data: 2023-09-25
For libMultiRobotPlanning
"""

import time
# import sqlite3
import argparse
import mysql.connector
import numpy as np
import yaml

EnableJieshibang = False
EnableQidu = True

DatabaseName = ""
MapStationName = ""
MapPathName = ""
FloorNum = ""
DataFilePath = ""
# map setting
Undirected = True # False
AllowWaitActions = True

if EnableJieshibang:
    DatabaseName = "warehouse_map"
    MapStationName = "map_station"
    MapPathName = "map_path"
    FloorNum = "2F"
    DataFilePath = "./"
    Undirected = True # False
    AllowWaitActions = True

if EnableQidu:
    DatabaseName = "warehouse_qidu"
    MapStationName = "mpp_station"
    MapPathName = "mpp_path"
    FloorNum = "qidu"
    DataFilePath = "/home/holly/ShareCode/warehouse/data/warehouse_qidu/"
    Undirected = True # False
    AllowWaitActions = True


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
    # cur.execute(sql语句)
    result = cur.execute("select * from " + MapStationName)
    result_list = cur.fetchall() # get information

    des = cur.description
    print("table keywords:")
    print(des)

    print("table content:")

    print("selected map code:", FloorNum)


    ## station
    vertices = {}
    for item in result_list:
        station_code = str(item[0])
        station_name = str(item[1])
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

        
        if FloorNum == map_code:
            vertices.update({station_name: [x0, y0]})
    

    ## path
    result = cur.execute("select * from " + MapPathName)
    result_list = cur.fetchall() # get information
    edges = []
    for item in result_list:
        path_code = item[0]
        path_name = item[1]
        map_code = item[2]
        start_station = str(item[3])
        end_station = str(item[4])
        path_length = item[5]
        type = item[6]
        bezier_conf = item[7]
        maximum_velocity = item[8]
        cost = item[9]
        obs_area = item[10]
        status = item[11]
        driving_angle = item[13]

        if FloorNum == map_code:
            edges.append([start_station, end_station])

    roadmap_data = {
        "undirected": Undirected,
        "allow_wait_actions": AllowWaitActions,
        "vertices": vertices,
        "edges": edges,
    }

    all_data = {}
    if EnableJieshibang:
        if FloorNum == "1F":
            all_data = {
                "roadmap": roadmap_data,
                "agents":[
                    {"name": "agent0", "start": "P201", "goal": "P217"},
                    {"name": "agent1", "start": "P225", "goal": "P202"},
                    {"name": "agent2", "start": "P234", "goal": "P216"},
                    {"name": "agent3", "start": "P230", "goal": "P218"},
                ],
            }

        elif FloorNum == "2F":
            all_data = {
                "roadmap": roadmap_data,
                "agents":[
                    {"name": "agent0", "start": "201", "goal": "1010"},
                    {"name": "agent1", "start": "202", "goal": "1008"},
                    {"name": "agent2", "start": "0907", "goal": "205-1"},
                    {"name": "agent3", "start": "0502", "goal": "203"},
                    {"name": "agent4", "start": "0902", "goal": "0908"},
                    {"name": "agent5", "start": "0609", "goal": "0610"},
                ],
            }

        """
        elif FloorNum == "2F":
            all_data = {
                "roadmap": roadmap_data,
                "agents":[
                    {"name": "agent0", "start": "201", "goal": "1010"},
                    {"name": "agent1", "start": "0804", "goal": "0702"},
                    {"name": "agent2", "start": "0907", "goal": "205-1"},
                    {"name": "agent3", "start": "0502", "goal": "203"},
                    {"name": "agent4", "start": "0902", "goal": "0908"},
                    {"name": "agent5", "start": "0609", "goal": "0610"},
                    {"name": "agent6", "start": "0510", "goal": "0504"},
                    {"name": "agent7", "start": "1009", "goal": "0708"},
                    {"name": "agent8", "start": "1001", "goal": "0901"},
                    {"name": "agent9", "start": "0402", "goal": "0409"},
                ],
            }
        """

            
        '''
        elif FloorNum == "2F":
            all_data = {
                "roadmap": roadmap_data,
                "agents":[
                    {"name": "agent0", "start": "P04", "goal": "P15"},
                    {"name": "agent1", "start": "P47", "goal": "P120"},
                    {"name": "agent2", "start": "0902", "goal": "1010"},
                    {"name": "agent3", "start": "0602", "goal": "203"},
                    # {"name": "agent4", "start": "p27", "goal": "0909"},
                    {"name": "agent5", "start": "0208", "goal": "P77"},
                    {"name": "agent6", "start": "0510", "goal": "0504"},
                    # {"name": "agent7", "start": "0102", "goal": "0811"},
                    # {"name": "agent8", "start": "P48", "goal": "P78"},
                    {"name": "agent9", "start": "0710", "goal": "P39"},
                    # {"name": "agent10", "start": "0509", "goal": "1003"},
                ],
            }
        '''
    
    if EnableQidu:

        all_data = {
        "roadmap": roadmap_data,
        "agents":[
            {"name": "agent0", "start": "103", "goal": "001001001"},
            {"name": "agent1", "start": "110", "goal": "011003001"},
            {"name": "agent2", "start": "116", "goal": "002005001"},
            {"name": "agent3", "start": "117", "goal": "006008001"},
            {"name": "agent4", "start": "122", "goal": "011001001"},
            {"name": "agent5", "start": "124", "goal": "015004001"},
            {"name": "agent6", "start": "132", "goal": "020006001"},

            {"name": "agent7", "start": "004001001", "goal": "105"},
            {"name": "agent8", "start": "006001001", "goal": "108"},
            {"name": "agent9", "start": "008008001", "goal": "119"},
            {"name": "agent10", "start": "021007001", "goal": "128"},
            {"name": "agent11", "start": "009003001", "goal": "125"},
            {"name": "agent12", "start": "012001001", "goal": "134"},
            {"name": "agent13", "start": "018006001", "goal": "135"},

            {"name": "agent14", "start": "020004001", "goal": "019001001"},
            {"name": "agent15", "start": "021008001", "goal": "022001001"},
            {"name": "agent16", "start": "023003001", "goal": "021001001"},
            {"name": "agent17", "start": "018007001", "goal": "015007001"},
            {"name": "agent18", "start": "017008001", "goal": "014006001"},
            {"name": "agent19", "start": "011008001", "goal": "009008001"},
        ],
    }

    '''
        all_data = {
        "roadmap": roadmap_data,
        "agents":[
            {"name": "agent0", "start": "S43-1", "goal": "001001001"},
            {"name": "agent1", "start": "S36-1", "goal": "011003001"},
            {"name": "agent2", "start": "S124-2", "goal": "S136-2"},
            {"name": "agent3", "start": "S128-2", "goal": "S2-1"},
            {"name": "agent4", "start": "S126-1", "goal": "S46-1"},
            {"name": "agent5", "start": "S129-1", "goal": "S131-1"},
            {"name": "agent6", "start": "S130-1", "goal": "S135-1"},
            {"name": "agent7", "start": "S125-1", "goal": "S120-1"},
            {"name": "agent8", "start": "S106-1", "goal": "S104-1"},
            {"name": "agent9", "start": "S105-2", "goal": "S108-2"},
            {"name": "agent10", "start": "021007001", "goal": "S15-1"},
            {"name": "agent11", "start": "018007001", "goal": "S117-2"},
            {"name": "agent12", "start": "S131-2", "goal": "106"},
            {"name": "agent13", "start": "S117-1", "goal": "S114-2"},
            {"name": "agent14", "start": "020004001", "goal": "111"},
            {"name": "agent15", "start": "020003001", "goal": "S125-2"},
            {"name": "agent16", "start": "023003001", "goal": "021008001"},
            {"name": "agent17", "start": "S126-2", "goal": "S127-2"},
            {"name": "agent18", "start": "S103-1", "goal": "S87-1"},
            {"name": "agent19", "start": "2003", "goal": "S112-2"},
            # {"name": "agent20", "start": "S85-1", "goal": "S107-2"},
        ],
    }
    '''



    
    print("vertices:", vertices)
    print("edges:", edges)
    with open(DataFilePath + 'roadmap_data.yaml', 'w', encoding='utf-8') as f:
        print("Save data to: ", DataFilePath + 'roadmap_data.yaml')
        yaml.dump_all(documents=[all_data], stream=f, allow_unicode=True)
 

    # close 
    cur.close()
    # close connection
    conn.close()


if __name__ == "__main__":
    main()