#include<boost/tokenizer.hpp>
#include <algorithm>    // std::shuffle
#include <random>      // std::default_random_engine
#include <chrono>       // std::chrono::system_clock
#include"Const.h"
#include"GeneralRoadmapInstance.h"
using namespace tinyxml2;

GeneralRoadmapInstance::GeneralRoadmapInstance(const string& map_fname, const string& agent_fname, 
	const string& agent_indices, 
	int num_of_rows, int num_of_cols):
	map_fname(map_fname), agent_fname(agent_fname),  agent_indices(agent_indices)
{
	bool succ = loadMap();
	if (!succ)
	{
		cerr << "Map file " << map_fname << " not found." << endl;
		exit(-1);
	}

	succ = loadAgents();
	if (!succ)
	{
		cerr << "Agent file " << agent_fname << " not found." << endl;
		exit(-1);
	}

}

bool GeneralRoadmapInstance::loadMap()
{
	using namespace std;

    cout << "Start getting roadmap from:" << map_fname << std::endl;
    tinyxml2::XMLDocument doc;
    if (doc.LoadFile(map_fname.c_str()) != tinyxml2::XMLError::XML_SUCCESS)
    {
        cout << "Error opening XML file:" << map_fname << std::endl;
        return false;
    }
    tinyxml2::XMLElement *root = 0, *element = 0, *data;
    std::string value;
    std::stringstream stream;
    root = doc.FirstChildElement("graphml")->FirstChildElement("graph");

    int counter = 0;
    for(element = root->FirstChildElement("node"); element; element = element->NextSiblingElement("node"))
    {
        gNode node;

        stream.str("");
        stream.clear();
        stream << element->Attribute("id");
        stream >> node.id_name;
        // cout << "id_name: " << node.id_name << std::endl;

        data = element->FirstChildElement();

        stream.str("");
        stream.clear();
        stream << data->GetText();
        stream >> value;
        auto it = value.find_first_of(",");
        stream.str("");
        stream.clear();
        stream << value.substr(0, it);
        double i;
        stream >> i;
        stream.str("");
        stream.clear();
        value.erase(0, ++it);
        stream << value;
        double j;
        stream >> j;
        node.i = i;
        node.j = j;
        node.id = counter;
        nodes.push_back(node);
        counter++;
        // cout << "Get node id:" << node.id << "  id_name:" << node.id_name << std::endl;
    }
    map_size = nodes_ize = nodes.size();
    my_map.resize(map_size, false); // no obs
    num_of_cols = num_of_rows = map_size;
    cout << "Get nodes from XML file finish!" << std::endl;
    for(element = root->FirstChildElement("edge"); element; element = element->NextSiblingElement("edge"))
    {
        std::string source = std::string(element->Attribute("source"));
        std::string target = std::string(element->Attribute("target"));
        int id1, id2;
        // Find index
        for(unsigned int i = 0; i < nodes_ize; i++)
        {
            if (source == nodes[i].id_name) id1 = nodes[i].id;
            if (target == nodes[i].id_name) id2 = nodes[i].id;
        }
        nodes[id1].neighbors.push_back(id2); // Index
        nodes[id1].neighborsList.push_back(id2);
        // cout << "source: " << source << "  have index:" << id1 << "      target:" << target << "  have index:" << id2 << std::endl;
    }
    cout << "Get edges from XML file finish!" << std::endl;
    for(gNode cur:nodes)
    {
        Node node;
        std::vector<Node> neighbors;
        neighbors.clear();
        for(unsigned int i = 0; i < cur.neighbors.size(); i++)
        {
            node.i = nodes[cur.neighbors[i]].i;
            node.j = nodes[cur.neighbors[i]].j;
            node.id = cur.neighbors[i];
            node.id_name = nodes[node.id].id_name;
            neighbors.push_back(node);
        }
        valid_moves.push_back(neighbors);
    }
    int size = int(nodes.size());
    cout << "Get nodes size:" << size << std::endl;
    return true;
}

bool GeneralRoadmapInstance::loadAgents()
{
	using namespace std;

    tinyxml2::XMLElement *root = 0, *agent = 0;
    tinyxml2::XMLDocument doc;

    // Load XML File
    if (doc.LoadFile(agent_fname.c_str()) != tinyxml2::XMLError::XML_SUCCESS)
    {
        cout << "Error opening XML file: " << agent_fname << std::endl;
        return false;
    }

    // Get ROOT element
    root = doc.FirstChildElement(CNS_TAG_ROOT);
    if (!root)
    {
        cout << "Error! No '" << CNS_TAG_ROOT << "' tag found in XML file!" << std::endl;
        return false;
    }

    for (agent = root->FirstChildElement(); agent; agent = agent->NextSiblingElement())
    {
        Agent a;
        a.agent_name = std::string(agent->Attribute(CNS_TAG_AGENT_ID));
        a.id = int(agents.size());

        a.start_id_name = std::string(agent->Attribute(CNS_TAG_START_ID));
        a.start_id = getIndexByName(a.start_id_name);
        a.start_i = getCoordinateX(a.start_id);
        a.start_j = getCoordinateY(a.start_id);
        start_locations.push_back(a.start_id);

        a.goal_id_name = std::string(agent->Attribute(CNS_TAG_GOAL_ID));
        a.goal_id = getIndexByName(a.goal_id_name);
        a.goal_i = getCoordinateX(a.goal_id);
        a.goal_j = getCoordinateY(a.goal_id);
        goal_locations.push_back(a.goal_id);

        // cout << "Agent agent_name:" << a.agent_name  << " start_id:" << a.start_id << " goal_id:" << a.goal_id << " start_i:" << a.start_i << " start_j:" << a.start_j << std::endl;
        agents.push_back(a);
        // if(int(agents.size()) == k)
        //     break;
    }
    num_of_agents = agents.size();
    cout << "Get tasks number:" << agents.size() << std::endl;

    return true;
}


void GeneralRoadmapInstance::printAgents() const
{
	for (int i = 0; i < num_of_agents; i++)
	{
		cout << "Agent" << i << " : S=(" << start_locations[i] << "," << agents[i].start_id_name << "," << agents[i].start_i << "," << agents[i].start_j
			 << ") ; G=(" << goal_locations[i] << "," << agents[i].goal_id_name << "," << agents[i].goal_i << "," << agents[i].goal_j << ")" << endl;
	}
}

int GeneralRoadmapInstance::getIndexByName(std::string id_name)const
{
    for(unsigned int i = 0; i < nodes_ize; i++)
    {
        if (id_name == nodes[i].id_name) return nodes[i].id;
    }

    cerr << "Warnning, Can not find an index for:" << id_name << endl;
    return -1;
}