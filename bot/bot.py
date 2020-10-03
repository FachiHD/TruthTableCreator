from discord.ext import commands
from bot import settings
import discord
import traceback
import solver

client = commands.Bot(command_prefix="#")


@client.command()
async def solve(ctx, *args):
    statement = " ".join(args)
    try:
        table = solver.create_truth_table(statement)
    except solver.SolverException as e:
        await ctx.send(f"```\n{e.error_message}```")

    except BaseException as e:
        # TODO: catch different exceptions and provide better information
        await ctx.send(f"```\n{traceback.format_exc()}```")

    else:
        embed = discord.Embed(
            title="Truth Table Creator",
            description=f"Statement: {statement}",
            color=discord.Color.green()
        )
        creator = await client.fetch_user(286907674531201025)
        embed.set_footer(
            text=f"Made by {creator}.",
            icon_url=creator.avatar_url
        )
        await ctx.send(embed=embed)
        string = solver.get_representational_string(table)
        await ctx.send(f"```{string}```")


client.run(settings.TOKEN)
