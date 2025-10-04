"""Goal model for tracking savings and financial goals."""
from typing import Optional, Dict


class Goal:
    """Represents a financial goal or savings target."""
    
    def __init__(self, goal_id: Optional[int] = None,
                 name: str = "",
                 target_amount: float = 0.0,
                 current_amount: float = 0.0,
                 deadline: Optional[str] = None,
                 icon: str = "flag",
                 color: str = "#4CAF50",
                 notes: str = "",
                 completed: bool = False):
        self.id = goal_id
        self.name = name
        self.target_amount = target_amount
        self.current_amount = current_amount
        self.deadline = deadline
        self.icon = icon
        self.color = color
        self.notes = notes
        self.completed = completed
        
    def get_percentage_complete(self) -> float:
        """Calculate percentage of goal completed."""
        if self.target_amount == 0:
            return 0
        return (self.current_amount / self.target_amount) * 100
    
    def get_remaining_amount(self) -> float:
        """Get remaining amount to reach goal."""
        return max(0, self.target_amount - self.current_amount)
        
    def to_dict(self) -> Dict:
        """Convert goal to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'deadline': self.deadline,
            'icon': self.icon,
            'color': self.color,
            'notes': self.notes,
            'completed': self.completed
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Goal':
        """Create goal from dictionary."""
        return Goal(
            goal_id=data.get('id'),
            name=data.get('name', ''),
            target_amount=data.get('target_amount', 0.0),
            current_amount=data.get('current_amount', 0.0),
            deadline=data.get('deadline'),
            icon=data.get('icon', 'flag'),
            color=data.get('color', '#4CAF50'),
            notes=data.get('notes', ''),
            completed=data.get('completed', False)
        )

