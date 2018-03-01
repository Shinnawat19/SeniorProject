import numpy as np
import glob
import math
import csv
import matplotlib.pyplot as plt
from keras import models, layers, optimizers, utils
from scipy import misc
from PIL import Image

def plot_stock(stock_datas):
    number = 0
    figure = plt.figure(frameon = False, figsize=(1, 1))
    figure_count = 0

    while figure_count <= len(stock_datas) - 30:
        high_plot = []
        low_plot = []

        for data in stock_datas[figure_count: figure_count + 30]:
            high_plot.append(data[0])
            low_plot.append(data[1])
        config = plt.Axes(figure, [0., 0., 1., 1.])
        config.set_axis_off()
        figure.add_axes(config)
        config.plot(np.arange(0, 30, 1), high_plot, 'g', low_plot, 'r')
        figure.savefig('fig_' + str(figure_count), dpi = 100)
        figure.clf()
        break
       

def load_stock_data(symbol):
    stock_data = []
    with open(symbol + '.BK.csv', 'r') as csv_file:
        file_data = csv.reader(csv_file, delimiter=',')
        file_data = list(file_data)[1:]
        for row in file_data:
            if row[2] is '':
                continue
            else:
                temp = [row[2], row[3]]
            temp = [float(x) for x in temp]
            stock_data.append(temp)

    return stock_data

def main():
    stock_datas = load_stock_data(symbol = "PTT")
    plot_stock(stock_datas)

if __name__ == '__main__':
    main()