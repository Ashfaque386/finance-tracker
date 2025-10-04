"""Script to generate sample data for testing."""
from datetime import datetime, timedelta
import random
from utils import Database
from models import Transaction, Account, Budget, Goal, Debt


def generate_sample_data():
    """Generate sample data for testing the Money Manager app."""
    
    # Initialize database
    db = Database("money_manager.db")
    
    print("Generating sample data...")
    
    # Check if accounts already exist (avoid duplicates)
    existing_accounts = db.get_accounts()
    
    if len(existing_accounts) > 1:
        print("Sample data already exists. Skipping...")
        return
    
    # Add sample accounts
    print("Adding sample accounts...")
    
    accounts = [
        Account(
            name="Main Bank Account",
            account_type="Bank",
            initial_balance=5000.0,
            current_balance=5000.0,
            icon="bank",
            color="#1976D2"
        ),
        Account(
            name="Cash Wallet",
            account_type="Cash",
            initial_balance=500.0,
            current_balance=500.0,
            icon="wallet",
            color="#4CAF50"
        ),
        Account(
            name="Credit Card",
            account_type="Card",
            initial_balance=0.0,
            current_balance=0.0,
            icon="credit-card",
            color="#F44336",
            is_credit_card=True,
            credit_limit=5000.0,
            due_date="2025-11-15"
        ),
    ]
    
    account_ids = []
    for account in accounts:
        account_id = db.add_account(account)
        account_ids.append(account_id)
        print(f"  Added: {account.name}")
    
    # Get categories
    expense_categories = db.get_categories("Expense")
    income_categories = db.get_categories("Income")
    
    # Add sample transactions for the last 3 months
    print("\nAdding sample transactions...")
    
    transaction_count = 0
    today = datetime.now()
    
    # Generate transactions
    for days_ago in range(90, 0, -1):
        transaction_date = today - timedelta(days=days_ago)
        
        # Generate 1-3 random transactions per day
        num_transactions = random.randint(1, 3)
        
        for _ in range(num_transactions):
            # 70% chance of expense, 30% chance of income
            if random.random() < 0.7:
                # Expense
                category = random.choice(expense_categories)
                amount = round(random.uniform(5, 200), 2)
                transaction_type = "Expense"
                descriptions = [
                    "Grocery shopping",
                    "Coffee",
                    "Restaurant",
                    "Gas station",
                    "Movie tickets",
                    "Online shopping",
                    "Utility bill",
                    "Pharmacy",
                    "Book store",
                    "Gym membership"
                ]
            else:
                # Income
                category = random.choice(income_categories)
                amount = round(random.uniform(100, 2000), 2)
                transaction_type = "Income"
                descriptions = [
                    "Salary",
                    "Freelance work",
                    "Bonus",
                    "Gift",
                    "Refund",
                    "Investment return"
                ]
            
            transaction = Transaction(
                transaction_type=transaction_type,
                amount=amount,
                category_id=category['id'],
                account_id=random.choice(account_ids),
                date=transaction_date,
                description=random.choice(descriptions),
                payment_method=random.choice(["Cash", "Card", "UPI", "Bank Transfer"])
            )
            
            db.add_transaction(transaction)
            transaction_count += 1
    
    print(f"  Added {transaction_count} transactions")
    
    # Add sample budgets
    print("\nAdding sample budgets...")
    
    budget_categories = random.sample(expense_categories, min(5, len(expense_categories)))
    
    for category in budget_categories:
        budget = Budget(
            category_id=category['id'],
            amount=round(random.uniform(200, 1000), 2),
            period="Monthly",
            alert_percentage=80.0
        )
        
        # Calculate current spending
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        db.add_budget(budget)
        db.update_budget_spent(category['id'], start_date, end_date)
        
        print(f"  Added budget for: {category['name']}")
    
    # Add sample goals
    print("\nAdding sample goals...")
    
    goals = [
        Goal(
            name="Emergency Fund",
            target_amount=10000.0,
            current_amount=3500.0,
            deadline=(today + timedelta(days=365)).strftime("%Y-%m-%d"),
            icon="shield-check",
            color="#2196F3",
            notes="Save for emergencies"
        ),
        Goal(
            name="Vacation Fund",
            target_amount=3000.0,
            current_amount=1200.0,
            deadline=(today + timedelta(days=180)).strftime("%Y-%m-%d"),
            icon="airplane",
            color="#00BCD4",
            notes="Summer vacation to Europe"
        ),
        Goal(
            name="New Laptop",
            target_amount=1500.0,
            current_amount=800.0,
            deadline=(today + timedelta(days=90)).strftime("%Y-%m-%d"),
            icon="laptop",
            color="#FF9800",
            notes="MacBook Pro"
        ),
    ]
    
    for goal in goals:
        db.add_goal(goal)
        print(f"  Added goal: {goal.name}")
    
    # Add sample debts
    print("\nAdding sample debts...")
    
    debts = [
        Debt(
            debt_type="Lent",
            person_name="John Smith",
            amount=500.0,
            amount_paid=200.0,
            date=(today - timedelta(days=30)).strftime("%Y-%m-%d"),
            due_date=(today + timedelta(days=30)).strftime("%Y-%m-%d"),
            notes="Lent money for emergency"
        ),
        Debt(
            debt_type="Borrowed",
            person_name="Jane Doe",
            amount=1000.0,
            amount_paid=400.0,
            date=(today - timedelta(days=60)).strftime("%Y-%m-%d"),
            due_date=(today + timedelta(days=60)).strftime("%Y-%m-%d"),
            notes="Borrowed for medical expenses"
        ),
    ]
    
    for debt in debts:
        db.add_debt(debt)
        print(f"  Added debt: {debt.debt_type} - {debt.person_name}")
    
    # Add recurring transactions
    print("\nAdding recurring transactions...")
    
    from models import RecurringTransaction
    
    recurring = [
        RecurringTransaction(
            transaction_type="Expense",
            amount=50.0,
            category_id=expense_categories[0]['id'],
            account_id=account_ids[0],
            description="Monthly Subscription",
            frequency="Monthly",
            start_date=today.strftime("%Y-%m-%d"),
            next_due_date=(today + timedelta(days=30)).strftime("%Y-%m-%d"),
            auto_create=True,
            active=True
        ),
        RecurringTransaction(
            transaction_type="Income",
            amount=3000.0,
            category_id=income_categories[0]['id'],
            account_id=account_ids[0],
            description="Monthly Salary",
            frequency="Monthly",
            start_date=today.strftime("%Y-%m-%d"),
            next_due_date=(today.replace(day=1) + timedelta(days=32)).replace(day=1).strftime("%Y-%m-%d"),
            auto_create=False,
            active=True
        ),
    ]
    
    for rec in recurring:
        db.add_recurring_transaction(rec)
        print(f"  Added recurring: {rec.description}")
    
    db.close()
    
    print("\n[SUCCESS] Sample data generation complete!")
    print("\nSummary:")
    print(f"  - {len(accounts)} accounts")
    print(f"  - {transaction_count} transactions")
    print(f"  - {len(budget_categories)} budgets")
    print(f"  - {len(goals)} goals")
    print(f"  - {len(debts)} debts")
    print(f"  - {len(recurring)} recurring transactions")


if __name__ == "__main__":
    generate_sample_data()

