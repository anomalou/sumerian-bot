import os
import discord
import asyncio

from dotenv import load_dotenv
from client import SumerianBot

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

sumerianBot = SumerianBot(command_prefix="!", intents=discord.Intents.all())

@sumerianBot.command(name="sumerian", help="Generate sumerian texts")
async def sumerian(interaction, length):
    await interaction.send(sumerianBot.gen_sumerian(int(length)))
    pass
    
@sumerianBot.command(name="echo", help="Echo text as many as you want")
async def echo(interaction, value, count):
    for _ in range(int(count)):
        await interaction.send(value)
        await asyncio.sleep(0.5)
    
def findVoiceChannel(userID:int, guild):
    for voiceChannel in guild.voice_channels:
        member = findMemberInChannel(userID, voiceChannel)
        if(member != None):
            return voiceChannel
        
    return None
    
def findMemberInChannel(userID:int, channel:discord.VoiceChannel):
    for member in channel.members:
        if(member.id == userID):
            return member
    return None

def findMember(userID:int, guild):
    for voiceChannel in guild.voice_channels:
        member = findMemberInChannel(userID, voiceChannel)
        if(member != None):
            return member
    
        
@sumerianBot.command(name="shutup", help="You know what it do")
async def shutup(interaction, userID:str):
    userID = int(userID[2:-1])
    
    member = findMember(userID, interaction.guild)
    if(member == None):
        return
    
    await member.edit(mute=True)
    
    
@sumerianBot.command(name="soundlist", help="Show all sounds in sound folder")
async def soundlist(interaction:discord.Integration):
    embed = discord.Embed(title="Sound list", description=os.listdir(sumerianBot.sound_dir[:-1]), color=discord.Color.dark_blue())
    await sumerianBot.main_channel.send(embed=embed)
    pass


@sumerianBot.command(name="download", help="Download youtube to mp3")
async def download(interaction:discord.Integration, url, name):
    embed = discord.Embed(title="Downloading", description=url, color=discord.Color.red())
    await sumerianBot.main_channel.send(embed=embed)
    sumerianBot.download_sound_YT(url, name)

    
@sumerianBot.command(name="play", help="Play sound from sound folder")
async def play(interaction:discord.Integration, sound):
    sound_is_valid = sumerianBot.check_sound(sound)
    
    if not sound_is_valid[0]:
        embed = discord.Embed(title="Sound not found!", description=f"You typed {sound}. Check name and try again", color=discord.Color.red())
        await sumerianBot.main_channel.send(embed=embed)
        return
    
    sound = sound_is_valid[1]
    
    if(sumerianBot.voice != None):
        await sumerianBot.add_playlist(sound)
        return
    
    voice = findVoiceChannel(interaction.author.id, interaction.guild)
    
    if voice == None:
        await sumerianBot.main_channel.send(f"# {sumerianBot.gen_random()}")
        return 
    
    await sumerianBot.connectToVoice(voice)
    await sumerianBot.add_playlist(sound)
    await sumerianBot.start_sound()
    
    pass


@sumerianBot.command(name="playlist", help="Current playlist")
async def playlist(interaction:discord.Integration):
    await sumerianBot.show_playlist()
    pass


@sumerianBot.command(name="stop", help="Stop sound playing")
async def stop(interaction:discord.Integration):
    await sumerianBot.stop_sound()
    pass
    
    
@sumerianBot.command(name="repeat", help="Repeat current sound")
async def repeat(interaction:discord.Integration):
    sumerianBot.repeat = not sumerianBot.repeat
    if sumerianBot.repeat:
        await sumerianBot.main_channel.send(embed=discord.Embed(title="Repeat track", description="Is ON now", color=discord.Color.dark_green()))
    else:
        await sumerianBot.main_channel.send(embed=discord.Embed(title="Repeat track", description="Is OFF now", color=discord.Color.dark_red()))
    pass


@sumerianBot.command(name="repeatall", help="Repeat playlist")
async def repeat(interaction:discord.Integration):
    sumerianBot.repeat_all = not sumerianBot.repeat_all
    if sumerianBot.repeat_all:
        await sumerianBot.main_channel.send(embed=discord.Embed(title="Repeat playlist", description="Is ON now", color=discord.Color.dark_green()))
    else:
        await sumerianBot.main_channel.send(embed=discord.Embed(title="Repeat playlist", description="Is ON now", color=discord.Color.dark_red()))
    pass


@sumerianBot.command(name="skip", help="Skip current song")
async def skip(interaction:discord.Integration):
    await sumerianBot.skip_sound()
    pass


@sumerianBot.command(name="playlists", help="List of avaible playlists")
async def playlists(interaction:discord.Integration):
    await sumerianBot.show_playlists()
    pass


@sumerianBot.command(name="playlist-save", help="Save current playlist with name")
async def playlist_save(interaction:discord.Integration, name):
    if(sumerianBot.save_playlist(name=name)):
        await sumerianBot.main_channel.send(embed=discord.Embed(title="Playlist saved!", description=f"Current playlist saved as {name}", color=discord.Color.green()))
    else:
        await sumerianBot.main_channel.send(embed=discord.Embed(title="Error!", description=f"Failed to save current playlist!", color=discord.Color.red()))
    pass


@sumerianBot.command(name="playlist-load", help="Load playlist with name")
async def playlist_load(interaction:discord.Integration, name):
    if(sumerianBot.load_playlist(name=name)):
        voice = findVoiceChannel(interaction.author.id, interaction.guild)
        await sumerianBot.connectToVoice(voice)
        await sumerianBot.start_sound()
        await sumerianBot.main_channel.send(embed=discord.Embed(title="Playlist loaded!", description=f"Current playlist is {name}", color=discord.Color.green()))
    else:
        await sumerianBot.main_channel.send(embed=discord.Embed(title="Error!", description=f"Failed to load playlist {name}!", color=discord.Color.red()))
    pass


@sumerianBot.command(name="leave", help="Leave from voice channel")
async def leave(interaction:discord.Integration):
    await sumerianBot.disconnect()
    pass


@sumerianBot.command(name="roflmode", help="Rolf mode. By default off")
async def roflmode(interaction:discord.Integration, state):
    sumerianBot.rofl_mode = True if state == "on" else False
    if(sumerianBot.rofl_mode):
        sumerianBot.jumpscare.start()
    else:
        sumerianBot.jumpscare.stop()
    pass        


# @sumerianBot.command(name="test", help="If i forgot off this do not use")
# async def test(interaction:discord.Integration):
#     sumerianBot.check_sound("")

            
sumerianBot.run(TOKEN)