import os
import discord
import discord.ext.commands
import asyncio

from dotenv import load_dotenv
from client import SumerianBot
from player import Player

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

sumerianBot = SumerianBot(command_prefix="!", intents=discord.Intents.all())

@sumerianBot.command(name="sumerian", help="Generate sumerian texts")
async def sumerian(context, length):
    await context.send(sumerianBot.gen_sumerian(int(length)))
    pass
    
@sumerianBot.command(name="echo", help="Echo text as many as you want")
async def echo(context, value, count):
    for _ in range(min(int(count), 10)):
        await context.send(value)
        await asyncio.sleep(0.5)
    pass
    
        
@sumerianBot.command(name="shutup", help="You know what it do")
async def shutup(context, userID:str):
    userID = int(userID[2:-1]) #get user ID by ping tag
    
    member = sumerianBot.findMember(userID, context.guild)
    if(member == None):
        return
    
    await member.edit(mute=True)
    
    
@sumerianBot.command(name="soundlist", help="Show all sounds in sound folder")
async def soundlist(context:discord.ext.commands.Context):
    embed = sumerianBot.show_soundlist()
    await context.send(embed=embed)
    pass


# @sumerianBot.command(name="download", help="Download youtube to mp3")
# async def download(context:discord.ext.commands.Context, url, name):
#     embed = discord.Embed(title="Downloading", description=url, color=discord.Color.red())
#     await sumerianBot.main_channel.send(embed=embed)
#     sumerianBot.download_sound_YT(url, name)

    
@sumerianBot.command(name="play", help="Play sound from sound folder")
async def play(context:discord.ext.commands.Context, sound):
    sound_is_valid = sumerianBot.check_sound(sound)
    
    if not sound_is_valid[0]:
        embed = discord.Embed(title="Sound not found!", description=f"You typed {sound}. Check name and try again", color=discord.Color.red())
        await context.send(embed=embed)
        return
    
    sound = sound_is_valid[1]
    
    if(sumerianBot.voice != None):
        embed = sumerianBot.add_playlist(sound)
        await context.send(embed=embed)
        await sumerianBot.start_sound()
        return
    
    voice = sumerianBot.findVoiceChannel(context.author.id, context.guild)
    
    if voice == None:
        await sumerianBot.main_channel.send(f"# {sumerianBot.gen_random()}")
        return 
    
    await sumerianBot.connectToVoice(voice)
    embed = sumerianBot.add_playlist(sound)
    await context.send(embed=embed)
    await sumerianBot.start_sound()
    
    pass


@sumerianBot.command(name="playlist", help="Current playlist")
async def playlist(context:discord.ext.commands.Context):
    embed = sumerianBot.show_playlist()
    await context.send(embed=embed)
    pass


@sumerianBot.command(name="stop", help="Stop sound playing")
async def stop(context:discord.ext.commands.Context):
    await sumerianBot.stop_playing()
    pass
    
    
@sumerianBot.command(name="repeat", help="Repeat current sound")
async def repeat(context:discord.ext.commands.Context):
    sumerianBot.repeat = not sumerianBot.repeat
    if sumerianBot.repeat:
        await context.send(embed=discord.Embed(title="Repeat track", description="Is ON now", color=discord.Color.dark_green()))
    else:
        await context.send(embed=discord.Embed(title="Repeat track", description="Is OFF now", color=discord.Color.dark_red()))
    pass


@sumerianBot.command(name="repeatall", help="Repeat playlist")
async def repeat(context:discord.ext.commands.Context):
    sumerianBot.repeat_all = not sumerianBot.repeat_all
    if sumerianBot.repeat_all:
        await context.send(embed=discord.Embed(title="Repeat playlist", description="Is ON now", color=discord.Color.dark_green()))
    else:
        await context.send(embed=discord.Embed(title="Repeat playlist", description="Is OFF now", color=discord.Color.dark_red()))
    pass


@sumerianBot.command(name="skip", help="Skip current song")
async def skip(context:discord.ext.commands.Context):
    embed = sumerianBot.skip_sound()
    await context.send(embed=embed)
    pass


@sumerianBot.command(name="pause", help="Pause current sound")
async def pause(context:discord.ext.commands.Context):
    if sumerianBot.pause_sound():
        await context.send(embed=discord.Embed(title="Sound is paused", description=sumerianBot.playlist[0], color=discord.Color.yellow()))
    else:
        await context.send(embed=discord.Embed(title="Error!", description="Can't pause the sound! Is even playing?", color=discord.Color.red()))
    pass


@sumerianBot.command(name="resume", help="Resume current sound")
async def pause(context:discord.ext.commands.Context):
    if sumerianBot.resume_sound():
        await context.send(embed=discord.Embed(title="Sound is resumed!", description=sumerianBot.playlist[0], color=discord.Color.green()))
    else:
        await context.send(embed=discord.Embed(title="Error!", description="Can't resume the sound! Is even paused?", color=discord.Color.red()))
    pass


@sumerianBot.command(name="playlists", help="List of available playlists")
async def playlists(context:discord.ext.commands.Context):
    embed = sumerianBot.show_playlists()
    await context.send(embed=embed)
    pass


@sumerianBot.command(name="playlist-save", help="Save current playlist with name")
async def playlist_save(context:discord.ext.commands.Context, name):
    if(sumerianBot.save_playlist(name=name)):
        await context.send(embed=discord.Embed(title="Playlist saved!", description=f"Current playlist saved as {name}", color=discord.Color.green()))
    else:
        await context.send(embed=discord.Embed(title="Error!", description=f"Failed to save current playlist!", color=discord.Color.red()))
    pass


@sumerianBot.command(name="playlist-load", help="Load playlist with name")
async def playlist_load(context:discord.ext.commands.Context, name):
    if(sumerianBot.load_playlist(name=name)):
        voice = sumerianBot.findVoiceChannel(context.author.id, context.guild)
        await sumerianBot.connectToVoice(voice)
        await sumerianBot.start_sound()
        await context.send(embed=discord.Embed(title="Playlist loaded!", description=f"Current playlist is {name}", color=discord.Color.green()))
    else:
        await context.send(embed=discord.Embed(title="Error!", description=f"Failed to load playlist {name}!", color=discord.Color.red()))
    pass


@sumerianBot.command(name="leave", help="Leave from voice channel")
async def leave(context:discord.ext.commands.Context):
    await sumerianBot.disconnect()
    pass


@sumerianBot.command(name="roflmode", help="Rolf mode. By default off")
async def roflmode(context:discord.ext.commands.Context, state):
    sumerianBot.rofl_mode = True if state == "on" else False
    if(sumerianBot.rofl_mode):
        sumerianBot.jumpscare.start()
    else:
        sumerianBot.jumpscare.stop()
    pass        


@sumerianBot.command(name="anime", help="Get anime pic (also hentai)")
async def get_anime(context:discord.ext.commands.Context, tags = ""):
    await sumerianBot.get_anime(tags)
    pass
    
    
@sumerianBot.command(name="whatday", help="What day today?")
async def what_day(context:discord.ext.commands.Context):
    image = await sumerianBot.what_day()
    await context.send(file=image)
    pass


@sumerianBot.command(name="test", help="If i forgot off this do not use")
async def test(context:discord.ext.commands.Context):
    view = Player(sumerianBot)
    
    try:
        await context.send("# Player", view=view)
    except Exception as ex:
        print(ex)
    pass

            
sumerianBot.run(TOKEN)