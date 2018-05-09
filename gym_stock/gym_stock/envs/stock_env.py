import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
from keras.models import load_model
import pandas as pd
import numpy as np
import os, json
import math

class StockEnv(gym.Env):
	def __init__(self):
		self.sym = pd.read_csv('PTT.BK.csv')
		self.i = 0
		self.market = self.sym.iloc[[0]]
		self.market.insert(5, "Average",  math.ceil( int(((self.market['Low'] + self.market['High']) / 2)) *4 ) /4 )
		self.balance = 100000
		self.portfolio = pd.DataFrame(None , columns = [
		"Date","Symbol",'Volume',"Average Price" ,"Market Price","Amount (Price)" , "Market Value","Unrealized P/L","%Unrealized P/L"])
		self.capital_n0 = self.balance
		self.state = np.array([self.balance, self.portfolio, self.market])
		self.action_space = spaces.Discrete(3)
		self.observation_space = spaces.Discrete(len(self.state))

	def load_model(self, model):
			self.model = load_model(model + '.h5')

	def reset(self):
		self.i = 0
		self.market = self.sym.iloc[[0]]
		self.resetPortfolio()
		self.market.insert(5, "Average",  math.ceil( int(((self.market['Low'] + self.market['High']) / 2)) *4 ) /4 )
		self.balance = 100000
		self.reward = 0
		self.capital_n0 = self.balance


	def resetPortfolio(self):
		self.portfolio = pd.DataFrame(None , columns = [
			"Date",
			"Symbol",
			'Volume',
			"Average Price",
			"Market Price",
			"Amount (Price)", 
			"Market Value",
			"Unrealized P/L",
			"%Unrealized P/L"
		])

	def isTodayClose(self):
		return self.market.isnull().values.any()

	def buy(self, amount):
		stock_price = self.market['Average'][self.i] * amount
		stock_price_with_commission = stock_price * (1 + 0.001578 * 1.07)

		if self.isBalanceEnough(stock_price_with_commission):
			self.balance -= stock_price_with_commission
			self.equilty = self.balance
			self.appendPortfolio(amount)
			# print("Success")
		else:
			# print("Not Enough Money !!!\n")
			pass

	def sell(self):
		if not self.isPortfolioEmpty():
			sold_stock_price = self.portfolio['Market Value'].sum() * (1 - 0.001578 * 1.07)
			self.balance = self.balance + sold_stock_price
			self.portfolio.drop(self.portfolio.index, inplace=True)
			# self.portfolio.drop(self.portfolio.index[order] , inplace=True)
			# self.portfolio.index = range(len(self.portfolio))
		else:
			print("No Order !!!\n")

	# def sell(self , order):
	# 	if not self.isPortfolioEmpty() :
	# 		self.balance = self.balance + self.portfolio['Market Value'][order]
	# 		self.portfolio.drop(self.portfolio.index[order] , inplace=True)
	# 		self.portfolio.index = range(len(self.portfolio))
	# 	else:
	# 		print("No Order !!!\n")

	def isBalanceEnough(self, amountPrice):
		return self.balance > amountPrice

	def appendPortfolio(self, amount):
		portfolio = self.createPortfolioObject(amount)
		self.portfolio = self.portfolio.append(portfolio, ignore_index=True)
        
	def createPortfolioObject(self, amount):
		averagePrice = marketPrice = self.market['Average'][self.i]
		marketValue = amountValue = averagePrice * amount

		return {
			'Date': self.market['Date'][self.i],
			"Symbol": 'PTT',
			'Volume': amount,
			'Average Price': averagePrice,
			'Market Price': marketPrice,
			'Amount (Price)': amountValue ,
			"Market Value": marketValue,
			"Unrealized P/L": 0,
			"%Unrealized P/L": 0
		}

	def setReward(self):
		capital_n1 = self.balance + self.portfolio['Market Value'].sum()

		if capital_n1 - self.capital_n0 > 0 :
			self.reward +=  1#(((self.capital_n0 * 100) /capital_n1 ) - 100 )  

		elif capital_n1 - self.capital_n0 < 0:
			self.reward -= 1

		self.capital_n0 = capital_n1

	def step(self, action):
		if self.isTodayClose():
			# print("Today Maket Close !!!\n")
			return
		if action == 0:
			self.buy(1000) #buy amout 100 volume
		elif action == 1:
			self.sell()
        
		done = self.balance <= 0

		self.state = np.array([self.portfolio,self.market,self.balance])
		return (self.state, self.reward, done)

	def updatePortfolio(self):
		self.portfolio['Market Price'] = self.market['Average'][self.i]
		self.portfolio['Market Value'] = self.market['Average'][self.i] * self.portfolio['Volume']
		self.portfolio['Unrealized P/L'] =  self.portfolio['Market Value'] - self.portfolio['Amount (Price)']
		self.portfolio['%Unrealized P/L'] = (self.portfolio['Unrealized P/L'] /self.portfolio['Amount (Price)'])*100

	def nextday(self):
		self.i += 1
		self.market = self.sym.iloc[[self.i]]
		if self.isTodayClose():
			# print("Today Maket Close !!!\n ")
			self.nextday()
		else:
			# print("Today Maket Open\n")
			self.market.insert(5, "Average",  math.ceil( int(((self.market['Low'] + self.market['High']) / 2)) *4 ) /4 )
			self.updatePortfolio()
			self.setReward()

	def isPortfolioEmpty(self):
		return self.portfolio.empty

	def render(self):
		print("STOCK MARKET \n")
		print(self.market.to_string())
		print("----------------------------------------------------------------------------------------------------------------------------------------------------")
		print("\nPORTFOLIO\n")
		if self.isPortfolioEmpty():
			print("")
			print("\nCash " , self.balance , "     Volume " , self.portfolio['Volume'].sum() , "     Current Price " , self.market['Average'][self.i] ,
			  	  "     Equity " , self.portfolio['Market Value'].sum() , "     Capital " , self.balance + self.portfolio['Market Value'].sum(),'\n')
		else:
			print(self.portfolio.to_string())
			print("\nCash " , self.balance , "     Volume " , self.portfolio['Volume'].sum() , "     Current Price " , self.market['Average'][self.i] ,
			      "     Equity " , self.portfolio['Market Value'].sum() , "     Capital " , self.balance + self.portfolio['Market Value'].sum(),'\n')
			
	def getObservation(self):
		'''
			Load models -> get 30 days data to predict for 30 days

			sample with one stock
		'''
		compared_moving_average = self.compared_with_moving_average()
		
		# waiting for 36 stocks

		# predicts = self.predict_for_30_days(compared_moving_average)
		# print(predicts)		

	def compared_with_moving_average(self):
		compared_moving_average = []
		for i in range(30):
			moving_average = (self.market[['Open', 'High', 'Low', 'Close']][i:30 + i].sum()/30).values.tolist()
			current = self.market[['Open', 'High', 'Low', 'Close']][30 + i:30 + i + 1].values.tolist()
			open = current[0][0] - moving_average[0]
			high = current[0][1] - moving_average[1]
			low = current[0][2] - moving_average[2]
			close = current[0][3] - moving_average[3]
			compared_moving_average.append([open, high, low, close])

		return compared_moving_average

	def predict_for_30_days(self, compared_moving_average):
		predicts = []
		test_data = np.asarray(compared_moving_average)
		for index in range(30):
			predict = self.model.predict(test_data, verbose = 0)
			predicts.append(predict[0])
			test_data = self.find_new_test_data(test_data, predict[0])

		return predicts

	def find_new_test_data(self, test_data, predict):
		for (index, element) in enumerate(test_data[0]):
			for i in range(len(element)):
				if i == 0:
					continue
				elif i < 29:
					element[i - 1] = element[i]
				else:
					element[i - 1] = element[i]
					element[i] = predict[index]

		return test_data

