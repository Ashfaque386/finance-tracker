"""Debt model for tracking money lent or borrowed."""
from typing import Optional, Dict


class Debt:
    """Represents debt (money lent to others or borrowed from others)."""
    
    def __init__(self, debt_id: Optional[int] = None,
                 debt_type: str = "Borrowed",
                 person_name: str = "",
                 amount: float = 0.0,
                 amount_paid: float = 0.0,
                 date: Optional[str] = None,
                 due_date: Optional[str] = None,
                 interest_rate: float = 0.0,
                 notes: str = "",
                 settled: bool = False):
        self.id = debt_id
        self.debt_type = debt_type  # Borrowed (liability), Lent (receivable)
        self.person_name = person_name
        self.amount = amount
        self.amount_paid = amount_paid
        self.date = date
        self.due_date = due_date
        self.interest_rate = interest_rate
        self.notes = notes
        self.settled = settled
        
    def get_remaining_amount(self) -> float:
        """Get remaining amount to be paid/received."""
        return max(0, self.amount - self.amount_paid)
    
    def get_percentage_paid(self) -> float:
        """Calculate percentage paid."""
        if self.amount == 0:
            return 0
        return (self.amount_paid / self.amount) * 100
        
    def to_dict(self) -> Dict:
        """Convert debt to dictionary."""
        return {
            'id': self.id,
            'debt_type': self.debt_type,
            'person_name': self.person_name,
            'amount': self.amount,
            'amount_paid': self.amount_paid,
            'date': self.date,
            'due_date': self.due_date,
            'interest_rate': self.interest_rate,
            'notes': self.notes,
            'settled': self.settled
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Debt':
        """Create debt from dictionary."""
        return Debt(
            debt_id=data.get('id'),
            debt_type=data.get('debt_type', 'Borrowed'),
            person_name=data.get('person_name', ''),
            amount=data.get('amount', 0.0),
            amount_paid=data.get('amount_paid', 0.0),
            date=data.get('date'),
            due_date=data.get('due_date'),
            interest_rate=data.get('interest_rate', 0.0),
            notes=data.get('notes', ''),
            settled=data.get('settled', False)
        )

