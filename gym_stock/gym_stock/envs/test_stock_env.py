import tensorflow as tf
import numpy as np
import gym
import gym_stock    
import time
import matplotlib.pyplot as plt
from ddpg import DDPG
import random
#####################  hyper parameters  ####################

MAX_EPISODES = 200
MAX_EP_STEPS = 200
LR_A = 0.001    # learning rate for actor
LR_C = 0.002    # learning rate for critic
GAMMA = 0.9     # reward discount
TAU = 0.01      # soft replacement
MEMORY_CAPACITY = 10000
BATCH_SIZE = 32

###############################  training  ####################################

env = gym.make('stock-v0')
env = env.unwrapped
env.seed(1)

a_dim = env.actions.shape[0]
a_bound = env.action_bound.high
s_dim = env.observation_space.shape[0]

ddpg = DDPG(a_dim, s_dim, a_bound)

# add randomness to action selection for exploration
var = 3  # control exploration
t1 = time.time()



capital_all = []
reward_all = []
espisode = 1

for i in range(espisode):
    s = env.reset()
    ep_reward = 0
    day = 0
    done = False
    while not done:

        a = ddpg.choose_action(s)    # add randomness to action selection for exploration
        s_, r, done, info = env.step(a)
        # env.render()
        if done:
          break

        ddpg.store_transition(s, a, r/10, s_)

        if ddpg.pointer > MEMORY_CAPACITY:
            var *= .9995    # decay the action randomness
            ddpg.learn()
        s = s_
        ep_reward += r
        # print('Espisode ', i, 'Day: ', day, ' Reward: ',ep_reward,' Capital: ', env.capital,'\n')
        
        day += 30
    capital_all.append(env.capital)
    reward_all.append(reward_all)


print('Running time: ', time.time() - t1)


###############################  plot result  ####################################
# fig, ax = plt.subplots()
# index = np.arange(100)
# bar_width = 0.35
# opacity = 0.8

# rects1 = plt.bar(index, capital_all, bar_width, alpha=opacity,color='b', label='Capital')

# rects2 = plt.bar(index + bar_width, reward_all, bar_width, alpha=opacity, color='g',label='Reward')

# plt.xlabel('Espisode')
# plt.ylabel('Scores')
# plt.title('Capital and Reward')
# plt.xticks(index + bar_width, ('Espisode',index))
# plt.legend()
# plt.tight_layout()
# plt.show()