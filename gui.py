import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from collections import deque
import re
from game import IntelligentLifeSim

def strip_ansi_codes(text):
    """Remove ANSI escape sequences from text"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

class LifeSimGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LifeSim: Natural Intelligence Edition")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2c3e50")
        
        self.game = IntelligentLifeSim()
        self.current_frame = None
        
        # Create container for all frames
        self.container = ttk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Configure styles
        self.configure_styles()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Show the login screen
        self.show_frame(LoginScreen)
        
    def show_frame(self, frame_class, *args):
        """Destroy current frame and show new one"""
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = frame_class(self.container, self, *args)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        
    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure main frame style
        style.configure("Main.TFrame", background="#2c3e50")
        
        # Configure button styles
        style.configure(
            "TButton", 
            background="#3498db", 
            foreground="white",
            font=("Segoe UI", 10),
            padding=(10, 5)
        )
        
        style.map(
            "TButton",
            background=[("active", "#2980b9"), ("pressed", "#1c638e")],
            relief=[("pressed", "sunken"), ("!pressed", "raised")]
        )
        
        # Configure label styles
        style.configure(
            "TLabel",
            background="#2c3e50",
            foreground="white",
            font=("Segoe UI", 10)
        )
        
        # Configure entry styles
        style.configure(
            "TEntry",
            fieldbackground="#34495e",
            foreground="white",
            font=("Segoe UI", 10),
            padding=(5, 5)
        )
        
        # Configure frame styles
        style.configure(
            "TLabelframe",
            background="#2c3e50",
            foreground="white"
        )
        
        style.configure(
            "TLabelframe.Label",
            background="#2c3e50",
            foreground="#3498db",
            font=("Segoe UI", 10, "bold")
        )
        
    def on_closing(self):
        """Handle window closing event"""
        if hasattr(self, 'game') and self.game.game_active:
            # Check if we're in the game screen
            if isinstance(self.current_frame, GameScreen):
                # Ask if user wants to save
                save = messagebox.askyesno(
                    "Save Before Exit", 
                    "Would you like to save your story one last time?"
                )
                
                if save:
                    # Save the game
                    game_state = self.game.get_game_state()
                    game_state['save_name'] = "Final_save"
                    if self.game.cloud_memory.store_memory("game_save", game_state, importance_score=10):
                        messagebox.showinfo("Saved", "Your story has been saved.")
                    else:
                        messagebox.showwarning("Save Failed", "Failed to save your story.")
                
                # Show farewell message
                messagebox.showinfo("Farewell", "Your story ends here. But it was a life!")
            
            # Sign out if authenticated
            if self.game.auth_system.is_authenticated():
                self.game.auth_system.sign_out()
        
        self.root.destroy()
        
    def run(self):
        self.root.mainloop()

class LoginScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(style="Main.TFrame")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main title
        title_label = ttk.Label(
            self, 
            text="🌟 LifeSim: Multi-Player Edition", 
            font=("Segoe UI", 24, "bold"),
            foreground="white"
        )
        title_label.pack(pady=50)
        
        # Subtitle
        subtitle_label = ttk.Label(
            self,
            text="Live any life you can imagine",
            font=("Segoe UI", 14),
            foreground="#bdc3c7"
        )
        subtitle_label.pack(pady=(0, 50))
        
        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=20)
        
        # Auth buttons
        signup_btn = ttk.Button(
            button_frame, 
            text="Sign Up", 
            width=20,
            command=self.show_signup
        )
        signup_btn.pack(pady=10)
        
        signin_btn = ttk.Button(
            button_frame, 
            text="Sign In", 
            width=20,
            command=self.show_signin
        )
        signin_btn.pack(pady=10)
        
        guest_btn = ttk.Button(
            button_frame, 
            text="Play as Guest", 
            width=20,
            command=self.play_as_guest
        )
        guest_btn.pack(pady=10)
        
        # Footer
        footer_label = ttk.Label(
            self,
            text="Your progress will be saved to the cloud when signed in",
            font=("Segoe UI", 10),
            foreground="#7f8c8d"
        )
        footer_label.pack(side=tk.BOTTOM, pady=20)
        
    def show_signup(self):
        SignupDialog(self.controller)
        
    def show_signin(self):
        SigninDialog(self.controller)
        
    def play_as_guest(self):
        # Reinitialize the game for guest play
        self.controller.game = IntelligentLifeSim()
        self.controller.game.game_state = "playing"
        
        # Show a message about guest mode
        messagebox.showinfo("Guest Mode", "Playing as guest. Your progress will be stored locally only.")
        
        # Move to the life selection screen
        self.controller.show_frame(LifeSelectionScreen)

class AuthDialog(tk.Toplevel):
    def __init__(self, parent, controller, title, auth_type):
        super().__init__(parent)
        self.controller = controller
        self.auth_type = auth_type
        
        self.title(title)
        self.geometry("400x300")
        self.configure(bg="#2c3e50")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        ttk.Label(
            self, 
            text=self.title(), 
            font=("Segoe UI", 16, "bold"),
            foreground="white"
        ).pack(pady=20)
        
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=20, padx=40, fill=tk.X)
        
        # Email field
        ttk.Label(form_frame, text="Email:", foreground="white").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(form_frame, width=30)
        self.email_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Password field
        ttk.Label(form_frame, text="Password:", foreground="white").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(form_frame, width=30, show="•")
        self.password_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Username field (only for signup)
        if self.auth_type == "signup":
            ttk.Label(form_frame, text="Username:", foreground="white").grid(row=2, column=0, sticky=tk.W, pady=5)
            self.username_entry = ttk.Entry(form_frame, width=30)
            self.username_entry.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Submit button
        submit_btn = ttk.Button(
            self, 
            text="Submit" if self.auth_type == "signup" else "Sign In",
            command=self.submit
        )
        submit_btn.pack(pady=20)
        
        # Focus on email field
        self.email_entry.focus()
        
    def submit(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not email or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
            
        if self.auth_type == "signup":
            username = self.username_entry.get().strip()
            if not username:
                messagebox.showerror("Error", "Please enter a username")
                return
                
            success = self.controller.game.auth_system.sign_up(email, password, username)
        else:
            success = self.controller.game.auth_system.sign_in(email, password)
            
        if success:
            self.destroy()
            self.controller.show_frame(LifeSelectionScreen)
        else:
            # Clear all fields on error
            self.email_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            
            # For signup, clear username too
            if self.auth_type == "signup":
                self.username_entry.delete(0, tk.END)
                
            messagebox.showerror("Error", "Authentication failed. Please check your credentials and try again.")

class SignupDialog(AuthDialog):
    def __init__(self, controller):
        super().__init__(controller.root, controller, "Create Account", "signup")

class SigninDialog(AuthDialog):
    def __init__(self, controller):
        super().__init__(controller.root, controller, "Sign In", "signin")

class LifeSelectionScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()
        
    def setup_ui(self):
        # Main content frame
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        # Title
        title_label = ttk.Label(
            content_frame, 
            text="How would you like to start your life?",
            font=("Segoe UI", 18, "bold"),
            foreground="white"
        )
        title_label.pack(pady=(0, 30))
        
        # Options frame
        options_frame = ttk.Frame(content_frame)
        options_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        # Option buttons
        new_life_btn = ttk.Button(
            options_frame, 
            text="Start New Life", 
            width=20,
            command=self.start_new_life
        )
        new_life_btn.pack(pady=10)
        
        load_life_btn = ttk.Button(
            options_frame, 
            text="Load Saved Life", 
            width=20,
            command=self.show_saved_lives
        )
        load_life_btn.pack(pady=10)
        
        random_btn = ttk.Button(
            options_frame, 
            text="Random Scenario", 
            width=20,
            command=self.random_scenario
        )
        random_btn.pack(pady=10)
        
        # Saved games panel
        self.saved_frame = ttk.LabelFrame(
            content_frame, 
            text="Saved Lives",
            padding=10
        )
        self.saved_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Load saved games
        self.load_saved_games()
        
    def load_saved_games(self):
        # Clear existing widgets
        for widget in self.saved_frame.winfo_children():
            widget.destroy()
            
        # Get saved games from cloud memory
        if self.controller.game.auth_system.is_authenticated():
            saves = self.controller.game.cloud_memory.get_memories("game_save")
            
            if not saves:
                ttk.Label(
                    self.saved_frame, 
                    text="No saved games found",
                    foreground="gray"
                ).pack(pady=20)
                return
                
            # Create a canvas for scrolling
            canvas = tk.Canvas(self.saved_frame, bg="#34495e")
            scrollbar = ttk.Scrollbar(self.saved_frame, orient=tk.VERTICAL, command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Add saved games
            for i, save in enumerate(saves):
                save_data = save['data']
                save_name = save_data.get('save_name', f"Unnamed Save {i+1}")
                save_day = save_data.get('day_count', 1)
                
                save_btn = ttk.Button(
                    scrollable_frame,
                    text=f"{save_name} (Day {save_day})",
                    width=30,
                    command=lambda s=save_data: self.load_saved_game(s)
                )
                save_btn.pack(pady=5, padx=10)
                
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
    def start_new_life(self):
        # Show dialog for character description
        self.get_character_description("new")
        
    def show_saved_lives(self):
        # Already shown in the panel
        pass
        
    def random_scenario(self):
        scenarios = [
            "I am a detective in 1940s noir city with the ability to see the last moments of murder victims",
            "I am a space station engineer in 2087 who discovers the AI is becoming sentient",
            "I am a medieval alchemist who accidentally created a potion that lets me talk to animals",
            "I am a college student who finds out my roommate is a time traveler",
            "I am a small-town librarian who inherits a bookstore that contains portals to fictional worlds"
        ]
        
        import random
        self.controller.game.character_description = random.choice(scenarios)
        self.start_game()
        
    def get_character_description(self, mode):
        dialog = tk.Toplevel(self)
        dialog.title("Describe Your Life")
        dialog.geometry("600x400")
        dialog.configure(bg="#2c3e50")
        dialog.transient(self.controller.root)
        dialog.grab_set()
        
        ttk.Label(
            dialog, 
            text="Describe yourself and your world:",
            font=("Segoe UI", 12),
            foreground="white"
        ).pack(pady=20)
        
        text_area = scrolledtext.ScrolledText(
            dialog, 
            width=70, 
            height=15,
            wrap=tk.WORD
        )
        text_area.pack(pady=10, padx=20)
        
        if mode == "load" and self.controller.game.character_description:
            text_area.insert(tk.END, self.controller.game.character_description)
        
        def submit():
            self.controller.game.character_description = text_area.get("1.0", tk.END).strip()
            dialog.destroy()
            self.start_game()
            
        ttk.Button(dialog, text="Start Life", command=submit).pack(pady=10)
        
    def load_saved_game(self, save_data):
        # Extract the actual game state from the save data
        game_state = save_data.get('game_state', {})
        
        if not game_state:
            messagebox.showerror("Error", "Invalid save file: missing game state")
            return
            
        # Set the game state
        self.controller.game.set_game_state(game_state)
        
        # Start the game directly without showing the character description dialog
        self.start_game()
        
    def start_game(self):
        self.controller.show_frame(GameScreen)

class GameScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()
        
        # Initialize idle tracking
        self.last_activity_time = time.time()
        self.idle_check_interval = 30000  # Check every 30 seconds
        self.idle_threshold = 120  # 2 minutes of inactivity
        
        # Start the idle checker
        self.check_idle()
        
        # Start the game
        self.start_game()
        
    def setup_ui(self):
        # Configure grid weights for proper resizing
        self.grid_columnconfigure(0, weight=3)  # Conversation area gets 3/4 of space
        self.grid_columnconfigure(1, weight=1)  # Status area gets 1/4 of space
        self.grid_rowconfigure(0, weight=1)     # Conversation area
        self.grid_rowconfigure(1, weight=0)     # Input area (fixed height)
        
        # Conversation area
        self.conversation_frame = ttk.Frame(self)
        self.conversation_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.conversation_frame.grid_columnconfigure(0, weight=1)
        self.conversation_frame.grid_rowconfigure(0, weight=1)
        
        self.conversation = scrolledtext.ScrolledText(
            self.conversation_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg="#2c3e50",
            fg="#ecf0f1",
            font=("Segoe UI", 11),
            padx=10,
            pady=10
        )
        self.conversation.grid(row=0, column=0, sticky="nsew")
        
        # Configure text tags
        self.conversation.tag_config("user", foreground="#e74c3c")
        self.conversation.tag_config("game", foreground="#3498db")
        self.conversation.tag_config("system", foreground="#2ecc71")
        self.conversation.tag_config("error", foreground="#e74c3c")
        self.conversation.tag_config("npc", foreground="#f39c12")
        
        # Setup ANSI colors
        self.setup_ansi_colors()
        
        # Input area
        input_frame = ttk.Frame(self)
        input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.input_entry = ttk.Entry(input_frame, font=("Segoe UI", 11))
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.input_entry.bind("<Return>", self.process_input)
        
        self.send_btn = ttk.Button(input_frame, text="Send", command=self.process_input)
        self.send_btn.grid(row=0, column=1)
        
        # Status panel - wider to show all stats clearly
        status_frame = ttk.LabelFrame(self, text="Status", padding=10, width=250)
        status_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(0, 10), pady=10)
        status_frame.grid_propagate(False)  # Prevent frame from shrinking
        
        # Configure status frame grid
        status_frame.grid_columnconfigure(1, weight=1)
        
        self.status_labels = {}
        status_items = [
            ("Day", "day_count"),
            ("Energy", "energy_level"),
            ("Stress", "stress_level"),
            ("Reputation", "global_reputation"),
            ("Mood", "current_mood")
        ]
        
        for i, (label, attr) in enumerate(status_items):
            ttk.Label(status_frame, text=f"{label}:", font=("Segoe UI", 10, "bold")).grid(
                row=i, column=0, sticky="w", pady=2, padx=(0, 5)
            )
            self.status_labels[attr] = ttk.Label(
                status_frame, 
                text="", 
                foreground="#3498db",
                font=("Segoe UI", 10)
            )
            self.status_labels[attr].grid(row=i, column=1, sticky="w", pady=2)
        
        # Add a separator
        ttk.Separator(status_frame, orient="horizontal").grid(
            row=len(status_items), column=0, columnspan=2, sticky="ew", pady=10
        )
        
        # Add relationships section
        ttk.Label(
            status_frame, 
            text="Relationships:", 
            font=("Segoe UI", 10, "bold")
        ).grid(row=len(status_items)+1, column=0, columnspan=2, sticky="w", pady=(5, 2))
        
        self.relationships_frame = ttk.Frame(status_frame)
        self.relationships_frame.grid(row=len(status_items)+2, column=0, columnspan=2, sticky="nsew")
        
        # Configure relationships frame to expand
        status_frame.grid_rowconfigure(len(status_items)+2, weight=1)
        
        # Focus on input
        self.input_entry.focus()
        
    def setup_ansi_colors(self):
        """Setup ANSI color mapping to Tkinter tags"""
        # Define ANSI color to Tkinter color mapping
        ansi_colors = {
            '30': 'black',           # Black
            '31': '#e74c3c',         # Red
            '32': '#2ecc71',         # Green
            '33': '#f39c12',         # Yellow
            '34': '#3498db',         # Blue
            '35': '#9b59b6',         # Magenta
            '36': '#1abc9c',         # Cyan
            '37': '#ecf0f1',         # White
            '39': '#ecf0f1',         # Default (white)
            '90': '#7f8c8d',         # Bright Black (Gray)
            '91': '#e74c3c',         # Bright Red
            '92': '#2ecc71',         # Bright Green
            '93': '#f1c40f',         # Bright Yellow
            '94': '#3498db',         # Bright Blue
            '95': '#9b59b6',         # Bright Magenta
            '96': '#1abc9c',         # Bright Cyan
            '97': '#ffffff',         # Bright White
            '0': '#ecf0f1',          # Reset to default
        }
        
        # Create tags for each color
        for code, color in ansi_colors.items():
            self.conversation.tag_config(f"ansi_{code}", foreground=color)
        
        # Default tag
        self.conversation.tag_config("ansi_default", foreground="#ecf0f1")
    
    def parse_ansi_codes(self, text):
        """Parse ANSI color codes and apply Tkinter tags"""
        import re
        
        # Pattern to match ANSI escape sequences
        pattern = re.compile(r'\033\[([0-9;]*)m')
        
        # Split text by ANSI codes
        parts = pattern.split(text)
        
        # The first part is before any ANSI codes
        current_tags = ["ansi_default"]
        
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # This is text content
                if part:
                    # Apply current tags to this text
                    self.conversation.insert(tk.END, part, tuple(current_tags))
            else:
                # This is an ANSI code
                codes = part.split(';')
                for code in codes:
                    if code in ['0']:
                        # Reset to default
                        current_tags = ["ansi_default"]
                    elif code in ['1']:
                        # Bold - we'll just use a brighter color
                        if "ansi_31" in current_tags:
                            current_tags = ["ansi_91"]  # Bright red
                        elif "ansi_32" in current_tags:
                            current_tags = ["ansi_92"]  # Bright green
                        elif "ansi_33" in current_tags:
                            current_tags = ["ansi_93"]  # Bright yellow
                        elif "ansi_34" in current_tags:
                            current_tags = ["ansi_94"]  # Bright blue
                        elif "ansi_35" in current_tags:
                            current_tags = ["ansi_95"]  # Bright magenta
                        elif "ansi_36" in current_tags:
                            current_tags = ["ansi_96"]  # Bright cyan
                        elif "ansi_37" in current_tags:
                            current_tags = ["ansi_97"]  # Bright white
                        else:
                            current_tags = ["ansi_97"]  # Default to bright white
                    elif code in ['30', '31', '32', '33', '34', '35', '36', '37',
                                 '90', '91', '92', '93', '94', '95', '96', '97']:
                        current_tags = [f"ansi_{code}"]
    
    def check_idle(self):
        """Check if the player has been idle for too long"""
        current_time = time.time()
        idle_time = current_time - self.last_activity_time
        
        if idle_time >= self.idle_threshold and not self.controller.game.is_waiting_for_input:
            # Use the correct method from your IdleSystem
            hours_passed = max(1, int(idle_time / 60))  # Convert seconds to hours (your accelerated time)
            idle_response = self.controller.game.idle_system.simulate_idle_time(hours_passed)
            
            if idle_response:
                self.add_message(idle_response, "system")
            
            # Reset the timer
            self.last_activity_time = time.time()
        
        # Schedule the next check
        self.after(self.idle_check_interval, self.check_idle)
        
    def update_relationships(self):
        """Update the relationships display"""
        # Clear existing widgets
        for widget in self.relationships_frame.winfo_children():
            widget.destroy()
            
        if not self.controller.game.relationships:
            ttk.Label(
                self.relationships_frame, 
                text="No relationships yet",
                foreground="gray",
                font=("Segoe UI", 9)
            ).pack(pady=5)
            return
            
        # Show top 5 relationships
        for npc_name, data in list(self.controller.game.relationships.items())[:5]:
            level = data.get('level', 0)
            desc = self.controller.game.npc_system.get_relationship_desc(level)
            
            relationship_text = f"{npc_name}: {desc}"
            ttk.Label(
                self.relationships_frame, 
                text=relationship_text,
                foreground="#2ecc71",
                font=("Segoe UI", 9)
            ).pack(anchor="w", pady=1)
        
    def start_game(self):
        # Check if this is a loaded game with existing state
        is_loaded_game = (
            len(self.controller.game.long_term_memory) > 0 or
            len(self.controller.game.short_term_memory) > 0 or
            self.controller.game.day_count > 1
        )
        
        if not is_loaded_game:
            # This is a new game, so send the initial prompt
            setup_prompt = f"I want to live this life: '{self.controller.game.character_description}'. Begin my story."
            self.controller.game.memory_system.add_to_short_term_memory("user", setup_prompt)
            
            # Get opening response in a thread to avoid blocking
            thread = threading.Thread(target=self.get_opening_response)
            thread.daemon = True
            thread.start()
        else:
            # This is a loaded game, so display a welcome back message
            # and show the last few messages from memory
            self.add_message("Welcome back to your life!", "system")
            
            # Display recent messages from short-term memory
            for memory in list(self.controller.game.short_term_memory)[-5:]:
                role = memory.get('role', 'unknown')
                content = memory.get('content', '')
                
                if role == 'user':
                    self.add_message(f"> {content}", "user")
                elif role == 'assistant':
                    self.add_message(content, "game")
            
            # Update the status panel
            self.update_status()
        
    def get_opening_response(self):
        opening_response = self.controller.game.ai_response_system.get_ai_response(
            self.controller.game.character_description
        )
        self.controller.game.memory_system.add_to_short_term_memory("assistant", opening_response)
        self.controller.game.memory_system.score_and_store_event(
            self.controller.game.character_description, opening_response
        )
        
        # Update UI in main thread
        self.after(0, self.add_message, opening_response, "game")
        self.after(0, self.update_status)
        
    def add_message(self, message, sender):
        self.conversation.config(state=tk.NORMAL)
        
        if sender == "user":
            self.conversation.insert(tk.END, f"> {message}\n\n", "user")
        elif sender == "system":
            self.conversation.insert(tk.END, f"{message}\n\n", "system")
        else:
            # Parse ANSI codes for game messages
            self.conversation.insert(tk.END, "\n")
            self.parse_ansi_codes(message)
            self.conversation.insert(tk.END, "\n\n")
            
        self.conversation.see(tk.END)
        self.conversation.config(state=tk.DISABLED)
        
    def handle_special_commands(self, user_input):
        """Handle special commands that shouldn't go to the LLM"""
        input_lower = user_input.lower()
        
        if input_lower == 'help':
            help_text = self.controller.game.show_help()
            self.add_message(help_text, "system")
            return True
            
        elif input_lower == 'reflect':
            reflection = self.controller.game.get_status_report()
            self.add_message(reflection, "system")
            return True
            
        elif input_lower == 'undo':
            result = self.controller.game.undo_last_action()
            self.add_message(result, "system")
            return True
            
        elif input_lower == 'personality':
            current = self.controller.game.current_personality
            desc = self.controller.game.ai_personalities[current]['description']
            response = f"Current narrative style: {current.upper()}\nDescription: {desc}"
            self.add_message(response, "system")
            return True
            
        elif input_lower == 'reputation':
            reputation_desc = self.controller.game.npc_system.get_reputation_desc(
                self.controller.game.global_reputation
            )
            reaction = self.controller.game.npc_system.get_reputation_reaction()
            response = f"Your reputation: {self.controller.game.global_reputation}/100 ({reputation_desc})\n{reaction}"
            self.add_message(response, "system")
            return True
            
        elif input_lower.startswith('apologize to '):
            parts = user_input[13:].split(' ', 1)
            if len(parts) < 2:
                self.add_message("Usage: apologize to [name] [your apology]", "error")
                return True
                
            npc_name = parts[0]
            apology = parts[1] if len(parts) > 1 else ""
            result = self.controller.game.npc_system.attempt_apology(npc_name, apology)
            self.add_message(result, "system")
            return True
        
        elif input_lower.startswith('save'):
            # Handle save command
            save_name = user_input[5:].strip()
            if not save_name:
                save_name = f"Save_{time.strftime('%Y%m%d_%H%M%S')}"
                
            game_state = self.controller.game.get_game_state()
            
            # Create save data with both metadata and the actual game state
            save_data = {
                'save_name': save_name,
                'day_count': self.controller.game.day_count,
                'timestamp': time.time(),
                'game_state': game_state  # This contains the actual game data
            }
            
            if self.controller.game.cloud_memory.store_memory("game_save", save_data, importance_score=10):
                self.add_message(f"Game saved as '{save_name}'.", "system")
            else:
                self.add_message("Failed to save game.", "error")
            return True
        
        elif input_lower == 'quit':
            # Handle quit command
            self.controller.on_closing()
            return True
            
        # Check for creative commands (these should go to LLM)
        creative_verbs = ['write ', 'create ', 'compose ', 'make ', 'code ', 'paint ', 'draw ', 'sing ', 'build ', 'design ']
        if any(input_lower.startswith(verb) for verb in creative_verbs):
            return False
            
        return False
        
    def process_input(self, event=None):
        user_input = self.input_entry.get().strip()
        if not user_input:
            return
            
        # Update last activity time
        self.last_activity_time = time.time()
        
        self.input_entry.delete(0, tk.END)
        self.add_message(user_input, "user")
        
        # Check for special commands
        if self.handle_special_commands(user_input):
            return  # Don't send to LLM if it's a special command
        
        # Process in a separate thread
        thread = threading.Thread(target=self.process_game_input, args=(user_input,))
        thread.daemon = True
        thread.start()
        
    def process_game_input(self, user_input):
        try:
            # Process through game systems
            self.controller.game.memory_system.add_to_short_term_memory("user", user_input)
            ai_response = self.controller.game.ai_response_system.get_ai_response(user_input)
            self.controller.game.memory_system.add_to_short_term_memory("assistant", ai_response)
            
            analysis = self.controller.game.memory_system.score_and_store_event(user_input, ai_response)
            enhanced_response = self.controller.game.ai_response_system.enhance_output(ai_response)
            
            # Update UI in main thread
            self.after(0, self.add_message, enhanced_response, "game")
            self.after(0, self.update_status)
            
        except Exception as e:
            self.after(0, self.add_message, f"Error: {str(e)}", "error")
            
    def update_status(self):
        for attr, label in self.status_labels.items():
            value = getattr(self.controller.game, attr, "")
            if isinstance(value, (int, float)):
                value = str(value)
            label.config(text=value.capitalize() if isinstance(value, str) else str(value))
        
        # Update relationships
        self.update_relationships()

if __name__ == "__main__":
    app = LifeSimGUI()
    app.run()