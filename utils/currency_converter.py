"""Currency converter utilities for multi-currency support."""
from typing import Dict, Optional
from datetime import datetime


class CurrencyConverter:
    """Simple currency converter with manual exchange rates."""
    
    # Default exchange rates (relative to USD)
    DEFAULT_RATES = {
        'USD': 1.0,
        'EUR': 0.85,
        'GBP': 0.73,
        'JPY': 110.0,
        'INR': 74.0,
        'AUD': 1.35,
        'CAD': 1.25,
        'CHF': 0.92,
        'CNY': 6.45,
        'BRL': 5.25,
        'ZAR': 14.50,
        'MXN': 20.0
    }
    
    def __init__(self):
        """Initialize currency converter with default rates."""
        self.rates = self.DEFAULT_RATES.copy()
        self.base_currency = 'USD'
        self.last_updated = datetime.now()
    
    def set_rate(self, currency: str, rate: float):
        """Set exchange rate for a currency."""
        self.rates[currency] = rate
        self.last_updated = datetime.now()
    
    def get_rate(self, currency: str) -> Optional[float]:
        """Get exchange rate for a currency."""
        return self.rates.get(currency)
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert amount from one currency to another."""
        if from_currency == to_currency:
            return amount
        
        if from_currency not in self.rates or to_currency not in self.rates:
            return amount  # Return original if currency not found
        
        # Convert to base currency first, then to target currency
        amount_in_base = amount / self.rates[from_currency]
        amount_in_target = amount_in_base * self.rates[to_currency]
        
        return round(amount_in_target, 2)
    
    def get_all_currencies(self) -> list:
        """Get list of all supported currencies."""
        return list(self.rates.keys())
    
    def format_amount(self, amount: float, currency: str) -> str:
        """Format amount with currency symbol."""
        symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
            'INR': '₹',
            'AUD': 'A$',
            'CAD': 'C$',
            'CHF': 'Fr',
            'CNY': '¥',
            'BRL': 'R$',
            'ZAR': 'R',
            'MXN': '$'
        }
        
        symbol = symbols.get(currency, currency)
        return f"{symbol}{amount:,.2f}"
    
    def get_currency_info(self) -> Dict:
        """Get information about all currencies."""
        currency_names = {
            'USD': 'US Dollar',
            'EUR': 'Euro',
            'GBP': 'British Pound',
            'JPY': 'Japanese Yen',
            'INR': 'Indian Rupee',
            'AUD': 'Australian Dollar',
            'CAD': 'Canadian Dollar',
            'CHF': 'Swiss Franc',
            'CNY': 'Chinese Yuan',
            'BRL': 'Brazilian Real',
            'ZAR': 'South African Rand',
            'MXN': 'Mexican Peso'
        }
        
        return {
            code: {
                'name': currency_names.get(code, code),
                'rate': self.rates.get(code, 1.0)
            }
            for code in self.rates.keys()
        }

