import matplotlib.pyplot as plt
from random_walk import RandomWalk

while True:  #当程序处于活动状态时，不断模拟随机漫步
    #创建一个RandomWalk实例，并将其包含的点都绘制出来
    rw = RandomWalk(50000)
    rw.fill_walk()

    plt.figure(figsize=(10,5))  #设置绘图窗口的尺寸

    point_numbers = list(range(rw.num_points))
    plt.scatter(rw.x_values,rw.y_values,c=point_numbers,cmap=plt.cm.Blues,s=1)

    #突出起点和终点
    plt.scatter (0,0,c='green',s=100)  #起点
    plt.scatter(rw.x_values[-1],rw.y_values[-1],c='red',s=100)  #终点

    #隐藏坐标轴
    plt.axes().get_xaxis().set_visible(False)
    plt.axes().get_yaxis().set_visible(False)

    plt.show()

    keep_running = input('Make another walk?(y/n):')
    if keep_running =='n':
        break