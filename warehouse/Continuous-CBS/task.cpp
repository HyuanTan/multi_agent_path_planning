#include "task.h"
Task::Task()
{
    agents.clear();
}

bool Task::get_task(const char *FileName, int k)
{
    tinyxml2::XMLElement *root = 0, *agent = 0;
    tinyxml2::XMLDocument doc;

    // Load XML File
    if (doc.LoadFile(FileName) != tinyxml2::XMLError::XML_SUCCESS)
    {
        std::cout << "Error opening XML file!" << std::endl;
        return false;
    }

    // Get ROOT element
    root = doc.FirstChildElement(CNS_TAG_ROOT);
    if (!root)
    {
        std::cout << "Error! No '" << CNS_TAG_ROOT << "' tag found in XML file!" << std::endl;
        return false;
    }

    for (agent = root->FirstChildElement(); agent; agent = agent->NextSiblingElement())
    {
        Agent a;
        a.start_i = agent->DoubleAttribute(CNS_TAG_START_I);
        a.start_j = agent->DoubleAttribute(CNS_TAG_START_J);
        a.start_id = agent->IntAttribute(CNS_TAG_START_ID);
        a.goal_i = agent->DoubleAttribute(CNS_TAG_GOAL_I);
        a.goal_j = agent->DoubleAttribute(CNS_TAG_GOAL_J);
        a.goal_id = agent->IntAttribute(CNS_TAG_GOAL_ID);
        a.start_id_name = std::to_string(a.start_id);
        a.goal_id_name = std::to_string(a.goal_id);
        a.id = int(agents.size());
        a.start_i = agent->DoubleAttribute(CNS_TAG_START_I);
        std::cout << "Agent id:" << a.id  << " start_id:" << a.start_id << " goal_id:" << a.goal_id << " start_i:" << a.start_i << " start_j:" << a.start_j << std::endl;
        agents.push_back(a);
        if(int(agents.size()) == k)
            break;
    }

    std::cout << "Get tasks number:" << agents.size() << std::endl;

    return true;
}


bool Task::get_robot123_task(const char *FileName, const Map &map, int k)
{
    std::cout << "Start getting tasks for robot123!" << std::endl;
    tinyxml2::XMLElement *root = 0, *agent = 0;
    tinyxml2::XMLDocument doc;

    // Load XML File
    if (doc.LoadFile(FileName) != tinyxml2::XMLError::XML_SUCCESS)
    {
        std::cout << "Error opening XML file!" << std::endl;
        return false;
    }

    // Get ROOT element
    root = doc.FirstChildElement(CNS_TAG_ROOT);
    if (!root)
    {
        std::cout << "Error! No '" << CNS_TAG_ROOT << "' tag found in XML file!" << std::endl;
        return false;
    }

    for (agent = root->FirstChildElement(); agent; agent = agent->NextSiblingElement())
    {
        Agent a;
        a.id = int(agents.size());
        a.start_id_name = agent->Attribute(CNS_TAG_START_ID);
        a.goal_id_name = agent->Attribute(CNS_TAG_GOAL_ID);
        a.agent_name = agent->Attribute("agent_id");
        std::cout << "--------- Agent id:" << a.id << std::endl;
        std::cout << "start_id_name:" << a.start_id_name << " goal_id_name:" << a.goal_id_name << std::endl;
        // Find index
        int nodes_ize = map.get_size();
        bool get_start_id, get_goal_id;
        for(int i = 0; i < nodes_ize; i++) 

        {
            gNode node = map.get_gNode(i);
            if (a.start_id_name == node.id_name) 
            {
                a.start_id = node.id;
                a.start_i = node.i;
                a.start_j = node.j;
                get_start_id = true;
            }
            if (a.goal_id_name == node.id_name) 
            {
                a.goal_id = node.id;
                a.goal_i = node.i;
                a.goal_j = node.j;
                get_goal_id = true;
            }
        }
        if(!get_start_id || !get_goal_id) std::cout << "Can't find start or goal data for Agent " << a.id << " Please check........"<< std::endl;
        std::cout << "start_id:" << a.start_id << " goal_id:" << a.goal_id << " start_i:" << a.start_i << " start_j:" << a.start_j << std::endl;
        
        agents.push_back(a);
        if(int(agents.size()) == k)
            break;
    }

    std::cout << "Get tasks number:" << agents.size() << std::endl;

    return true;
}


void Task::make_ids(int width)
{
    for(size_t i = 0; i < agents.size(); i++)
    {
        agents[i].start_id = int(agents[i].start_i)*width + int(agents[i].start_j);
        agents[i].goal_id = int(agents[i].goal_i)*width + int(agents[i].goal_j);
        //std::cout<<agents[i].start_i<<" "<<agents[i].start_j<<"  "<<agents[i].goal_i<<" "<<agents[i].goal_j<<"\n";
    }
}

void Task::make_ij(const Map& map)
{
    std::cout << "Fill the coordinates for tasks" << std::endl;
    for(unsigned int i = 0; i < agents.size(); i++)
    {
        gNode start = map.get_gNode(agents[i].start_id), goal = map.get_gNode(agents[i].goal_id);
        std::cout << "goal.i: " << goal.i << " goal.j:" << goal.j << std::endl;
        agents[i].start_i = start.i;
        agents[i].start_j = start.j;
        agents[i].goal_i = goal.i;
        agents[i].goal_j = goal.j;
    }
    std::cout << "Fill the coordinates for tasks finish" << std::endl;
}

Agent Task::get_agent(int id) const
{
    if(id >= 0 && id < int(agents.size()))
        return agents[id];
    else
        return Agent();
}
