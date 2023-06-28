from discord.ext import commands
from discord.ext import tasks
from collections import deque
from waifuim import WaifuAioClient
from datetime import date
import os
import random
import discord
import asyncio
import youtube_dl


class SumerianBot(commands.Bot):
    rofl_mode = False
    repeat = False
    repeat_all = False
    
    playlist = deque()
    
    voice:discord.VoiceClient = None
    
    main_guild = None
    main_channel = None
    
    sound_dir = "sounds/"
    playlist_dir = "playlists/"
    week_dir = "week/"
    
    waifuClient = WaifuAioClient()
    
    #######################################################################################################
    ########################    BASE SECTION    ###########################################################
    #######################################################################################################
    
    
    async def on_ready(self):
        self.sounds = os.getenv("JUMPSCARE_SND").split(",")
        self.call_word = os.getenv("CALL_PHRASE").split(",")
        self.kill_word = os.getenv("KILL_PHRASE").split(",")
        
        for guild in self.guilds:
            if(guild.id == int(os.getenv("GUILD_ID"))):
                self.main_guild = guild
            for channel in guild.text_channels:
                if(channel.id == int(os.getenv("MAIN_CHN"))):
                    self.main_channel = channel
                    break
        
        if self.rofl_mode:
            self.jumpscare.start()
        
        print(f"{self.user} has connected!")
        
        
    ##################  MESSAGES  ##################
        
        
    async def on_message(self, message, /) -> None:
        if message.author == self.user:
            return
        
        #Commands processing
        if(message.content.startswith("!")):
            await self.process_commands(message)
            await message.delete()
            return
        
        if not self.rofl_mode:
            return
        
        #Rofl mode features
        
        #Bot call
        if(any(sub in message.content for sub in self.call_word)):
            await self.gen_sound(message.author.voice.channel)
            return
        
        #Bot kill
        if(any(sub in message.content for sub in self.kill_word)):
            await self.voice.disconnect()
            self.voice = None
        
        #Bot random phrase reply
        value = random.random()
        if(value > 0.5):
            await message.channel.send(self.gen_random_sumerian())
            
        pass
    
    
    ##################  ERROR HANDLER  ##################
    
    
    async def on_command_error(self, interaction, error):
        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(title="Command error!", description="Command not found!", color=discord.Color.red())
            await interaction.send(embed=embed)
    
    
    #######################################################################################################
    ########################    TASK SECTION    ###########################################################
    #######################################################################################################
    
    ##################  JUMPSCARE  ##################
    
    @tasks.loop(hours=2, count=None)
    async def jumpscare(self):
        channels = []
        
        for channel in self.main_guild.voice_channels:
            if len(channel.members) > 0 and channel.id != int(os.getenv("AFK_CHN")):
                channels.append(channel)
        
        if(random.random() > .7):
            await self.gen_sound(random.choice(channels))
        else:
            print("Jumpscare failed! I will try later")
        pass
    
    
    ##################  SOUND PLAYING  ##################
    

    @tasks.loop(seconds=1, count=None)
    async def playing(self):
        if len(self.playlist) <= 0:
            return
            
        next_sound = self.playlist[0]
        
        self.play_sound(next_sound)
            
        await self.main_channel.send(embed=discord.Embed(title="Playing", description=next_sound, color=discord.Color.green()))
        print(f"Playing: {next_sound}")
        
        while(self.voice.is_playing() or self.voice.is_paused()):
            await asyncio.sleep(1)
        
        if(not self.repeat):
            if(len(self.playlist) > 0):
                self.playlist.popleft()
            
            if(self.repeat_all):
                self.playlist.append(next_sound)
                
        if(len(self.playlist) <= 0):
            self.playing.stop()
        pass
    
    
    #######################################################################################################
    ########################    FUNCTIONS SECTION    ######################################################
    #######################################################################################################
    
    ##################  UTILITY  ##################
    
    def findVoiceChannel(self, userID:int, guild):
        for voiceChannel in guild.voice_channels:
            member = self.findMemberInChannel(userID, voiceChannel)
            if(member != None):
                return voiceChannel
            
        return None
    
    def findMemberInChannel(self, userID:int, channel:discord.VoiceChannel):
        for member in channel.members:
            if(member.id == userID):
                return member
        return None

    def findMember(self, userID:int, guild):
        for voiceChannel in guild.voice_channels:
            member = self.findMemberInChannel(userID, voiceChannel)
            if(member != None):
                return member
    
    
    ##################  SOUND WORK  ##################
    
          
    async def gen_sound(self, channel):
        
        value = random.choice(self.sounds)
        
        await self.play_sound_leave(channel, value)
        pass
    
    
    async def play_sound_leave(self, channel, sound):
        await self.connectToVoice(channel)
        
        self.play_sound(sound)
        
        while(self.voice.is_playing()):
            await asyncio.sleep(1.0)
        
        await self.voice.disconnect()
        self.voice = None
        pass
    
            
    def check_sound(self, sound:str):
        sounds = os.listdir(self.sound_dir[:-1])
        for s in sounds:
            if(sound.lower() == s.lower()):
                return True, s
            if(sound.lower() == s.split(".", 1)[0].lower()):
                return True, s
            
        return False, sound
        pass
    
        
    def play_sound(self, sound):
        if(self.voice == None):
            return
            
        if(self.voice.is_playing()):
            return
        
        self.voice.play(source=discord.FFmpegPCMAudio(executable="util/ffmpeg.exe", source=f"{self.sound_dir}{sound}"))
            
        pass
    
        
    async def start_sound(self):
        if(not self.playing.is_running()):
            self.playing.start()
        pass
        
        
    async def stop_playing(self):
        if(self.voice == None):
            return
        
        self.playlist.clear()
        self.voice.stop()
        self.repeat = False
        
        
    def stop_sound(self):
        if(self.voice == None):
            return
        
        if(self.voice.is_playing()):
            self.voice.stop()
            
    def pause_sound(self):
        if(self.voice == None):
            return
        
        if not self.voice.is_paused():   
            self.voice.pause()
            return True
        else:
            return False
        pass
    
    
    def resume_sound(self):
        if(self.voice == None):
            return
        
        if self.voice.is_paused():
            self.voice.resume()
            return True
        else:
            return False
        pass
        
        
    async def skip_sound(self):
        if(self.voice == None):
            return
        
        if(len(self.playlist) <= 0):
            return
        
        sound = self.playlist[0]
            
        self.voice.stop()
        
        await self.main_channel.send(embed=discord.Embed(title="Skipped", description=sound, color=discord.Color.red()))
        pass
    
    
    ##################  PLAYLISTS  ##################
        
        
    def show_soundlist(self) -> discord.Embed:
        sounds = os.listdir(self.sound_dir[:-1])
        result = ""
        number = 1
        for sound in sounds:
            result += f"{number}. {sound}\n"
        embed = discord.Embed(title="Sound list", description=result, color=discord.Color.dark_blue())
        return embed
        pass
        
        
    def show_playlist(self):
        result = ""
        position = 1
        for sound in self.playlist:
            string = f"{position}. {sound}"
            result += string
            if(self.playlist.index(sound) == 0):
                result += " - :loud_sound:"
            result += "\n"
        
        embed = discord.Embed(title="Playlist", description=result, color=discord.Color.purple())
        
        return embed
            
        
        
    def add_playlist(self, sound) -> discord.Embed:
        self.playlist.append(sound)
        return discord.Embed(title="Added", description=sound, color=discord.Color.yellow())
        
        
    def show_playlists(self):
        return discord.Embed(title="Available playlists", description=os.listdir(self.playlist_dir[:-1]), color=discord.Color.gold())
        pass
        
    
    def save_playlist(self, name):
        try:
            file = open(f"{self.playlist_dir}{name}", "w")
            for sound in self.playlist:
                file.write(sound + "\n")
                
            file.close()
            print(f"Saved as {name}")
        except:
            return False
        
        return True
            
        
    def load_playlist(self, name):
        try:
            file = open(f"{self.playlist_dir}{name}", "r")
            playlist = file.readlines()
            for sound in playlist:
                self.playlist.append(sound[:-1])
                
            print(f"Loaded: {playlist}")
        except:
            return False
        
        return True
        
        
    ##################  VOICE  ##################
        
        
    async def connectToVoice(self, channel):
        if(self.voice != None):
            return
        
        self.voice = await channel.connect()
        
    
    async def disconnect(self):
        if(self.voice == None):
            return
        
        self.playlist.clear()    
            
        if(self.voice.is_playing()):
            self.voice.stop()
            
        while self.playing.is_running():
            await asyncio.sleep(1)    
        
        await self.voice.disconnect()
        self.voice = None
        
        pass
        
        
    ##################  OTHERS  ##################
        
        
    def gen_random_sumerian(self):
        length = random.randint(5, 20)
        return self.gen_sumerian(length)
        pass

        
    def gen_sumerian(self, l) -> str:
        result = ""
        for i in range(l):
            value = random.randint(160, 223)
            code = 66304 + value
            result += chr(code)

        sign = [' ', '!', '?']
        result += random.choice(sign)
        
        return result
        pass
    
    
    def download_sound_YT(self, url, name):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{self.sound_dir}{name}.mp3',
        }
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        
    async def get_anime(self, tags:str):
        image = None
        
        if(len(tags) != 0):
            tags = tags.replace(" ", "")
            tags = tags.split(",")
            try:
                image = await self.waifuClient.search(included_tags=tags)
            except Exception:
                await self.main_channel.send(embed=discord.Embed(title="Error!", description="Typed tag is incorrect!", color=discord.Color.red()))
        else:
            image = await self.waifuClient.search()
            
        if(image == None):
            return
            
        embed = discord.Embed(title="Picture", description=tags, type="image", color=discord.Color.blurple())
        embed.set_image(url=image.url)
        await self.main_channel.send(embed=embed)
        
        print(f"Picture loaded: {image.url}")
        
    async def what_day(self):
        today = date.today()
        weekday = today.weekday()
        
        try:
            with open(f"{self.week_dir}{weekday}.gif", "rb") as file:
                image = discord.File(file)
                return image
        except Exception:
            await self.main_channel.send(embed=discord.Embed(title="Sorry!", description="No to celebrate today", color=discord.Color.red()))
        
        
        