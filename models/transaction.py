"""Transaction model for expense, income, and transfer tracking."""
from datetime import datetime
from typing import Optional, List, Dict


class Transaction:
    """Represents a financial transaction (Expense, Income, or Transfer)."""
    
    def __init__(self, transaction_id: Optional[int] = None, 
                 transaction_type: str = "Expense",
                 amount: float = 0.0,
                 category_id: Optional[int] = None,
                 subcategory_id: Optional[int] = None,
                 account_id: Optional[int] = None,
                 to_account_id: Optional[int] = None,
                 date: Optional[datetime] = None,
                 time: Optional[str] = None,
                 description: str = "",
                 payment_method: str = "",
                 tags: str = "",
                 receipt_path: Optional[str] = None,
                 recurring_id: Optional[int] = None):
        self.id = transaction_id
        self.transaction_type = transaction_type  # Expense, Income, Transfer
        self.amount = amount
        self.category_id = category_id
        self.subcategory_id = subcategory_id
        self.account_id = account_id
        self.to_account_id = to_account_id  # For transfers
        self.date = date or datetime.now()
        self.time = time or datetime.now().strftime("%H:%M")
        self.description = description
        self.payment_method = payment_method
        self.tags = tags  # Comma-separated tags
        self.receipt_path = receipt_path
        self.recurring_id = recurring_id
        
    def to_dict(self) -> Dict:
        """Convert transaction to dictionary."""
        return {
            'id': self.id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'category_id': self.category_id,
            'subcategory_id': self.subcategory_id,
            'account_id': self.account_id,
            'to_account_id': self.to_account_id,
            'date': self.date.strftime("%Y-%m-%d") if isinstance(self.date, datetime) else self.date,
            'time': self.time,
            'description': self.description,
            'payment_method': self.payment_method,
            'tags': self.tags,
            'receipt_path': self.receipt_path,
            'recurring_id': self.recurring_id
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Transaction':
        """Create transaction from dictionary."""
        date_str = data.get('date')
        if isinstance(date_str, str):
            date = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            date = date_str
            
        return Transaction(
            transaction_id=data.get('id'),
            transaction_type=data.get('transaction_type', 'Expense'),
            amount=data.get('amount', 0.0),
            category_id=data.get('category_id'),
            subcategory_id=data.get('subcategory_id'),
            account_id=data.get('account_id'),
            to_account_id=data.get('to_account_id'),
            date=date,
            time=data.get('time'),
            description=data.get('description', ''),
            payment_method=data.get('payment_method', ''),
            tags=data.get('tags', ''),
            receipt_path=data.get('receipt_path'),
            recurring_id=data.get('recurring_id')
        )

