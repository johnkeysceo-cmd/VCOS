"""
Hook Engine - Template Library
Hook templates structured as objects
"""

from dataclasses import dataclass
from typing import List

@dataclass
class HookTemplate:
    """Hook template structure"""
    structure: str
    angle: str
    weight: float = 1.0  # Performance weight (updated by feedback trainer)
    
    def format(self, **kwargs) -> str:
        """Format template with provided values"""
        try:
            return self.structure.format(**kwargs)
        except KeyError as e:
            # Return structure if formatting fails
            return self.structure

# Hook templates categorized by emotional angle
TEMPLATES: List[HookTemplate] = [
    # Speed angle
    HookTemplate("I rebuilt {target} in {timeframe}", "speed", 1.0),
    HookTemplate("I built {target} in {timeframe}", "speed", 1.0),
    HookTemplate("Creating {target} in {timeframe}", "speed", 0.9),
    
    # Replacement angle
    HookTemplate("This replaces {target}.", "replacement", 1.0),
    HookTemplate("Why I stopped using {target}", "replacement", 0.95),
    HookTemplate("This is better than {target}", "replacement", 0.9),
    
    # Controversy angle
    HookTemplate("Why {target} isn't enough.", "controversy", 0.85),
    HookTemplate("{target} is outdated. Here's why.", "controversy", 0.9),
    HookTemplate("The problem with {target}", "controversy", 0.8),
    
    # Challenge angle
    HookTemplate("Can I build {target} in {timeframe}?", "challenge", 0.9),
    HookTemplate("I challenged myself to rebuild {target}", "challenge", 0.85),
    HookTemplate("Building {target} from scratch", "challenge", 0.9),
    
    # Secret angle
    HookTemplate("The secret to {target}", "secret", 0.8),
    HookTemplate("Nobody talks about {target}", "secret", 0.75),
    HookTemplate("Hidden feature in {target}", "secret", 0.7),
    
    # Authority angle
    HookTemplate("As a {role}, here's why {target}", "authority", 0.85),
    HookTemplate("After {count} years, I learned {target}", "authority", 0.8),
    
    # Proof angle
    HookTemplate("I tested {count} {target} tools", "proof", 0.9),
    HookTemplate("Here's proof {target} works", "proof", 0.85),
]

def get_templates_by_angle(angle: str) -> List[HookTemplate]:
    """Get all templates for a specific emotional angle"""
    return [t for t in TEMPLATES if t.angle == angle]

def get_all_templates() -> List[HookTemplate]:
    """Get all templates"""
    return TEMPLATES

def update_template_weight(template_structure: str, new_weight: float):
    """Update weight for a template (called by feedback trainer)"""
    for template in TEMPLATES:
        if template.structure == template_structure:
            template.weight = new_weight
            break
