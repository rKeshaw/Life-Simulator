import json
import random

class MemorySystem:
    def __init__(self, game):
        self.game = game
    
    def score_and_store_event(self, user_action: str, ai_response: str):
        scoring_prompt = [
          {"role": "system", "content": (
            "You are an intelligent memory manager. Analyze the 'Action' and 'Narrative' below. "
            "Respond ONLY with a valid JSON object containing these exact keys:\n"
            "- 'importance_score' (1-10)\n"
            "- 'memory_type' (choose one: 'character_growth', 'world_building', 'relationship', 'plot_event')\n"
            "- 'summary' (a concise one-sentence description)\n"
            "- 'energy_impact' (1-10, how draining was this?)\n"
            "- 'stress_impact' (-5 to +10, negative for relaxing, positive for stressful)\n"
            "- 'relationship_impact' (-10 to +10, negative for harmful, positive for beneficial interactions with others)\n"
            "EXTREMELY IMPORTANT: Only output the JSON object. Do not add any other text, explanations, or formatting."
        )},
          {"role": "user", "content": f"Action: {user_action}\nNarrative: {ai_response}"}
        ]
        try:
          completion = self.game.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=scoring_prompt,
            temperature=0.2,
            response_format={"type": "json_object"}
          )
          response_text = completion.choices[0].message.content
          response_text = response_text.strip()
          # if '```' in response_text and response_text.count('```') >= 2:
          #   response_text = response_text.split('```')[1]
          # if response_text.startswith('json'):
          #   response_text = response_text[4:]
          # response_text = response_text.strip()

          if '```json' in response_text:
              start = response_text.find('```json') + 7
              end = response_text.find('```', start)
              if end != -1:
                  response_text = response_text[start:end]
        
          start_index = response_text.find('{')
          end_index = response_text.rfind('}') + 1
          if start_index != -1 and end_index != 0:
            json_string = response_text[start_index:end_index]
            analysis = json.loads(json_string)
          else:
            raise json.JSONDecodeError("No JSON found", response_text, 0)
        
          self.game.energy_level = max(0, self.game.energy_level - analysis.get('energy_impact', 3))
          self.game.stress_level = max(0, min(100, self.game.stress_level + analysis.get('stress_impact', 0)))
          self.game.action_count += 1
       
          # Scale reputation loss to stress impact:
          if analysis.get('stress_impact', 0) > 0:
              rep_loss = min(analysis.get('stress_impact', 0) * 2, 10)  # Cap at 10
              self.game.global_reputation = max(0, self.game.global_reputation - rep_loss) 
                    
          importance = analysis.get('importance_score', 0)
          memory_type = analysis.get('memory_type', 'event')
          summary = analysis.get('summary', 'Unknown event')
          relationship_impact = analysis.get('relationship_impact', 0)
        
          if relationship_impact != 0:
            self.game.global_reputation = max(0, min(100, self.game.global_reputation + relationship_impact))
            self.game.reputation_history.append({
                'day': self.game.day_count,
                'change': relationship_impact,
                'reason': summary,
                'new_level': self.game.global_reputation
            })
       
          if importance >= 7:
            sensory_snippet = ' '.join(ai_response.split()[:7])
            memory_data = {
                'day': self.game.day_count,
                'summary': summary,
                'sensory_snippet': sensory_snippet
            }
            self.game.long_term_memory.append(memory_data)
            
            if self.game.auth_system.is_authenticated():
              self.game.cloud_memory.store_memory("long_term_memory", memory_data, importance)
          
          if memory_type == 'character_growth' and importance >= 5:
            if 'character_growth' not in self.game.character_memory:
              self.game.character_memory['character_growth'] = []
            self.game.character_memory['character_growth'].append(summary)

            if self.game.auth_system.is_authenticated():
                self.game.cloud_memory.store_memory("character_growth", {
                    'growth': summary,
                    'day': self.game.day_count
                }, importance)
            
          if memory_type == 'relationship' and self.game.auth_system.is_authenticated():
                self.game.cloud_memory.store_memory("relationship", {
                    'summary': summary,
                    'day': self.game.day_count,
                    'impact': relationship_impact
                }, importance)
            
          if self.game.energy_level < 15 and self.game.action_count > 3:
            self.game.auto_rest()
     
        except json.JSONDecodeError as e:
          print(f"[Debug] Failed to parse AI memory analysis as JSON. Response was: {response_text}")
          analysis = {'importance_score': 3, 'memory_type': 'plot_event', 'summary': 'An event occurred.', 'energy_impact': 3, 'stress_impact': 0, 'relationship_impact': 0}
        except Exception as e:
          print(f"[Debug] Memory analysis failed completely: {e}")
          analysis = {'importance_score': 3, 'memory_type': 'plot_event', 'summary': 'An event occurred.', 'energy_impact': 3, 'stress_impact': 0, 'relationship_impact': 0}
        return analysis
    
    def build_context_memory(self):
        context = []
        if self.game.character_description:
          context.append(f"CHARACTER CORE: {self.game.character_description}")
        if self.game.character_memory.get('character_growth'):
          recent_growth = self.game.character_memory['character_growth'][-3:]
          context.append(f"CHARACTER DEVELOPMENT: {' | '.join(recent_growth)}")
        if self.game.world_facts:
          context.append(f"WORLD PHYSICS/RULES: {' | '.join(self.game.world_facts[-5:])}")
        if self.game.long_term_memory:
            recent_events = []
            for item in self.game.long_term_memory[-8:]:
                if isinstance(item, dict):
                    day = item.get('day', 'Unknown')
                    summary = item.get('summary', 'No summary')
                    recent_events.append(f"• [Day {day}] {summary}")
                else:
                    recent_events.append(f"• {item}")
            context.append(f"KEY STORY EVENTS:\n{chr(10).join(recent_events)}")
        
        if self.game.relationships:
            active_relationships = []
            for char, data in list(self.game.relationships.items())[-5:]:
                interactions = data['interactions']
                level = data['level']
                if interactions:
                    last_interaction = interactions[-1]
                    # Try to extract day from interaction text more carefully
                    last_day = self.game.day_count  # Default to current day
                    
                    if 'Day' in last_interaction:
                        try:
                            # Extract the number after "Day"
                            day_part = last_interaction.split('Day')[1].split()[0]
                            # Remove any non-numeric characters (like colons)
                            day_str = ''.join(filter(str.isdigit, day_part))
                            if day_str:  # Add this check!
                                last_day = int(day_str)
                            else:
                                last_day = self.game.day_count  # Use current day as fallback
                        except (IndexError, ValueError):
                            # If parsing fails, use the current day
                            last_day = self.game.day_count
                    
                    off_screen_activity = self.game.npc_system.generate_npc_activity(char, last_day)
                else:
                    last_interaction = "No recent contact"
                    off_screen_activity = ""
              
                relation_desc = self.game.npc_system.get_relationship_desc(level)
                active_relationships.append(f"{char} ({relation_desc}): {last_interaction}{off_screen_activity}")
            if active_relationships:
                context.append(f"RELATIONSHIPS: {chr(10).join(active_relationships)}")
              
        if self.game.world_events:
          recent_rumors = []
          for event_id, event_data in list(self.game.world_events.items())[-3:]:
              recent_rumors.append(f"Rumor: {event_data['current_rumor']}")
          context.append(f"RECENT RUMORS: {' | '.join(recent_rumors)}")
          
          if self.game.auth_system.is_authenticated():
            try:
                cloud_memories = self.game.cloud_memory.get_memories(limit=5, min_importance=7)
                if cloud_memories:
                    cloud_context = []
                    for memory in cloud_memories:
                        if memory and 'data' in memory:
                            memory_data = memory['data']
                            if isinstance(memory_data, dict) and 'summary' in memory_data:
                                cloud_context.append(f"• {memory_data['summary']}")
                    if cloud_context:
                        context.append(f"CLOUD MEMORIES: {chr(10).join(cloud_context)}")
            except Exception as e:
                print(f"[Debug] Failed to load cloud memories for context: {e}")
                
        return "\n\n".join(context)
    
    def hint_at_memory(self, user_input, importance_score):
        if importance_score >= 5 and random.random() < 0.5:
            print(f"\n\033[90m[You get the distinct feeling this moment will stay with you.]\033[0m")
            
            if self.game.auth_system.is_authenticated() and importance_score >= 8:
                self.game.cloud_memory.store_memory("memory_hint", {
                    'action': user_input,
                    'importance': importance_score,
                    'day': self.game.day_count
                }, importance_score)
        elif importance_score >= 9:
            print(f"\n\033[93m[This moment etches itself into your soul, a memory you know will define you.]\033[0m")
    
    def add_to_short_term_memory(self, role: str, content: str):
        self.game.short_term_memory.append({"role": role, "content": content})
        
        # Store important short-term memories in cloud
        if self.game.auth_system.is_authenticated() and role == "assistant":
            # Only store AI responses that seem significant
            if len(content) > 100 and any(word in content.lower() for word in ['important', 'crucial', 'remember', 'never forget']):
                self.game.cloud_memory.store_memory("short_term_memory", {
                    'role': role,
                    'content': content[:200] + "..." if len(content) > 200 else content,
                    'day': self.game.day_count
                }, importance_score=4)
                
    def load_memories_from_cloud(self):
        """Load important memories from cloud storage when user signs in"""
        if not self.game.auth_system.is_authenticated():
            return
            
        try:
            # Load long-term memories
            cloud_long_term = self.game.cloud_memory.get_memories("long_term_memory", limit=20)
            for memory in cloud_long_term:
                if memory and 'data' in memory:
                    memory_data = memory['data']
                    if memory_data not in self.game.long_term_memory:
                        self.game.long_term_memory.append(memory_data)
            
            # Load character growth
            cloud_growth = self.game.cloud_memory.get_memories("character_growth", limit=10)
            if 'character_growth' not in self.game.character_memory:
                self.game.character_memory['character_growth'] = []
            
            for memory in cloud_growth:
                if memory and 'data' in memory and 'growth' in memory['data']:
                    growth = memory['data']['growth']
                    if growth not in self.game.character_memory['character_growth']:
                        self.game.character_memory['character_growth'].append(growth)
            
            print("Cloud memories loaded successfully.")
            
        except Exception as e:
            print(f"Failed to load cloud memories: {e}")