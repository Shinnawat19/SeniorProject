import gym
from gym import error, spaces, utils
from gym.utils import seeding
from keras.models import load_model
import pandas as pd
import numpy as np
import os, json

class StockEnv(gym.Env):
	metadata = {'render.modes': ['human']}

	def __init__(self):
		super(StockEnv, self).__init__()
		self.action_space = ['b', 'h', 's']
		self.n_actions = len(self.action_space)
		self.n_features = 2
		self.build_stock_market()
		amount = 100

	def load_model(self, model):
		self.model = load_model(model + '.h5')

	def build_stock_market(self):
		self.sym = pd.read_csv("PTT.BK.csv")
		self.i = 60
		self.market = self.sym.iloc[0: self.i]
		self.balance = 1000000
		self.equity = self.balance
		self.portfolio = pd.DataFrame(None , columns = 
		[
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
		# self.reward = 0
	def step(self, action):
		if self.market.isnull().values.any():
			print("Today Maket Close")
		else:
			if action == 0: #BUY
				averageprice = self.market['Open'][self.i]
				amountprice = self.market['Open'][self.i] * amount
				marketprice = self.market['Open'][self.i]
				marketvalue = self.market['Open'][self.i] * amount
				unrealized = amountprice - marketvalue
				perunrealized = (unrealized / amountprice)*100
				if self.balance < amountprice:
					print("Not Enough Money")
				else:
					self.balance = self.balance - amountprice
					self.equity = self.balance
					self.portfolio = self.portfolio.append(
					{'Date' : self.market['Date'][self.i] , "Symbol" : 'PTT' ,'Volume' : amount, 'Average Price' : averageprice ,'Market Price' : marketprice ,
					'Amount (Price)' : amountprice ,"Market Value" : marketvalue,"Unrealized P/L":unrealized,"%Unrealized P/L":perunrealized} 
					, ignore_index=True)
					self.equity = self.equity + self.portfolio['Unrealized P/L'].sum()
					print("Success")
			elif action == 1: #SELL
				self.balance = self.equity
				self.portfolio = pd.DataFrame(None , columns = [
				"Date","Symbol",'Volume',"Average Price" ,"Market Price","Amount (Price)" , "Market Value","Unrealized P/L","%Unrealized P/L"
				])
				self.equity = self.balance
			else: #HOLD
				print('Hold')
				pass



			if self.equity - self.balance > 0:
				reward = 1
			elif self.equity == self.balance:
				reward = 0
			else:
				reward = -1

        
			if self.balance == 0:
				done = True
			else:
				done = False
			return reward, done
			
	def reset(self):
		self.i = 0
		self.market = self.sym.iloc[[0]]
		self.balance = 100000
		self.equity = self.balance
		self.portfolio = pd.DataFrame(None , columns = 
			[
		    "Date",
		    "Symbol",
		    'Volume',
		    "Average Price",
		    "Market Price","Amount (Price)",
		    "Market Value",
		    "Unrealized P/L",
		    "%Unrealized P/L"
			])
		return (self.balance , self.equity , self.portfolio)

	def render(self, mode='human', close=False):
		print("STOCK MARKET \n")
		print(self.market.to_string())
		print("-----------------------------------------------------------------------------------")
		print("\nPORTFOLIO\n")
		if self.portfolio.empty:
			print("")
			print("\nCash " , self.balance ,"     Capital " , self.equity)
		else:
			print(self.portfolio.to_string())
			print("\nCash " , self.balance , "     Volume " , self.portfolio['Volume'].sum() , "     Capital " , self.equity ,)

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