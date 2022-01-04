import discordgame
import datetime
import dotenv
import discord
from discord.ext import commands
import os

dotenv.load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


games = {}
gameHistory = []

bot = commands.Bot(
    command_prefix=".",
    intents=discord.Intents.all()
)

def getGameEmbed(game: discordgame.Game):
    embed = discord.Embed(title=f"Chess: {game.player1.display_name} vs {game.player2.display_name}", description=f"```{game.getBoardString()}```", color=game.hexcolor)
    embed.set_footer(text=f"Turn: {game.turnNum}, Last move: {game.lastMove}")
    return embed

def endGame(game: discordgame.Game, gameResult):
    global games, gameHistory
    games.pop(game.player1.id)
    games.pop(game.player2.id)
    gameHistory.append(gameResult)
    del game

async def actualMove(author, contextOrChannel, moveString):
    global games
    if author.id not in games.keys():
        await contextOrChannel.send("You are currently not in a game.")
        return
    game: discordgame.Game = games[author.id]
    if game.getActivePlayer() != author:
        await contextOrChannel.send("It is not your turn to move yet.")
        return
    error = game.move(moveString)  # only makes move if there is no error, otherwise the error is returned
    if error is not None:
        await contextOrChannel.send(error)
        return
    await contextOrChannel.send(f"Your move is: {moveString}")
    await contextOrChannel.send(embed=getGameEmbed(game))
    outcome = game.processTurn()
    if isinstance(outcome, discord.Member):
        outcome: discord.Member
        await contextOrChannel.send(f"{outcome.display_name} has won the chess game with a checkmate!")
        time = str(datetime.datetime.now())
        time = time[:-10]
        if outcome == game.player1:
            result = f"{game.player1.display_name} won against {game.player2.display_name} at {time}"
        else:
            result = f"{game.player1.display_name} lost against {game.player2.display_name} at {time}"
        endGame(game, result)
    elif outcome == "stalemate":
        time = str(datetime.datetime.now())
        time = time[:-10]
        await contextOrChannel.send("The game has resulted in a stalemate.")
        result = f"The game between {game.player1.display_name} and {game.player2.display_name} at {time} resulted in stalemate"
        endGame(game, result)

@bot.event
async def on_ready():
    print("Bot is connected to discord services.")

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    text: str = message.content
    if text[0] == ".":
        if (text[1:].split(" "))[0].lower() in ["c", "chess", "m", "move", "i", "info", "h", "history"]:
            await bot.process_commands(message)
        else:
            await actualMove(message.author, message.channel, text[1:])

@bot.command(aliases=["c", "Chess", "C"])
async def chess(ctx: commands.Context, otherUser: discord.Member):
    global games
    messageUser: discord.Member = ctx.author
    if messageUser.id in games.keys() or otherUser.id in games.keys():
        await ctx.send("You or the user you have challenged is currently in another game.")
        return
    game = discordgame.Game(messageUser, otherUser)
    games[messageUser.id] = game
    games[otherUser.id] = game
    await ctx.send(f"Chess game created between {messageUser.display_name} and {otherUser.display_name}")
    await ctx.send(embed=getGameEmbed(game))
    game.processTurn()

@chess.error
async def chess_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please specify the user you would like to challenge.")

@bot.command(aliases=["m", "Move", "M"])
async def move(ctx: commands.Context, moveString: str):
    await actualMove(ctx.author, ctx, moveString)


@bot.command(aliases=["h", "History", "H"])
async def history(ctx: commands.Context):
    global gameHistory
    embed = discord.Embed(title="Game History", color=0xffffff)
    for i, game in enumerate(gameHistory):
        embed.add_field(name=f"Game #{i+1}", value=game, inline=False)
    if len(gameHistory) == 0:
        embed.add_field(name="No games have been played yet.", value="Go play some games", inline=False)
    await ctx.send(embed=embed)

@bot.command(aliases=["i", "Info", "I"])
async def info(ctx: commands.Context):
    embed = discord.Embed(title="Chess Bot Info", color=0xffffff)
    embed.add_field(name="What this bot is",
                    value="This is a simple discord bot made for you to play chess with right in your chat. It fully supports all standard rules of chess (with the exception of the threefold repetition and the 50-move draw)",
                    inline=False)
    embed.add_field(name="How to play",
                    value="All you have to do is to start a new game with `.c`. Moves can then be made by first putting in a `.` followed by a valid move. Ex. `.e4`\n\nPawn moves (except promotion) can be specified by 2 characters.\nEx. `.e4` for pawn to e4\n\nNormal unambiguous moves can be specified by 3 characters.\nEx. `.bc4` for bishop to c4\n\nPawn promotion must be specified by 4 characters.\nEx. `.pe8q` for pawn to e8 + promote to queen\n\nAmbiguous moves must be specified by 5 characters.\nEx. `.ng1f3` for knight on g1 to f3\n\nThe 5 character notation can always be used in place of the 2 or 3 character notation.",
                    inline=False)
    await ctx.send(embed=embed)

if __name__ == '__main__':
    bot.run(TOKEN)