#pragma once

#include"common.h"
#include <cmath> // for sqrt and pow
#include"Instance.h"
#include "tinyxml2.h"

struct Agent
{
    double start_i, start_j, goal_i, goal_j;
    int start_id, goal_id;
    std::string start_id_name, goal_id_name;
    int id;
    std::string agent_name;
    double size;
    Agent(int s_id = -1, int g_id = -1, int _id = -1)
        :start_id(s_id), goal_id(g_id), id(_id) {}
};

struct gNode
{
    double i;
    double j;
    int     id; // 2023-12
    std::string  id_name; // 2023-12

    std::vector<int> neighbors;
	std::list<int> neighborsList; // redundancy, adjust to the Algorithm call 
    gNode(double i_ = -1, double j_ = -1):i(i_), j(j_) {}
    gNode(double i_, double j_, int id_, std::string  id_name_){i = i_; j = j_; id = id_; id_name = id_name_;}
    // gNode(double i_ = -1, double j_ = -1, int id_ = -1, std::string  id_name_ = ""):i(i_), j(j_), id(id_), id_name(id_name_) {}
    ~gNode(){neighbors.clear(); neighborsList.clear();}
};

struct Node
{
    int     id;
    std::string  id_name; // 2023-12
    double  f, g, i, j;
    Node*   parent;
    std::pair<double, double> interval;
    int interval_id;
    Node(int _id = -1, double _f = -1, double _g = -1, double _i = -1, double _j = -1, Node* _parent = nullptr, double begin = -1, double end = -1)
        :id(_id), f(_f), g(_g), i(_i), j(_j), parent(_parent), interval(std::make_pair(begin, end)) {interval_id = 0;}

    bool operator <(const Node& other) const //required for heuristic calculation
    {
        return this->g < other.g;
    }
};

// Currently only works for undirected unweighted 4-neighbor grids
class GeneralRoadmapInstance: public Instance 
{
public:

	GeneralRoadmapInstance() = default;
	GeneralRoadmapInstance(const string& map_fname, const string& agent_fname, 
		const string& agent_indices = "",
		int num_of_rows = 0, int num_of_cols = 0);
	
	/////////////////////////////////////////////////////////////////////////
	/// not used in roadmap
    //////////////////////////////////////////////////////////////////////
	inline bool validMove(int curr, int next) const override 
	{
		if (next < 0 || next >= map_size)
			return false;
		if (my_map[next])
			return false;
		return getManhattanDistance(curr, next) < 2;
	}

    inline int linearizeCoordinate(int row, int col) const override { return ( this->num_of_cols * row + col); }
	inline int linearizeCoordinate(const pair<int, int>& cell) const override { return linearizeCoordinate(cell.first, cell.second); }
	inline int getRowCoordinate(int id) const override { return id / this->num_of_cols; }
	inline int getColCoordinate(int id) const override { return id % this->num_of_cols; }
	inline pair<int, int> getCoordinate(int id) const override { return make_pair(id / this->num_of_cols, id % this->num_of_cols); }
	inline int getManhattanDistance(const pair<int, int>& loc1, const pair<int, int>& loc2) const override
	{
		return abs(loc1.first - loc2.first) + abs(loc1.second - loc2.second);
	}
	//////////////////////////////////////////////////////////////////////
	//////////////////////////////////////////////////////////////////////
	inline double euclideanDistance2D(double x1, double y1, double x2, double y2) const 
	{
		return sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2));
	}

	// Note: In roadmap, we calculate the Euclidean distance and return the distance as an int(Not sure whether work or not )
	// TODO: Step or Summary of Euclidean distance of each step
	inline int getManhattanDistance(int loc1, int loc2) const override
	{
		double distance = euclideanDistance2D(nodes[loc1].i, nodes[loc1].j, nodes[loc2].i, nodes[loc2].j);
		return static_cast<int>(std::round(distance));
	}

	// return the number of neighbors
	int getDegree(int loc) const override {return (nodes[loc].neighbors).size();}
 
	int getDefaultNumberOfAgents() const override { return num_of_agents; }

	void printAgents() const override;

	list<int> getNeighbors(int curr) const override {return nodes[curr].neighborsList;}

	inline gNode getGNode(int id) const {if(id < int(nodes.size())) return nodes[id]; return gNode();}
	inline int getIndexByName(std::string id_name) const;

	std::string getIdName(int index) const override {return nodes[index].id_name;}
	double getCoordinateX (int index) const override {return nodes[index].i;}
    double getCoordinateY (int index) const override {return nodes[index].j;}
	std::string getAgentName(int id) const override {return agents[id].agent_name;}

private:
	// int moves_offset[MOVE_COUNT];
	vector<bool> my_map; // TODO: use to record the block station or edg
	string map_fname;
	string agent_fname;
	string agent_indices;
	int num_of_agents = 0;
	unsigned int nodes_ize;

	// Road map
	std::vector<gNode> nodes;
	std::vector<std::vector<Node>> valid_moves;
	std::vector<Agent> agents;
	
	bool loadMap() override;
	bool loadAgents() override;

	// Class  SingleAgentSolver can access private members of Node
	friend class SingleAgentSolver;
};

