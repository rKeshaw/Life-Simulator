import openai
import time
import random
from collections import deque
from datetime import datetime

from auth_system import AuthSystem
from cloud_memory import CloudMemory
from colors import Colors
from environment import Environment
from npc import NpcSystem
from memory import MemorySystem
from idle import IdleSystem
from personality import PersonalitySystem
from save_load import SaveLoadSystem
from ai_response import AiResponseSystem

class IntelligentLifeSim(Colors):
    def __init__(self):
        # API Setup
        self.api_key = "unused"
        self.client = openai.OpenAI(
            base_url="https://api.llm7.io/v1",
            api_key=self.api_key
        )
        
        # Initialize auth system first
        self.auth_system = AuthSystem()
        self.cloud_memory = CloudMemory(self.auth_system)
       
        # Memory Systems
        self.short_term_memory = deque(maxlen=6)
        self.long_term_memory = []
        self.character_memory = {}
        self.world_facts = []
        self.relationships = {}
        
        # Hidden Stats
        self.current_mood = 'neutral'
        self.energy_level = 100
        self.stress_level = 0
        self.day_count = 1
        self.action_count = 0
        self.global_reputation = 50
        self.reputation_history = []
        self.economy = {'food_price': 1.0, 'metal_price': 1.0, 'luxury_price': 1.0, 'stability': 50}
        
        # Environment
        self.environment_type = "default"
        self.flora = []
        self.fauna = []
        self.weather = 'clear'
        self.weather_counter = 0
        
        # Dream state
        self.dream_log = []
        self.last_dream_day = 0
        
        # Temporal System
        self.temporal_energy = 5
        self.save_states = []
        
        # Idle System
        self.last_action_time = time.time()
        self.idle_check_interval = 30
        self.idle_threshold = 120
        self.is_waiting_for_input = False
        self.last_activity_time = time.time()
        
        # NPC System
        self.last_npc_initiation_time = time.time()
        self.npc_initiation_cooldown = 300
        self.npc_personalities = {}
        self.cultural_norms = {
            'personal_space': random.uniform(0.3, 0.9),
            'formality': random.uniform(0.2, 0.8),
            'directness': random.uniform(0.3, 0.9),
        }
        
        # World Events
        self.last_world_event_time = time.time()
        self.world_event_cooldown = 600
        self.world_events = {}
        self.npc_initiative_chance = 0.05
        self.world_event_chance = 0.02
        
        # AI Personalities
        self.ai_personalities = {
            'default': {
                'temperature': 0.75,
                'style_keywords': 'balanced, immersive, descriptive',
                'description': 'Standard narrative style - rich and engaging'
            },
            'noir': {
                'temperature': 0.85,
                'style_keywords': 'cynical, hard-boiled, metaphorical, shadowy',
                'description': 'Dark, moody detective fiction style'
            },
            'epic': {
                'temperature': 0.9,
                'style_keywords': 'grandiose, heroic, dramatic, monumental',
                'description': 'Mythic and larger-than-life storytelling'
            },
            'whimsical': {
                'temperature': 1.0,
                'style_keywords': 'playful, humorous, absurd, delightful',
                'description': 'Lighthearted and slightly surreal'
            },
            'horror': {
                'temperature': 0.65,
                'style_keywords': 'dread, atmospheric, unsettling, ominous',
                'description': 'Slow-building terror and unease'
            },
            'journalistic': {
                'temperature': 0.6,
                'style_keywords': 'factual, concise, observational, precise',
                'description': 'Objective reporter style'
            },
            'poetic': {
                'temperature': 0.8,
                'style_keywords': 'lyrical, rhythmic, metaphorical, emotional',
                'description': 'Poetic and expressive style'
            },
            'sci_fi': {
                'temperature': 0.7,
                'style_keywords': 'futuristic, technological, speculative, innovative',
                'description': 'Science fiction style with tech focus'
            }
        }
        self.current_personality = 'default'
        self.personality_history = []
        
        # Game State
        self.game_active = True
        self.character_description = ""
       
        # Initialize subsystems
        self.environment = Environment(self)
        self.npc_system = NpcSystem(self)
        self.memory_system = MemorySystem(self)
        self.idle_system = IdleSystem(self)
        self.personality_system = PersonalitySystem(self)
        self.save_load_system = SaveLoadSystem(self)
        self.ai_response_system = AiResponseSystem(self)
        
        # Initialize environment
        self.environment.initialize_environment()
    
    def handle_authentication(self):
        """Handle user authentication at startup"""
        print("\nWelcome! You can play as a guest or create an account to save your progress across devices.")
        print("1. Continue as guest (local saves only)")
        print("2. Sign in to existing account")
        print("3. Create new account")
        
        while True:
            auth_choice = input("\nChoose (1-3): ").strip()
            
            if auth_choice == "1":
                print("Continuing as guest. Your saves will be stored locally.")
                return True
                
            elif auth_choice == "2":
                email = input("Email: ").strip()
                password = input("Password: ").strip()
                if self.auth_system.sign_in(email, password):
                    print(f"Welcome back! Cloud saves enabled.")
                    return True
                else:
                    print("Sign in failed. Try again or continue as guest.")
                    continue
                    
            elif auth_choice == "3":
                email = input("Email: ").strip()
                password = input("Password: ").strip()
                username = input("Username: ").strip()
                if self.auth_system.sign_up(email, password, username):
                    self.auth_system.sign_in(email, password)
                    print("Welcome to a Life!")
                    return True
                else:
                    print("Account creation failed. Try again or continue as guest.")
                    continue
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
    
    def load_user_saves(self):
        """Load saves based on authentication status"""
        if self.auth_system.is_authenticated():
            # Load from cloud storage
            cloud_saves = self.cloud_memory.get_memories("game_save", limit=10)
            local_saves = self.save_load_system.show_save_files()
            
            all_saves = []
            
            # Add cloud saves
            for save in cloud_saves:
                if save and 'data' in save:
                    save_data = save['data']
                    display_name = save_data.get('display_name', 'Unknown Save')
                    preview = save_data.get('preview', 'No description available')
                    day_count = save_data.get('day_count', 1)
                    character_desc = save_data.get('character_description', 'Unknown')[:30]
                    
                    all_saves.append({
                        'type': 'cloud',
                        'data': save_data,
                        'display_name': display_name,
                        'preview': preview,
                        'day_count': day_count,
                        'character_desc': character_desc
                    })
            
            # Add local saves
            for filename in local_saves:
                try:
                    import pickle
                    with open(filename, 'rb') as f:
                        save_data = pickle.load(f)
                    
                    display_name = filename.replace('lifesim_', '').replace('.pkl', '')
                    preview = save_data.get('preview', 'No description available')
                    day_count = save_data.get('day_count', 1)
                    character_desc = save_data.get('character_description', 'Unknown')[:30]
                    
                    all_saves.append({
                        'type': 'local',
                        'filename': filename,
                        'data': save_data,
                        'display_name': display_name,
                        'preview': preview,
                        'day_count': day_count,
                        'character_desc': character_desc
                    })
                except:
                    continue
            
            if all_saves:
                print("\nAvailable saved lives:")
                for i, save in enumerate(all_saves, 1):
                    source = "☁️ Cloud" if save['type'] == 'cloud' else "💾 Local"
                    print(f"{i}. {save['display_name']} ({source})")
                    print(f"   {self.DIM}{save['preview']}{self.RESET}")
                    print(f"   Day {save['day_count']}, {save['character_desc']}...")
                    print()
                
                return all_saves
            else:
                print("No save files found.")
                return []
        else:
            # Guest mode - only local saves
            local_saves = self.save_load_system.show_save_files()
            return [{'type': 'local', 'filename': f} for f in local_saves]
    
    def load_selected_save(self, all_saves, selection_index):
        """Load a save file based on user selection"""
        try:
            save = all_saves[selection_index]
            
            if save['type'] == 'cloud':
                # Load from cloud save data
                save_data = save['data']
                self.restore_game_state(save_data)
                return f"Game loaded from cloud save: {save['display_name']}"
            else:
                # Load from local file
                return self.save_load_system.load_game_state(save['filename'])
                
        except Exception as e:
            return f"Failed to load save: {e}"
    
    def restore_game_state(self, save_data):
        """Restore game state from save data"""
        self.short_term_memory = deque(save_data.get('short_term_memory', []), maxlen=6)
        self.long_term_memory = save_data.get('long_term_memory', [])
        self.character_memory = save_data.get('character_memory', {})
        self.world_facts = save_data.get('world_facts', [])
        self.relationships = save_data.get('relationships', {})
        self.energy_level = save_data.get('energy_level', 100)
        self.stress_level = save_data.get('stress_level', 0)
        self.day_count = save_data.get('day_count', 1)
        self.action_count = save_data.get('action_count', 0)
        self.temporal_energy = save_data.get('temporal_energy', 5)
        self.character_description = save_data.get('character_description', "")
        self.global_reputation = save_data.get('global_reputation', 50)
        self.reputation_history = save_data.get('reputation_history', [])
        self.economy = save_data.get('economy', {'food_price': 1.0, 'metal_price': 1.0, 'luxury_price': 1.0, 'stability': 50})
        self.dream_log = save_data.get('dream_log', [])
        self.last_dream_day = save_data.get('last_dream_day', 0)
        self.weather = save_data.get('weather', 'clear')
        self.npc_personalities = save_data.get('npc_personalities', {})
        self.cultural_norms = save_data.get('cultural_norms', {
            'personal_space': random.uniform(0.3, 0.9),
            'formality': random.uniform(0.2, 0.8),
            'directness': random.uniform(0.3, 0.9)
        })
        self.current_personality = save_data.get('current_personality', 'default')
        self.personality_history = save_data.get('personality_history', [])
        self.current_mood = save_data.get('current_mood', 'neutral')
        self.environment_type = save_data.get('environment_type', 'default')
        self.flora = save_data.get('flora', [])
        self.fauna = save_data.get('fauna', [])
        self.npc_initiative_chance = save_data.get('npc_initiative_chance', 0.05)
        self.world_event_chance = save_data.get('world_event_chance', 0.02)
        self.world_events = save_data.get('world_events', {})
        self.last_npc_initiation_time = save_data.get('last_npc_initiation_time', time.time())
        self.last_world_event_time = save_data.get('last_world_event_time', time.time())
    
    def save_current_game(self, save_name=None):
        """Save current game state to appropriate storage"""
        if self.auth_system.is_authenticated():
            # Save to both cloud and local for backup
            save_data = self.save_load_system.create_save_data(save_name)
            
            # Store in cloud
            cloud_result = self.cloud_memory.store_memory(
                "game_save", 
                save_data, 
                importance_score=7
            )
            
            # Also save locally as backup
            local_result = self.save_load_system.save_game_state(save_name)
            
            if cloud_result:
                return f"Game saved to cloud (with local backup): {save_data.get('display_name', 'Unknown')}"
            else:
                return local_result
        else:
            # Guest mode - save locally only
            return self.save_load_system.save_game_state(save_name)
    
    def get_game_state(self):
        """Return the current game state for saving"""
        game_state = {
            'character_description': self.character_description,
            'short_term_memory': list(self.short_term_memory),
            'long_term_memory': self.long_term_memory,
            'character_memory': self.character_memory,
            'world_facts': self.world_facts,
            'relationships': self.relationships,
            'current_mood': self.current_mood,
            'energy_level': self.energy_level,
            'stress_level': self.stress_level,
            'day_count': self.day_count,
            'action_count': self.action_count,
            'global_reputation': self.global_reputation,
            'reputation_history': self.reputation_history,
            'economy': self.economy,
            'environment_type': self.environment_type,
            'flora': self.flora,
            'fauna': self.fauna,
            'weather': self.weather,
            'weather_counter': self.weather_counter,
            'dream_log': self.dream_log,
            'last_dream_day': self.last_dream_day,
            'temporal_energy': self.temporal_energy,
            'save_states': self.save_states,
            'last_action_time': self.last_action_time,
            'idle_check_interval': self.idle_check_interval,
            'idle_threshold': self.idle_threshold,
            'is_waiting_for_input': self.is_waiting_for_input,
            'last_activity_time': self.last_activity_time,
            'last_npc_initiation_time': self.last_npc_initiation_time,
            'npc_initiation_cooldown': self.npc_initiation_cooldown,
            'npc_personalities': self.npc_personalities,
            'cultural_norms': self.cultural_norms,
            'last_world_event_time': self.last_world_event_time,
            'world_event_cooldown': self.world_event_cooldown,
            'world_events': self.world_events,
            'npc_initiative_chance': self.npc_initiative_chance,
            'world_event_chance': self.world_event_chance,
            'current_personality': self.current_personality,
            'personality_history': self.personality_history,
            'game_active': self.game_active,
        }
        return game_state

    def set_game_state(self, game_state):
        """Restore a saved game state"""
        # Restore basic attributes
        for key, value in game_state.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Convert short_term_memory back to deque
        if 'short_term_memory' in game_state:
            self.short_term_memory = deque(game_state['short_term_memory'], maxlen=6)
        
        print("Game state restored successfully")
    
    def _generate_dream(self):
        if self.day_count - self.last_dream_day < 3:
            return None
      
        if not self.long_term_memory or len(self.long_term_memory) < 3:
            return None
      
        self.last_dream_day = self.day_count
  
        memory_context = ""
        for memory in self.long_term_memory[-5:]:
            if isinstance(memory, dict):
                memory_context += f"- {memory['summary']}\n"
            else:
                memory_context += f"- {memory}\n"
  
        prompt = f"""
    Generate a dream sequence based on the player's recent experiences and emotional state.
    The dream should be surreal, symbolic, and emotionally resonant with their experiences.
    Incorporate elements from these recent memories:
    {memory_context}
  
    Current emotional tone: {self.current_mood}
    Current stress level: {self.stress_level}
  
    Write the dream as a vivid, first-person experience (using "you") that lasts 2-3 paragraphs.
    The dream should feel meaningful but not necessarily provide direct answers or solutions.
    """
  
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
                max_tokens=400
            )
            dream = completion.choices[0].message.content.strip()
            self.dream_log.append({
                'day': self.day_count,
                'dream': dream,
                'mood': self.current_mood
            })
            return dream
        except Exception as e:
            print(f"{self.RED}Dream generation failed: {e}{self.RESET}")
            return None
    
    def auto_rest(self):
        self.energy_level = min(100, self.energy_level + 40)
        self.stress_level = max(0, self.stress_level - 20)
        dream = self._generate_dream()
        if dream:
            print(f"\n{self.BRIGHT_MAGENTA}💤 During your rest, you dream...{self.RESET}")
            print(f"{self.DIM}{dream}{self.RESET}")
            print(f"{self.BRIGHT_MAGENTA}You wake feeling strangely affected by this dream.{self.RESET}")
        self.day_count += 1
        if self.world_events:
            for event_id in list(self.world_events.keys()):
                self.ai_response_system.distort_rumor(event_id)
        self.action_count = 0
    
    def player_creation(self, user_input: str) -> str:
        creation_type = "creation"
        input_lower = user_input.lower()
        if "poem" in input_lower or "poetry" in input_lower:
            creation_type = "poem"
        # ... (full if-elif for types)
        prompt = f"""
    You are a creative assistant helping the player create {creation_type} based on their character.
    Player's character: {self.character_description}
    Player's request: {user_input}
    Generate a {creation_type} that fits the player's character and request. Make it authentic and immersive.
    If it's a poem, write it in verse. If it's code, write it in a programming language with comments. If it's a story, write a short narrative.
    Output only the {creation_type} itself, without any additional explanation or framing.
    REMEMBER, if you can't do it, say something in prose (if for poem) or 'coding language' (if for code) or like that. Don't EVER include yourself, and represent yourself as I.
    """
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
                max_tokens=400
            )
            creation = completion.choices[0].message.content.strip()
            # Store creative works in memory
            if self.auth_system.is_authenticated():
                self.cloud_memory.store_memory("creation", {
                    'type': creation_type,
                    'content': creation,
                    'request': user_input,
                    'day': self.day_count
                }, importance_score=5)
            return creation
        except Exception as e:
            return f"Failed to create {creation_type}: {e}"
    
    def _generate_world_event(self):
        if not self.world_facts and len(self.long_term_memory) < 2:
            return None
        context = self.memory_system.build_context_memory()
        status = self.ai_response_system.get_hidden_status_context()
        prompt = f"""
    Generate a significant world event that happens independently of the player. This could be a political announcement, a war, a natural disaster, an economic shift, or any major event that would affect the world.
    The event should be consistent with the established world facts and history. It should feel like something the player would hear about through rumors or news.
    NEVER use the term "NPC" or "non-player character" - all characters are real people (or animals).
    Write this as a brief news bulletin or widespread rumor, in the style of the game world. Keep it to 1-2 sentences.
    Current World State:
    {context}
    {status}
    World Event:
    """
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=150
            )
            event_text = completion.choices[0].message.content.strip()
            return event_text
        except Exception as e:
            print(f"{self.RED}Failed to generate world event: {e}{self.RESET}")
            return None
    
    def _analyze_event_impact(self, event_text):
        event_lower = event_text.lower()
  
        if any(word in event_lower for word in ['peace', 'celebration', 'victory', 'success', 'boom', 'recovery']):
            self.stress_level = max(0, self.stress_level - 15)
            self.energy_level = min(100, self.energy_level + 10)
            print(f"{self.DIM}You feel a sense of relief and renewed energy from the positive news.{self.RESET}")
  
        elif any(word in event_lower for word in ['war', 'attack', 'disaster', 'crisis', 'death', 'collapse', 'shortage']):
            self.stress_level = min(100, self.stress_level + 25)
            self.energy_level = max(0, self.energy_level - 15)
            print(f"{self.DIM}The distressing news weighs heavily on you, sapping your energy.{self.RESET}")
  
        else:
            self.stress_level = min(100, self.stress_level + 5)
            print(f"{self.DIM}The news leaves you contemplative.{self.RESET}")
    
    def undo_last_action(self):
        if self.temporal_energy < 1:
          return "A faint ripple passes through the air, but nothing changes. The moment is stuck fast, immutable. You've strained against the flow of time too much."
        if len(self.short_term_memory) < 2:
          return "There is nothing recent enough to undo."
        self.short_term_memory.pop()
        if self.short_term_memory:
          self.short_term_memory.pop()
        self.energy_level = min(100, self.energy_level + 10)
        self.stress_level = max(0, self.stress_level - 5)
        self.action_count = max(0, self.action_count - 1)
        self.temporal_energy -= 1
        return "The world gutters like a candle flame. For a heart-stopping moment, everything flows in reverse—words unsaid, steps retraced. As reality snaps back into place, a profound weariness settles in your bones. The act has cost you."
    
    def get_status_report(self):
        if self.long_term_memory:
            recent_events_list = []
            for item in self.long_term_memory[-3:]:
                if isinstance(item, dict):
                    recent_events_list.append(item['summary'])
                else:
                    recent_events_list.append(item)
            recent_events_str = ' | '.join(recent_events_list)
        else:
            recent_events_str = 'Just getting started'
        status_prompt = f"""Based on the player's journey so far, write a brief, natural reflection on their current situation. Include:
- How they're feeling physically and mentally (based on recent actions)
- Key relationships and how others see them
- Important abilities or resources they've gained
- Current challenges or opportunities
CHARACTER: {self.character_description}
DAY: {self.day_count}
RECENT EVENTS: {recent_events_str}
RELATIONSHIPS: {list(self.relationships.keys())[-5:] if self.relationships else 'No significant relationships yet'}
Write this as a natural narrative moment of self-reflection, not a status report."""
        try:
          completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": status_prompt}],
            temperature=0.6,
            max_tokens=200
          )
          return completion.choices[0].message.content
        except:
          return "You take a moment to reflect on your journey so far..."
    
    def show_help(self):
        help_text = """
🎮 COMMANDS:
• Just type what you want to do naturally
• 'undo' - Use temporal energy to undo your last action
• 'reflect' - Take a moment to assess your situation
• 'personality' - Show current narrative style and available options
• 'save' or 'save [name]' - Save your current life
• 'help' - Show this help
• 'quit' - End your current life
• 'write [something]' - Create a poem, story, code, etc. based on your character
• 'create [something]' - Similar to write
• 'compose [something]' - Create music or song
• 'code [something]' - Write a program
• 'paint [something]' - Create art
• 'make [something]' - Create an item or recipe
💡 TIPS:
• The AI remembers everything important automatically
• Your energy and stress are managed naturally - the AI will hint when you need rest
• Build relationships by interacting with characters repeatedly
• Establish world rules through your actions - they'll be remembered
• The more detailed your actions, the richer the story becomes
        """
        # print(help_text)
        return help_text
        
    def initial_game_prompt(self):
        print("Options:")
        print("1. Start new life")
        print("2. Load saved life")
        print("3. Quick start (random scenario)")
 
        choice = input("\nChoose (1-3): ").strip()
        
        if choice == "2":
            all_saves = self.load_user_saves()
            if all_saves:
                try:
                    file_num = int(input("Enter file number to load: ")) - 1
                    if 0 <= file_num < len(all_saves):
                        result = self.load_selected_save(all_saves, file_num)
                        print(f"\n{result}")
                        print("Resuming your life...")
                    else:
                        print("Invalid selection, starting new life.")
                        choice = "1"
                except:
                    print("Invalid input, starting new life.")
                    choice = "1"
            else:
                print("No save files found.")
                choice = "1"
      
        elif choice == "3":
          scenarios = [
            "I am a detective in 1940s noir city with the ability to see the last moments of murder victims",
            "I am a space station engineer in 2087 who discovers the AI is becoming sentient",
            "I am a medieval alchemist who accidentally created a potion that lets me talk to animals",
            "I am a college student who finds out my roommate is a time traveler",
            "I am a small-town librarian who inherits a bookstore that contains portals to fictional worlds"
          ]
          self.character_description = random.choice(scenarios)
          print(f"\n🎲 Random scenario: {self.character_description}")
          
        if choice == "1" or (choice == "3" and not self.character_description):
          self.character_description = input("\nDescribe yourself and your world: ")
  
        if choice in ["1", "3"]:
            setup_prompt = f"I want to live this life: '{self.character_description}'. Begin my story."
            self.memory_system.add_to_short_term_memory("user", setup_prompt)
            opening_response = self.ai_response_system.get_ai_response(setup_prompt)
            self.memory_system.add_to_short_term_memory("assistant", opening_response)
            self.memory_system.score_and_store_event(setup_prompt, opening_response)
            print(f"\n{self.personality_system.get_mood_color()}{'-' * 60}{self.RESET}")
            print("Your life begins...")
            print(f"{self.personality_system.get_mood_color()}{'-' * 60}{self.RESET}")
            print(opening_response)
    
    def run_game(self):
        ### wait
        
        if not self.auth_system.is_authenticated:
            print("🌟 Welcome to LifeSim: Natural Intelligence Edition")
            print("Live any life you can imagine - the AI will make it feel real.")
            print("-" * 60)
       
        # Handle authentication first
        if not self.handle_authentication():
            print("Authentication cancelled. Exiting...")
            return
        
        if self.cloud_memory.is_connected():
            print(f"{self.DIM}Memory archiving enabled ☁️{self.RESET}")
            
        # print("Options:")
        # print("1. Start new life")
        # print("2. Load saved life")
        # print("3. Quick start (random scenario)")
 
        # choice = input("\nChoose (1-3): ").strip()
        
        # if choice == "2":
        #     all_saves = self.load_user_saves()
        #     if all_saves:
        #         try:
        #             file_num = int(input("Enter file number to load: ")) - 1
        #             if 0 <= file_num < len(all_saves):
        #                 result = self.load_selected_save(all_saves, file_num)
        #                 print(f"\n{result}")
        #                 print("Resuming your life...")
        #             else:
        #                 print("Invalid selection, starting new life.")
        #                 choice = "1"
        #         except:
        #             print("Invalid input, starting new life.")
        #             choice = "1"
        #     else:
        #         print("No save files found.")
        #         choice = "1"
      
        # elif choice == "3":
        #   scenarios = [
        #     "I am a detective in 1940s noir city with the ability to see the last moments of murder victims",
        #     "I am a space station engineer in 2087 who discovers the AI is becoming sentient",
        #     "I am a medieval alchemist who accidentally created a potion that lets me talk to animals",
        #     "I am a college student who finds out my roommate is a time traveler",
        #     "I am a small-town librarian who inherits a bookstore that contains portals to fictional worlds"
        #   ]
        #   self.character_description = random.choice(scenarios)
        #   print(f"\n🎲 Random scenario: {self.character_description}")
          
        # if choice == "1" or (choice == "3" and not self.character_description):
        #   self.character_description = input("\nDescribe yourself and your world: ")
  
        # if choice in ["1", "3"]:
        #     setup_prompt = f"I want to live this life: '{self.character_description}'. Begin my story."
        #     self.memory_system.add_to_short_term_memory("user", setup_prompt)
        #     opening_response = self.ai_response_system.get_ai_response(setup_prompt)
        #     self.memory_system.add_to_short_term_memory("assistant", opening_response)
        #     self.memory_system.score_and_store_event(setup_prompt, opening_response)
        #     print(f"\n{self.personality_system.get_mood_color()}{'-' * 60}{self.RESET}")
        #     print("Your life begins...")
        #     print(f"{self.personality_system.get_mood_color()}{'-' * 60}{self.RESET}")
        #     print(opening_response)
        
        self.initial_game_prompt()
        
        while self.game_active:
          print(f"\n{self.personality_system.get_mood_color()}{'-' * 40}{self.RESET}")
          self.last_activity_time = time.time()
          self.is_waiting_for_input = True
        
          self.personality_system.adjust_personality_based_on_context()
       
          try:
            user_input = input("What do you do? (or 'help' for commands): ").strip()
          except EOFError:
            print("Your world destroys itself and returns toward singularity.")
            break
            # user_input = "quit"
        
          self.is_waiting_for_input = False
          self.last_activity_time = time.time()
          if user_input.lower() == 'quit':
            save = input("Would you like to save your story one last time? (y/n): ").lower().strip()
            if save == 'y':
              result = self.save_current_game()
              print(f"{result}")
            print("Your story ends here. But it was a life!")
            print()
            print("What would you do now?")
            print("1. Live Again")
            print("2. Sign Out")
            print("Type 1 or 2: ")
            while True:  # Loop until valid input
                inp = input().strip()
                if inp == "2":
                    self.auth_system.sign_out()
                    self.game_active = False
                    break
                elif inp == "1":
                    self.initial_game_prompt()
                    break
                else:
                    print("Invalid choice. Type 1 or 2:")
            continue
            # break
          elif user_input.lower() == 'help':
            self.show_help()
            continue
          elif user_input.lower() == 'undo':
            result = self.undo_last_action()
            print(f"\n{result}")
            continue
          elif user_input.lower() == 'reflect':
            reflection = self.get_status_report()
            print(f"\n{self.personality_system.get_mood_color()}--- Moment of Reflection ---{self.RESET}")
            print(reflection)
            print(f"{self.personality_system.get_mood_color()}--- End Reflection ---{self.RESET}")
            continue
          elif user_input.lower() == 'personality':
            current = self.current_personality
            desc = self.ai_personalities[current]['description']
            print(f"\nCurrent narrative style: {current.upper()}")
            print(f"Description: {desc}")
            print("\nAvailable personalities:")
            for personality, info in self.ai_personalities.items():
                print(f" {personality}: {info['description']}")
            continue
          elif user_input.lower().startswith('save'):
                parts = user_input.split(' ', 1)
                save_name = parts[1] if len(parts) > 1 else None
                result = self.save_current_game(save_name)
                print(f"\n{result}")
                continue
          elif user_input.lower() == 'reputation':
            reputation_desc = self.npc_system.get_reputation_desc(self.global_reputation)
            reaction = self.npc_system.get_reputation_reaction()
            print(f"\nYour reputation: {self.global_reputation}/100 ({reputation_desc})")
            print(f"{reaction}")
          
            if self.reputation_history:
                print("\nRecent reputation changes:")
                for event in self.reputation_history[-3:]:
                    change = "+" + str(event['change']) if event['change'] > 0 else event['change']
                    print(f"Day {event['day']}: {change} ({event['reason'][:30]}...)")
            continue
          elif user_input.lower().startswith('apologize to '):
            parts = user_input[13:].split(' ', 1)
            if len(parts) < 2:
                print("Not the correct way! Try saying in the form: apologize to [name] [your apology]")
            else:
                npc_name = parts[0]
                apology = parts[1] if len(parts) > 1 else ""
                result = self.npc_system.attempt_apology(npc_name, apology)
                print(f"\n{result}")
            continue
          elif any(user_input.lower().startswith(verb) for verb in ['write ', 'create ', 'compose ', 'make ', 'code ', 'paint ', 'draw ', 'sing ', 'build ', 'design ']):
            creation = self.player_creation(user_input)
            print(f"\n{creation}")
            continue
          elif not user_input:
            print("Please enter an action or command.")
            continue
        
          self.memory_system.add_to_short_term_memory("user", user_input)
          ai_response = self.ai_response_system.get_ai_response(user_input)
          self.memory_system.add_to_short_term_memory("assistant", ai_response)
        
          analysis = self.memory_system.score_and_store_event(user_input, ai_response)
          print(f"\n{self.ai_response_system.enhance_output(ai_response)}")
          self.memory_system.hint_at_memory(user_input, analysis.get('importance_score', 0))
        
          self.environment.change_weather()
        
          self.last_activity_time = time.time()
          current_time = time.time()
          if (current_time - self.last_npc_initiation_time >= self.npc_initiation_cooldown and
              random.random() < self.npc_initiative_chance):
              initiation = self.npc_system.npc_initiates_interaction()
              if initiation:
                  print(f"\n{self.GREEN}{initiation}{self.RESET}")
                  self.memory_system.add_to_short_term_memory("assistant", initiation)
                  self.last_npc_initiation_time = current_time
                  
          if (current_time - self.last_world_event_time >= self.world_event_cooldown and
            random.random() < self.world_event_chance):
            event = self._generate_world_event()
            if event:
                print(f"\n{self.YELLOW}*** WORLD NEWS ***{self.RESET}")
                print(f"{self.YELLOW}{event}{self.RESET}")
                event_id = f"event_{int(time.time())}"
                self.world_events[event_id] = {
                    'true_event': event,
                    'current_rumor': event,
                    'day_occurred': self.day_count,
                    'distortion_level': 0
                }
                self.long_term_memory.append({
                    'day': self.day_count,
                    'summary': f"World event: {event[:50]}...",
                    'sensory_snippet': event
                })
                self._analyze_event_impact(event)
                self.last_world_event_time = current_time
                
                if self.auth_system.is_authenticated():
                    self.cloud_memory.store_memory("world_event", {
                        'event': event,
                        'day': self.day_count,
                        'impact_analyzed': True
                    }, importance_score=6)
                
        self.idle_system.stop_idle_timer()

if __name__ == "__main__":
  game = IntelligentLifeSim()
  game.run_game()