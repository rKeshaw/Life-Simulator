# Life Simulator

**Life Simulator** is an immersive, narrative-driven simulation game designed in Python. It leverages advanced AI (LLMs) to generate narrative responses and simulate a consistently logical, interactive world. The project supports both CLI and GUI (Tkinter) interfaces, multiplayer cloud saves (via Supabase), dynamic memory management, and deep character/world simulation.

**Note: This project is actively being developed and is still a work in progress. Features and APIs may change.**

---

## Features

- **Narrative AI Simulation**: Player actions are interpreted and responded to by an AI system that maintains world, character, and narrative consistency using LLMs (like GPT-4o-mini).
- **RPG-like World**: The world adapts to your character description, with variable settings (fantasy, sci-fi, noir, etc.), weather, flora, fauna, NPCs, and events.
- **NPCs with Real Personalities**: Non-player characters have behavior trees, personalities, memory, and social logic. They can react, initiate interaction, hold grudges or friendships, and act autonomously.
- **Memory & Event System**: Both short-term and long-term memories are tracked, influencing the world's logic and narrative. Important memories and world facts are considered in all AI responses.
- **Cloud Integration**: Optional cloud saves, user authentication, and cross-device syncing using [Supabase](https://supabase.io).
- **GUI (Tkinter)**: A modern, styled graphical interface for easier gameplay, including login/signup, save/load management, and colored narrative text.
- **Idle Simulation**: The world advances even when the player is inactive, with logical, context-aware time skips.
- **Personality/Style Adaptation**: The narrative style adapts to recent game events and player mood (noir, epic, poetic, horror, etc.).
- **Commands & Creativity**: Players can issue creative commands to write poems, code, stories, or make/compose/paint things in-game.
- **Robust Save/Load**: Both local and cloud save/load support, with automatic backup and old save cleanup.
- **ANSI Color Output**: Both CLI and GUI versions support colored text for enhanced immersion.

---

## How It Works

1. **Start the Game**: Players describe their character and world, or select a random scenario.
2. **Interact Naturally**: Type what you'd like to do; the AI interprets your input and simulates the world's response.
3. **Evolving World**: The world, NPCs, and events change based on your actions, memories, and relationships.
4. **Save & Resume**: Progress can be saved locally or in the cloud (requires Supabase credentials).

---

## Installation

### Prerequisites

- Python 3.8+
- [Supabase account & project](https://supabase.io) (for cloud saves)
- OpenAI-compatible API endpoint (default: [llm7.io](https://api.llm7.io/v1) for GPT-4o-mini)
- `pip install openai supabase dotenv tkinter` (Tkinter is included with most Python installations)

### Clone the Repository

```bash
git clone https://github.com/rKeshaw/Life-Simulator.git
cd Life-Simulator
```

### Environment Variables

Create a `.env` file in the project root:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_or_service_key
```

> If you do not wish to use cloud saves, you can skip the Supabase setup—your saves will be local only.

---

## Usage

### Start (CLI Version)

```bash
python game.py
```

### Start (GUI Version)

```bash
python gui.py
```

---

## Gameplay

- Type actions or commands naturally, e.g., `go to the market`, `talk to Sarah`, `write a poem about the rain`.
- Special commands:  
  - `help` – Show command help  
  - `undo` – Undo last action (if temporal energy available)  
  - `reflect` – Moment of self-reflection  
  - `personality` – Show/change narrative style  
  - `save` – Save your progress  
  - `quit` – Exit the game  
  - Creative commands: `write`, `create`, `compose`, `paint`, `code`, etc.

---

## Project Structure

```
.
├── ai_response.py      # AI narrative/response engine
├── auth_system.py      # User authentication (Supabase)
├── behavior_tree.py    # NPC behavior logic
├── cloud_memory.py     # Memory management, cloud/local
├── colors.py           # ANSI color codes
├── environment.py      # Dynamic world/environment
├── game.py             # Main CLI game loop
├── gui.py              # Tkinter GUI
├── idle.py             # Idle simulation logic
├── memory.py           # Memory/context engine
├── npc.py              # NPC management and logic
├── personality.py      # Narrative tone/personality
├── save_load.py        # Save/load functions
└── requirements.txt    # Python dependencies
```

---

## Advanced Features

- **Supabase Integration**: For multiplayer and persistent cloud saves, configure your Supabase URL and key in `.env`.
- **API Customization**: You can point the LLM API to your own endpoint or adjust the model used by editing `game.py` and related files.
- **Extensible**: Add new narrative styles, NPC behaviors, events, or environments by editing the respective modules.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Credits

- [OpenAI](https://openai.com/) for API compatibility
- [Supabase](https://supabase.com/) for cloud backend
- Inspired by AI-powered narrative games and simulation systems

---

## Contributing

Pull requests and suggestions are welcome! Please open issues or submit PRs for improvements, bug fixes, or new features.

---

**Enjoy living infinite lives—every story is unique!**
