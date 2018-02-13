from gym.envs.registration import register

register(
    id='stock-v0',
    entry_point='gym_stock.envs:StockEnv',
)