from discord.ext import commands
import os
import hashlib
import tempfile
import discord
import traceback
import solver
import time

client = commands.Bot(command_prefix="#", owner_id=286907674531201025)


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
        with open(f"cached/{fp}", "r") as f:
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
            with open(f"cached/{fp}", "w+") as f:
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
        if os.path.exists(f"cached/{hash_}.txt"):
            await ctx.send(
                "```The message was too long so it is in this file.```",
                file=discord.File(f"cached/{hash_}.txt", f"{hash_}.txt")
            )
        else:
            await ctx.send("```Error: The message was too long but the table was not cached.```")
    else:
        await ctx.send(f"```\n{string}```")


client.run("NzYxNTU3MTc3MjkwMTk1MDM2.X3cVZA.37thwm2CS1tN9sV8y_50XskE5rQ")
