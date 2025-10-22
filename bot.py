import requests  # so we can get google calendar info
import datetime  # stuff to find certain CTF events
import interactions # discord interactions.py
from dotenv import load_dotenv
import os
# utility to get one full year forward of CTF events
from dateutil.relativedelta import relativedelta

load_dotenv()

TOKEN = os.getenv("TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
RESET_LEADERBOARD_ID = os.getenv("RESET_LEADERBOARD_ID")
ANNOUNCEMENTS_CHANNEL_ID = int(os.getenv("ANNOUNCEMENTS_CHANNEL_ID"))

bot = interactions.Client()

@interactions.slash_command(name="ctfinfo", description="Get more information about a CTF event")
@interactions.slash_option(
    name="eventid",
    description="the event id of the ctf on ctftime",
    required=True,
    opt_type=interactions.OptionType.NUMBER
)
async def ctfinfo(ctx, eventid: int):
    eventid = round(eventid)
    headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    }
    r = requests.get(
        "https://ctftime.org/api/v1/events/" + str(eventid) + "/", headers=headers
    )

    # get json data from api call
    data = r.json()
    event_title = data["title"]
    event_url = data["url"]
    event_start = data["start"]
    event_end = data["finish"]
    event_description = data["description"]

    # get the event image url
    event_image = data["logo"]

    # convert start time to unix timestamp in unix epoch time
    event_start = datetime.datetime.strptime(event_start, "%Y-%m-%dT%H:%M:%S%z")
    event_start = event_start.timestamp()

    # convert end time to unix timestamp in unix epoch time
    event_end = datetime.datetime.strptime(event_end, "%Y-%m-%dT%H:%M:%S%z")
    event_end = event_end.timestamp()

    # create embed
    embed = interactions.Embed(
        title=event_title,
        url=event_url,
        description=event_description,
        type="article",
    )

    # Add tumbnail to embed
    embed.set_thumbnail(url=event_image)

    embed.add_field(
        name="Start Date",
        value="<t:" + str(int(event_start)) + ":d>",
        inline=True,
    )

    embed.add_field(
        name="End Date",
        value="<t:" + str(int(event_end)) + ":d>",
        inline=True,
    )

    # new line
    embed.add_field(name="\u200b", value="\u200b", inline=True)

    # Add a non-relative start time for the event
    embed.add_field(
        name="Start Time",
        value="<t:" + str(int(event_start)) + ":t>",
        inline=True,
    )

    embed.add_field(
        name="End Time",
        value="<t:" + str(int(event_end)) + ":t>",
        inline=True,
    )

    # new line
    embed.add_field(name="\u200b", value="\u200b", inline=True)

    # add fields to embed
    embed.add_field(
        name="When?",
        value="<t:" + str(int(event_start)) + ":R>",
        inline=False,
    )

    # send embed
    await ctx.send(embed=embed)


@interactions.slash_command(name="upcoming", description="Get the next 7 days of CTF events")
async def upcoming(ctx):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36"
        "(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    }

    # get the utc time now in unix epoch time
    now = datetime.datetime.now(datetime.UTC).timestamp()

    # get the utc time + 5 days in unix epoch time
    seven_days = datetime.datetime.now(datetime.UTC) + relativedelta(days=+7)
    seven_days = seven_days.timestamp()

    r = requests.get(
        "https://ctftime.org/api/v1/events/?limit=100"
        + "&start="
        + str(int(now))
        + "&finish="
        + str(int(seven_days)),
        headers=headers,
    )

    data = r.json()

    # create embed with title and description
    embed = interactions.Embed(
        title="Upcoming CTF Events",
        description="Here are the upcoming CTF events in the next 7 days.",
        type="article",
    )

    # loop through all events
    for event in data:
        # get the event title
        event_title = event["title"]

        # get the event url
        event_url = event["url"]

        # get the event start time
        event_start = event["start"]

        event_id = event["id"]

        # convert start time to unix timestamp in unix epoch time
        event_start = datetime.datetime.strptime(event_start, "%Y-%m-%dT%H:%M:%S%z")
        event_start = event_start.timestamp()

        # add a field to the embed
        embed.add_field(
            name=event_title,
            value=event_url,
            inline=True,
        )

        # add id field to embed
        embed.add_field(
            name="Event ID",
            value=event_id,
            inline=True,
        )

        # add a field to the embed
        embed.add_field(
            name="Start Date",
            value="<t:" + str(int(event_start)) + ":f>",
            inline=True,
        )

    # send embed
    await ctx.send(embed=embed)


# ADD DECORATOR TO CHECK FOR USERID 
@interactions.slash_command(name="addctfchannels",
              description="add ctf category channel by name")
@interactions.slash_option(
    name="ctf_name",
    description="the name of the ctf",
    required=True,
    opt_type=interactions.OptionType.STRING
)
@interactions.slash_option(
    name="headers",
    description="if you need first message of the channel to be a header from the bot with disclaimers",
    required=True,
    opt_type=interactions.OptionType.BOOLEAN
)
@interactions.slash_option(
    name="announce",
    description="announce on a channel id",
    required=True,
    opt_type=interactions.OptionType.BOOLEAN
)
async def add_ctf_channels(ctx, ctf_name: str, headers: bool=True, announce: bool=True):
  if ctx.user.id == OWNER_ID:

    channels = ["flag-feedback", "general", "web", "crypto", "pwn", "rev", "forensics", "misc"]

    await ctx.send(f"added new CTF category: {ctf_name}", ephemeral=True)
    category = await ctx.guild.create_category(ctf_name)
    for idx, chann in enumerate(channels):
        if idx == 0:
            overwrite = interactions.PermissionOverwrite(
                id=ctx.guild.default_role.id,
                type=0,  # 0 = role, 1 = member
                allow=interactions.Permissions.VIEW_CHANNEL,
                deny=interactions.Permissions.SEND_MESSAGES
            )
            await ctx.guild.create_text_channel(chann, category=category, permission_overwrites=[overwrite])
        else:
            await ctx.guild.create_text_channel(chann, category=category)

    if headers:
        for chann in category.channels:
            if chann.name == channels[0]:
               await chann.send(f"🔥 This is the FLAG FEEDBACK channel for {ctf_name}! 🚩💻\n\n"
                                f"here <@{RESET_LEADERBOARD_ID}> will send the claimed flag from the current CTF.\n\n"
                                 "**You can claim a flag with /flag NAME_OF_THE_CHALLENGE_HERE.**\n\n"
                                "*please do not spam the bot with fake solved challenges🙏*\n"
                                "--------------------------w---")
               
            elif chann.name == channels[1]:
                await chann.send(f"🌐 Welcome to the General CTF Channel for {ctf_name}! 🏴‍☠️💻\n\n"
                                "here you can talk about pretty much everything (please keep it related to the ctf though 🙏) and please don't share flags here\n"
                                "-----------------------------")
            else:
                 await chann.send(f"🚩 Welcome to the CTF Channel related to {chann.name}! 🕵️‍♂️💻\n\n"
                                "Share your knowledge, discuss vulns, and collaborate here! Let's get this! 💪\n"
                                "**Important: it's not good practice to share the flags here as intruders could steal them from us ( and we dont want that ofc )**\n"
                                f"Remember, keep the conversation focused on {chann.name} CTF topic. Go Reset!! :ResetSec:\n"
                                "-----------------------------")
    if announce:
        chann = bot.get_channel(ANNOUNCEMENTS_CHANNEL_ID)
        message = await chann.send(f"new ctf category for {ctf_name} added!")
        emoji = '\U0001F973'
        await message.add_reaction(emoji)
  else:
     await ctx.send("you are not allowed to run this command!", ephemeral=True)

# purge ctf channels command?

def vrfy_ctf_category(category) -> bool:
  vrfy_channels = ["web", "forensics"]
  count = 0
  for vrf in vrfy_channels:
    for chann in category.channels:
      if str(chann.name) == vrf:
        count += 1
  if count >= 2:
    return True
  else:
    return False
        


# broken
"""
@interactions.slash_command(name="delctfcategory",
              description="del ctf category channels by name")
@interactions.slash_option(
    name="headers",
    description="if you need first message of the channel to be a header from the bot with disclaimers",
    required=True,
    opt_type=interactions.OptionType.
)
async def del_ctf_channels(ctx, category):
  if ctx.user.id == OWNER_ID:

    channels = category.channels

    if vrfy_ctf_category(category):
        await ctx.send(f"Deleted CTF category: {category.name}", ephemeral=True)
        for chann in channels:
            await chann.delete()
        await category.delete()
    else:
        await ctx.send("this is not a CTF category!", ephemeral=True)
  else:
      await ctx.send("you are not allowed to run this command!", ephemeral=True)
"""

bot.start(TOKEN)
