import asyncio

from discord.ext.commands.core import has_permissions
import discordgame
import datetime
import dotenv
import discord
from discord.ext import commands
import json
import os

dotenv.load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

games = {}
gameHistory = []
elo = {}
challenges = {}
moveTimers = {}

bot = commands.Bot(
    command_prefix=".",
    intents=discord.Intents.all()
)


def getGameEmbed(game: discordgame.Game):
    embed = discord.Embed(title=f"Chess: {game.player1.display_name} vs {game.player2.display_name}",
                          description=f"```{game.getBoardString()}```", color=game.getHexColor())
    embed.add_field(name=f"{game.player1.display_name} remaining move time:",
                    value=f"{game.moveTimes[game.player1.id] // 60} minutes {game.moveTimes[game.player1.id] % 60} seconds")
    embed.add_field(name=f"{game.player2.display_name} remaining move time:",
                    value=f"{game.moveTimes[game.player2.id] // 60} minutes {game.moveTimes[game.player2.id] % 60} seconds")
    if game.getActivePlayer() == game.player1:
        color = "White"
    else:
        color = "Black"
    embed.set_footer(text=f"Turn: {game.getTurnNum()}, Last move: {game.getLastMove()}, Current Turn: {game.getActivePlayer().display_name} ({color})")
    return embed


def endGame(game: discordgame.Game, gameResult):
    global games, gameHistory, elo, gameHistory
    games.pop(game.player1.id)
    games.pop(game.player2.id)
    gameHistory.append(gameResult)
    with open("elo.json", "w") as elojson:
        json.dump(elo, elojson)
    with open("match_history.json", "w") as historyjson:
        json.dump(gameHistory, historyjson)
    del moveTimers[game.player1.id]
    del moveTimers[game.player2.id]
    del game


async def actualMove(author, contextOrChannel, moveString, source):
    global games, elo, moveTimers
    if author.id not in games.keys():
        if source == "command":
            await contextOrChannel.send("You are currently not in a game.")
        elif source == "onmessage":
            await contextOrChannel.send("You have entered an invalid command.")
        return
    game: discordgame.Game = games[author.id]
    if game.getActivePlayer() != author:
        await contextOrChannel.send("It is not your turn to move yet.")
        return
    if author.id == game.player1.id:
        otherPlayer = game.player2
    else:
        otherPlayer = game.player1
    if moveString == "resign":
        await contextOrChannel.send(f"{author.display_name} resigned the chess game.")
        elo[author.id] -= 5
        elo[otherPlayer.id] += 5
        time = datetime.datetime.now()
        if author == game.player2:
            result = f"{game.player1.display_name} won against {game.player2.display_name} at {time}"
        else:
            result = f"{game.player1.display_name} lost against {game.player2.display_name} at {time}"
    # only makes move if there is no error, otherwise the error is returned
    error = game.attemptMove(moveString)
    if error is not None:
        await contextOrChannel.send(error)
        return
    outcome = game.processTurn()
    if author.id in moveTimers.keys():
        moveTimers[author.id].cancel()
    await contextOrChannel.send(f"Your move is: {moveString}")
    await contextOrChannel.send(embed=getGameEmbed(game))
    moveTimers[otherPlayer.id] = asyncio.create_task(asyncio.sleep(game.moveTimes[otherPlayer.id]))
    startingMoveTime = datetime.datetime.now()
    try:
        await(moveTimers[otherPlayer.id])
        await contextOrChannel.send(f"{author.display_name} has won the chess game with a time advantage.")
        time = str(datetime.datetime.now())
        time = time[:-10]
        elo[author.id] += 5
        elo[otherPlayer.id] -= 5
        if author == game.player1:
            result = f"{game.player1.display_name} won against {game.player2.display_name} at {time}"
        else:
            result = f"{game.player1.display_name} lost against {game.player2.display_name} at {time}"
        endGame(game, result)
    except asyncio.CancelledError:
        endingMoveTime = datetime.datetime.now()
        delta: datetime.timedelta = endingMoveTime - startingMoveTime
        # print(f"delta = {delta.seconds}")
        game.moveTimes[otherPlayer.id] -= delta.seconds - game.timeIncrement
        # print(game.moveTimes)
    if isinstance(outcome, discord.Member):
        outcome: discord.Member
        await contextOrChannel.send(f"{outcome.display_name} has won the chess game with a checkmate!")
        time = str(datetime.datetime.now())
        time = time[:-10]
        if outcome == game.player1:
            result = f"{game.player1.display_name} won against {game.player2.display_name} at {time}"
            elo[game.player1.id] += 5
            elo[game.player2.id] -= 5
        else:
            result = f"{game.player1.display_name} lost against {game.player2.display_name} at {time}"
            elo[game.player1.id] -= 5
            elo[game.player2.id] += 5
        endGame(game, result)
    elif outcome == "stalemate":
        time = str(datetime.datetime.now())
        time = time[:-10]
        await contextOrChannel.send("The game has resulted in a stalemate.")
        result = f"The game between {game.player1.display_name} and {game.player2.display_name} at {time} resulted in stalemate"
        endGame(game, result)


@bot.event
async def on_ready():
    global elo, gameHistory
    print("Syncing json data...")
    try:
        with open("elo.json", "r") as elofile:
            elo = dict(json.load(elofile))
    except json.JSONDecodeError:
        print("Elo loading error, skipping...")
    try:
        with open("match_history.json", "r") as historyjson:
            gameHistory = list(json.load(historyjson))
    except json.JSONDecodeError:
        print("Game history loading error, skipping...")
    print("Bot is connected to discord services.")


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    text: str = message.content
    if text[0] == ".":
        if (text[1:].split(" "))[0].lower() in ["c", "chess", "challenge", "m", "move", "i", "info", "h", "history", "a", "accept", "d", "decline", "r", "resign", "die", "e", "elo"]:
            await bot.process_commands(message)
        else:
            await actualMove(message.author, message.channel, text[1:], "onmessage")


@bot.command(aliases=["c", "Chess", "C", "challenge", "Challenge"])
async def chess(ctx: commands.Context, otherUser: discord.Member, color="w", startingMoveTime=600, increments=0):
    global games, challenges, elo
    messageUser: discord.Member = ctx.author
    if otherUser == bot.user:
        await ctx.send("You cannot challenge the bot to a game!")
        return
    if color not in "wb":
        await ctx.send("Please specify a valid colour you would like to use.")
        return
    if messageUser.id in games.keys() or otherUser.id in games.keys():
        await ctx.send("You or the user you have challenged is currently in another game.")
        return
    challenges[otherUser.id] = [asyncio.create_task(asyncio.sleep(30)), False]
    await ctx.send(f"You have challenged {otherUser.display_name} to a game of chess. Waiting for them to accept...")
    try:
        await challenges[otherUser.id][0]
        await ctx.send("Your challenge request has been ignored.")
        del challenges[otherUser.id]
    except asyncio.CancelledError:
        if challenges[otherUser.id][1] is False:
            await ctx.send("The user you have challenged has declined your offer.")
            return
        if color == "b":
            game = discordgame.Game(otherUser, messageUser, startingMoveTime, increments)
        else:
            game = discordgame.Game(messageUser, otherUser, startingMoveTime, increments)
        if messageUser.id not in elo.keys():
            elo[messageUser.id] = 1000
        if otherUser.id not in elo.keys():
            elo[otherUser.id] = 1000
        games[messageUser.id] = game
        games[otherUser.id] = game
        await ctx.send(f"Chess game created between {messageUser.display_name} and {otherUser.display_name}")
        await ctx.send(embed=getGameEmbed(game))
        game.processTurn()


def respondToChallenge(ctx, offer):
    global challenges
    if ctx.author.id in challenges.keys():
        # print("cancel async sleep")
        challenges[ctx.author.id][0].cancel()
        challenges[ctx.author.id][1] = offer


@bot.command(aliases=["a", "Accept", "A"])
async def accept(ctx: commands.Context):
    # print("accept")
    respondToChallenge(ctx, True)


@bot.command(aliases=["d", "Decline", "D"])
async def decline(ctx: commands.Context):
    # print("decline")
    respondToChallenge(ctx, False)


@chess.error
async def chess_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please specify the user you would like to challenge.")


@bot.command(aliases=["m", "Move", "M"])
async def move(ctx: commands.Context, moveString: str):
    await actualMove(ctx.author, ctx, moveString, "command")


@bot.command(aliases=["h", "History", "H"])
async def history(ctx: commands.Context):
    global gameHistory
    embed = discord.Embed(title="Game History", color=0xffffff)
    for i, game in enumerate(gameHistory):
        embed.add_field(name=f"Game #{i+1}", value=game, inline=False)
    if len(gameHistory) == 0:
        embed.add_field(name="No games have been played yet.",
                        value="Go play some games", inline=False)
    await ctx.send(embed=embed)


@bot.command(aliases=["i", "Info", "I"])
async def info(ctx: commands.Context):
    embed = discord.Embed(title="Chess Bot Info", color=0xffffff)
    embed.add_field(name="What this bot is",
                    value="This is a simple discord bot made for you to play chess with right in your chat. It fully supports all standard rules of chess (with the exception of the threefold repetition and the 50-move draw)",
                    inline=False)
    embed.add_field(name="How to play",
                    value="All you have to do is to start a new game with `.c user color`, where `user` is the user you would like to challenge and color is either `w` or `b` to select what color you want to play. Moves can then be made by first putting in a `.` followed by a valid move, OR by doing `.m`/`.move` followed by the move notation. Ex. `.e4` OR `.move e4`\n\nPawn moves (except promotion) can be specified by 2 characters.\nEx. `.e4` for pawn to e4\n\nNormal unambiguous moves can be specified by 3 characters.\nEx. `.bc4` for bishop to c4\n\nPawn promotion must be specified by 4 characters.\nEx. `.pe8q` for pawn to e8 + promote to queen\n\nAmbiguous moves must be specified by 5 characters.\nEx. `.ng1f3` for knight on g1 to f3\n\nThe 5 character notation can always be used in place of the 2 or 3 character notation.",
                    inline=False)
    embed.add_field(name="Other Commands",
                    value="`.info` shows this message.\n`.accept` will let you accept a challenge.\n`.decline` will let you decline a challenge.\n`.history` will show a game history of all matches that have been played.\n\nYou can also use only the first letters of each command to run them. For example shortening `.accept` to `.a`",
                    inline=False)
    await ctx.send(embed=embed)


@bot.command()
@has_permissions(administrator=True)
async def die(ctx: commands.Context):
    global elo, gameHistory
    await ctx.send("Killing the bot process...")
    with open("elo.json", "w") as elojson:
        json.dump(elo, elojson)
    with open("match_history.json", "w") as historyjson:
        json.dump(gameHistory, historyjson)
    exit()


@bot.command(aliases=["r", "Resign", "R"])
async def resign(ctx: commands.Context):
    await actualMove(ctx.author, ctx, "resign", "command")


@bot.command(aliases=["e", "ELO", "E"])
async def elo(ctx: commands.Context, user: discord.Member=None):
    global elo
    if user is None:
        user = ctx.author
    await ctx.send(f"{user.display_name}'s elo rating is: {elo[str(user.id)]}")

if __name__ == '__main__':
    bot.run(TOKEN)
