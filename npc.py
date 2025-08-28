import random
from behavior_tree import BehaviorTree, Selector, Sequence, Condition, Action

class EatAction(Action):
    def __init__(self, npc_name):
        self.npc_name = npc_name
        
    def execute(self, agent):
        print(f"{self.npc_name} eats.")
        agent['hunger'] = 0
        return 'success'

class IdleAction(Action):
    def __init__(self, npc_name):
        self.npc_name = npc_name
        
    def execute(self, agent):
        print(f"{self.npc_name} idles.")
        return 'success'

class NpcSystem:
    def __init__(self, game):
        self.game = game
    
    def generate_npc_personality(self, npc_name: str) -> dict:
        personality_traits = {
            'openness': random.uniform(0, 1),
            'conscientiousness': random.uniform(0, 1),
            'extraversion': random.uniform(0, 1),
            'agreeableness': random.uniform(0, 1),
            'neuroticism': random.uniform(0, 1),
            'boldness': random.uniform(0, 1),
            'traditionalism': random.uniform(0, 1),
        }

        descriptor = []
        if personality_traits['agreeableness'] < 0.3:
            descriptor.append("reserved")
        elif personality_traits['agreeableness'] > 0.7:
            descriptor.append("friendly")
        
        if personality_traits['neuroticism'] > 0.7:
            descriptor.append("sensitive")
        elif personality_traits['neuroticism'] < 0.3:
            descriptor.append("composed")
        
        if personality_traits['boldness'] > 0.7:
            descriptor.append("bold")
        elif personality_traits['boldness'] < 0.3:
            descriptor.append("cautious")
        
        personality_traits['description'] = " ".join(descriptor) if descriptor else "balanced"

        personality_traits['bt'] = BehaviorTree(
            Selector([
                Sequence([
                    Condition(lambda agent: agent.get('hunger', 0) > 50),
                    EatAction(npc_name)
                ]),
                IdleAction(npc_name)
            ])
        )

        return personality_traits
    
    def get_npc_reaction(self, npc_name: str, action: str, relationship_level: int) -> str:
        if npc_name not in self.game.npc_personalities:
            return "neutral"
      
        personality = self.game.npc_personalities[npc_name]
  
        inappropriate_keywords = ['kiss', 'touch', 'grab', 'steal', 'attack', 'threaten', 'insult']
        action_lower = action.lower()
        is_inappropriate = any(keyword in action_lower for keyword in inappropriate_keywords)
  
        if 'touch' in action_lower or 'kiss' in action_lower:
            if self.game.cultural_norms['personal_space'] > 0.7:
                is_inappropriate = True
            elif self.game.cultural_norms['personal_space'] < 0.4:
                is_inappropriate = False
  
        if is_inappropriate:
            if personality['agreeableness'] > 0.8 and relationship_level > 50:
                return "accept"
            elif personality['agreeableness'] < 0.3 or relationship_level < -20:
                return "reject"
            else:
                return "reject"
  
        if personality['agreeableness'] > 0.7 and relationship_level > 30:
            return "enthusiastic"
        elif personality['agreeableness'] < 0.4 or relationship_level < 0:
            return "reluctant"
        else:
            return "neutral"
    
    def get_cultural_context(self) -> str:
        norms = []
        if self.game.cultural_norms['personal_space'] > 0.7:
            norms.append("People value their personal space and maintain distance in interactions.")
        elif self.game.cultural_norms['personal_space'] < 0.4:
            norms.append("People are comfortable with close proximity and physical contact.")
      
        if self.game.cultural_norms['formality'] > 0.7:
            norms.append("Social interactions tend to be formal and follow established protocols.")
        elif self.game.cultural_norms['formality'] < 0.4:
            norms.append("Social interactions are casual and informal.")
      
        if self.game.cultural_norms['directness'] > 0.7:
            norms.append("Communication is direct and blunt.")
        elif self.game.cultural_norms['directness'] < 0.4:
            norms.append("Communication is indirect and subtle.")
      
        return " ".join(norms)
    
    def npc_intervention(self, npc_name: str, action: str) -> str:
        personality = self.game.npc_personalities.get(npc_name, {'boldness': 0.5, 'agreeableness': 0.5})
  
        if personality['boldness'] < 0.6:
            return None
      
        prompt = f"""
    The NPC {npc_name} is witnessing inappropriate behavior from the player: {action}
    Based on {npc_name}'s personality, generate their intervention response.
    {npc_name} is described as: {personality.get('description', 'balanced')}
  
    Write a brief, in-character response where {npc_name} intervenes or objects to the player's behavior.
    """
  
        try:
            completion = self.game.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=100
            )
            return completion.choices[0].message.content.strip()
        except:
            return None
    
    def get_relationship_desc(self, level: int) -> str:
        if level > 80:
            return "Soulmate"
        elif level > 60:
            return "Close Friend"
        elif level > 40:
            return "Friend"
        elif level > 20:
            return "Acquaintance"
        elif level > 0:
            return "Positive"
        elif level == 0:
            return "Neutral"
        elif level > -20:
            return "Unfriendly"
        elif level > -40:
            return "Rival"
        elif level > -60:
            return "Enemy"
        else:
            return "Archenemy"
    
    def attempt_apology(self, npc_name: str, apology: str) -> str:
        if npc_name not in self.game.relationships:
            return f"You don't know anyone named {npc_name}."
  
        relationship = self.game.relationships[npc_name]
        personality = self.game.npc_personalities.get(npc_name, {'agreeableness': 0.5, 'neuroticism': 0.5})
  
        base_chance = personality['agreeableness'] * 0.5 + min(1, max(0, relationship['level'] / 100)) * 0.5
        acceptance_chance = base_chance * (1 - personality['neuroticism'] * 0.3)
  
        if random.random() < acceptance_chance:
            repair_amount = int(20 * personality['agreeableness'])
            relationship['level'] = min(100, relationship['level'] + repair_amount)
            return f"{npc_name} accepts your apology. The relationship has improved slightly."
        else:
            return f"{npc_name} does not accept your apology. They need more time to forgive you."
    
    def generate_npc_activity(self, npc_name: str, last_interaction_day: int) -> str:
        if self.game.day_count - last_interaction_day < 2:
            return ""
        if random.random() > 0.3:
            return ""
        context = f"""
    Generate exactly one sentence about what {npc_name} has been doing off-screen since Day {last_interaction_day}. It is now Day {self.game.day_count}.
    Be realistic, mundane, and brief. Integrate naturally with the established world. Remember, NPCs also have their life.
    Examples: "He mentions he's been repairing his roof." "She looks tired from long nights at the forge."
    IMPORTANT: Output ONLY the one sentence. Do not use quotes or prefix it with anything. Do not use example from this, make it creative but real.
    """
        try:
            completion = self.game.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": context}],
                temperature=0.8,
                max_tokens=30
            )
            activity = completion.choices[0].message.content.strip()
            activity = activity.replace('"', '').strip()
            if activity.endswith('.'):
                return f" {activity}"
            else:
                return f" {activity}."
        except:
            return ""
    
    def npc_initiates_interaction(self):
        if random.random() > self.game.npc_initiative_chance:
            return None
        if not self.game.relationships:
            return None
        npc_name = random.choice(list(self.game.relationships.keys()))
        data = self.game.relationships[npc_name]
        level = data['level']
        relation_desc = self.get_relationship_desc(level)
        reputation_desc = self.get_reputation_desc(self.game.global_reputation)
  
        context = self.game.memory_system.build_context_memory()
        status = self.game.ai_response_system.get_hidden_status_context()
        prompt = f"""
    The person named {npc_name} is initiating an interaction with the player. Based on the current world state, recent events, player's relationship history and his reputation in the society, generate a brief reason for why they are approaching the player now.
    The player's relationship with {npc_name} is currently {relation_desc} (level: {level}) and has (repuation: {reputation_desc}).
    Write this in the style of the game: as a direct quote from {npc_name}, followed by a brief description of their actions or demeanor.
    Keep it to one or two sentences. Do not continue the conversation beyond the initiation.
    NEVER refer to characters as NPCs - they are all real people with their own lives.
  
Current World State:
{context}
{status}
Initiation from {npc_name}:
    """
        try:
            completion = self.game.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=100
            )
            initiation_text = completion.choices[0].message.content.strip()
            return f"{npc_name} approaches you. {initiation_text}"
        except Exception as e:
            print(f"{self.game.RED}Failed to generate NPC initiation: {e}{self.game.RESET}")
            return None
    
    def get_reputation_desc(self, level: int) -> str:
        if level > 80:
            return "Heroic"
        elif level > 60:
            return "Respected"
        elif level > 40:
            return "Neutral"
        elif level > 20:
            return "Questionable"
        else:
            return "Notorious"
    
    def get_reputation_reaction(self):
        if self.game.global_reputation > 75:
            return "People often smile and nod respectfully as you pass."
        elif self.game.global_reputation > 50:
            return "Most people treat you with neutral courtesy."
        elif self.game.global_reputation > 25:
            return "You notice some suspicious glances and hushed conversations when you enter a room."
        else:
            return "People actively avoid making eye contact, and shopkeepers seem suddenly busy when you approach."