import gym
from gym import error, spaces, utils
from gym.utils import seeding
import pandas as pd
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

	def build_stock_market(self):
		self.sym = pd.read_csv("PTT.BK.csv")
		self.i = 0
		self.market = self.sym.iloc[[0]]
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
