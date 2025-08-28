class BehaviorTree:
    def __init__(self, root):
        self.root = root
    
    def tick(self, agent):  # Run BT for an NPC/agent
        return self.root.execute(agent)

class Node:  # Base base
    def execute(self, agent):
        raise NotImplementedError

class Sequence(Node):  # All children must succeed
    def __init__(self, children):
        self.children = children
    
    def execute(self, agent):
        for child in self.children:
            if child.execute(agent) != 'success':
                return 'failure'
        return 'success'

class Selector(Node):  # First success wins
    def __init__(self, children):
        self.children = children
    
    def execute(self, agent):
        for child in self.children:
            result = child.execute(agent)
            if result == 'success':
                return 'success'
        return 'failure'

class Condition(Node):  # Check condition
    def __init__(self, func):  # func: lambda agent: bool
        self.func = func
    
    def execute(self, agent):
        return 'success' if self.func(agent) else 'failure'

class Action(Node):  # Perform action
    def __init__(self, func):  # func: lambda agent: 'success' or 'failure'
        self.func = func
    
    def execute(self, agent):
        return self.func(agent)