class Instance {
public:

    int num_of_cols;
    int num_of_rows;
	int map_size;

	vector<int> start_locations;
	vector<int> goal_locations;

    virtual void printAgents() const = 0;

};

class GripMapInstance: public Instance 
{
    void printAgents() const
    {
        for (int i = 0; i < num_of_agents; i++)
        {
            cout << "Agent" << i << " : S=(" << getRowCoordinate(start_locations[i]) << "," << getColCoordinate(start_locations[i])
                << ") ; G=(" << getRowCoordinate(goal_locations[i]) << "," << getColCoordinate(goal_locations[i]) << ")" << endl;
        }
    }
};


Instance* createInstance(const string& data_format, const string& map_file, const string& agent_file, 
    int agent_num, const string& agent_idx, int rows, int cols, int obs, int warehouse_width) {

    if ((data_format.compare("gripmap")) == 0) {

		return new GripMapInstance(map_file, agent_file, agent_num, agent_idx, rows, cols, obs, warehouse_width);

    } else if ((data_format.compare("roadmap")) == 0) {
		return new GeneralRoadmapInstance(map_file, agent_file, agent_num, agent_idx, rows, cols, obs, warehouse_width);
    }
    return nullptr;  // Default case, could also throw an exception or handle differently
}

int main(int argc, char** argv)
{
    Instance* instance = createInstance(vm["format"].as<string>(), vm["map"].as<string>(), vm["agents"].as<string>(),
			vm["agentNum"].as<int>(), vm["agentIdx"].as<string>(),
			vm["rows"].as<int>(), vm["cols"].as<int>(), vm["obs"].as<int>(), vm["warehouseWidth"].as<int>());
    if (instance) cout << "Initialize instance for format: " << vm["format"].as<string>() << endl;
	else {
        // Handle error or unexpected setting
		cerr << "ERROR in initialize instance for format: " << vm["format"].as<string>() << endl;
		return 0;
    }
}