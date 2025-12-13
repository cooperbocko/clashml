from agent import Agent

bot = Agent('configs/mac_monitor_config.json', True)
bot.train(100)