from lxml import etree
"""
https://lxml.de/tutorial.html
"""

# 创建根节点
root = etree.Element("graphml")
root.set("xmlns", "http://graphml.graphdrawing.org/xmlns")
# root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
# root.set("xsi:schemaLocation", "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd")
 
# 创建子节点
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

child_node = etree.SubElement(child_graph, "node")
child_node.set("id", "n0")
child_data = etree.SubElement(child_node, "data")
child_data.set("key", "key0")
child_data.text = "70,182"
 
# 创建并写入XML文件
tree = etree.ElementTree(root)
tree.write("file.xml", encoding="utf-8", xml_declaration=True, pretty_print=True)