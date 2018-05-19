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
model_name = 'cnn'
env.load_model(model_name = model_name, is_train = True)
env.seed(1)


a_dim = env.actions.shape[0]
a_bound = env.action_bound.high
s_dim = env.observation_space.shape[0]

ddpg = DDPG(a_dim, s_dim, a_bound, model_name)

t1 = time.time()



capital_all = []
reward_all = []
espisode = 1000

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

        s = s_
        ep_reward += r
        
        day += 30

    ddpg.learn()
    print('Espisode ', i, 'Day: ', day, ' Reward: ',ep_reward,' Capital: ', env.capital,'\n')
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