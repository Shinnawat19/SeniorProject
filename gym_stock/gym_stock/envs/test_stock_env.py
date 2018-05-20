import tensorflow as tf
import numpy as np
import gym
import gym_stock    
import time
import matplotlib.pyplot as plt
from ddpg import DDPG
import random

env = gym.make('stock-v0')
env = env.unwrapped
model_name = 'cnnlstm'
env.load_model(model_name = model_name, is_train = True, threshold = 30)
env.seed(1)



a_dim = env.actions.shape[0]
a_bound = env.action_bound.high
s_dim = env.observation_space.shape[0]

ddpg = DDPG(a_dim, s_dim, a_bound)
# ddpg.load_model('./ddpg_model/cnn_30')


epoch = 1000
capital_all = []
reward_all = []

for i in range(epoch):
    s = env.reset()
    ep_reward = 0
    day = 0
    done = False
    while not done:

        a = ddpg.choose_action(s)
        s_, r, done, info = env.step(a)
        # env.render()
        if done:
        	break

        ddpg.store_transition(s, a, r/10, s_)

        s = s_
        ep_reward += r
        
        day += 30

    ddpg.learn()
    print('Espisode ', i, 'Day: ', day, ' Reward: ',ep_reward,' Capital: ', env.capital,'\n')
    capital_all.append(env.capital)
    reward_all.append(reward_all)
ddpg.save_model('/cnnlstm_30/' + model_name)


