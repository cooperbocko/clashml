from agent import Agent

bot = Agent('configs/mac.json', 'secret.env', True)

bot.train(100)