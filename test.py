# test_energy_stress.py (fixed to account for stress impact)
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from memory import MemorySystem
import json
from unittest.mock import patch

class MockGame:
    def __init__(self):
        self.energy_level = 100
        self.stress_level = 0
        self.action_count = 0
        self.global_reputation = 50
        self.reputation_history = []
        self.day_count = 1
        self.long_term_memory = []
        self.character_memory = {}
        self.auth_system = MockAuth()
        self.cloud_memory = MockCloudMemory()
        self.npc_system = MockNpcSystem()
        
        # Create a proper mock for the OpenAI client
        self.client = MockOpenAIClient()

class MockAuth:
    def is_authenticated(self):
        return False

class MockCloudMemory:
    def store_memory(self, memory_type, data, importance_score):
        return True

class MockNpcSystem:
    pass

class MockOpenAIClient:
    """Proper mock for the OpenAI client"""
    class Chat:
        class Completions:
            def create(self, model, messages, temperature, response_format):
                # Create a mock response that matches the expected format
                response_data = {
                    "importance_score": 8, 
                    "memory_type": "plot_event", 
                    "summary": "Test event", 
                    "energy_impact": 5, 
                    "stress_impact": 3, 
                    "relationship_impact": 2
                }
                
                class MockMessage:
                    content = json.dumps(response_data)
                
                class MockChoice:
                    message = MockMessage()
                
                class MockResponse:
                    choices = [MockChoice()]
                
                return MockResponse()
        
        completions = Completions()
    
    chat = Chat()

# Mock the random.randint to return a fixed value for predictable testing
@patch('random.randint')
def test_energy_stress_impact(mock_randint):
    # Make randint return 10 when called
    mock_randint.return_value = 10
    
    game = MockGame()
    memory_system = MemorySystem(game)
    
    initial_energy = game.energy_level
    initial_stress = game.stress_level
    initial_reputation = game.global_reputation
    
    analysis = memory_system.score_and_store_event("test action", "test response")
    
    # Check that energy and stress were updated
    assert game.energy_level == initial_energy - 5, f"Expected {initial_energy - 5}, got {game.energy_level}"
    assert game.stress_level == initial_stress + 3, f"Expected {initial_stress + 3}, got {game.stress_level}"
    
    # Calculate expected reputation: initial - stress_loss + relationship_impact
    # stress_loss is 10 (from our mock), relationship_impact is 2
    expected_reputation = initial_reputation - 10 + 2
    assert game.global_reputation == expected_reputation, f"Expected {expected_reputation}, got {game.global_reputation}"
    
    assert game.action_count == 1
    
    print("✅ Energy/stress impact test passed!")

if __name__ == "__main__":
    test_energy_stress_impact()