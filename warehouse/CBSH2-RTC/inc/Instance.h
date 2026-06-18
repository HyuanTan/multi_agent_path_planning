// Instance.h
#ifndef INSTANCE_H
#define INSTANCE_H

#include"common.h"

using namespace std;

class Instance {
public:

    int num_of_cols;
    int num_of_rows;
	int map_size;

	vector<int> start_locations;
	vector<int> goal_locations;

    Instance() = default;
	Instance(const string& map_fname, const string& agent_fname, 
		int num_of_agents = 0, const string& agent_indices = "",
		int num_of_rows = 0, int num_of_cols = 0, int num_of_obstacles = 0, int warehouse_width = 0);
    ~Instance() {}

    virtual void printAgents() const = 0;
    virtual inline bool validMove(int curr, int next) const = 0;

	virtual list<int> getNeighbors(int curr) const = 0;
    virtual inline int linearizeCoordinate(int row, int col) const = 0;
	virtual inline int linearizeCoordinate(const pair<int, int>& cell) const = 0;
	virtual inline int getRowCoordinate(int id) const = 0;
	virtual inline int getColCoordinate(int id) const = 0;
    virtual inline int getManhattanDistance(int loc1, int loc2) const = 0;
    virtual inline pair<int, int> getCoordinate(int id) const = 0;

    virtual inline int getManhattanDistance(const pair<int, int>& loc1, const pair<int, int>& loc2) const = 0;
    virtual int getDegree(int loc) const = 0;

    virtual int getDefaultNumberOfAgents() const = 0;

	virtual std::string getIdName(int index) const = 0;
	virtual double getCoordinateX (int index) const = 0;
    virtual double getCoordinateY (int index) const = 0;
	virtual std::string getAgentName(int id) const = 0;

    // Grip Map
	int walkCounterClockwise(int from, int to) const
	{
		assert(validMove(from, to));
		int dir = turnLeft(to - from);
		while (!validMove(from, from + dir))
			dir = turnLeft(dir);
		return from + dir;
	}
	inline int turnLeft(int dir) const
	{
		if (dir ==  1) 
			return -num_of_cols;
		else if (dir == -num_of_cols)
			return - 1;
		else if (dir == -1)
			return num_of_cols;
		else if (dir == num_of_cols)
			return 1;
		else
			return 0;
	 }


private:
	virtual bool loadMap() = 0;
	virtual bool loadAgents() = 0;

};

#endif // INSTANCE_H
