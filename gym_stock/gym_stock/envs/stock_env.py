import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
import pandas as pd
import numpy as np
import os, json
import math
import requests
import json

class StockEnv(gym.Env):
	def __init__(self):
		self.SET50 = ['ADVANC', 'AOT', 'BANPU', 'BBL', 'BCP', 'BDMS', 'BEM', 'BH', 'BJC', 'BTS', 'CENTEL', 'CPALL', 'CPF', 'CPN', 'DTAC', 'EGCO', 'HMPRO', 'INTUCH', 'IRPC', 'KBANK', 'KCE', 'KKP', 'KTB', 'LH', 'MINT', 'PTT', 'PTTEP', 'ROBINS', 'SCB', 'SCC', 'TCAP', 'TISCO', 'TMB', 'TOP', 'TRUE', 'TU']
		self.skip_days = 60
		self.BUY = 0
		self.SELL = 1
		self.actions = np.zeros(shape=(36,))
		self.action_bound = spaces.Box(low=-1.0, high=1.0, shape=(1,), dtype=np.float32)

	def set_demo(self, is_demo):
		self.set_demo = is_demo

	def load_model(self, model_name, is_train, threshold):
		self.threshold = threshold
		if is_train:
			self.model_name = model_name
		else:
			self.skip_days = 1715
			self.model_name = model_name + 'Test'
		self.predicted_data = np.loadtxt(self.model_name + 'Predictions.txt', dtype=float)

		self.initialize_stock_data()
		self.initialize_variable()
		self.initialize_portfolio()

		self.observation_space = self.get_observation()

	def create_bot(self, bot_name):
		self.bot_name = bot_name
		if self.set_demo:
			conn = requests.post("http://localhost:8000/trading/bot", data = json.dumps({"name": self.bot_name}))

	def initialize_variable(self):
		self.balance = 1000000.
		self.capital_n0 = self.balance
		self.capital = self.balance
		self.reward = 0
		self.i = 0
		self.market = [symbol.iloc[self.i + self.skip_days: self.i + self.skip_days + 1] for symbol in self.symbols]
		self.date = self.market[0].iloc[0]['Date']
		self.done = False

	def initialize_stock_data(self):
		symbols = []
		for stock in self.SET50:
			temp = pd.read_csv('../../../Data set/SET50_OHLC_FIXED/' + stock + '.BK.csv')
			symbols.append(temp)

		self.symbols = symbols

	def initialize_portfolio(self):
		self.portfolio = [ {
			'Date': self.date,
			"Symbol": self.SET50[i],
			'Volume': 0,
			'Average Price': 0,
			'Market Price': self.calculate_mean_open_close(i),
		} for i in range(len(self.SET50))]

	def calculate_mean_open_close(self, index):
		return (self.market[index].iloc[0]['Open'] + self.market[index].iloc[0]['Close'])/2

	def update_date_and_market_price_portfolio(self):
		for (index, portfolio) in enumerate(self.portfolio):
			portfolio['Market Price'] = self.calculate_mean_open_close(index)
			portfolio['Date'] = self.date

	def reset(self):
		self.initialize_variable()
		self.initialize_portfolio()
		return self.get_observation()

	def step(self, actions):
		for (index, action) in enumerate(actions):
			if action > 0:
				max_price = 20000
				volume = (max_price * action) // self.calculate_mean_open_close(index)
				self.buy(index, volume)
			elif action < 0:
				self.sell(index, action)

		self.capital = self.balance + self.find_portfolio_sum()
		if self.set_demo:
			conn = requests.put("http://localhost:8000/trading/capital", 
				data = json.dumps({"name": self.bot_name, "capital": self.capital}))
		self.sendPortfolio()
		self.set_reward()
		self.next_day()

		return self.get_observation(), self.reward, self.done,{}

	def buy(self, index, volume):
		base_price = self.calculate_mean_open_close(index)
		stock_price_with_commission = self.calculate_stock_price(self.BUY, base_price, volume)

		if self.is_balance_enough(stock_price_with_commission):
			self.balance = self.balance - stock_price_with_commission
			old_volume = self.portfolio[index]['Volume']
			if old_volume != 0:
				old_price = self.portfolio[index]['Average Price']
				base_price = self.calculate_new_average_price(old_volume, old_price, base_price, volume)

			if self.set_demo:
				conn = requests.post("http://localhost:8000/trading/trade", 
					data = json.dumps({"name": self.bot_name, "symbol": self.SET50[index], "action": "BUY",
					"volume": volume, "averagePrice": base_price, "date": self.date}))

			self.portfolio[index]['Average Price'] = base_price
			self.portfolio[index]['Volume'] = old_volume + volume

	def sell(self, index, percentage):
		if not self.is_portfolio_empty(index):
			old_volume = self.portfolio[index]['Volume']
			sell_volume = abs(round(old_volume * percentage))
			if sell_volume != 0:
				base_price = self.calculate_mean_open_close(index)

				if self.set_demo:
					conn = requests.post("http://localhost:8000/trading/trade", 
						data = json.dumps({"name": self.bot_name, "symbol": self.SET50[index], "action": "SELL",
						"volume": sell_volume, "averagePrice": base_price, "date": self.date}))

				self.balance = self.balance + self.calculate_stock_price(self.SELL, base_price, sell_volume)
				self.portfolio[index]['Volume'] = old_volume - sell_volume

	def sendPortfolio(self):
		portfolios = [{
			"symbol": portfolio['Symbol'],
			"volume": portfolio['Volume'],
			"averagePrice": portfolio['Average Price'],
			"marketPrice": portfolio['Market Price']
		} for portfolio in self.portfolio]

		if self.set_demo:
			conn = requests.post("http://localhost:8000/trading/portfolio",
				data = json.dumps({"name": self.bot_name, "portfolios": portfolios}))

	def is_portfolio_empty(self, index):
		return self.portfolio[index]['Volume'] == 0

	def calculate_stock_price(self, action, base_price, amount):
		if action == self.BUY:
			commision_rate = 1 + 0.001578 * 1.07
		elif action == self.SELL:
			commision_rate = 1 - 0.001578 * 1.07

		return base_price * amount * commision_rate

	def calculate_new_average_price(self, old_volume, old_price, new_volume, new_price):
		old_amount = old_volume * old_price
		new_amount = new_volume * new_price
		return (old_amount + new_amount) / (old_volume + new_volume)

	def find_portfolio_sum(self):
		portfolio = [ stock['Volume'] * stock['Market Price'] for stock in self.portfolio]
		portfolio = np.asarray(portfolio)
		return np.sum(portfolio)

	def is_balance_enough(self, amountPrice):
		return self.balance > amountPrice

	def set_reward(self):
		capital_n1 = self.balance + self.find_portfolio_sum()

		self.reward = capital_n1 - self.capital_n0

		self.capital_n0 = capital_n1
		
	def next_day(self):
		if  (self.i + 1) * 30 < self.predicted_data.shape[1]  :
			self.i += 1
			self.market = [symbol.iloc[self.i * self.threshold + self.skip_days: self.i * self.threshold + self.skip_days + 1] for symbol in self.symbols]
			self.date = self.market[0].iloc[0]['Date']
			self.update_date_and_market_price_portfolio()
		else:
			self.done = True

	def render(self):
		print("\nPORTFOLIO on ", self.date, "\n")
		for (index, portfolio) in enumerate(self.portfolio):
			if not self.is_portfolio_empty(index):
				print("Symbol: ", self.portfolio[index]['Symbol'], " Volume: ", self.portfolio[index]['Volume'], " Average price: ", self.portfolio[index]['Average Price'], " Market price: ", self.portfolio[index]['Market Price'])
			
		print("\nCash: " , self.balance , " Capital: " , self.capital,'\n')
				
	def get_observation(self):
		observation = np.asarray([ predict[self.i: self.i + 30] for predict in self.predicted_data])
		observation = observation.reshape(observation.shape[0] * observation.shape[1])
		return observation