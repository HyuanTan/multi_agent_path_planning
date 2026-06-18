## Install dependence
```
sudo apt-get install libffi-dev
sudo apt-get install python2-dev
sudo apt-get install python-tk

pip2 install polytope
# https://support.gurobi.com/hc/en-us/articles/12872879801105
# retrieve and set up a Gurobi license
# Download grbgetkey tools: https://support.gurobi.com/hc/en-us/articles/360059842732
# https://support.gurobi.com/hc/en-us/articles/360040113232-How-do-I-resolve-the-error-grbgetkey-command-not-found-or-grbgetkey-is-not-recognized-
pip2 install gurobipy
pip2 install queuelib
pip2 install shapely
pip2 install pytest-timeit

pip2 install -U setuptools


# https://github.com/cvxopt/cvxopt/issues/121 --- Not work

pip2 install cvxopt==1.1.9

# version problem
pip2 install pycddlib
pip2 install pypoman
pip2 install matplotlib
```

gurobipy, 需要使用商用的Gurobi 数学规划器-可以求解常规的混合整数线性规划，也支持非凸二次规划和广义非线性优化