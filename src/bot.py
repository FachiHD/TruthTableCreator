from discord.ext import commands
import os
import hashlib
import discord
import traceback
import solver
import configparser

config = configparser.ConfigParser()
config.read("config.ini")
sections = config.sections()
# TODO: add more comments on what options do
owner_id = int(config.get("BOT", "owner_id", fallback=None))
command_prefix = config.get("BOT", "command_prefix", fallback="#")
token = config.get("BOT", "token", fallback=None)
# TODO: implement any of these option
caching = config.get("CACHING", "use_caching", fallback=True)
caching_dir = config.get("CACHING", "caching_dir", fallback="cached")


client = commands.Bot(command_prefix=command_prefix, owner_id=owner_id)


@client.command()
@commands.is_owner()
async def clear_cache(ctx, *args):
    await ctx.send("Cache cleared!")


@client.command()
async def solve(ctx, *args):
    statement = " ".join(args)
    pre_processed = solver.pre_process_statement(" ".join(args))
    hasher = hashlib.sha256(pre_processed.encode())
    hash_ = hasher.hexdigest()
    fp = f"{hash_}.txt"

    cached = False
    if not os.path.exists("cached"):
        os.mkdir("cached")

    if fp in os.listdir("cached"):
        with open(f"src/cached/{fp}", "r") as f:
            string = f.read()
            cached = True
    else:
        try:
            table = solver.create_truth_table(pre_processed, pre_process=False)
        except solver.SolverException as e:
            string = e.error_message

        except BaseException as e:
            # TODO: catch different exceptions and provide better information
            string = traceback.format_exc()

        else:
            with open(f"src/cached/{fp}", "w+") as f:
                string = solver.get_representational_string(table)
                f.write(string)
                cached = False

    embed_statement = pre_processed.replace(solver.EQUAL_SIGN, "\\" + solver.EQUAL_SIGN)
    embed = discord.Embed(
        title="Truth Table Creator",
        description=f"Original Statement: {statement}\nStatement: {embed_statement}\nHash: {hash_}\nCached: {cached}",
        color=discord.Color.green()
    )
    creator = await client.fetch_user(286907674531201025)
    embed.set_footer(
        text=f"Made by {creator}.",
        icon_url=creator.avatar_url
    )
    await ctx.send(embed=embed)

    if len(string) + 8 > 2000:
        if os.path.exists(f"src/cached/{hash_}.txt"):
            await ctx.send(
                "```The message was too long so it is in this file.```",
                file=discord.File(f"cached/{hash_}.txt", f"{hash_}.txt")
            )
        else:
            await ctx.send("```Error: The message was too long but the table was not cached.```")
    else:
        await ctx.send(f"```\n{string}```")


client.run(token)
