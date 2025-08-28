import time
import threading

class IdleSystem:
    def __init__(self, game):
        self.game = game
        self.idle_lock = threading.Lock()
        self.idle_timer = None
        self.stop_idle_check = False
        self.start_idle_timer()
    
    def start_idle_timer(self):
        with self.idle_lock:
            self.stop_idle_check = False
            if self.idle_timer is None or not self.idle_timer.is_alive():
                self.idle_timer = threading.Thread(target=self.idle_check_loop)
                self.idle_timer.daemon = True
                self.idle_timer.start()
          
    def stop_idle_timer(self):
        with self.idle_lock:
            self.stop_idle_check = True
            if self.idle_timer is not None and self.idle_timer.is_alive():
                self.idle_timer.join(timeout=3.0)
                if self.idle_timer.is_alive():
                    print("[Warning] Idle timer thread did not shut down gracefully")
            self.idle_timer = None
  
    def idle_check_loop(self):
        check_interval = max(0.1, getattr(self.game, 'idle_check_interval', 1))
        idle_threshold = max(1, getattr(self.game, 'idle_threshold', 5))
        
        while not self.stop_idle_check:
            try:
                time.sleep(check_interval)
              
                if not getattr(self.game, 'is_waiting_for_input', False):
                    continue
                  
                current_time = time.time()
                last_activity = getattr(self.game, 'last_activity_time', current_time)
                
                # FIX 3: Handle edge cases in time calculation
                time_diff = current_time - last_activity
                
                # Skip if time difference is invalid (clock changes, etc.)
                if time_diff <= 0 or time_diff < idle_threshold:
                    continue
                
                # FIX 4: Add reasonable upper limit to prevent extreme values
                max_idle_hours = 168  # 1 week maximum
                hours_passed = max(1, min(max_idle_hours, int(time_diff / 60)))  # Your accelerated time
                
                if hours_passed < 1:
                    hours_passed = 1
              
                self.simulate_idle_time(hours_passed)
                self.game.last_activity_time = current_time
                
            except Exception as e:
                # FIX 5: Better error handling in loop
                print(f"[Warning] Idle check loop error: {e}")
                time.sleep(5)  # Wait before retrying
 
    # In idle.py, implement the direct approach:

    def simulate_idle_time(self, hours_passed: int):
        # Get the core context - the player's original character description
        character_context = getattr(self.game, 'character_description', 'An adventurer')
        if not character_context or not character_context.strip():
            character_context = 'An adventurer'
        if len(character_context) > 500:
            character_context = character_context[:500] + "..."
            
        # Get recent events for additional context
        recent_context = self._get_recent_context()
        
        prompt = f"""
        CRITICAL CONTEXT - NEVER FORGET THIS:
        THE PLAYER AND THEIR WORLD ARE: {character_context}
        
        THIS DEFINES EVERYTHING ABOUT THE WORLD AND WHAT IS POSSIBLE.
        
        RECENT CONTEXT:
        {recent_context}
        
        INSTRUCTIONS:
        - The player has been inactive for {hours_passed} hours of in-game time
        - Simulate what happens during this time from their perspective
        - MOST IMPORTANT: Never mentions the word game or NPC. This is real life and the people are real, they exist with their own stories, dreams and plans.
        - ALSO IMPORTANT: Don't directly mention how much time has passed. Weave it in the argument so that it seems seamless.
        - EVERY SINGLE DETAIL must be consistent with the player's nature and world
        - If the player is a god, show cosmic events, divine phenomena, universal workings
        - If the player is in space, show space phenomena, orbital mechanics, cosmic events
        - If the player is digital, show data flows, system processes, virtual environments
        - DO NOT include earthly phenomena like sunrises, animals, or weather unless explicitly appropriate
        - The player is observing events unfold around them
        - Keep events mundane and logical for their reality
        - Write in second person present tense
        
        NARRATIVE OF EVENTS DURING IDLE TIME:
        """
        
        try:
            completion = self.game.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=250
            )
            narrative = completion.choices[0].message.content.strip()
            
            # Store memory and update stats
            self.game.long_term_memory.append({
                'day': self.game.day_count,
                'summary': f"Idle period: {narrative[:50]}...",
                'sensory_snippet': narrative
            })
            
            self.game.energy_level = min(100, self.game.energy_level + (10 * hours_passed))
            self.game.stress_level = max(0, self.game.stress_level - (5 * hours_passed))
            self.game.action_count = 0
            
            if hours_passed >= 24:
                self.game.day_count += 1
                
            # Return the narrative instead of printing it
            return f"~ Time passes... ~\n{narrative}\n~ A new day has dawned. ~" if hours_passed >= 24 else f"~ Time passes... ~\n{narrative}"
                
        except ConnectionError as e:
            return f"Connection lost to the realm of possibilities. Check your network.\n[Debug] Network error: {e}"
        except TimeoutError as e:
            return f"The cosmic forces are slow to respond. Try again in a moment.\n[Debug] Timeout error: {e}"
        except Exception as e:
            error_type = type(e).__name__
            if "auth" in str(e).lower() or "key" in str(e).lower():
                return f"The ancient powers reject your credentials. Check your API configuration.\n[Debug] {error_type}: {e}"
            elif "rate" in str(e).lower() or "limit" in str(e).lower():
                return f"You've drawn too much power too quickly. Wait a moment before trying again.\n[Debug] {error_type}: {e}"
            else:
                return f"The world seems to pause as reality stutters.\n[Debug] {error_type}: {e}"

    def _get_recent_context(self):
        """Get a brief summary of recent events"""
        if not hasattr(self.game, 'long_term_memory') or not self.game.long_term_memory:
            return "No recent events"
        
        recent_events = []
        try:
            for event in self.game.long_term_memory[-3:]:
                if isinstance(event, dict):
                    # Safe access to summary with fallback
                    summary = event.get('summary', 'Unknown event')
                    # Limit individual event length
                    if len(summary) > 100:
                        summary = summary[:100] + "..."
                    recent_events.append(summary)
                elif event is not None:
                    # Convert to string but limit length
                    event_str = str(event)
                    if len(event_str) > 100:
                        event_str = event_str[:100] + "..."
                    recent_events.append(event_str)
        except Exception as e:
            print(f"[Debug] Error building context: {e}")
            return "Recent events unclear"
        
        if not recent_events:
            return "No recent events"
            
        context = "Recent events: " + " | ".join(recent_events)
        
        # FIX 11: Limit total context length to prevent API issues
        if len(context) > 500:
            context = context[:500] + "..."
            
        return context