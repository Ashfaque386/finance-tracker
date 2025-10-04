"""Chart and visualization utilities using Matplotlib."""
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Kivy
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import io
from typing import List, Dict, Tuple
from datetime import datetime
import os


class ChartUtils:
    """Utilities for creating charts and visualizations."""
    
    @staticmethod
    def create_pie_chart(data: List[Tuple], title: str = "Expenses by Category", 
                        filename: str = "pie_chart.png") -> str:
        """Create a pie chart for expenses by category."""
        if not data:
            return None
        
        labels = [row[0] for row in data]
        sizes = [row[2] for row in data]
        colors = [row[1] for row in data]
        
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
               startangle=90, textprops={'fontsize': 10})
        ax.axis('equal')
        plt.title(title, fontsize=14, fontweight='bold')
        
        # Save to file
        filepath = os.path.join("charts", filename)
        os.makedirs("charts", exist_ok=True)
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    @staticmethod
    def create_bar_chart(data: List[Dict], title: str = "Income vs Expense", 
                        filename: str = "bar_chart.png") -> str:
        """Create a bar chart for income vs expense over time."""
        if not data:
            return None
        
        months = [item['month'] for item in data]
        income = [item['income'] for item in data]
        expense = [item['expense'] for item in data]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = range(len(months))
        width = 0.35
        
        ax.bar([i - width/2 for i in x], income, width, label='Income', color='#4CAF50')
        ax.bar([i + width/2 for i in x], expense, width, label='Expense', color='#F44336')
        
        ax.set_xlabel('Month', fontweight='bold')
        ax.set_ylabel('Amount', fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(months, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # Save to file
        filepath = os.path.join("charts", filename)
        os.makedirs("charts", exist_ok=True)
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    @staticmethod
    def create_line_chart(data: List[Dict], title: str = "Spending Trend", 
                         filename: str = "line_chart.png") -> str:
        """Create a line chart for spending trends over time."""
        if not data:
            return None
        
        months = [item['month'] for item in data]
        income = [item['income'] for item in data]
        expense = [item['expense'] for item in data]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(months, income, marker='o', linewidth=2, label='Income', color='#4CAF50')
        ax.plot(months, expense, marker='s', linewidth=2, label='Expense', color='#F44336')
        
        # Calculate and plot net (income - expense)
        net = [i - e for i, e in zip(income, expense)]
        ax.plot(months, net, marker='^', linewidth=2, label='Net', color='#2196F3', linestyle='--')
        
        ax.set_xlabel('Month', fontweight='bold')
        ax.set_ylabel('Amount', fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        
        # Add zero line
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        # Save to file
        filepath = os.path.join("charts", filename)
        os.makedirs("charts", exist_ok=True)
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    @staticmethod
    def create_budget_chart(budgets: List[Dict], filename: str = "budget_chart.png") -> str:
        """Create a horizontal bar chart for budget usage."""
        if not budgets:
            return None
        
        categories = [b.get('category_name', 'Unknown') for b in budgets]
        amounts = [b['amount'] for b in budgets]
        spent = [b['spent'] for b in budgets]
        
        fig, ax = plt.subplots(figsize=(10, max(6, len(budgets) * 0.5)))
        
        y_pos = range(len(categories))
        
        # Plot budget amounts (background)
        ax.barh(y_pos, amounts, color='#E0E0E0', label='Budget')
        
        # Plot spent amounts (foreground) with color coding
        colors = ['#F44336' if s > a else '#FFC107' if s > a * 0.8 else '#4CAF50' 
                  for s, a in zip(spent, amounts)]
        ax.barh(y_pos, spent, color=colors, label='Spent')
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(categories)
        ax.set_xlabel('Amount', fontweight='bold')
        ax.set_title('Budget Usage', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(axis='x', alpha=0.3)
        
        # Save to file
        filepath = os.path.join("charts", filename)
        os.makedirs("charts", exist_ok=True)
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    @staticmethod
    def create_account_balance_chart(accounts: List[Dict], filename: str = "account_chart.png") -> str:
        """Create a bar chart showing account balances."""
        if not accounts:
            return None
        
        names = [acc['name'] for acc in accounts]
        balances = [acc['current_balance'] for acc in accounts]
        colors = [acc.get('color', '#2196F3') for acc in accounts]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars = ax.bar(names, balances, color=colors)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height:.2f}',
                   ha='center', va='bottom', fontweight='bold')
        
        ax.set_xlabel('Account', fontweight='bold')
        ax.set_ylabel('Balance', fontweight='bold')
        ax.set_title('Account Balances', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        
        # Save to file
        filepath = os.path.join("charts", filename)
        os.makedirs("charts", exist_ok=True)
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    @staticmethod
    def cleanup_old_charts():
        """Remove old chart files."""
        charts_dir = "charts"
        if os.path.exists(charts_dir):
            for file in os.listdir(charts_dir):
                if file.endswith(".png"):
                    try:
                        os.remove(os.path.join(charts_dir, file))
                    except:
                        pass

