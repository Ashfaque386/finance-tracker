"""Main application file for Money Manager."""
import os
import sys

# Set image provider before importing Kivy
os.environ['KIVY_IMAGE'] = 'pil'

# Android-specific settings
if hasattr(sys, 'getandroidapilevel'):
    # Running on Android
    os.environ['KIVY_LOG_MODE'] = 'PYTHON'
    
    # Request storage permissions on Android
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.READ_EXTERNAL_STORAGE,
        Permission.CAMERA
    ])

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from datetime import datetime, timedelta
from typing import Optional
import traceback

# Import utilities and models
from utils import Database, ChartUtils, FileIO, Security, CurrencyConverter, ReminderManager
from models import Transaction, Account, Budget, Goal, Debt

# Set minimum window size
Window.size = (360, 640)


class DashboardScreen(Screen):
    """Dashboard screen showing overview and quick stats."""
    
    def on_enter(self):
        """Called when screen is entered."""
        self.refresh_dashboard()
    
    def refresh_dashboard(self):
        """Refresh dashboard data."""
        app = MDApp.get_running_app()
        
        # Update total balance
        total_balance = app.db.get_total_balance()
        self.ids.total_balance_label.text = f"${total_balance:,.2f}"
        
        # Get this month's data
        today = datetime.now()
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        
        income_expense = app.db.get_income_vs_expense(start_date, end_date)
        self.ids.income_label.text = f"${income_expense['income']:,.2f}"
        self.ids.expense_label.text = f"${income_expense['expense']:,.2f}"
        
        # Load recent transactions
        self.load_recent_transactions()
        
        # Create dashboard chart
        self.create_dashboard_chart()
    
    def load_recent_transactions(self):
        """Load and display recent transactions."""
        app = MDApp.get_running_app()
        self.ids.recent_transactions_list.clear_widgets()
        
        transactions = app.db.get_transactions(limit=10)
        
        for trans in transactions:
            item = TwoLineAvatarIconListItem(
                text=f"{trans.get('category_name', 'Uncategorized')} - ${trans['amount']:.2f}",
                secondary_text=f"{trans['date']} - {trans.get('account_name', '')}",
            )
            
            icon = IconLeftWidget(
                icon=trans.get('category_icon', 'tag')
            )
            item.add_widget(icon)
            
            self.ids.recent_transactions_list.add_widget(item)
    
    def create_dashboard_chart(self):
        """Create and display dashboard chart."""
        app = MDApp.get_running_app()
        
        # Get monthly trend data
        trend_data = app.db.get_monthly_trend(months=6)
        
        if trend_data:
            chart_path = app.chart_utils.create_line_chart(
                trend_data,
                title="6 Month Trend",
                filename="dashboard_trend.png"
            )
            if chart_path and os.path.exists(chart_path):
                self.ids.dashboard_chart.source = chart_path
    
    def add_transaction(self, transaction_type):
        """Open transaction form dialog."""
        app = MDApp.get_running_app()
        app.show_transaction_form(transaction_type)
    
    def show_notifications(self):
        """Show notifications and reminders."""
        app = MDApp.get_running_app()
        notifications = app.reminder_manager.get_all_notifications()
        
        if not notifications:
            Snackbar(text="No notifications").open()
            return
        
        message = f"You have {len(notifications)} notifications"
        Snackbar(text=message).open()
    
    def go_to_settings(self):
        """Navigate to settings screen."""
        self.manager.current = 'settings'
    
    def show_more_menu(self):
        """Show more menu options."""
        menu_items = [
            {
                "text": "Budgets",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.go_to_screen("budgets"),
            },
            {
                "text": "Goals",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.go_to_screen("goals"),
            },
            {
                "text": "Settings",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.go_to_screen("settings"),
            },
        ]
        
        app = MDApp.get_running_app()
        if not hasattr(app, 'more_menu'):
            app.more_menu = MDDropdownMenu(
                caller=self.ids.bottom_nav,
                items=menu_items,
                width_mult=4,
            )
        app.more_menu.open()
    
    def go_to_screen(self, screen_name):
        """Navigate to specified screen."""
        app = MDApp.get_running_app()
        if hasattr(app, 'more_menu'):
            app.more_menu.dismiss()
        self.manager.current = screen_name


class TransactionsScreen(Screen):
    """Transactions list and management screen."""
    
    filter_type = StringProperty('All')
    
    def on_enter(self):
        """Called when screen is entered."""
        self.load_transactions()
    
    def load_transactions(self):
        """Load and display transactions."""
        app = MDApp.get_running_app()
        self.ids.transactions_list.clear_widgets()
        
        transactions = app.db.get_transactions()
        
        # Apply filter
        if self.filter_type != 'All':
            transactions = [t for t in transactions if t['transaction_type'] == self.filter_type]
        
        for trans in transactions:
            item = TwoLineAvatarIconListItem(
                text=f"{trans.get('category_name', 'Uncategorized')} - ${trans['amount']:.2f}",
                secondary_text=f"{trans['date']} - {trans['description']}",
            )
            
            icon = IconLeftWidget(
                icon=trans.get('category_icon', 'tag')
            )
            item.add_widget(icon)
            
            # Add options button
            icon_right = IconRightWidget(
                icon="dots-vertical",
                on_release=lambda x, t=trans: self.show_transaction_options(t)
            )
            item.add_widget(icon_right)
            
            self.ids.transactions_list.add_widget(item)
    
    def filter_transactions(self, filter_type):
        """Filter transactions by type."""
        self.filter_type = filter_type
        self.load_transactions()
    
    def add_transaction(self):
        """Open add transaction dialog."""
        app = MDApp.get_running_app()
        app.show_transaction_form()
    
    def show_transaction_options(self, transaction):
        """Show options for a transaction."""
        app = MDApp.get_running_app()
        
        dialog = MDDialog(
            title="Transaction Options",
            text=f"What would you like to do with this transaction?",
            buttons=[
                MDFlatButton(
                    text="EDIT",
                    on_release=lambda x: self.edit_transaction(transaction, dialog)
                ),
                MDFlatButton(
                    text="DELETE",
                    on_release=lambda x: self.delete_transaction(transaction, dialog)
                ),
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        dialog.open()
    
    def edit_transaction(self, transaction, dialog):
        """Edit a transaction."""
        dialog.dismiss()
        app = MDApp.get_running_app()
        app.show_transaction_form(edit_transaction=transaction)
    
    def delete_transaction(self, transaction, dialog):
        """Delete a transaction."""
        dialog.dismiss()
        app = MDApp.get_running_app()
        app.db.delete_transaction(transaction['id'])
        Snackbar(text="Transaction deleted").open()
        self.load_transactions()
    
    def show_filter_dialog(self):
        """Show advanced filter dialog."""
        Snackbar(text="Advanced filters - Coming soon").open()
    
    def show_search(self):
        """Show search functionality."""
        Snackbar(text="Search - Coming soon").open()


class ReportsScreen(Screen):
    """Reports and analytics screen."""
    
    current_period = StringProperty('month')
    
    def on_enter(self):
        """Called when screen is entered."""
        self.refresh_reports()
    
    def refresh_reports(self):
        """Refresh all report data."""
        app = MDApp.get_running_app()
        
        # Get date range based on period
        today = datetime.now()
        
        if self.current_period == 'week':
            start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        elif self.current_period == 'month':
            start_date = today.replace(day=1).strftime("%Y-%m-%d")
        elif self.current_period == 'year':
            start_date = today.replace(month=1, day=1).strftime("%Y-%m-%d")
        else:
            start_date = today.replace(day=1).strftime("%Y-%m-%d")
        
        end_date = today.strftime("%Y-%m-%d")
        
        # Get income vs expense
        income_expense = app.db.get_income_vs_expense(start_date, end_date)
        self.ids.report_income.text = f"${income_expense['income']:,.2f}"
        self.ids.report_expense.text = f"${income_expense['expense']:,.2f}"
        
        net = income_expense['income'] - income_expense['expense']
        self.ids.report_net.text = f"${net:,.2f}"
        
        # Create charts
        self.create_charts(start_date, end_date)
        
        # Load category summary
        self.load_category_summary(start_date, end_date)
    
    def create_charts(self, start_date, end_date):
        """Create and display charts."""
        app = MDApp.get_running_app()
        
        # Pie chart - Expenses by category
        expense_data = app.db.get_expense_by_category(start_date, end_date)
        if expense_data:
            pie_path = app.chart_utils.create_pie_chart(
                expense_data,
                title="Expenses by Category",
                filename="report_pie.png"
            )
            if pie_path and os.path.exists(pie_path):
                self.ids.pie_chart.source = pie_path
        
        # Line chart - Trend
        trend_data = app.db.get_monthly_trend(months=6)
        if trend_data:
            line_path = app.chart_utils.create_line_chart(
                trend_data,
                title="Income vs Expense Trend",
                filename="report_line.png"
            )
            if line_path and os.path.exists(line_path):
                self.ids.line_chart.source = line_path
        
        # Bar chart - Monthly comparison
        if trend_data:
            bar_path = app.chart_utils.create_bar_chart(
                trend_data,
                title="Monthly Comparison",
                filename="report_bar.png"
            )
            if bar_path and os.path.exists(bar_path):
                self.ids.bar_chart.source = bar_path
    
    def load_category_summary(self, start_date, end_date):
        """Load category summary list."""
        app = MDApp.get_running_app()
        self.ids.category_summary_list.clear_widgets()
        
        expense_data = app.db.get_expense_by_category(start_date, end_date)
        
        for row in expense_data:
            item = TwoLineAvatarIconListItem(
                text=row[0],
                secondary_text=f"${row[2]:,.2f}",
            )
            self.ids.category_summary_list.add_widget(item)
    
    def set_period(self, period):
        """Set report period."""
        self.current_period = period
        self.refresh_reports()
    
    def show_custom_period(self):
        """Show custom period selector."""
        Snackbar(text="Custom period - Coming soon").open()
    
    def export_report(self):
        """Export report data."""
        Snackbar(text="Export - Coming soon").open()


class AccountsScreen(Screen):
    """Accounts management screen."""
    
    def on_enter(self):
        """Called when screen is entered."""
        self.load_accounts()
    
    def load_accounts(self):
        """Load and display accounts."""
        app = MDApp.get_running_app()
        
        # Update total balance
        total_balance = app.db.get_total_balance()
        self.ids.total_balance.text = f"${total_balance:,.2f}"
        
        # Clear and reload accounts
        self.ids.accounts_container.clear_widgets()
        
        accounts = app.db.get_accounts()
        
        for account in accounts:
            # Create account card (simplified, not using custom class)
            from kivymd.uix.card import MDCard
            from kivymd.uix.boxlayout import MDBoxLayout
            from kivymd.uix.label import MDLabel
            from kivymd.uix.button import MDIconButton
            
            card = MDCard(size_hint_y=None, height=100, elevation=2, padding=16)
            layout = MDBoxLayout(orientation='horizontal', spacing=10)
            
            name_label = MDLabel(text=account['name'], font_style="H6", bold=True)
            balance_label = MDLabel(
                text=f"${account['current_balance']:,.2f}",
                font_style="H6",
                bold=True,
                size_hint_x=None,
                width=150
            )
            
            layout.add_widget(name_label)
            layout.add_widget(balance_label)
            
            card.add_widget(layout)
            self.ids.accounts_container.add_widget(card)
    
    def add_account(self):
        """Open add account dialog."""
        app = MDApp.get_running_app()
        app.show_account_form()


class BudgetsScreen(Screen):
    """Budgets management screen."""
    
    def on_enter(self):
        """Called when screen is entered."""
        self.load_budgets()
    
    def load_budgets(self):
        """Load and display budgets."""
        app = MDApp.get_running_app()
        
        budgets = app.db.get_budgets()
        
        # Calculate totals
        total_budget = sum(b['amount'] for b in budgets)
        total_spent = sum(b['spent'] for b in budgets)
        total_remaining = total_budget - total_spent
        
        self.ids.total_budget.text = f"${total_budget:,.2f}"
        self.ids.total_spent.text = f"${total_spent:,.2f}"
        self.ids.total_remaining.text = f"${total_remaining:,.2f}"
        
        # Load budget cards
        self.ids.budgets_container.clear_widgets()
        
        for budget in budgets:
            from kivymd.uix.card import MDCard
            from kivymd.uix.boxlayout import MDBoxLayout
            from kivymd.uix.label import MDLabel
            from kivymd.uix.progressbar import MDProgressBar
            
            card = MDCard(size_hint_y=None, height=140, elevation=2, padding=16)
            layout = MDBoxLayout(orientation='vertical', spacing=8)
            
            # Title
            title_label = MDLabel(
                text=budget.get('category_name', 'Unknown'),
                font_style="H6",
                bold=True,
                size_hint_y=None,
                height=30
            )
            
            # Amount
            amount_label = MDLabel(
                text=f"${budget['spent']:.2f} / ${budget['amount']:.2f}",
                size_hint_y=None,
                height=25
            )
            
            # Progress bar
            progress = MDProgressBar(
                size_hint_y=None,
                height=8,
                value=(budget['spent'] / budget['amount'] * 100) if budget['amount'] > 0 else 0
            )
            
            # Percentage
            percentage = (budget['spent'] / budget['amount'] * 100) if budget['amount'] > 0 else 0
            percent_label = MDLabel(
                text=f"{percentage:.1f}% used",
                font_style="Caption",
                size_hint_y=None,
                height=20
            )
            
            layout.add_widget(title_label)
            layout.add_widget(amount_label)
            layout.add_widget(progress)
            layout.add_widget(percent_label)
            
            card.add_widget(layout)
            self.ids.budgets_container.add_widget(card)
    
    def add_budget(self):
        """Open add budget dialog."""
        Snackbar(text="Add Budget - Coming soon").open()


class GoalsScreen(Screen):
    """Goals and savings screen."""
    
    def on_enter(self):
        """Called when screen is entered."""
        self.load_goals()
    
    def load_goals(self):
        """Load and display goals."""
        app = MDApp.get_running_app()
        
        goals = app.db.get_goals()
        
        self.ids.goals_container.clear_widgets()
        
        for goal in goals:
            if goal['completed']:
                continue
            
            from kivymd.uix.card import MDCard
            from kivymd.uix.boxlayout import MDBoxLayout
            from kivymd.uix.label import MDLabel
            from kivymd.uix.progressbar import MDProgressBar
            from kivymd.uix.button import MDRaisedButton
            
            card = MDCard(size_hint_y=None, height=180, elevation=2, padding=16)
            layout = MDBoxLayout(orientation='vertical', spacing=10)
            
            # Title
            title_label = MDLabel(
                text=goal['name'],
                font_style="H6",
                bold=True,
                size_hint_y=None,
                height=30
            )
            
            # Progress bar
            progress = MDProgressBar(
                size_hint_y=None,
                height=8,
                value=(goal['current_amount'] / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
            )
            
            # Amounts
            amount_layout = MDBoxLayout(size_hint_y=None, height=30)
            current_label = MDLabel(
                text=f"${goal['current_amount']:.2f}",
                font_style="H6",
                bold=True
            )
            target_label = MDLabel(
                text=f"${goal['target_amount']:.2f}",
                halign='right'
            )
            amount_layout.add_widget(current_label)
            amount_layout.add_widget(target_label)
            
            # Percentage
            percentage = (goal['current_amount'] / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
            percent_label = MDLabel(
                text=f"{percentage:.1f}% Complete",
                size_hint_y=None,
                height=20
            )
            
            layout.add_widget(title_label)
            layout.add_widget(progress)
            layout.add_widget(amount_layout)
            layout.add_widget(percent_label)
            
            card.add_widget(layout)
            self.ids.goals_container.add_widget(card)
    
    def add_goal(self):
        """Open add goal dialog."""
        Snackbar(text="Add Goal - Coming soon").open()


class SettingsScreen(Screen):
    """Settings screen."""
    
    def get_currency(self):
        """Get current currency setting."""
        app = MDApp.get_running_app()
        return app.db.get_setting('currency') or 'USD'
    
    def get_theme(self):
        """Get current theme setting."""
        app = MDApp.get_running_app()
        return app.db.get_setting('theme') or 'Light'
    
    def get_date_format(self):
        """Get current date format setting."""
        app = MDApp.get_running_app()
        return app.db.get_setting('date_format') or '%Y-%m-%d'
    
    def get_month_start(self):
        """Get financial month start setting."""
        app = MDApp.get_running_app()
        return app.db.get_setting('financial_month_start') or '1'
    
    def change_currency(self):
        """Change currency setting."""
        Snackbar(text="Currency settings - Coming soon").open()
    
    def change_theme(self):
        """Change theme setting."""
        app = MDApp.get_running_app()
        current_theme = self.get_theme()
        
        if current_theme == 'Light':
            app.theme_cls.theme_style = "Dark"
            app.db.set_setting('theme', 'Dark')
        else:
            app.theme_cls.theme_style = "Light"
            app.db.set_setting('theme', 'Light')
        
        Snackbar(text=f"Theme changed to {app.theme_cls.theme_style}").open()
    
    def change_date_format(self):
        """Change date format setting."""
        Snackbar(text="Date format settings - Coming soon").open()
    
    def change_month_start(self):
        """Change financial month start."""
        Snackbar(text="Month start settings - Coming soon").open()
    
    def setup_pin(self):
        """Setup PIN lock."""
        Snackbar(text="PIN setup - Coming soon").open()
    
    def create_backup(self):
        """Create backup."""
        app = MDApp.get_running_app()
        backup_path = app.file_io.create_backup(app.db.db_path)
        
        if backup_path:
            Snackbar(text=f"Backup created successfully").open()
        else:
            Snackbar(text="Backup failed").open()
    
    def restore_backup(self):
        """Restore from backup."""
        Snackbar(text="Restore backup - Coming soon").open()
    
    def export_data(self):
        """Export data."""
        Snackbar(text="Export data - Coming soon").open()
    
    def import_data(self):
        """Import data."""
        Snackbar(text="Import data - Coming soon").open()
    
    def manage_categories(self):
        """Manage categories."""
        Snackbar(text="Manage categories - Coming soon").open()
    
    def manage_recurring(self):
        """Manage recurring transactions."""
        Snackbar(text="Manage recurring - Coming soon").open()
    
    def manage_debts(self):
        """Manage debts."""
        Snackbar(text="Manage debts - Coming soon").open()
    
    def show_help(self):
        """Show help."""
        Snackbar(text="Help & Support - Coming soon").open()


class MoneyManagerApp(MDApp):
    """Main application class."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = None
        self.chart_utils = None
        self.file_io = None
        self.security = None
        self.currency_converter = None
        self.reminder_manager = None
    
    def build(self):
        """Build the application."""
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "700"
        self.theme_cls.theme_style = "Light"
        
        # Initialize utilities
        self.db = Database("money_manager.db")
        self.chart_utils = ChartUtils()
        self.file_io = FileIO()
        self.security = Security()
        self.currency_converter = CurrencyConverter()
        self.reminder_manager = ReminderManager(self.db)
        
        # Load KV files
        Builder.load_file('kv/dashboard.kv')
        Builder.load_file('kv/transactions.kv')
        Builder.load_file('kv/reports.kv')
        Builder.load_file('kv/accounts.kv')
        Builder.load_file('kv/budgets.kv')
        Builder.load_file('kv/goals.kv')
        Builder.load_file('kv/settings.kv')
        
        # Create screen manager
        sm = ScreenManager()
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(TransactionsScreen(name='transactions'))
        sm.add_widget(ReportsScreen(name='reports'))
        sm.add_widget(AccountsScreen(name='accounts'))
        sm.add_widget(BudgetsScreen(name='budgets'))
        sm.add_widget(GoalsScreen(name='goals'))
        sm.add_widget(SettingsScreen(name='settings'))
        
        # Check recurring transactions on startup
        Clock.schedule_once(lambda dt: self.check_recurring_transactions(), 1)
        
        return sm
    
    def check_recurring_transactions(self):
        """Check and create due recurring transactions."""
        created = self.reminder_manager.create_recurring_transaction_instances()
        if created > 0:
            Snackbar(text=f"Created {created} recurring transaction(s)").open()
    
    def show_transaction_form(self, transaction_type='Expense', edit_transaction=None):
        """Show transaction form dialog."""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.textfield import MDTextField
        from kivymd.uix.button import MDFlatButton, MDRaisedButton
        
        content = MDBoxLayout(orientation='vertical', spacing=15, size_hint_y=None, height=400, padding=20)
        
        # Amount field
        amount_field = MDTextField(
            hint_text="Amount",
            input_filter="float",
        )
        content.add_widget(amount_field)
        
        # Description field
        description_field = MDTextField(
            hint_text="Description",
        )
        content.add_widget(description_field)
        
        # Pre-fill if editing
        if edit_transaction:
            amount_field.text = str(edit_transaction['amount'])
            description_field.text = edit_transaction.get('description', '')
        
        def save_transaction(instance):
            try:
                amount = float(amount_field.text)
                description = description_field.text
                
                # Get default account
                accounts = self.db.get_accounts()
                if not accounts:
                    Snackbar(text="Please create an account first").open()
                    return
                
                account_id = accounts[0]['id']
                
                # Get default category
                categories = self.db.get_categories(transaction_type)
                category_id = categories[0]['id'] if categories else None
                
                transaction = Transaction(
                    transaction_type=transaction_type,
                    amount=amount,
                    description=description,
                    account_id=account_id,
                    category_id=category_id,
                    date=datetime.now()
                )
                
                if edit_transaction:
                    transaction.id = edit_transaction['id']
                    self.db.update_transaction(transaction)
                    Snackbar(text="Transaction updated").open()
                else:
                    self.db.add_transaction(transaction)
                    Snackbar(text="Transaction added").open()
                
                dialog.dismiss()
                
                # Refresh current screen
                if self.root.current == 'dashboard':
                    self.root.get_screen('dashboard').refresh_dashboard()
                elif self.root.current == 'transactions':
                    self.root.get_screen('transactions').load_transactions()
                
            except ValueError:
                Snackbar(text="Please enter a valid amount").open()
        
        dialog = MDDialog(
            title=f"{'Edit' if edit_transaction else 'Add'} {transaction_type}",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="SAVE",
                    on_release=save_transaction
                ),
            ],
        )
        dialog.open()
    
    def show_account_form(self, edit_account=None):
        """Show account form dialog."""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.textfield import MDTextField
        from kivymd.uix.button import MDFlatButton, MDRaisedButton
        
        content = MDBoxLayout(orientation='vertical', spacing=15, size_hint_y=None, height=300, padding=20)
        
        # Account name field
        name_field = MDTextField(hint_text="Account Name")
        content.add_widget(name_field)
        
        # Account type field
        type_field = MDTextField(hint_text="Type (Cash, Bank, Card)")
        content.add_widget(type_field)
        
        # Initial balance field
        balance_field = MDTextField(hint_text="Initial Balance", input_filter="float", text="0")
        content.add_widget(balance_field)
        
        # Pre-fill if editing
        if edit_account:
            name_field.text = edit_account['name']
            type_field.text = edit_account['account_type']
            balance_field.text = str(edit_account['initial_balance'])
        
        def save_account(instance):
            try:
                name = name_field.text
                account_type = type_field.text or "Cash"
                initial_balance = float(balance_field.text or 0)
                
                if not name:
                    Snackbar(text="Please enter account name").open()
                    return
                
                account = Account(
                    name=name,
                    account_type=account_type,
                    initial_balance=initial_balance,
                    current_balance=initial_balance
                )
                
                if edit_account:
                    account.id = edit_account['id']
                    self.db.update_account(account)
                    Snackbar(text="Account updated").open()
                else:
                    self.db.add_account(account)
                    Snackbar(text="Account added").open()
                
                dialog.dismiss()
                
                # Refresh accounts screen if visible
                if self.root.current == 'accounts':
                    self.root.get_screen('accounts').load_accounts()
                
            except ValueError:
                Snackbar(text="Please enter valid values").open()
        
        dialog = MDDialog(
            title=f"{'Edit' if edit_account else 'Add'} Account",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="SAVE",
                    on_release=save_account
                ),
            ],
        )
        dialog.open()
    
    def on_stop(self):
        """Called when app is closing."""
        if self.db:
            self.db.close()


if __name__ == '__main__':
    try:
        app = MoneyManagerApp()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        
        # On Android, write error to log file
        if hasattr(sys, 'getandroidapilevel'):
            try:
                with open('/sdcard/money_manager_error.txt', 'w') as f:
                    f.write(f"Error: {e}\n")
                    traceback.print_exc(file=f)
            except:
                pass

