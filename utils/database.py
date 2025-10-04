"""Database management utilities using SQLite."""
import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
from models import Transaction, Account, Budget, Goal, Debt, Category, Subcategory, RecurringTransaction


class Database:
    """SQLite database manager for Money Manager app."""
    
    def __init__(self, db_path: str = "money_manager.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
        self.initialize_default_data()
    
    def connect(self):
        """Connect to database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """Create all necessary database tables."""
        # Categories table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category_type TEXT NOT NULL,
                icon TEXT,
                color TEXT
            )
        ''')
        
        # Subcategories table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS subcategories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category_id INTEGER,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')
        
        # Accounts table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                account_type TEXT NOT NULL,
                initial_balance REAL DEFAULT 0,
                current_balance REAL DEFAULT 0,
                currency TEXT DEFAULT 'USD',
                icon TEXT,
                color TEXT,
                is_credit_card INTEGER DEFAULT 0,
                credit_limit REAL DEFAULT 0,
                due_date TEXT,
                interest_rate REAL DEFAULT 0,
                notes TEXT
            )
        ''')
        
        # Transactions table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                category_id INTEGER,
                subcategory_id INTEGER,
                account_id INTEGER,
                to_account_id INTEGER,
                date TEXT NOT NULL,
                time TEXT,
                description TEXT,
                payment_method TEXT,
                tags TEXT,
                receipt_path TEXT,
                recurring_id INTEGER,
                FOREIGN KEY (category_id) REFERENCES categories(id),
                FOREIGN KEY (subcategory_id) REFERENCES subcategories(id),
                FOREIGN KEY (account_id) REFERENCES accounts(id),
                FOREIGN KEY (to_account_id) REFERENCES accounts(id),
                FOREIGN KEY (recurring_id) REFERENCES recurring_transactions(id)
            )
        ''')
        
        # Budgets table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                amount REAL NOT NULL,
                period TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                alert_percentage REAL DEFAULT 80,
                spent REAL DEFAULT 0,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')
        
        # Goals table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                current_amount REAL DEFAULT 0,
                deadline TEXT,
                icon TEXT,
                color TEXT,
                notes TEXT,
                completed INTEGER DEFAULT 0
            )
        ''')
        
        # Debts table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debt_type TEXT NOT NULL,
                person_name TEXT NOT NULL,
                amount REAL NOT NULL,
                amount_paid REAL DEFAULT 0,
                date TEXT,
                due_date TEXT,
                interest_rate REAL DEFAULT 0,
                notes TEXT,
                settled INTEGER DEFAULT 0
            )
        ''')
        
        # Recurring transactions table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS recurring_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                category_id INTEGER,
                subcategory_id INTEGER,
                account_id INTEGER,
                description TEXT,
                frequency TEXT NOT NULL,
                custom_interval INTEGER DEFAULT 1,
                start_date TEXT,
                end_date TEXT,
                next_due_date TEXT,
                auto_create INTEGER DEFAULT 1,
                active INTEGER DEFAULT 1,
                FOREIGN KEY (category_id) REFERENCES categories(id),
                FOREIGN KEY (subcategory_id) REFERENCES subcategories(id),
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        ''')
        
        # Settings table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        self.conn.commit()
    
    def initialize_default_data(self):
        """Initialize default categories and settings if not exists."""
        # Check if categories already exist
        self.cursor.execute("SELECT COUNT(*) FROM categories")
        count = self.cursor.fetchone()[0]
        
        if count == 0:
            # Default expense categories
            expense_categories = [
                ("Food & Dining", "restaurant", "#FF5722"),
                ("Shopping", "cart", "#E91E63"),
                ("Transportation", "car", "#9C27B0"),
                ("Entertainment", "movie", "#673AB7"),
                ("Bills & Utilities", "file-document", "#3F51B5"),
                ("Healthcare", "hospital", "#2196F3"),
                ("Education", "school", "#03A9F4"),
                ("Travel", "airplane", "#00BCD4"),
                ("Personal", "account", "#009688"),
                ("Others", "dots-horizontal", "#795548")
            ]
            
            for name, icon, color in expense_categories:
                self.cursor.execute(
                    "INSERT INTO categories (name, category_type, icon, color) VALUES (?, ?, ?, ?)",
                    (name, "Expense", icon, color)
                )
            
            # Default income categories
            income_categories = [
                ("Salary", "cash", "#4CAF50"),
                ("Business", "briefcase", "#8BC34A"),
                ("Investments", "trending-up", "#CDDC39"),
                ("Gifts", "gift", "#FFC107"),
                ("Other Income", "plus", "#FF9800")
            ]
            
            for name, icon, color in income_categories:
                self.cursor.execute(
                    "INSERT INTO categories (name, category_type, icon, color) VALUES (?, ?, ?, ?)",
                    (name, "Income", icon, color)
                )
            
            self.conn.commit()
        
        # Check if default account exists
        self.cursor.execute("SELECT COUNT(*) FROM accounts")
        count = self.cursor.fetchone()[0]
        
        if count == 0:
            # Create default cash account
            self.cursor.execute(
                "INSERT INTO accounts (name, account_type, initial_balance, current_balance, icon, color) VALUES (?, ?, ?, ?, ?, ?)",
                ("Cash", "Cash", 0, 0, "wallet", "#4CAF50")
            )
            self.conn.commit()
        
        # Initialize settings
        default_settings = {
            "currency": "USD",
            "date_format": "%Y-%m-%d",
            "theme": "Light",
            "pin_code": "",
            "auto_backup": "0",
            "backup_frequency": "weekly",
            "financial_month_start": "1"
        }
        
        for key, value in default_settings.items():
            self.cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))
        
        self.conn.commit()
    
    # Transaction methods
    def add_transaction(self, transaction: Transaction) -> int:
        """Add a new transaction."""
        self.cursor.execute('''
            INSERT INTO transactions (transaction_type, amount, category_id, subcategory_id, 
                                     account_id, to_account_id, date, time, description, 
                                     payment_method, tags, receipt_path, recurring_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction.transaction_type, transaction.amount, transaction.category_id,
            transaction.subcategory_id, transaction.account_id, transaction.to_account_id,
            transaction.date.strftime("%Y-%m-%d") if isinstance(transaction.date, datetime) else transaction.date,
            transaction.time, transaction.description, transaction.payment_method,
            transaction.tags, transaction.receipt_path, transaction.recurring_id
        ))
        
        transaction_id = self.cursor.lastrowid
        
        # Update account balances
        if transaction.transaction_type == "Expense" and transaction.account_id:
            self.update_account_balance(transaction.account_id, -transaction.amount)
        elif transaction.transaction_type == "Income" and transaction.account_id:
            self.update_account_balance(transaction.account_id, transaction.amount)
        elif transaction.transaction_type == "Transfer":
            if transaction.account_id:
                self.update_account_balance(transaction.account_id, -transaction.amount)
            if transaction.to_account_id:
                self.update_account_balance(transaction.to_account_id, transaction.amount)
        
        self.conn.commit()
        return transaction_id
    
    def get_transactions(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict]:
        """Get all transactions."""
        query = '''
            SELECT t.*, c.name as category_name, c.icon as category_icon, 
                   c.color as category_color, a.name as account_name
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            LEFT JOIN accounts a ON t.account_id = a.id
            ORDER BY t.date DESC, t.id DESC
        '''
        
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        
        transactions = []
        for row in rows:
            trans_dict = dict(row)
            transactions.append(trans_dict)
        
        return transactions
    
    def update_transaction(self, transaction: Transaction):
        """Update an existing transaction."""
        # Get old transaction to adjust balances
        old_trans = self.get_transaction_by_id(transaction.id)
        
        # Revert old balance changes
        if old_trans:
            if old_trans['transaction_type'] == "Expense" and old_trans['account_id']:
                self.update_account_balance(old_trans['account_id'], old_trans['amount'])
            elif old_trans['transaction_type'] == "Income" and old_trans['account_id']:
                self.update_account_balance(old_trans['account_id'], -old_trans['amount'])
        
        # Update transaction
        self.cursor.execute('''
            UPDATE transactions 
            SET transaction_type=?, amount=?, category_id=?, subcategory_id=?, 
                account_id=?, to_account_id=?, date=?, time=?, description=?, 
                payment_method=?, tags=?, receipt_path=?
            WHERE id=?
        ''', (
            transaction.transaction_type, transaction.amount, transaction.category_id,
            transaction.subcategory_id, transaction.account_id, transaction.to_account_id,
            transaction.date.strftime("%Y-%m-%d") if isinstance(transaction.date, datetime) else transaction.date,
            transaction.time, transaction.description, transaction.payment_method,
            transaction.tags, transaction.receipt_path, transaction.id
        ))
        
        # Apply new balance changes
        if transaction.transaction_type == "Expense" and transaction.account_id:
            self.update_account_balance(transaction.account_id, -transaction.amount)
        elif transaction.transaction_type == "Income" and transaction.account_id:
            self.update_account_balance(transaction.account_id, transaction.amount)
        
        self.conn.commit()
    
    def delete_transaction(self, transaction_id: int):
        """Delete a transaction."""
        # Get transaction to revert balance
        trans = self.get_transaction_by_id(transaction_id)
        
        if trans:
            if trans['transaction_type'] == "Expense" and trans['account_id']:
                self.update_account_balance(trans['account_id'], trans['amount'])
            elif trans['transaction_type'] == "Income" and trans['account_id']:
                self.update_account_balance(trans['account_id'], -trans['amount'])
        
        self.cursor.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
        self.conn.commit()
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Dict]:
        """Get a single transaction by ID."""
        self.cursor.execute("SELECT * FROM transactions WHERE id=?", (transaction_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    # Account methods
    def add_account(self, account: Account) -> int:
        """Add a new account."""
        self.cursor.execute('''
            INSERT INTO accounts (name, account_type, initial_balance, current_balance, 
                                 currency, icon, color, is_credit_card, credit_limit, 
                                 due_date, interest_rate, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            account.name, account.account_type, account.initial_balance, account.current_balance,
            account.currency, account.icon, account.color, account.is_credit_card,
            account.credit_limit, account.due_date, account.interest_rate, account.notes
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_accounts(self) -> List[Dict]:
        """Get all accounts."""
        self.cursor.execute("SELECT * FROM accounts ORDER BY id")
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_account_by_id(self, account_id: int) -> Optional[Dict]:
        """Get a single account by ID."""
        self.cursor.execute("SELECT * FROM accounts WHERE id=?", (account_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_account(self, account: Account):
        """Update an existing account."""
        self.cursor.execute('''
            UPDATE accounts 
            SET name=?, account_type=?, initial_balance=?, current_balance=?, 
                currency=?, icon=?, color=?, is_credit_card=?, credit_limit=?, 
                due_date=?, interest_rate=?, notes=?
            WHERE id=?
        ''', (
            account.name, account.account_type, account.initial_balance, account.current_balance,
            account.currency, account.icon, account.color, account.is_credit_card,
            account.credit_limit, account.due_date, account.interest_rate, account.notes,
            account.id
        ))
        self.conn.commit()
    
    def delete_account(self, account_id: int):
        """Delete an account."""
        self.cursor.execute("DELETE FROM accounts WHERE id=?", (account_id,))
        self.conn.commit()
    
    def update_account_balance(self, account_id: int, amount: float):
        """Update account balance by adding amount."""
        self.cursor.execute(
            "UPDATE accounts SET current_balance = current_balance + ? WHERE id=?",
            (amount, account_id)
        )
        self.conn.commit()
    
    def get_total_balance(self) -> float:
        """Get total balance across all accounts."""
        self.cursor.execute("SELECT SUM(current_balance) FROM accounts")
        result = self.cursor.fetchone()[0]
        return result if result else 0.0
    
    # Category methods
    def add_category(self, category: Category) -> int:
        """Add a new category."""
        self.cursor.execute('''
            INSERT INTO categories (name, category_type, icon, color)
            VALUES (?, ?, ?, ?)
        ''', (category.name, category.category_type, category.icon, category.color))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_categories(self, category_type: Optional[str] = None) -> List[Dict]:
        """Get all categories, optionally filtered by type."""
        if category_type:
            self.cursor.execute(
                "SELECT * FROM categories WHERE category_type=? ORDER BY name",
                (category_type,)
            )
        else:
            self.cursor.execute("SELECT * FROM categories ORDER BY category_type, name")
        
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def update_category(self, category: Category):
        """Update a category."""
        self.cursor.execute('''
            UPDATE categories SET name=?, category_type=?, icon=?, color=? WHERE id=?
        ''', (category.name, category.category_type, category.icon, category.color, category.id))
        self.conn.commit()
    
    def delete_category(self, category_id: int):
        """Delete a category."""
        self.cursor.execute("DELETE FROM categories WHERE id=?", (category_id,))
        self.conn.commit()
    
    # Budget methods
    def add_budget(self, budget: Budget) -> int:
        """Add a new budget."""
        self.cursor.execute('''
            INSERT INTO budgets (category_id, amount, period, start_date, end_date, 
                                alert_percentage, spent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            budget.category_id, budget.amount, budget.period, budget.start_date,
            budget.end_date, budget.alert_percentage, budget.spent
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_budgets(self) -> List[Dict]:
        """Get all budgets."""
        self.cursor.execute('''
            SELECT b.*, c.name as category_name, c.icon as category_icon, c.color as category_color
            FROM budgets b
            LEFT JOIN categories c ON b.category_id = c.id
            ORDER BY b.id
        ''')
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def update_budget(self, budget: Budget):
        """Update a budget."""
        self.cursor.execute('''
            UPDATE budgets 
            SET category_id=?, amount=?, period=?, start_date=?, end_date=?, 
                alert_percentage=?, spent=?
            WHERE id=?
        ''', (
            budget.category_id, budget.amount, budget.period, budget.start_date,
            budget.end_date, budget.alert_percentage, budget.spent, budget.id
        ))
        self.conn.commit()
    
    def delete_budget(self, budget_id: int):
        """Delete a budget."""
        self.cursor.execute("DELETE FROM budgets WHERE id=?", (budget_id,))
        self.conn.commit()
    
    def update_budget_spent(self, category_id: int, period_start: str, period_end: str):
        """Recalculate spent amount for a budget."""
        self.cursor.execute('''
            SELECT SUM(amount) FROM transactions 
            WHERE category_id=? AND transaction_type='Expense' 
            AND date BETWEEN ? AND ?
        ''', (category_id, period_start, period_end))
        
        result = self.cursor.fetchone()[0]
        spent = result if result else 0.0
        
        self.cursor.execute('''
            UPDATE budgets SET spent=? WHERE category_id=?
        ''', (spent, category_id))
        self.conn.commit()
    
    # Goal methods
    def add_goal(self, goal: Goal) -> int:
        """Add a new goal."""
        self.cursor.execute('''
            INSERT INTO goals (name, target_amount, current_amount, deadline, 
                              icon, color, notes, completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            goal.name, goal.target_amount, goal.current_amount, goal.deadline,
            goal.icon, goal.color, goal.notes, goal.completed
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_goals(self) -> List[Dict]:
        """Get all goals."""
        self.cursor.execute("SELECT * FROM goals ORDER BY completed, deadline")
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def update_goal(self, goal: Goal):
        """Update a goal."""
        self.cursor.execute('''
            UPDATE goals 
            SET name=?, target_amount=?, current_amount=?, deadline=?, 
                icon=?, color=?, notes=?, completed=?
            WHERE id=?
        ''', (
            goal.name, goal.target_amount, goal.current_amount, goal.deadline,
            goal.icon, goal.color, goal.notes, goal.completed, goal.id
        ))
        self.conn.commit()
    
    def delete_goal(self, goal_id: int):
        """Delete a goal."""
        self.cursor.execute("DELETE FROM goals WHERE id=?", (goal_id,))
        self.conn.commit()
    
    # Debt methods
    def add_debt(self, debt: Debt) -> int:
        """Add a new debt."""
        self.cursor.execute('''
            INSERT INTO debts (debt_type, person_name, amount, amount_paid, date, 
                              due_date, interest_rate, notes, settled)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            debt.debt_type, debt.person_name, debt.amount, debt.amount_paid,
            debt.date, debt.due_date, debt.interest_rate, debt.notes, debt.settled
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_debts(self) -> List[Dict]:
        """Get all debts."""
        self.cursor.execute("SELECT * FROM debts ORDER BY settled, due_date")
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def update_debt(self, debt: Debt):
        """Update a debt."""
        self.cursor.execute('''
            UPDATE debts 
            SET debt_type=?, person_name=?, amount=?, amount_paid=?, date=?, 
                due_date=?, interest_rate=?, notes=?, settled=?
            WHERE id=?
        ''', (
            debt.debt_type, debt.person_name, debt.amount, debt.amount_paid,
            debt.date, debt.due_date, debt.interest_rate, debt.notes,
            debt.settled, debt.id
        ))
        self.conn.commit()
    
    def delete_debt(self, debt_id: int):
        """Delete a debt."""
        self.cursor.execute("DELETE FROM debts WHERE id=?", (debt_id,))
        self.conn.commit()
    
    # Recurring transaction methods
    def add_recurring_transaction(self, recurring: RecurringTransaction) -> int:
        """Add a new recurring transaction."""
        self.cursor.execute('''
            INSERT INTO recurring_transactions 
            (transaction_type, amount, category_id, subcategory_id, account_id, 
             description, frequency, custom_interval, start_date, end_date, 
             next_due_date, auto_create, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            recurring.transaction_type, recurring.amount, recurring.category_id,
            recurring.subcategory_id, recurring.account_id, recurring.description,
            recurring.frequency, recurring.custom_interval, recurring.start_date,
            recurring.end_date, recurring.next_due_date, recurring.auto_create,
            recurring.active
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_recurring_transactions(self) -> List[Dict]:
        """Get all recurring transactions."""
        self.cursor.execute('''
            SELECT r.*, c.name as category_name 
            FROM recurring_transactions r
            LEFT JOIN categories c ON r.category_id = c.id
            WHERE r.active = 1
            ORDER BY r.next_due_date
        ''')
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def update_recurring_transaction(self, recurring: RecurringTransaction):
        """Update a recurring transaction."""
        self.cursor.execute('''
            UPDATE recurring_transactions 
            SET transaction_type=?, amount=?, category_id=?, subcategory_id=?, 
                account_id=?, description=?, frequency=?, custom_interval=?, 
                start_date=?, end_date=?, next_due_date=?, auto_create=?, active=?
            WHERE id=?
        ''', (
            recurring.transaction_type, recurring.amount, recurring.category_id,
            recurring.subcategory_id, recurring.account_id, recurring.description,
            recurring.frequency, recurring.custom_interval, recurring.start_date,
            recurring.end_date, recurring.next_due_date, recurring.auto_create,
            recurring.active, recurring.id
        ))
        self.conn.commit()
    
    def delete_recurring_transaction(self, recurring_id: int):
        """Delete a recurring transaction."""
        self.cursor.execute("DELETE FROM recurring_transactions WHERE id=?", (recurring_id,))
        self.conn.commit()
    
    # Settings methods
    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting value."""
        self.cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = self.cursor.fetchone()
        return row[0] if row else None
    
    def set_setting(self, key: str, value: str):
        """Set a setting value."""
        self.cursor.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
        self.conn.commit()
    
    # Analytics methods
    def get_expense_by_category(self, start_date: str, end_date: str) -> List[Tuple]:
        """Get expenses grouped by category for a date range."""
        self.cursor.execute('''
            SELECT c.name, c.color, SUM(t.amount) as total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.transaction_type = 'Expense' AND t.date BETWEEN ? AND ?
            GROUP BY c.id, c.name, c.color
            ORDER BY total DESC
        ''', (start_date, end_date))
        return self.cursor.fetchall()
    
    def get_income_vs_expense(self, start_date: str, end_date: str) -> Dict:
        """Get total income and expense for a date range."""
        self.cursor.execute('''
            SELECT 
                SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END) as income,
                SUM(CASE WHEN transaction_type = 'Expense' THEN amount ELSE 0 END) as expense
            FROM transactions
            WHERE date BETWEEN ? AND ?
        ''', (start_date, end_date))
        row = self.cursor.fetchone()
        return {
            'income': row[0] if row[0] else 0,
            'expense': row[1] if row[1] else 0
        }
    
    def get_monthly_trend(self, months: int = 6) -> List[Dict]:
        """Get monthly income/expense trend."""
        self.cursor.execute('''
            SELECT 
                strftime('%Y-%m', date) as month,
                SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END) as income,
                SUM(CASE WHEN transaction_type = 'Expense' THEN amount ELSE 0 END) as expense
            FROM transactions
            WHERE date >= date('now', '-' || ? || ' months')
            GROUP BY month
            ORDER BY month
        ''', (months,))
        rows = self.cursor.fetchall()
        return [{'month': row[0], 'income': row[1], 'expense': row[2]} for row in rows]
    
    def search_transactions(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search transactions with filters."""
        sql = '''
            SELECT t.*, c.name as category_name, a.name as account_name
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            LEFT JOIN accounts a ON t.account_id = a.id
            WHERE 1=1
        '''
        params = []
        
        if query:
            sql += " AND (t.description LIKE ? OR t.tags LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%"])
        
        if filters:
            if filters.get('transaction_type'):
                sql += " AND t.transaction_type = ?"
                params.append(filters['transaction_type'])
            
            if filters.get('category_id'):
                sql += " AND t.category_id = ?"
                params.append(filters['category_id'])
            
            if filters.get('account_id'):
                sql += " AND t.account_id = ?"
                params.append(filters['account_id'])
            
            if filters.get('start_date'):
                sql += " AND t.date >= ?"
                params.append(filters['start_date'])
            
            if filters.get('end_date'):
                sql += " AND t.date <= ?"
                params.append(filters['end_date'])
        
        sql += " ORDER BY t.date DESC, t.id DESC"
        
        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

