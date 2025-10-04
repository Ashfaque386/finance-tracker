"""Recurring transaction model for automated transactions."""
from typing import Optional, Dict
from datetime import datetime


class RecurringTransaction:
    """Represents a recurring transaction pattern."""
    
    def __init__(self, recurring_id: Optional[int] = None,
                 transaction_type: str = "Expense",
                 amount: float = 0.0,
                 category_id: Optional[int] = None,
                 subcategory_id: Optional[int] = None,
                 account_id: Optional[int] = None,
                 description: str = "",
                 frequency: str = "Monthly",
                 custom_interval: int = 1,
                 start_date: Optional[str] = None,
                 end_date: Optional[str] = None,
                 next_due_date: Optional[str] = None,
                 auto_create: bool = True,
                 active: bool = True):
        self.id = recurring_id
        self.transaction_type = transaction_type
        self.amount = amount
        self.category_id = category_id
        self.subcategory_id = subcategory_id
        self.account_id = account_id
        self.description = description
        self.frequency = frequency  # Daily, Weekly, Monthly, Yearly, Custom
        self.custom_interval = custom_interval  # For custom frequency
        self.start_date = start_date
        self.end_date = end_date
        self.next_due_date = next_due_date
        self.auto_create = auto_create
        self.active = active
        
    def to_dict(self) -> Dict:
        """Convert recurring transaction to dictionary."""
        return {
            'id': self.id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'category_id': self.category_id,
            'subcategory_id': self.subcategory_id,
            'account_id': self.account_id,
            'description': self.description,
            'frequency': self.frequency,
            'custom_interval': self.custom_interval,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'next_due_date': self.next_due_date,
            'auto_create': self.auto_create,
            'active': self.active
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'RecurringTransaction':
        """Create recurring transaction from dictionary."""
        return RecurringTransaction(
            recurring_id=data.get('id'),
            transaction_type=data.get('transaction_type', 'Expense'),
            amount=data.get('amount', 0.0),
            category_id=data.get('category_id'),
            subcategory_id=data.get('subcategory_id'),
            account_id=data.get('account_id'),
            description=data.get('description', ''),
            frequency=data.get('frequency', 'Monthly'),
            custom_interval=data.get('custom_interval', 1),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            next_due_date=data.get('next_due_date'),
            auto_create=data.get('auto_create', True),
            active=data.get('active', True)
        )

