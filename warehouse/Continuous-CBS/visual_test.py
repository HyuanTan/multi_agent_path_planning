#!/usr/bin/env python3
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch, PathPatch
from matplotlib.patheffects import withStroke

fig, (ax1, ax2) = plt.subplots(1, 2)

# 在第一个子图中绘制数据
ax1.plot([0, 1], [0, 1], 'ro')

# 在第二个子图中绘制数据
ax2.plot([0, 1], [1, 0], 'bo')

# 创建一个 ConnectionPatch
con = ConnectionPatch(xyA=(0.2, 0.2), xyB=(0.8, 0.8), coordsA="data", coordsB="data",
                      axesA=ax2, axesB=ax1, arrowstyle="->", color="red")
# 添加阴影效果
con.set_path_effects([withStroke(linewidth=4, foreground="black")])

# 将 ConnectionPatch 添加到第二个子图
ax2.add_artist(con)

plt.show()
