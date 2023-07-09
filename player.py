from typing import Optional
from client import SumerianBot
import discord
import os

class Player(discord.ui.View):
    client = None
    sound_page = 0
    
    def __init__(self, client: SumerianBot, page: int | None = 0):
        super().__init__()
        
        self.client = client
        self.sound_page = page
        
        self.add_sound_selector()
        
        
    @discord.ui.button(label="Resume", style=discord.ButtonStyle.green, row=3)
    async def resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.client.resume_sound()
        await interaction.response.edit_message(content=f"# Player \n {self.client.playlist[0]}")
        
    
    @discord.ui.button(label="Pause", style=discord.ButtonStyle.primary, row=3)
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.client.pause_sound()
        await interaction.response.edit_message(content=f"# Player ||\n {self.client.playlist[0]}")
        
    
    @discord.ui.button(label="Skip", style=discord.ButtonStyle.secondary, row=3)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = self.client.skip_sound()
        await interaction.response.send_message(embed=embed)
    
        
    @discord.ui.button(label="Stop", style=discord.ButtonStyle.red, row=3)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.client.stop_playing()
        await interaction.response.edit_message(content=f"# Player")
        
        
    @discord.ui.button(label="Leave", style=discord.ButtonStyle.danger, row=3)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.client.disconnect()
        await interaction.response.edit_message(content=f"# Player")
        
        
    def soundlist_selection(self, list_index) -> list:
        soundlist = os.listdir(self.client.sound_dir[:-1])
        selections = []
        result = []
        for sound in soundlist:
            selections.append(discord.SelectOption(label=sound))
            
        for i in range(0, len(selections), 25):
            selection = selections[i: i + 25]
            result.append(selection)
            
        return (result[list_index], len(soundlist))
    
    def add_sound_selector(self):
        selector = discord.ui.Select(placeholder=f"Select sound (page: {self.sound_page})", options=self.soundlist_selection(self.sound_page)[0], row=0)
        
        async def select_sound(interaction: discord.Interaction):
            if self.client.voice == None:
                voice = self.client.findVoiceChannel(interaction.user.id, interaction.guild)
                await self.client.connectToVoice(voice)
                
            embed = self.client.add_playlist(selector.values[0])
            await interaction.response.edit_message(content=f"# Player \n {self.client.playlist[0]}")
            await interaction.followup.send(embed=embed)
            await self.client.start_sound()
        
        selector.callback = select_sound
        
        self.add_item(selector)
        
        pages = []
        for i in range(round(self.soundlist_selection(0)[1] / 25)):
            pages.append(discord.SelectOption(label=i))
        
        page = discord.ui.Select(placeholder="Pages", options=pages, row=1)
        
        async def select_page(interaction: discord.Interaction):
            sound_page = int(page.values[0])
            await interaction.response.edit_message(view=Player(self.client, sound_page))
            
        page.callback = select_page
        
        self.add_item(page)
            