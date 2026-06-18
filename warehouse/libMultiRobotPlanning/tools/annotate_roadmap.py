#!/usr/bin/env python3
import argparse
from multiprocessing import Pool
from typing import List, Tuple

import numpy as np
import yaml
from lxml import etree # https://lxml.de/tutorial.html
import os
import sys


N_PROCESSES = 8
EnableSaveXml = True
XmlRoadmapTaskName = "roadmap_task.xml"
XmlRoadmapName = "roadmap.xml"
SaveDirectory = "./"


if __name__ != "__main__":
    from . import collision


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("map", help="input file containing roadmap")
    parser.add_argument("out", help="output file containing annotated roadmap")
    parser.add_argument("radius", help="radius of robot",
                        type=float, default=0.3, nargs="?")
    args = parser.parse_args()
    print(args)

    SaveDirectory = os.path.dirname(args.map) + "/"
    out_path = SaveDirectory + args.out
    xml_roadmap_task_path = SaveDirectory + XmlRoadmapTaskName
    xml_roadmap_path = SaveDirectory + XmlRoadmapName
    print("Save path: ", SaveDirectory)
    print("Output file: ", out_path)
    print("Xml RoadmapTask Path:", xml_roadmap_task_path)
    print("Xml Roadmap save path:", xml_roadmap_path)
    
    # sys.exit()

    with open(args.map) as map_file:
        roadmap = yaml.safe_load(map_file)

    if "roadmap" not in roadmap:
        print("Not a roadmap file!")
        exit()

    roadmap = add_self_edges(roadmap, xml_roadmap_path, xml_roadmap_task_path)
    roadmap = add_edge_conflicts(args.radius, roadmap)

    with open(out_path, 'w') as f:
        yaml.dump(roadmap, f)


def add_edge_conflicts(radius, roadmap):
    conflicts = compute_edge_conflicts(radius, roadmap)
    roadmap["roadmap"]["conflicts"] = conflicts
    return roadmap


def add_self_edges(roadmap, xml_roadmap_path, xml_roadmap_task_path):
    # if undirected, convert to a directed version
    if roadmap["roadmap"]["undirected"]:
        
        # Check the double edgs, 2023-12
        for [start, goal] in roadmap["roadmap"]["edges"]:
            add_flag = True
            for [start2, goal2] in roadmap["roadmap"]["edges"]:
                if goal == start2 and start == goal2:
                    add_flag = False
                    # print([goal, start], "---------", [start2, goal2])
                    break
            if add_flag:
                print("Add:", [goal, start])
                roadmap["roadmap"]["edges"].extend([[goal, start]])
        
                    
        # new_edges = [[goal, start]
        #              for start, goal in roadmap["roadmap"]["edges"]]
        # roadmap["roadmap"]["edges"].extend(new_edges)
        roadmap["roadmap"]["undirected"] = False

    if(EnableSaveXml):
        save_roadmap2xml(roadmap, xml_roadmap_path)
        save_task2xml(roadmap, xml_roadmap_task_path)
        

    # if wait actions are allowed, add self-edges
    if roadmap["roadmap"]["allow_wait_actions"]:
        new_edges = [[v, v] for v in roadmap["roadmap"]["vertices"]]
        roadmap["roadmap"]["edges"].extend(new_edges)
        roadmap["roadmap"]["allow_wait_actions"] = False

    return roadmap


def check_proxy(args):
    """Prox method to call the collision checker with the right arguments."""
    _, _, E, p0, p1, q0, q1 = args
    return collision.ellipsoid_collision_motion(E, p0, p1, q0, q1)


def compute_edge_conflicts(radius, map):
    # compute the pairwise collisions and add them to the map
    E = np.diag([radius, radius])
    num_edges = len(map["roadmap"]["edges"])
    v_dict = map["roadmap"]["vertices"]
    edges = map["roadmap"]["edges"]
    conflicts = [[] for _ in range(num_edges)]
    edges_to_check: List[Tuple[
        int, int, np.ndarray,  # i, j, E
        np.ndarray, np.ndarray, np.ndarray, np.ndarray  # p0, p1, q0, q1
    ]] = []
    # print("-------------------------")
    # print(edges[0])
    # print(v_dict[edges[0][0]])
    # print(v_dict)
    # print("=======================")
    for i in range(0, num_edges):
        p0 = np.asarray(v_dict[edges[i][0]])
        p1 = np.asarray(v_dict[edges[i][1]])
        for j in range(i+1, num_edges):
            if collision.precheck_indices(edges[i], edges[j]):
                # trivial case
                conflicts[i].append(j)
                conflicts[j].append(i)
            else:
                q0 = np.asarray(v_dict[edges[j][0]])
                q1 = np.asarray(v_dict[edges[j][1]])
                if collision.precheck_bounding_box(E, p0, p1, q0, q1):
                    edges_to_check.append((i, j, E, p0, p1, q0, q1))

    # check all edges in parallel
    with Pool(N_PROCESSES) as p:
        results = p.map(check_proxy, edges_to_check)
    for result, (i, j, _, _, _, _, _) in zip(results, edges_to_check):
        if result:
            conflicts[i].append(j)
            conflicts[j].append(i)

    return conflicts

def save_roadmap2xml(roadmap, file_path):
    print("Save roadmap to XML file..............")
    # Creat root
    root = etree.Element("graphml")
    root.set("xmlns", "http://graphml.graphdrawing.org/xmlns")
    # root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    # root.set("xsi:schemaLocation", "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd")
    
    # Creat node
    child_key0 = etree.SubElement(root, "key")
    child_key0.set("id", "key0")
    child_key0.set("for", "node")
    child_key0.set("attr.name", "coords")
    child_key0.set("attr.type", "string")

    child_key1 = etree.SubElement(root, "key")
    child_key1.set("id", "key1")
    child_key1.set("for", "edge")
    child_key1.set("attr.name", "weight")
    child_key1.set("attr.type", "double")


    child_graph = etree.SubElement(root, "graph")
    child_graph.set("id", "G")
    child_graph.set("edgedefault", "directed")
    child_graph.set("parse.nodeids", "free")
    child_graph.set("parse.edgeids", "canonical")
    child_graph.set("parse.order", "nodesfirst")

    v_dict = roadmap["roadmap"]["vertices"]
    for vertices in v_dict:
        # print(v_dict[vertices])
        child_node = etree.SubElement(child_graph, "node")
        child_node.set("id", vertices)
        child_data = etree.SubElement(child_node, "data")
        child_data.set("key", "key0")
        x = str(v_dict[vertices][0])
        y = str(v_dict[vertices][1])
        child_data.text = x + "," + y
    
    edges = roadmap["roadmap"]["edges"]
    for i in range(0, len(edges)):
        # print(edges[0])
        child_node = etree.SubElement(child_graph, "edge")
        child_node.set("id", edges[i][0] + "-" + edges[i][1]) # TODO: Get from database or protocal
        child_node.set("source", edges[i][0])
        child_node.set("target", edges[i][1])
        child_data = etree.SubElement(child_node, "data")
        child_data.set("key", "key1")
        child_data.text = "1" # TODO: Can be changed according to distance

    # Write and save to XML file
    tree = etree.ElementTree(root)
    tree.write(file_path, encoding="utf-8", xml_declaration=True, pretty_print=True)

def save_task2xml(roadmap, file_path):
    print("Save tasks to XML file..............")
    root = etree.Element("root")
    
    agents = roadmap["agents"]
    for i in range(0, len(agents)):
        # print(agents)
        child_agent = etree.SubElement(root, "agent")
        child_agent.set("agent_id", agents[i]["name"])
        child_agent.set("start_id", agents[i]["start"])
        child_agent.set("goal_id", agents[i]["goal"])
    tree = etree.ElementTree(root)
    tree.write(file_path, encoding="utf-8", xml_declaration=True, pretty_print=True)

if __name__ == "__main__":
    import collision
    main()
