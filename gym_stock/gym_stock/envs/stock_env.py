import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
import pandas as pd
import numpy as np
import os, json
import math

class StockEnv(gym.Env):
	'''
		portfolio for 36 stocks (initialize with 0 volumes)

		market store only today

		portfolio
			- date
			- symbol
			- volume
			- market price
			- average price
	'''
	def __init__(self):
		self.SET50 = ['ADVANC', 'AOT', 'BANPU', 'BBL', 'BCP', 'BDMS', 'BEM', 'BH', 'BJC', 'BTS', 'CENTEL', 'CPALL', 'CPF', 'CPN', 'DTAC', 'EGCO', 'HMPRO', 'INTUCH', 'IRPC', 'KBANK', 'KCE', 'KKP', 'KTB', 'LH', 'MINT', 'PTT', 'PTTEP', 'ROBINS', 'SCB', 'SCC', 'TCAP', 'TISCO', 'TMB', 'TOP', 'TRUE', 'TU']
		self.skip_days = 60

		self.initialize_stock_data()
		self.initialize_variable()

		self.model_name = 'cnn'
		self.predicted_data = np.loadtxt(self.model_name + 'Predictions.txt', dtype=float)
		print('Prediction with ' + self.model_name)

		self.actions = np.zeros(shape=(36,))
		self.action_bound = spaces.Box(low=-1.0, high=1.0, shape=(1,), dtype=np.float32)
		self.observation_space = self.getObservation()

	def initialize_variable(self):
		self.balance = 1000000.
		self.lost = self.balance / 10
		self.capital_n0 = self.balance
		self.reward = 0
		self.i = 0
		self.market = [symbol.iloc[self.i + self.skip_days: self.i + self.skip_days + 1] for symbol in self.symbols]
		self.resetPortfolio()
		self.capital = self.balance + self.portfolio['Market Value'].sum()
		self.done = False

	def initialize_stock_data(self):
		symbols = []
		for stock in self.SET50:
			temp = pd.read_csv('../../../Data set/SET50_OHLC/' + stock + '.BK.csv')
			symbols.append(temp)

		self.symbols = symbols

	def initialize_portfolio(self):
		self.portfolio = [ self.createPortfolioObject(symbol) for symbol in self.SET50]

	def reset(self):
		self.initialize_variable()
		# self.initialize_portfolio()
		return self.getObservation()

	def resetPortfolio(self):
		self.portfolio = pd.DataFrame(None , columns = ["Date", "Symbol", "Volume", "Average Price", "Market Price", "Amount (Price)", "Market Value", "Unrealized P/L", "%Unrealized P/L"])

	def isTodayClose(self):
		return self.market.isnull().values.any()

	def step(self, actions):
		if self.isTodayClose():
			# print("Today Maket Close !!!\n")
			return self.getObservation(), self.reward, self.done,{}
		else:
			if action == 0:
				self.buy(1000) #buy amout 100 volume
			elif action == 1:
				self.sell()

			self.capital = self.balance + self.portfolio['Market Value'].sum()

			if self.capital < self.lost:
				self.done = True
			else:
				self.done = False

			self.setReward()

			return self.getObservation(), self.reward, self.done,{}

	def buy(self, amount):
		stock_price = self.market['Average'][0] * amount
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
			# print("No Order !!!\n")
			pass

	def isBalanceEnough(self, amountPrice):
		return self.balance > amountPrice

	def appendPortfolio(self, amount):
		portfolio = self.createPortfolioObject(amount)
		self.portfolio = self.portfolio.append(portfolio, ignore_index=True)
        
	def createPortfolioObject(self, symbol):
		return {
			'Date': self.market[0]['Date'],
			"Symbol": symbol,
			'Volume': 0,
			'Average Price': 0,
			'Market Price': 0,
		}

	def setReward(self):
		self.reward = 0
		capital_n1 = self.balance + self.portfolio['Market Value'].sum()

		if capital_n1 - self.capital_n0 > 0 :
			self.reward +=  1#(((self.capital_n0 * 100) /capital_n1 ) - 100 )  

		elif capital_n1 - self.capital_n0 < 0:
			self.reward -= 1

		self.capital_n0 = capital_n1

		# print('REWARD     ',self.reward)


	def updatePortfolio(self):
		self.portfolio['Market Price'] = self.market['Average'][0]
		self.portfolio['Market Value'] = self.market['Average'][0] * self.portfolio['Volume']
		self.portfolio['Unrealized P/L'] =  self.portfolio['Market Value'] - self.portfolio['Amount (Price)']
		self.portfolio['%Unrealized P/L'] = (self.portfolio['Unrealized P/L'] /self.portfolio['Amount (Price)'])*100

	def nextday(self):
		if self.i + 60 < self.sym.shape[0]-1:
			self.i += 30
			self.market = self.sym.iloc[self.i + self.skip_days: self.i + self.skip_days + 1]

			if self.isTodayClose():
				# print("Today Maket Close !!!\n ")
				self.nextday()
			else:
				# print("Today Maket Open\n")
				# self.market.insert(5, "Average",  round((self.market['Low'] + self.market['High']) / 2))
				self.updatePortfolio()
				# self.setReward()
		else:
			self.done = True
		return self.done

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
		observation = self.predicted_data[self.i: self.i + 30]
		observation = observation.reshape(observation.shape[0] * observation.shape[1])	
		# # # including portfolio
		# balance = np.array([self.balance])
		# observation = np.append(observation, balance)
		print(self.market[0]['Date'])
		return observation