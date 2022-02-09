import os
import random
import discord
from discord.ext import commands
from replit import db
from keepAlive import keepAlive
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

@bot.event
async def on_member_remove(member):
  if str(member.id) in db[str(member.guild.id)]['users']:
    del db[str(member.guild.id)]['users'][str(member.id)]


@bot.command(
  aliases=['ca'],
  help='Creates an account in this server so you can use SocialStatus Bot'
)
async def createAccount(ctx):
  if str(ctx.message.author.id) in db[str(ctx.guild.id)]['users']:
    await ctx.send('You already have an account in this server!')

  else:
    db[str(ctx.guild.id)]['users'][str(ctx.message.author.id)] = {'socialCredit': 0}
    await ctx.send('Account created!')


@bot.command(
  name='credit',
  help='Shows how much social credit you have.',
  shorthelp='Shows how much social credit you have'
)
async def socialCredit(ctx):
  if str(ctx.message.author.id) in db[str(ctx.guild.id)]['users']:
    sc = db[str(ctx.guild.id)]['users'][str(ctx.message.author.id)]['socialCredit']
    await ctx.send(f'You have {sc} social credit')
  else:
    await ctx.send('You need to make an account for this server first! Use "sc ca" to do that.')


@bot.command(
  name='edit',
  help='Directly edit the social credit of another user with an account. This requires you to have the "SC Editor" role. You must mention the target user, and the operations are "plus", "minus", and "set". The operation must be spelled out completely.'
)
async def editSC(ctx, user: discord.User, operation, modifier):
  if discord.utils.get(ctx.guild.roles, name='SC Editor') is None:
    await ctx.send('The server does not have the role required! Ask an admin to add the "SC Editor" role.')
    return

  role = discord.utils.get(ctx.message.author.roles, name="SC Editor")
  if role is None:
    await ctx.send('You don\'t have the role to do this!')
    return

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
    return

  if operation == 'minus':
    await minus()
    return

  if operation == 'set':
    await setSC()
    return

  await ctx.send('The operation must be "plus", "minus", or "set"!')

@editSC.error
async def editSCError(ctx, error):
  if isinstance(error, commands.BadArgument):
    await ctx.send('Could not find that user')


@bot.command(
  help='Grind for social credit. There is a chance to lose social credit from grinding, though...'
)
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
    scChange = random.randint(500, 50000000)
    db[str(ctx.guild.id)]['users'][str(user.id)]['socialCredit'] -= scChange
    
    embed = discord.Embed(title=f'{user.name}\'s losses')
    embed.add_field(name='Losses', value=f'You lost {scChange} social credit for {actions.randLose()}')

    await ctx.send(embed=embed)
  
  if random.randint(1, 10) > 1:
    await gainSC()
  else:
    await loseSC()

@grind.error
async def grindError(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.send(f'This command is on cooldown! Try again after {round(error.retry_after, 1)} seconds!')


@bot.command(
  name='lb',
  help='Shows the top X people in the server, where x is whatever number you input.'
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

@leaderboard.error
async def lbError(ctx, error):
  if isinstance(error, commands.BadArgument):
    await ctx.send('X must be an integer!')


@bot.command()
async def support(ctx):
  await ctx.send(f'Here is the link to the support server\nhttps://discord.gg/ZspCYGpdwH')

keepAlive()
bot.run(os.getenv('TOKEN'))