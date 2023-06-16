from discord.ext import commands
from discord.ext import tasks
from collections import deque
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
    
    sounds = os.getenv("JUMPSCARE_SND").split(",")
    call_word = os.getenv("CALL_PHRASE").split(",")
    kill_word = os.getenv("KILL_PHRASE").split(",")
    
    sound_dir = "sounds/"
    playlist_dir = "playlists/"
    
    async def on_ready(self):
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
            await message.channel.send(self.gen_random())
            
        pass
    
    
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
    

    @tasks.loop(seconds=1, count=None)
    async def playing(self):
        if len(self.playlist) <= 0:
            return
            
        next_sound = self.playlist[0]
        
        self.play_sound(next_sound)
            
        await self.main_channel.send(embed=discord.Embed(title="Playing", description=next_sound, color=discord.Color.green()))
        print(f"Playing: {next_sound}")
        
        while(self.voice.is_playing()):
            await asyncio.sleep(2)
        
        if(not self.repeat):
            self.playlist.popleft()
            
            if(self.repeat_all):
                self.playlist.append(next_sound)
        
        pass
    
          
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
        self.playing.start()
        
        
    async def stop_sound(self):
        if(self.voice == None):
            return
        
        self.voice.stop()
        self.playing.stop()
        self.repeat = False
        
        
    async def show_playlist(self):
        result = ""
        position = 1
        for sound in self.playlist:
            string = f"{position}: {sound}\n"
            result += string
            position += 1
        
        await self.main_channel.send(embed=discord.Embed(title="Playlist", description=result, color=discord.Color.purple()))
            
        
        
    async def add_playlist(self, sound):
        self.playlist.append(sound)
        await self.main_channel.send(embed=discord.Embed(title="Added", description=sound, color=discord.Color.yellow()))
        
        
    async def show_playlists(self):
        await self.main_channel.send(embed=discord.Embed(title="Avaible playlists", description=os.listdir(self.playlist_dir[:-1]), color=discord.Color.gold()))
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
            self.playlist.clear()
            for sound in playlist:
                self.playlist.append(sound[:-1])
                
            print(f"Loaded: {playlist}")
        except:
            return False
        
        return True
        
        
    async def skip_sound(self):
        if(self.voice == None):
            return
        
        if(len(self.playlist) <= 0):
            return
        
        sound = self.playlist[0]
        
        if(self.repeat):
            self.playlist.popleft()
            
        self.voice.stop()
        
        await self.main_channel.send(embed=discord.Embed(title="Skipped", description=sound, color=discord.Color.red()))
        
        
    async def connectToVoice(self, channel):
        if(self.voice != None):
            return
        
        self.voice = await channel.connect()
        
    
    async def disconnect(self):
        if(self.voice == None):
            return
        
        self.playing.stop()
        await self.voice.disconnect()
        self.voice = None
        self.playlist.clear()
        
        pass
        
        
    def gen_random(self):
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
        