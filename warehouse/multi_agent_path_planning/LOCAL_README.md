## Test
```
cd /home/holly/ShareCode/warehouse/multi_agent_path_planning/centralized/cbs

# run
python3 cbs.py input.yaml output.yaml

# visualize 
python3 ../visualize.py input.yaml output.yaml

# Post-processing with TPG
cd /home/holly/ShareCode/warehouse/multi_agent_path_planning/centralized/scheduling

python3 minimize.py ../cbs/output.yaml real_schedule.yaml
```