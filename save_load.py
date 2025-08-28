import os
import re
import pickle
import shutil
import random
import time
from datetime import datetime
from collections import deque

class SaveLoadSystem:
    def __init__(self, game):
        self.game = game
    
    def generate_save_name(self):
        recent_event = self.game.long_term_memory[-1]['summary'] if self.game.long_term_memory else 'Beginning'
        prompt = f"""
    Create a very short descriptive name (2-4 words) for a life simulation save file based on this character and recent event.
    Character: {self.game.character_description}
    Recent event: {recent_event}
    The name should be evocative and specific. Return only the name, no other text.
    """
  
        try:
            completion = self.game.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=15
            )
            name = completion.choices[0].message.content.strip()
            name = re.sub(r'[^a-zA-Z0-9 ]', '', name)
            name = name.replace(' ', '_')
            if len(name) > 50:
                name = name[:50]
            return f"lifesim_{name}.pkl"
        except Exception as e:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"lifesim_save_{timestamp}.pkl"
    
    def create_save_data(self, display_name=None):
        """Create save data dictionary for both local and cloud storage"""
        if not display_name:
            if self.game.long_term_memory:
                recent_event = self.game.long_term_memory[-1]['summary'] if isinstance(self.game.long_term_memory[-1], dict) else str(self.game.long_term_memory[-1])
                display_name = recent_event[:30] + "..." if len(recent_event) > 30 else recent_event
            else:
                display_name = "New Life"
        
        save_data = {
            'version': '1.0',
            'display_name': display_name,
            'short_term_memory': list(self.game.short_term_memory),
            'long_term_memory': self.game.long_term_memory,
            'character_memory': self.game.character_memory,
            'world_facts': self.game.world_facts,
            'relationships': self.game.relationships,
            'energy_level': self.game.energy_level,
            'stress_level': self.game.stress_level,
            'day_count': self.game.day_count,
            'action_count': self.game.action_count,
            'temporal_energy': self.game.temporal_energy,
            'character_description': self.game.character_description,
            'save_time': datetime.now().isoformat(),
            'global_reputation': self.game.global_reputation,
            'reputation_history': self.game.reputation_history,
            'economy': self.game.economy,
            'dream_log': self.game.dream_log,
            'last_dream_day': self.game.last_dream_day,
            'weather': self.game.weather,
            'npc_personalities': self.game.npc_personalities,
            'cultural_norms': self.game.cultural_norms,
            'current_personality': self.game.current_personality,
            'personality_history': self.game.personality_history,
            'current_mood': self.game.current_mood,
            'environment_type': self.game.environment_type,
            'flora': self.game.flora,
            'fauna': self.game.fauna,
            'npc_initiative_chance': self.game.npc_initiative_chance,
            'world_event_chance': self.game.world_event_chance,
            'world_events': self.game.world_events,
            'last_npc_initiation_time': self.game.last_npc_initiation_time,
            'last_world_event_time': self.game.last_world_event_time
        }
  
        # Generate preview
        preview_prompt = f"""
    Create a brief, evocative description of the current state of this life story.
    Character: {self.game.character_description}
    Recent events: {self.game.long_term_memory[-1]['summary'] if self.game.long_term_memory else 'Beginning'}
    Day: {self.game.day_count}
  
    Write a 1-2 sentence preview that captures the essence of this moment in the story.
    """
  
        try:
            completion = self.game.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": preview_prompt}],
                temperature=0.8,
                max_tokens=100
            )
            preview = completion.choices[0].message.content.strip()
            save_data['preview'] = preview
        except:
            save_data['preview'] = "A life in progress."
            
        return save_data
    
    def cleanup_old_saves(self, current_filename, keep_count=5):
        try:
            save_files = [f for f in os.listdir('.') if f.startswith('lifesim_') and f.endswith('.pkl')]
            backup_files = [f for f in os.listdir('.') if f.startswith('lifesim_') and f.endswith('.pkl.backup')]
          
            all_files = save_files + backup_files
            all_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
          
            files_to_remove = all_files[keep_count*2:]
          
            for old_file in files_to_remove:
                if old_file != current_filename and old_file != current_filename + '.backup':
                    try:
                        os.remove(old_file)
                        print(f"{self.game.DIM}Removed old file: {old_file}{self.game.RESET}")
                    except:
                        pass
                  
        except Exception as e:
            print(f"{self.game.DIM}Could not clean up old files: {e}{self.game.RESET}")
    
    def save_game_state(self, custom_name: str = None):
        """Save game state to local file"""
        filename = custom_name if custom_name and custom_name.endswith('.pkl') else self.generate_save_name()
        save_data = self.create_save_data(custom_name)
  
        try:
            # Create backup if file exists
            if os.path.exists(filename):
                backup_name = f"{filename}.backup"
                if os.path.exists(backup_name):
                    os.remove(backup_name)
                os.rename(filename, backup_name)
          
            # Save new file
            with open(filename, 'wb') as f:
                pickle.dump(save_data, f)
          
            # Verify save
            with open(filename, 'rb') as f:
                test_load = pickle.load(f)
                if 'version' not in test_load:
                    raise ValueError("Save verification failed")
          
            self.cleanup_old_saves(filename)
          
            return f"Game saved locally as {filename}"
  
        except Exception as e:
            # Restore backup if save failed
            backup_name = f"{filename}.backup"
            if os.path.exists(backup_name):
                os.rename(backup_name, filename)
            return f"Save failed: {e}. Previous game state restored."
    
    def load_game_state(self, filename: str):
        """Load game state from local file"""
        try:
            if not os.path.exists(filename):
                return f"Save file {filename} not found."
          
            # Create backup before loading
            backup_name = f"{filename}.backup"
            if os.path.exists(backup_name):
                os.remove(backup_name)
            shutil.copy2(filename, backup_name)
          
            # Load save data
            with open(filename, 'rb') as f:
                save_data = pickle.load(f)
          
            if 'version' not in save_data:
                return "Invalid save file format."
          
            # Restore game state using the main game's restore method
            self.game.restore_game_state(save_data)
          
            # Restart idle system
            with self.game.idle_system.idle_lock:
                self.game.idle_system.stop_idle_timer()
                self.game.idle_system.start_idle_timer()
          
            return f"Game loaded from {filename}"
  
        except Exception as e:
            # Restore backup if load failed
            backup_name = f"{filename}.backup"
            if os.path.exists(backup_name):
                shutil.copy2(backup_name, filename)
            return f"Load failed: {e}. Previous save file restored."
    
    def show_save_files(self):
        """Show available local save files"""
        try:
            save_files = [f for f in os.listdir('.') if f.startswith('lifesim_') and f.endswith('.pkl')]
            save_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            return save_files
        except:
            return []
    
    def get_save_file_info(self, filename):
        """Get information about a save file for display"""
        try:
            with open(filename, 'rb') as f:
                save_data = pickle.load(f)
            
            preview = save_data.get('preview', 'No description available')
            display_name = filename.replace('lifesim_', '').replace('.pkl', '')
            day_count = save_data.get('day_count', 1)
            character_desc = save_data.get('character_description', 'Unknown')[:30]
            save_time = save_data.get('save_time', 'Unknown time')
            
            return {
                'display_name': display_name,
                'preview': preview,
                'day_count': day_count,
                'character_desc': character_desc,
                'save_time': save_time,
                'filename': filename
            }
        except:
            return {
                'display_name': filename,
                'preview': 'Corrupted save file',
                'day_count': 0,
                'character_desc': 'Unknown',
                'save_time': 'Unknown',
                'filename': filename
            }