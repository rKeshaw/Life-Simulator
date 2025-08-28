import random

class Environment:
    def __init__(self, game):
        self.game = game
        self.initialize_environment()
    
    def determine_environment_type(self):
        desc = self.game.character_description.lower()
      
        if any(word in desc for word in ['space', 'alien', 'planet', 'starship', 'galaxy']):
            return "space"
        elif any(word in desc for word in ['cyber', 'digital', 'virtual', 'ai', 'robot']):
            return "digital"
        elif any(word in desc for word in ['fantasy', 'magic', 'dragon', 'elf', 'wizard']):
            return "fantasy"
        elif any(word in desc for word in ['underwater', 'ocean', 'sea', 'aquatic']):
            return "aquatic"
        elif any(word in desc for word in ['postapocalyptic', 'wasteland', 'dystopian']):
            return "postapocalyptic"
        else:
            return "earthlike"
    
    def initialize_environment(self):
        self.game.environment_type = self.determine_environment_type()
      
        if self.game.environment_type == "space":
            self.game.flora = ['glowing crystal', 'silicon plant', 'bio-luminescent fungus', 'metallic lichen']
            self.game.fauna = ['energy being', 'robotic drone', 'floating crystal', 'nanite swarm']
        elif self.game.environment_type == "digital":
            self.game.flora = ['data tree', 'code vine', 'pixel flower', 'algorithmic growth']
            self.game.fauna = ['data stream', 'firewall guardian', 'algorithm creature', 'AI entity']
        elif self.game.environment_type == "fantasy":
            self.game.flora = ['enchanted oak', 'glowing mushroom', 'whispering willow', 'crystal flower']
            self.game.fauna = ['dragon', 'unicorn', 'gryphon', 'fairy']
        elif self.game.environment_type == "aquatic":
            self.game.flora = ['kelp forest', 'coral formation', 'bioluminescent algae', 'sea anemone']
            self.game.fauna = ['dolphin', 'giant squid', 'manta ray', 'anglerfish']
        elif self.game.environment_type == "postapocalyptic":
            self.game.flora = ['mutated weed', 'radioactive fungus', 'hardy scrub', 'twisted tree']
            self.game.fauna = ['mutant rat', 'scavenger bird', 'radroach', 'wasteland dog']
        else:
            self.game.flora = ['oak tree', 'pine tree', 'willow tree', 'rose bush', 'daisy', 'fern', 'moss', 'ivy']
            self.game.fauna = ['squirrel', 'bird', 'deer', 'rabbit', 'fox', 'wolf', 'butterfly', 'bee']
    
    def get_random_flora(self):
        if not self.game.flora:
            self.initialize_environment()
          
        if self.game.environment_type == "earthlike":
            seasonal_flora = {
                'spring': ['daisy', 'rose bush', 'buttercup', 'tulip'],
                'summer': ['oak tree', 'pine tree', 'fern', 'ivy'],
                'autumn': ['maple tree', 'oak tree', 'berry bush', 'moss'],
                'winter': ['pine tree', 'holly bush', 'evergreen', 'moss']
            }
            season_index = (self.game.day_count % 365) // 91
            seasons = ['spring', 'summer', 'autumn', 'winter']
            current_season = seasons[season_index]
            return random.choice(seasonal_flora.get(current_season, self.game.flora))
      
        return random.choice(self.game.flora)
    
    def get_random_fauna(self):
        if not self.game.fauna:
            self.initialize_environment()
          
        if self.game.environment_type == "earthlike":
            if self.game.weather == 'rainy':
                return random.choice(['frog', 'worm', 'snail', 'duck'])
            elif self.game.weather == 'stormy':
                return random.choice(['bird', 'bat', 'owl'])
      
        return random.choice(self.game.fauna)
    
    def has_environmental_elements(self):
        return self.game.environment_type not in ["space", "digital"]
    
    def change_weather(self):
        if random.random() < 0.1:
            weather_options = ['clear', 'rainy', 'stormy', 'windy', 'foggy']
            new_weather = random.choice(weather_options)
            if new_weather != self.game.weather:
                self.game.weather = new_weather
                if self.game.weather == 'rainy':
                    self.game.stress_level = min(100, self.game.stress_level + 5)
                elif self.game.weather == 'stormy':
                    self.game.stress_level = min(100, self.game.stress_level + 10)
                    self.game.energy_level = max(0, self.game.energy_level - 5)
                elif self.game.weather == 'windy':
                    self.game.energy_level = max(0, self.game.energy_level - 3)
                elif self.game.weather == 'foggy':
                    self.game.stress_level = min(100, self.game.stress_level + 3)