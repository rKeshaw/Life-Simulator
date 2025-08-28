class PersonalitySystem:
    def __init__(self, game):
        self.game = game
    
    def analyze_emotional_tone(self):
        if not self.game.long_term_memory:
            return 'neutral'
  
        recent_text = ""
        for event in self.game.long_term_memory[-3:]:
            if isinstance(event, dict):
                recent_text += event['summary'] + " "
            else:
                recent_text += event + " "
  
        recent_text = recent_text.lower()
  
        tone_keywords = {
            'tense': ['attack', 'danger', 'threat', 'fear', 'enemy', 'fight'],
            'triumphant': ['victory', 'success', 'achievement', 'won', 'completed'],
            'sad': ['loss', 'death', 'failed', 'regret', 'goodbye', 'mourn'],
            'joyful': ['celebration', 'happy', 'laugh', 'friend', 'love', 'peace'],
            'mysterious': ['secret', 'unknown', 'puzzle', 'mystery', 'hidden']
        }
  
        for tone, keywords in tone_keywords.items():
            if any(keyword in recent_text for keyword in keywords):
                return tone
  
        return 'neutral'
    
    def get_mood_color(self):
        mood_colors = {
            'tense': self.game.BRIGHT_RED,
            'triumphant': self.game.BRIGHT_YELLOW,
            'sad': self.game.BRIGHT_BLUE,
            'joyful': self.game.BRIGHT_GREEN,
            'mysterious': self.game.BRIGHT_MAGENTA,
            'neutral': self.game.WHITE
        }
        return mood_colors.get(self.game.current_mood, self.game.WHITE)
    
    def adjust_personality_based_on_context(self):
        current_tone = self.analyze_emotional_tone()
        self.game.current_mood = current_tone
  
        tone_to_personality = {
            'tense': 'horror',
            'triumphant': 'epic',
            'sad': 'noir',
            'joyful': 'whimsical',
            'mysterious': 'noir',
            'neutral': 'default',
            'romantic': 'poetic',
            'technological': 'sci_fi'
        }
  
        new_personality = tone_to_personality.get(current_tone, 'default')
  
        should_change = False
        if new_personality != self.game.current_personality:
            if len(self.game.personality_history) == 0:
                should_change = True
            elif len(self.game.personality_history) < 2:
                should_change = True
            else:
                should_change = self.game.personality_history[-1] != new_personality
  
        if should_change:
            self.game.current_personality = new_personality
            self.game.personality_history.append(new_personality)
          
            if len(self.game.personality_history) > 5:
                self.game.personality_history.pop(0)
          
            personality_name = self.game.current_personality.upper()
            print(f"{self.game.DIM}[The narrative style shifts to {personality_name}...]{self.game.RESET}")