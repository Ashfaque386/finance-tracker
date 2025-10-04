"""Account model for managing different financial accounts."""
from typing import Optional, Dict


class Account:
    """Represents a financial account (Bank, Cash, Card, UPI, etc.)."""
    
    def __init__(self, account_id: Optional[int] = None,
                 name: str = "",
                 account_type: str = "Cash",
                 initial_balance: float = 0.0,
                 current_balance: float = 0.0,
                 currency: str = "USD",
                 icon: str = "wallet",
                 color: str = "#2196F3",
                 is_credit_card: bool = False,
                 credit_limit: float = 0.0,
                 due_date: Optional[str] = None,
                 interest_rate: float = 0.0,
                 notes: str = ""):
        self.id = account_id
        self.name = name
        self.account_type = account_type  # Cash, Bank, Card, UPI, Wallet, etc.
        self.initial_balance = initial_balance
        self.current_balance = current_balance
        self.currency = currency
        self.icon = icon
        self.color = color
        self.is_credit_card = is_credit_card
        self.credit_limit = credit_limit
        self.due_date = due_date
        self.interest_rate = interest_rate
        self.notes = notes
        
    def to_dict(self) -> Dict:
        """Convert account to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'account_type': self.account_type,
            'initial_balance': self.initial_balance,
            'current_balance': self.current_balance,
            'currency': self.currency,
            'icon': self.icon,
            'color': self.color,
            'is_credit_card': self.is_credit_card,
            'credit_limit': self.credit_limit,
            'due_date': self.due_date,
            'interest_rate': self.interest_rate,
            'notes': self.notes
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Account':
        """Create account from dictionary."""
        return Account(
            account_id=data.get('id'),
            name=data.get('name', ''),
            account_type=data.get('account_type', 'Cash'),
            initial_balance=data.get('initial_balance', 0.0),
            current_balance=data.get('current_balance', 0.0),
            currency=data.get('currency', 'USD'),
            icon=data.get('icon', 'wallet'),
            color=data.get('color', '#2196F3'),
            is_credit_card=data.get('is_credit_card', False),
            credit_limit=data.get('credit_limit', 0.0),
            due_date=data.get('due_date'),
            interest_rate=data.get('interest_rate', 0.0),
            notes=data.get('notes', '')
        )

