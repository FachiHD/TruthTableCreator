from discord.ext import commands
import os
import hashlib
import discord
import traceback
import solver
import configparser
import random

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
    """
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
    """
    try:
        statement = " ".join(args)
        pre_processed = solver.pre_process_statement(" ".join(args))
        solver.get_matching_brackets(pre_processed)
        variables, method_tree = solver.create_method_tree(pre_processed)
        method_tree = solver.optimize_truth_table(method_tree)
        optimized_statement = solver.reconstruct_from_tree(method_tree)
        table = solver.generate_truth_values(variables)
        table = solver.run_truth_table(method_tree, table, variables)
        pre_processed = pre_processed.replace(solver.EQUAL_SIGN, "\\" + solver.EQUAL_SIGN)
        optimized_statement = solver.reconstruct_from_tree(method_tree)

        embed = discord.Embed(
            title="Truth Table Creator",
            description=f"Original Statement: {statement}\nStatement: {pre_processed}\nOptimized: {optimized_statement}",
            color=discord.Color.green()
        )
        creator = await client.fetch_user(286907674531201025)

        embed.set_footer(
            text=f"Made by {creator}.",
            icon_url=creator.avatar_url
        )
        await ctx.send(embed=embed)
        string = solver.get_representational_string(table)
    except solver.SolverException as e:
        string = e.error_message
    except BaseException as e:
        # TODO: catch different exceptions and provide better information
        string = traceback.format_exc()

    """
    else:
        with open(f"cached/{fp}", "w+") as f:
            string = solver.get_representational_string(table)
            f.write(string)
            cached = False
    """

    if len(string) + 8 > 2000:
        # TODO: use tempfile
        fp = f"cached/{random.randint(1, 1000)}.txt"
        with open(fp, "rw+") as f:
            f.write(string)
            await ctx.send(
                "```The message was too long so it was put in this file.```",
                file=discord.File(fp, fp.lstrip("cached/"))
            )

        os.remove(fp)
    else:
        await ctx.send(f"```\n{string}```")


client.run(token)
