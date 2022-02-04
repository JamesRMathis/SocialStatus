import os
import random
import discord
from discord.ext import commands
from replit import db
import actions

bot = commands.Bot(command_prefix='sc ')

# for k in db.keys():
#   del db[k]

@bot.event
async def on_ready():
  print('Bot is ready')
  await bot.change_presence(activity=discord.Game(name="use sc help"))

@bot.event
async def on_guild_join(guild):
  db[str(guild.id)] = {
    'users': {}
  }

@bot.event
async def on_guild_remove(guild):
  del db[str(guild.id)]


@bot.command(
  aliases=['ca']
)
async def createAccount(ctx):
  if str(ctx.message.author.id) in db[str(ctx.guild.id)]['users']:
    await ctx.send('You already have an account in this server!')

  else:
    db[str(ctx.guild.id)]['users'][str(ctx.message.author.id)] = {'socialCredit': 0}
    await ctx.send('Account created!')


@bot.command(
  name='credit'
)
async def socialCredit(ctx):
  if str(ctx.message.author.id) in db[str(ctx.guild.id)]['users']:
    sc = db[str(ctx.guild.id)]['users'][str(ctx.message.author.id)]['socialCredit']
    await ctx.send(f'You have {sc} social credit')
  else:
    await ctx.send('You need to make an account for this server first! Use "sc ca" to do that.')


@bot.command(
  name='edit',
  help=''
)
@commands.hasRole('SC Editor')
async def editSC(ctx, user: discord.User, operation, modifier):
  if str(user.id) not in db[str(ctx.guild.id)]['users']:
    await ctx.send('This user has not made an account in this server!')
    return

  try:
    modifier = int(modifier)
  except:
    await ctx.send('The modifier must be an integer!')

  async def plus():
    db[str(ctx.guild.id)]['users'][str(user.id)]['socialCredit'] += modifier
    await ctx.send(f'{user.mention} You have gained {modifier} social credit!')
  
  async def minus():
    db[str(ctx.guild.id)]['users'][str(user.id)]['socialCredit'] -= modifier
    await ctx.send(f'{user.mention} You have lost {modifier} social credit!')
  
  async def setSC():
    db[str(ctx.guild.id)]['users'][str(user.id)]['socialCredit'] = modifier
    await ctx.send(f'{user.mention} Your social credit has been set to {modifier}!')

  operation = operation.lower()

  if operation == 'plus':
    await plus()
  elif operation == 'minus':
    await minus()
  elif operation == 'set':
    await setSC()
  else:
    await ctx.send('The operation must be "plus", "minus", or "set"!')

  await ctx.message.delete()

@editSC.error
async def editSCError(ctx, error):
  if isinstance(error, commands.BadArgument):
    await ctx.send('Could not find that user')


@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def grind(ctx):
  if str(ctx.message.author.id) not in db[str(ctx.guild.id)]['users']:
    await ctx.send('You need to make an account before you can grind! Use "sc ca"')
    return

  user = ctx.message.author

  async def gainSC():
    scChange = random.randint(10, 30)
    db[str(ctx.guild.id)]['users'][str(user.id)]['socialCredit'] += scChange
    
    embed = discord.Embed(title=f'{user.name}\'s gains')
    embed.add_field(name='Gains', value=f'You earned {scChange} social credit for {actions.randGain()}')

    await ctx.send(embed=embed)

  async def loseSC():
    scChange = random.randint(30, 100)
    db[str(ctx.guild.id)]['users'][str(user.id)]['socialCredit'] -= scChange
    
    embed = discord.Embed(title=f'{user.name}\'s losses')
    embed.add_field(name='Losses', value=f'You lost {scChange} social credit for {actions.randLose()}')

    await ctx.send(embed=embed)
  
  if random.randint(1, 10) > 4:
    await gainSC()
  else:
    await loseSC()

@grind.error
async def grindError(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.send(f'This command is on cooldown! Try again after {round(error.retry_after, 1)} seconds!')


@bot.command(
  name='lb'
)
async def leaderboard(ctx, topX=10):
  lb = {}
  scores = []

  for user in db[str(ctx.guild.id)]['users']:
    score = db[str(ctx.guild.id)]['users'][user]['socialCredit']
    lb[score] = user
    scores.append(score)

  scores = sorted(scores, reverse=True)

  embed = discord.Embed(
    title=f'Top {topX} users in the server',
    color=0xe74c3c
  )

  i = 1
  for score in scores:
    id = lb[score]
    user = await bot.fetch_user(id)

    embed.add_field(
      name=f'{i}. {user}',
      value=f'Social Credit: {score}',
      inline=False
    )

    if i == topX:
      break
    else:
      i += 1

  await ctx.send(embed=embed)

bot.run(os.getenv('TOKEN'))