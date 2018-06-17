# seniorProject


## Prerequisite
#### Software
``` bash
  cuda 9.0
  cuDNN
```
#### Python3 based on [Anaconda3](https://www.anaconda.com/download/)
#### Python package
###### pip install package==version [pip3 for linux]
``` bash
  tensorflow 1.5.0
  tensorflow-gpu 1.8.0
  numpy 1.14.3
  pandas 0.20.3
  pandas-datareader 0.6.0
  Keras 2.1.6
  gym 0.10.5
  jupyter
```

## install our gym environment
```bash
  cd gym_stock
  pip install -e .
```

## Data set
1.  Raw Data: Generate data from YahooFinance
2.  FIXED: Raw Data with interpolation (1 values: Avg of Open and Close)
3.  FIXED_OHLC: Raw Data with interpolation (4 values: open, high, low and close) [**ERROR DATA USING FIXED_OHLC_FIXED**]

## Convolution neural networks
1. Compare CNNs 9 types (1-3 Conv layers and 1-3 Fully-connected layers)
2. First CNN use 64 filters with 7\*1, other 32 filters with 3\*1
3. FC use 1024, 256, 36 nodes

## Long short-term memory
1. Compare LSTM 3 types (1-3 LSTM layers)
2. Every lstm layers use 512 neural

## Convolution neural networks + Long short-term memory
1. Use 1 Conv layer with 3 Lstm layers
2. Remove FC after Conv layer

## Type of Data
1. Compared with yesterday
2. Compared with 30 days moving average: 1 value (avg of open and close)
3. Compared with 30 days moving average: 4 values (open, high, low and close) with 1 output (avg of open and close)
4. Compared with 30 days moving average: 4 values with 4 outputs
