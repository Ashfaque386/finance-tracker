"""Reminder and notification utilities."""
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class ReminderManager:
    """Manage reminders and notifications for bills, budgets, and goals."""
    
    def __init__(self, database):
        """Initialize reminder manager with database reference."""
        self.database = database
    
    def check_recurring_transactions(self) -> List[Dict]:
        """Check for due recurring transactions."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        recurring = self.database.get_recurring_transactions()
        due_transactions = []
        
        for trans in recurring:
            if trans['next_due_date'] and trans['next_due_date'] <= today:
                if trans['active'] and trans['auto_create']:
                    due_transactions.append(trans)
        
        return due_transactions
    
    def create_recurring_transaction_instances(self):
        """Automatically create transactions from due recurring patterns."""
        from models import Transaction
        
        due_transactions = self.check_recurring_transactions()
        created_count = 0
        
        for recurring in due_transactions:
            # Create new transaction
            transaction = Transaction(
                transaction_type=recurring['transaction_type'],
                amount=recurring['amount'],
                category_id=recurring['category_id'],
                subcategory_id=recurring['subcategory_id'],
                account_id=recurring['account_id'],
                description=recurring['description'],
                date=datetime.now(),
                recurring_id=recurring['id']
            )
            
            self.database.add_transaction(transaction)
            
            # Update next due date
            next_date = self.calculate_next_due_date(
                recurring['next_due_date'],
                recurring['frequency'],
                recurring['custom_interval']
            )
            
            self.database.cursor.execute(
                "UPDATE recurring_transactions SET next_due_date=? WHERE id=?",
                (next_date, recurring['id'])
            )
            self.database.conn.commit()
            
            created_count += 1
        
        return created_count
    
    def calculate_next_due_date(self, current_date: str, frequency: str, 
                                interval: int = 1) -> str:
        """Calculate next due date based on frequency."""
        date = datetime.strptime(current_date, "%Y-%m-%d")
        
        if frequency == "Daily":
            next_date = date + timedelta(days=interval)
        elif frequency == "Weekly":
            next_date = date + timedelta(weeks=interval)
        elif frequency == "Monthly":
            # Add months (approximate)
            next_date = date + timedelta(days=30 * interval)
        elif frequency == "Yearly":
            next_date = date + timedelta(days=365 * interval)
        else:
            next_date = date + timedelta(days=interval)
        
        return next_date.strftime("%Y-%m-%d")
    
    def check_budget_alerts(self) -> List[Dict]:
        """Check for budgets that need alerts."""
        budgets = self.database.get_budgets()
        alerts = []
        
        for budget in budgets:
            percentage = (budget['spent'] / budget['amount'] * 100) if budget['amount'] > 0 else 0
            
            if percentage >= budget['alert_percentage']:
                alerts.append({
                    'type': 'budget_alert',
                    'category': budget.get('category_name', 'Unknown'),
                    'percentage': percentage,
                    'spent': budget['spent'],
                    'amount': budget['amount'],
                    'severity': 'high' if percentage >= 100 else 'medium'
                })
        
        return alerts
    
    def check_debt_due_dates(self) -> List[Dict]:
        """Check for debts with upcoming due dates."""
        debts = self.database.get_debts()
        today = datetime.now()
        alerts = []
        
        for debt in debts:
            if debt['settled'] or not debt['due_date']:
                continue
            
            due_date = datetime.strptime(debt['due_date'], "%Y-%m-%d")
            days_until_due = (due_date - today).days
            
            if days_until_due <= 7:  # Alert 7 days before
                alerts.append({
                    'type': 'debt_due',
                    'person': debt['person_name'],
                    'amount': debt['amount'] - debt['amount_paid'],
                    'due_date': debt['due_date'],
                    'days_until_due': days_until_due,
                    'severity': 'high' if days_until_due <= 0 else 'medium'
                })
        
        return alerts
    
    def check_goal_deadlines(self) -> List[Dict]:
        """Check for goals with approaching deadlines."""
        goals = self.database.get_goals()
        today = datetime.now()
        alerts = []
        
        for goal in goals:
            if goal['completed'] or not goal['deadline']:
                continue
            
            deadline = datetime.strptime(goal['deadline'], "%Y-%m-%d")
            days_until_deadline = (deadline - today).days
            
            percentage = (goal['current_amount'] / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
            
            if days_until_deadline <= 30 and percentage < 100:  # Alert 30 days before
                alerts.append({
                    'type': 'goal_deadline',
                    'name': goal['name'],
                    'percentage': percentage,
                    'remaining': goal['target_amount'] - goal['current_amount'],
                    'deadline': goal['deadline'],
                    'days_until_deadline': days_until_deadline,
                    'severity': 'low'
                })
        
        return alerts
    
    def get_all_notifications(self) -> List[Dict]:
        """Get all pending notifications."""
        notifications = []
        
        # Check recurring transactions
        due_recurring = self.check_recurring_transactions()
        for trans in due_recurring:
            notifications.append({
                'type': 'recurring_due',
                'title': 'Recurring Transaction Due',
                'message': f"{trans['description']} - ${trans['amount']:.2f}",
                'severity': 'medium'
            })
        
        # Check budget alerts
        budget_alerts = self.check_budget_alerts()
        notifications.extend(budget_alerts)
        
        # Check debt due dates
        debt_alerts = self.check_debt_due_dates()
        notifications.extend(debt_alerts)
        
        # Check goal deadlines
        goal_alerts = self.check_goal_deadlines()
        notifications.extend(goal_alerts)
        
        return notifications

