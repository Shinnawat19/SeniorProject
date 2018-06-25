import tensorflow as tf
import numpy as np
import gym
import gym_stock    
import time
import matplotlib.pyplot as plt
from ddpg import DDPG
import random
import time

env = gym.make('stock-v0')

#######################
model = 'cnn'
threshold = 7
is_train = False
is_demo = False # require web demo, run web demo in demo folder before run this bot
epoch = 1000 if is_train else 1
capital_all = []
reward_all = []
#######################

env.load_model(model_name = model + str(threshold), 
                is_train = is_train, 
                threshold= threshold)

#######################
a_dim = env.actions.shape[0]
a_bound = env.action_bound.high
s_dim = env.observation_space.shape[0]
#######################

env.set_demo(is_demo)
if is_demo:
    env.create_bot('botname')
    time.sleep(1)

ddpg = DDPG(a_dim, s_dim, a_bound)

if not is_train:
    ddpg.load_model('./ddpg_model/' + model + '_' + str(threshold) + '/')

for i in range(epoch):
    s = env.reset()
    ep_reward = 0
    day = 0
    done = False
    while not done:

        a = ddpg.choose_action(s)
        s_, r, done, info = env.step(a)
        if done:
            break

        ddpg.store_transition(s, a, r/10, s_)
        s = s_
        ep_reward += r
        day += threshold
        env.render()
        if is_demo:
            time.sleep(4)
    
    print('Epochs:', i)
    print('Day: ', day, ' Reward: ',ep_reward + r,' Capital: ', env.capital,'\n')
    ddpg.learn()
    capital_all.append(env.capital)
    reward_all.append(reward_all)

if is_train:
    ddpg.save_model('/' + model + '_' + str(threshold) + '/' + model)
