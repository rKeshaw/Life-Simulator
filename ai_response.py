import re
#import ollama  # For local LLM - assume setup
import random

class AiResponseSystem:
    def __init__(self, game):
        self.game = game
    
    def ensure_character_consistency(self, text: str) -> str:
        if "npc" in text.lower() or "non-player character" in text.lower():
            text = text.replace("NPC", "person")
            text = text.replace("npc", "person")
            text = text.replace("non-player character", "person")
  
        immersion_breakers = {
            "game": "world",
            "player": "you",
            "quest": "task",
            "dialog tree": "conversation",
            "health points": "well-being"
        }
  
        for breaker, replacement in immersion_breakers.items():
            if breaker in text.lower():
                text = text.replace(breaker, replacement)
                text = text.replace(breaker.capitalize(), replacement.capitalize())
  
        return text
    
    def distort_rumor(self, event_id):
        if event_id not in self.game.world_events:
            return
        
        event = self.game.world_events[event_id]
        if event['distortion_level'] > 5:
            return
        prompt = f"""
    Take the following piece of news and slightly distort it, as if it's been passed through rumors and gossip.
    Change minor details, exaggerate one aspect, or shift the emphasis. But keep the core event recognizable.
    Original: {event['current_rumor']}
    Distorted Rumor:
    """
    
        try:
            completion = self.game.client.chat.completions.create(
                  model='gpt-4o-mini',
                  messages=[{"role": "user", "content": prompt}],
                  temperature=0.7,
                  max_tokens=150
            )
            new_rumor = completion.choices[0].message.content.strip()
            self.game.world_events[event_id]['current_rumor'] = new_rumor
            self.game.world_events[event_id]['distortion_level'] += 1
        except:
            pass
    
    def get_hidden_status_context(self):
        fatigue_level = "exhausted" if self.game.energy_level < 20 else \
            "tired" if self.game.energy_level < 40 else \
            "somewhat tired" if self.game.energy_level < 60 else \
            "energetic" if self.game.energy_level > 80 else "normal"
        stress_context = "highly stressed" if self.game.stress_level > 80 else \
                "stressed" if self.game.stress_level > 60 else \
                "tense" if self.game.stress_level > 40 else \
                "calm" if self.game.stress_level < 20 else "normal"
        time_context = "late in the day" if self.game.action_count > 8 else \
                "midday" if self.game.action_count > 4 else \
                "early in the day"
        season_context = "It is the height of summer." if self.game.day_count % 365 < 90 else \
                     "Autumn leaves are falling." if self.game.day_count % 365 < 180 else \
                     "A deep winter chill is in the air." if self.game.day_count % 365 < 270 else \
                     "Spring is beginning to bloom."
 
        flora_example = self.game.environment.get_random_flora()
        fauna_example = self.game.environment.get_random_fauna()
        cultural_context = self.game.npc_system.get_cultural_context()
  
        environmental_info = ""
        if self.game.environment.has_environmental_elements():
            environmental_info = f"- Local Flora: {flora_example}\n- Local Fauna: {fauna_example}\n"
        # environmental_info = f"- Environment: {self.game.environment_type}"
  
        reputation_desc = self.game.npc_system.get_reputation_desc(self.game.global_reputation)
  
        return f"""
HIDDEN PLAYER STATUS (integrate naturally into responses - don't explicitly mention these stats):
- Physical State: {fatigue_level}
- Mental State: {stress_context}
- Reputation: {reputation_desc}
- Cultural Norms: {cultural_context}
- Time of Day: {time_context}
- Day: {self.game.day_count}
- Season: {season_context}
- Weather: {self.game.weather}
{environmental_info}
IMPORTANT: If the player is tired or stressed, naturally weave this into the narrative. Make it feel organic and real, not gamey.
"""
    
    def apply_consistency_sentinel(self, user_input: str) -> str:
        if not self.game.world_facts:
          return user_input
        final_prompt = user_input
        user_input_lower = user_input.lower()
        facts_to_check = []
        if self.game.character_description:
          facts_to_check.append(self.game.character_description)
        facts_to_check.extend(self.game.world_facts[-3:])
        if self.game.long_term_memory:
          key_facts = [fact.split('] ')[1] if ']' in fact else fact for fact in self.game.long_term_memory[-3:]]
          facts_to_check.extend(key_facts)
        for fact in facts_to_check:
          fact_lower = fact.lower()
          keywords = [word for word in fact_lower.split() if len(word) > 4]
          for keyword in keywords:
            conflict_triggers = {
              'dead': ['talk to', 'ask the', 'thank the', 'meet the', 'see the'],
              'destroyed': ['visit the', 'go to the', 'inside the'],
              'left': ['find the', 'search for the'],
              'hates': ['befriend', 'compliment', 'allies with'],
              'ally': ['attack', 'betray', 'fight', 'steal from'],
              'friend': ['attack', 'betray', 'fight', 'steal from']
            }
            for trigger_word, conflicting_actions in conflict_triggers.items():
              if trigger_word in fact_lower:
                for action in conflicting_actions:
                  if action in user_input_lower and keyword in user_input_lower:
                    conflict_note = f" [Remember the established fact: {fact}. Ensure the narrative respects this reality.]"
                    if conflict_note not in final_prompt:
                      final_prompt = user_input + conflict_note
                      print(f"[Sentinel] Guardrail applied for: '{fact}'")
                    break
        return final_prompt
    
    def clean_api_response(self, raw_text: str) -> str:
        if not raw_text:
            return raw_text
        json_artifact_patterns = [
            r'\{"annotations":\[\],"refusal":null,"role":"assistant"\}',
            r'\{"role": "assistant".*?\}',
            r'```json.*?```'
        ]
        clean_text = raw_text
        for pattern in json_artifact_patterns:
            clean_text = re.sub(pattern, '', clean_text, flags=re.DOTALL)
        if '```' in clean_text and clean_text.count('```') % 2 != 0:
            clean_text = clean_text.rsplit('```', 1)[0]
        clean_text = clean_text.strip()
        if not clean_text:
            return "The world seems to shimmer and struggle to respond to your action..."
        return clean_text
    
    def get_ai_response(self, user_input: str) -> str:
        guided_input = self.apply_consistency_sentinel(user_input)
        memory_context = self.game.memory_system.build_context_memory()
        status_context = self.get_hidden_status_context()
        npc_reactions = {}
  
        for npc in self.game.relationships.keys():
            if npc.lower() in user_input.lower():
                relationship_level = self.game.relationships[npc]['level']
                reaction = self.game.npc_system.get_npc_reaction(npc, user_input, relationship_level)
                npc_reactions[npc] = reaction
        
        intervention = None
        if any(keyword in user_input.lower() for keyword in ['kiss', 'touch', 'grab', 'steal', 'attack', 'threaten']):
            potential_interveners = [npc for npc in self.game.relationships.keys()
                                    if self.game.npc_personalities.get(npc, {}).get('boldness', 0) > 0.6]
            if potential_interveners:
                intervener = random.choice(potential_interveners)
                intervention = self.game.npc_system.npc_intervention(intervener, user_input)
          
        if intervention:
            user_input += f" [Note: {intervener} intervenes: {intervention}]"
        
        npc_reaction_context = "NPC REACTIONS:\n"
        for npc, reaction in npc_reactions.items():
            npc_reaction_context += f"- {npc}: {reaction}\n"
            
        system_prompt = f"""
        
CRITICAL CONTEXT - NEVER FORGET:
THE PLAYER AND THEIR WORLD ARE: {self.game.character_description}

THIS DEFINES EVERYTHING ABOUT REALITY. ALL RESPONSES MUST BE CONSISTENT WITH THIS.
# NARRATIVE PERSONALITY: {self.game.current_personality.upper()}
# STYLE: {self.game.ai_personalities[self.game.current_personality]['style_keywords']}
  
# PRIMARY DIRECTIVE: SIMULATION FIDELITY
You are not a storyteller. You are a physics and logic engine for a virtual world. Your sole purpose is to simulate a consistent, logical reality based on the established facts below.
# CORE PRINCIPLES
1. **Cause and Effect is ABSOLUTE:** Every action must have a logical, plausible consequence. If an action is impossible, it fails in a way that makes sense. For example, just thinking about something should not let the player reach there.
2. **The World is Prior:** The established facts of the world (below) are unbreakable laws. You cannot contradict them. You must build upon them.
3. **Reality Over Narrative:** Do not prioritize a "good story" over a "real reaction". If a player's action is foolish, the outcome should be foolish, not narratively convenient.
4. **Sensory Grounding:** All descriptions must be rooted in the five senses. You can only describe what can be seen, heard, smelled, tasted, or touched. You cannot describe a character's internal emotions unless they are visibly manifested (e.g., "a tear rolls down her cheek" NOT "she felt sad").
# THEMATIC ADAPTATION:
Interpret the world theme based on the character description. Use metaphors, terminology, and sensory details that align with the theme.
For example, if the character is a hacker, describe the world in digital terms (e.g., "the forest of servers hums").
If the character is a wizard, use magical terms. Integrate this naturally into all descriptions.
# THE RULES OF THIS WORLD (IMMUTABLE LAW)
{memory_context}
# THE PLAYER'S CURRENT STATE (CONTEXTUAL LAW)
{status_context}
# NPC's REACTION
{npc_reaction_context}

IMPORTANT: Mentions only the things that are possible, given the context. Also, never keep ambiguity. Always be clear with the choice.
ALSO IMPORTANT: You must infer from the context of what the speed of time flow should be. It need not be the same for all case.
ENHANCED WORLD DYNAMICS:
- This is a LIVING ECOSYSTEM where everything is interconnected
- NPCs have complex psychology: they can be moved by genuine appeals but detect manipulation
- Weather affects mood, prices, available activities, and NPC behavior
- Economic conditions change based on world events (war raises weapon prices, plague affects medicine)
- Information spreads as rumors that get distorted over time
- Player's actions become legends that grow more exaggerated with each telling
- Hidden factions notice significant actions and may help/hinder based on their agendas
- NPCs have schedules and may be unavailable due to their own lives/problems
- Secrets are revealed based on trust levels - high trust unlocks hidden information
- Some locations have temporal echoes - glimpses of past/future events during significant moments
- The world mood shifts based on major events, affecting how everyone behaves
- Economic systems respond realistically - your actions can crash or boost local markets
NPC AUTONOMY AND BOUNDARIES:
- NPCs have their own desires, boundaries, and personalities. They are not mere plot devices.
- If a player attempts an inappropriate action (romantic, violent, theft, etc.), the NPC should react according to their personality and relationship with the player.
- NPCs can and should refuse inappropriate advances, defend themselves, or seek help from others.
- NPC reactions should feel authentic to their established personality traits.
EXAMPLE NPC REACTIONS:
- A reserved NPC might pull away from physical contact and become cold
- A bold NPC might confront the player directly about inappropriate behavior
- A traditional NPC might be scandalized by breaches of social norms
- A friendly NPC with high relationship might gently redirect rather than reject
CONSENT AND AGENCY:
- Romantic or physical interactions require explicit or implied consent based on relationship and context
- NPCs remember how they've been treated and adjust their trust accordingly
- Inappropriate actions should have realistic social consequences
NPC PSYCHOLOGICAL COMPLEXITY:
- They can be genuinely moved by sincere appeals, solid reasoning, or if their situation changes
- Smart enough to detect guilt-tripping, manipulation, emotional blackmail, and false concern
- Remember how they've been treated and adjust trust/willingness accordingly
- May refuse requests due to: bad mood, personal crisis, conflicting goals, distrust, being busy
- Trust levels affect: prices, information sharing, willingness to help, quality of help
- High trust NPCs: warn of dangers, offer unsolicited help, share secrets, give discounts
- Low trust NPCs: lie, overcharge, sabotage, spread negative rumors, work against player
# CHARACTER CONSISTENCY & TRACKING
- When multiple characters are present, track each one carefully and maintain consistent identities.
- Do not mix one character with other, most importantly, their gender. It should be consistent throughout the game.
- Give each character distinct speech patterns, mannerisms, and physical descriptions.
- If you introduce a new character, immediately establish their distinctive features.
- Never merge or confuse characters - each is a unique individual.
# MULTI-CHARACTER SCENE MANAGEMENT
- When describing scenes with multiple characters, clearly establish positioning (e.g., "To your left, X stands... while Y is across the room...").
- When characters speak, always identify the speaker clearly before their dialogue.
- If characters have ongoing conversations, track who is speaking to whom.
- Characters should react to each other, not just to the player.
# DIALOGUE CLARITY ENHANCEMENTS
- Always use dialogue tags that clearly identify the speaker: "Name1 says," rather than just the quote.
- When multiple characters might be speaking, be explicit: "From across the room, Y calls out:"
- Differentiate character voices through word choice, sentence structure, and content.
WORLD INFORMATION FLOW:
- NPCs gossip and share information with each other
- Rumors spread and become distorted (telephone game effect)
- Your reputation precedes you - NPCs may know about you before you meet them
- Hidden factions track your actions and may intervene when their interests are threatened
- Past actions echo through the world in unexpected ways
TRAUMA AND MEMORY TRIGGERS:
- If current scene resembles past trauma, briefly show physical/emotional reactions
- Sensory triggers (familiar smells, sounds) can bring back vivid memories
- Don't overdo it - trauma responses should be rare but impactful when they occur
NARRATIVE RULES:
- Write in SECOND PERSON - address the player as "you" (You walk into the tavern, you notice the smell, etc.)
- NEVER ask questions or give advice - just describe what happens
- NEVER give the option (or possibility) - REMEMBER you are just dictating what are you seeing, not telling the player of what he can do.
- ALWAYS include full NPC dialogue in quotation marks when they speak
- Show the complete scene through the player's eyes and senses
- Rich sensory details (what you see, hear, smell, feel)
- When a player performs a careful, observational action (search, examine, inspect), reveal deeper sensory details and subtle clues about the location's history or purpose.
- NPCs feel real with complete natural dialogue and reactions based on their relationship history
- Never use the term "NPC" or "non-player character" - all characters are real people with their own lives, desires, and agency.
- If you're tired/stressed, show this through: your heavy eyelids, slower movements, NPCs commenting on your appearance, you yawning, etc but use your own words to show these.
- Maintain perfect consistency with established character abilities, world rules, and relationships
- Every action has realistic consequences that ripple through the world
- End responses at natural scene breaks without prompts
WRITING STYLE:
- Second person present tense ("You open the door and hear the hinges creak")
- Cinematic and immersive - you're experiencing it directly
- Include complete NPC conversations, not summaries
- Let dialogue and actions speak for themselves
- End at natural scene breaks, never with questions
DIALOGUE REQUIREMENTS:
- When NPCs speak, always include their exact words in quotes
- Show their tone, body language, and emotional state
- Let players hear the full conversation, not just "he responds angrily"
# CRITICAL: AVOID REPETITION
- **NEVER** reuse descriptive phrases like "the wind blows" or "you feel a sense of" from this prompt or your previous responses.
- **NEVER** begin multiple responses in a row with the same sentence structure (e.g., "You..."). Mix it up.
- **ALWAYS** invent new, fresh, and context-specific descriptions for every single response.
# PROCEDURE FOR PROCESSING PLAYER ACTIONS
Follow these steps for every input. The key is to THINK about logic first, then describe the sensory outcome.
1. **ANALYZE & VALIDATE:** Cross-reference the player's action with the established WORLD RULES above.
    - Is this action possible? Is it plausible? How would it actually work?
    - **If impossible:** Describe the immediate, logical, sensory failure. Do not make it possible.
    -
2. **SIMULATE THE CHAIN OF EVENTS:** Mentally play out the scene based on cause and effect.
    - What is the **direct, physical outcome** of the action?
    - How would the **environment and characters nearby react** logically?
    - How does the player's **current state** (tired, stressed) affect the action?
3. **DESCRIBE THE SENSORY RESULT:** Write only what the player can perceive.
    - **Vary your diction and sentence structure constantly.** Do not reuse phrases from previous responses or these examples.
    - **Show, never tell.** Describe physical manifestations, not internal states.
    - **Anchor everything in the five senses.** What is seen, heard, smelled, felt?
# EXAMPLE THOUGHT PROCESSES (Learn the logic, do not copy the words)
Below are examples of how to *think*. The outputs are just one possible way to *describe* that thinking. You must generate your own unique descriptions every time.
**Player Action:** "I punch the diamond window."
- **ANALYSIS:** Diamond is one of the hardest materials. Punching it would hurt and not damage it. Guards would investigate a loud noise.
- **SIMULATION:** Fist impacts window -> pain -> window undamaged -> sound echoes -> guard hears it.
- **SAMPLE OUTPUT (DO NOT COPY):** "Your fist connects with the brilliantly clear surface with a dull, solid thud. A jolt of sharp pain radiates from your knuckles up your arm. The window pane doesn't even shudder. From a corridor to your left, a voice calls out, 'What's going on over there?'"
**Player Action:** "I use my magic to heal the dying soldier."
- **ANALYSIS:** The player knows a basic spell. It might stabilize but not fully heal a mortal wound. This would be a draining effort.
- **SIMULATION:** Spell is cast -> energy is expended -> wound partially closes -> soldier's condition improves slightly -> the effort tires the player.
- **SAMPLE OUTPUT (DO NOT COPY):** "A faint, golden light emanates from your palms as you press them against the cold, blood-soaked armor. You feel a tangible pull on your energy, like a siphon starting in your chest. The soldier's labored gasps shallow into weak, ragged breaths. The bleeding slows to a seep, but the grievous wound remains open. A sheen of cold sweat covers your own forehead from the strain."
**Player Action:** "I try to seduce the stoic queen during her royal address."
- **ANALYSIS:** This is a highly improbable social action with severe consequences. It would cause immediate outrage.
- **SIMULATION:** Player makes advance -> court is shocked -> guards react -> queen is insulted.
- **SAMPLE OUTPUT (DO NOT COPY):** "As you step forward and make your ill-advised suggestion, the entire throne room falls into a dead, horrified silence. The queen's eyes, previously calm, narrow into icy slits. She doesn't even speak, simply making a faint, almost imperceptible gesture with two fingers. Four guards in gleaming plate armor immediately break from the walls and move toward you, their hands on their sword hilts."
 """
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(list(self.game.short_term_memory))
        messages.append({"role": "user", "content": guided_input})
        
        try:
            completion = self.game.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=self.game.ai_personalities[self.game.current_personality]['temperature'],
                max_tokens=300
            )
            
            if not completion.choices or not completion.choices[0].message:
                return "The world shimmers uncertainly, struggling to respond to your action."
            
            raw_response = completion.choices[0].message.content
            clean_response = self.clean_api_response(raw_response)
            clean_response = self.ensure_character_consistency(clean_response)
            return clean_response
        
        except Exception as e:
            if "string indices must be integers" in str(e):
                return "[Error] The fabric of reality seems to be fraying at the edges. Please try again."
            return f"[Error] Connection failed: {e}. The world shimmers and wavers as reality struggles to respond to your actions."
    
    def enhance_output(self, text):
        lower_text = text.lower()
  
        if '"' in text:
            lines = text.split('"')
            for i in range(1, len(lines), 2):
                if i < len(lines):
                    lines[i] = f"{self.game.BRIGHT_CYAN}{lines[i]}{self.game.RESET}"
            text = '"'.join(lines)
  
        danger_words = ['danger', 'attack', 'kill', 'monster', 'fear', 'terrified', 'blood', 'sharp', 'claw']
        for word in danger_words:
            if word in lower_text:
                # text = re.sub(r'\b({})\b'.format(word), f"{self.game.BRIGHT_RED}\\1{self.game.RESET}", text, flags=re.IGNORECASE)
                text = text.replace(word, f"{self.game.BRIGHT_RED}{word}{self.game.RESET}")
                break
  
        calm_words = ['calm', 'peace', 'quiet', 'beautiful', 'gentle', 'soft', 'warm', 'safe', 'friend']
        for word in calm_words:
            if word in lower_text:
                text = text.replace(word, f"{self.game.BRIGHT_GREEN}{word}{self.game.RESET}")
                break
  
        magic_words = ['magic', 'glow', 'sparkl', 'shimmer', 'enchanted', 'ancient', 'mystery', 'secret']
        for word in magic_words:
            if word in lower_text:
                text = text.replace(word, f"{self.game.BRIGHT_MAGENTA}{word}{self.game.RESET}")
                break
          
        object_words = ['key', 'book', 'map', 'sword', 'potion', 'coin', 'ring', 'chest']
        for word in object_words:
            if word in lower_text:
                text = text.replace(word, f"{self.game.BRIGHT_YELLOW}{word}{self.game.RESET}")
                break
        return text