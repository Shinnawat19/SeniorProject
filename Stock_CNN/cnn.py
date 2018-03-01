import numpy as np
import glob
import math
import csv
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Convolution2D, Dense, Dropout, Activation, Flatten, MaxPooling2D
from keras.optimizers import SGD
from scipy import misc
from PIL import Image

def create_model():
    model = Sequential()
    
    model.add(Convolution2D(32, 3, 3, border_mode="valid", input_shape=(100, 100, 3)))
    model.add(Activation('relu'))
    model.add(Convolution2D(32, 3 ,3))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Dropout(0.25))  
      
    model.add(Flatten())  
    model.add(Dense(256))  
    model.add(Activation('relu'))  
    model.add(Dropout(0.5))

    model.add(Dense(2))  
    model.add(Activation('softmax'))  

    return model

def get_mean_value(stock_datas):
    values = []
    count = 30
    while count < len(stock_datas) - 4:
        current_mean = np.mean(stock_datas[count])
        future_mean = np.mean(stock_datas[count + 4])
        values.append(math.log(future_mean/ current_mean))
        count += 1
    
    return values

def get_pixel_from_image():
    pixels = []
    for image_file in glob.glob('*.png'):
        pixels.append(misc.imread(image_file))
    
    return pixels

def plot_stock(stock_datas):
    number = 0
    figure = plt.figure(frameon = False, figsize=(1, 1))
    figure_count = 0

    while figure_count <= len(stock_datas) - 35:
        high_plot = []
        low_plot = []

        for data in stock_datas[figure_count: figure_count + 30]:
            high_plot.append(data[0])
            low_plot.append(data[1])
            
        file_name = 'fig_' + str(figure_count)
        config = plt.Axes(figure, [0., 0., 1., 1.])
        config.set_axis_off()
        figure.add_axes(config)
        config.plot(np.arange(0, 30, 1), high_plot, 'g', low_plot, 'r')
        figure.savefig(file_name, dpi = 100)
        figure.clf()
        image = Image.open(file_name + '.png').convert('RGB')
        image.save(file_name + '.png')
        figure_count += 1
       
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
    # plot_stock(stock_datas)

    x = np.asarray(get_pixel_from_image())
    y = np.asarray(get_mean_value(stock_datas))

    x_train = (x[0:3000].astype('float32') /255)
    y_train = y[0:3000]
    
    x_test = (x[3000:3684].astype('float32') /255)
    y_test = y[3000:3684]

    model = create_model()
    sgd = SGD(lr = 0.01, momentum = 0.9, decay=1e-6, nesterov = True)
    model.compile(loss='sparse_categorical_crossentropy', optimizer=sgd)
    
    epochs = 10
    model.fit(x_train, y_train, validation_data = (x_test, y_test), epochs = epochs, shuffle = True, batch_size = 200, verbose= 1)

    classes = list(model.predict_classes(x_test, verbose = 0))
    print(classes)


if __name__ == '__main__':
    main()