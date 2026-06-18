## Install
```
git clone https://github.com/Jiaoyang-Li/EECBS.git

sudo apt install libboost-all-dev

# go into the directory of the source code and compile it with CMake:
cmake -DCMAKE_BUILD_TYPE=RELEASE .
make

# run the code:
./eecbs -m random-32-32-20.map -a random-32-32-20-random-1.scen -o test.csv --outputPaths=paths.txt -k 50 -t 60 --suboptimality=1.2 
```