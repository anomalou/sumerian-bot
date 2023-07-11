from typing import Optional
from client import SumerianBot
import discord
import os
import math

class Player(discord.ui.View):
    client = None
    sound_page = 0
    
    def __init__(self, client: SumerianBot, page: int | None = 0):
        super().__init__()
        
        self.client = client
        self.sound_page = page
        
        self.add_sound_selector()
        
    ##############################################################################
    ####################    CONTROL BUTTONS     ##################################
    ##############################################################################
        
    @discord.ui.button(label="Resume", style=discord.ButtonStyle.green, row=3)
    async def resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.client.resume_sound()
        await interaction.response.edit_message(content=f"# Player")
        
    
    @discord.ui.button(label="Pause", style=discord.ButtonStyle.primary, row=3)
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.client.pause_sound()
        await interaction.response.edit_message(content=f"# Player ||")
        
    
    @discord.ui.button(label="Skip", style=discord.ButtonStyle.secondary, row=3)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = self.client.skip_sound()
        await interaction.response.edit_message(embed=self.client.show_playlist())
        await interaction.followup.send(embed=embed)
    
        
    @discord.ui.button(label="Stop", style=discord.ButtonStyle.red, row=3)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.client.stop_playing()
        await interaction.response.edit_message(content=f"# Player", embed=self.client.show_playlist())
        
        
    @discord.ui.button(label="Leave", style=discord.ButtonStyle.danger, row=3)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.client.disconnect()
        await interaction.response.edit_message(content=f"# Player", embed=None)
        pass
        
        
    ##############################################################################
    ####################    SOUND SELECTOR     ###################################
    ##############################################################################    
        
        
    def get_sound_variants(self) -> tuple:
        soundlist = os.listdir(self.client.sound_dir[:-1])
        
        raw_result = []
        
        for i in range(0, len(soundlist), 25):
            raw = soundlist[i: i + 25]
            raw_result.append(raw)
        
        prepared_result = []
        
        for page in raw_result:
            prepared_page = []
            for sound in page:
                prepared_page.append(discord.SelectOption(label=sound))
                
            prepared_result.append(prepared_page)
            
        return (raw_result, prepared_result, len(soundlist))
        pass
    
    
    def add_sound_selector(self):
        sound_variants = self.get_sound_variants()
        
        selector = discord.ui.Select(placeholder=f"Select sound (page: {self.sound_page + 1})", options=sound_variants[1][self.sound_page], row=0)
        
        async def select_sound(interaction: discord.Interaction):
            if self.client.voice == None:
                voice = self.client.findVoiceChannel(interaction.user.id, interaction.guild)
                await self.client.connectToVoice(voice)
                
            embed = self.client.add_playlist(selector.values[0])
            await interaction.response.edit_message(content=f"# Player", embed=self.client.show_playlist())
            await interaction.followup.send(embed=embed)
            await self.client.start_sound()
        
        selector.callback = select_sound
        
        self.add_item(selector)
        
        
        pages = []
        
        for i in range(math.ceil(sound_variants[2] / 25)):
            # [0][i][0][0] - raw_result -> i page -> first list item -> first test symbol
            # [0][i][-1][0] - raw_result -> i page -> last list item -> first test symbol
            pages.append(discord.SelectOption(label=f"Page {i + 1}: {sound_variants[0][i][0][0]} - {sound_variants[0][i][-1][0]}", value=i))
        
        page = discord.ui.Select(placeholder="Pages", options=pages, row=1)
        
        async def select_page(interaction: discord.Interaction):
            sound_page = int(page.values[0])
            await interaction.response.edit_message(view=Player(self.client, sound_page))
            
        page.callback = select_page
        
        self.add_item(page)
        pass
            