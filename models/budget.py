"""Budget model for tracking spending limits by category."""
from typing import Optional, Dict


class Budget:
    """Represents a budget for a specific category and period."""
    
    def __init__(self, budget_id: Optional[int] = None,
                 category_id: Optional[int] = None,
                 amount: float = 0.0,
                 period: str = "Monthly",
                 start_date: Optional[str] = None,
                 end_date: Optional[str] = None,
                 alert_percentage: float = 80.0,
                 spent: float = 0.0):
        self.id = budget_id
        self.category_id = category_id
        self.amount = amount
        self.period = period  # Weekly, Monthly, Yearly, Custom
        self.start_date = start_date
        self.end_date = end_date
        self.alert_percentage = alert_percentage
        self.spent = spent
        
    def get_percentage_used(self) -> float:
        """Calculate percentage of budget used."""
        if self.amount == 0:
            return 0
        return (self.spent / self.amount) * 100
    
    def is_over_budget(self) -> bool:
        """Check if budget is exceeded."""
        return self.spent > self.amount
    
    def should_alert(self) -> bool:
        """Check if alert threshold is reached."""
        return self.get_percentage_used() >= self.alert_percentage
        
    def to_dict(self) -> Dict:
        """Convert budget to dictionary."""
        return {
            'id': self.id,
            'category_id': self.category_id,
            'amount': self.amount,
            'period': self.period,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'alert_percentage': self.alert_percentage,
            'spent': self.spent
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Budget':
        """Create budget from dictionary."""
        return Budget(
            budget_id=data.get('id'),
            category_id=data.get('category_id'),
            amount=data.get('amount', 0.0),
            period=data.get('period', 'Monthly'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            alert_percentage=data.get('alert_percentage', 80.0),
            spent=data.get('spent', 0.0)
        )

