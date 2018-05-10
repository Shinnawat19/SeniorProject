import gym
import gym_stock
env = gym.make('stock-v0')


Episodes = 1
count = 0
done = False

action = env.action_space.sample()
for _ in range(Episodes):
	observation = env.reset()
	done = False
	count = 0
	while not done:
		action = env.action_space.sample()# random
		observation, reward, done = env.step(action)
		env.render()
		env.nextday()
		if done:
			print(reward)
			print(count)
