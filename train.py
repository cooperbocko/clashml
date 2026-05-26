from ppoagent import PPOAgent

bot = PPOAgent('./configs/mac.json')

bot.train(2)