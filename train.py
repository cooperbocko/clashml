from agent import Agent

bot = Agent('configs/pc.json', 'secret.env', True)

bot.train(100)