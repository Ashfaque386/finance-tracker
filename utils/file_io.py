"""File import/export utilities for backup and data exchange."""
import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import shutil


class FileIO:
    """Utilities for importing and exporting data."""
    
    @staticmethod
    def export_to_json(data: Dict, filepath: str) -> bool:
        """Export data to JSON file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    @staticmethod
    def import_from_json(filepath: str) -> Optional[Dict]:
        """Import data from JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error importing from JSON: {e}")
            return None
    
    @staticmethod
    def export_transactions_to_csv(transactions: List[Dict], filepath: str) -> bool:
        """Export transactions to CSV file."""
        try:
            if not transactions:
                return False
            
            # Define CSV columns
            fieldnames = [
                'id', 'date', 'time', 'transaction_type', 'amount', 
                'category_name', 'account_name', 'description', 
                'payment_method', 'tags'
            ]
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(transactions)
            
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    @staticmethod
    def import_transactions_from_csv(filepath: str) -> Optional[List[Dict]]:
        """Import transactions from CSV file."""
        try:
            transactions = []
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    transactions.append(dict(row))
            return transactions
        except Exception as e:
            print(f"Error importing from CSV: {e}")
            return None
    
    @staticmethod
    def create_backup(db_path: str, backup_dir: str = "backups") -> Optional[str]:
        """Create a backup of the database."""
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"money_manager_backup_{timestamp}.db"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            shutil.copy2(db_path, backup_path)
            
            return backup_path
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
    
    @staticmethod
    def restore_backup(backup_path: str, db_path: str) -> bool:
        """Restore database from backup."""
        try:
            if not os.path.exists(backup_path):
                return False
            
            # Create a backup of current database before restoring
            if os.path.exists(db_path):
                current_backup = f"{db_path}.before_restore"
                shutil.copy2(db_path, current_backup)
            
            shutil.copy2(backup_path, db_path)
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
    
    @staticmethod
    def list_backups(backup_dir: str = "backups") -> List[str]:
        """List all available backups."""
        try:
            if not os.path.exists(backup_dir):
                return []
            
            backups = [f for f in os.listdir(backup_dir) if f.endswith('.db')]
            backups.sort(reverse=True)  # Most recent first
            return backups
        except Exception as e:
            print(f"Error listing backups: {e}")
            return []
    
    @staticmethod
    def export_report_data(data: Dict, filepath: str, format: str = 'json') -> bool:
        """Export report data in specified format."""
        try:
            if format == 'json':
                return FileIO.export_to_json(data, filepath)
            elif format == 'csv':
                # Flatten complex data for CSV export
                if 'transactions' in data:
                    return FileIO.export_transactions_to_csv(data['transactions'], filepath)
            return False
        except Exception as e:
            print(f"Error exporting report: {e}")
            return False
    
    @staticmethod
    def auto_cleanup_old_backups(backup_dir: str = "backups", keep_count: int = 10):
        """Automatically remove old backups, keeping only the most recent."""
        try:
            backups = FileIO.list_backups(backup_dir)
            
            if len(backups) > keep_count:
                for backup in backups[keep_count:]:
                    backup_path = os.path.join(backup_dir, backup)
                    os.remove(backup_path)
        except Exception as e:
            print(f"Error cleaning up backups: {e}")
    
    @staticmethod
    def validate_import_data(data: Dict, data_type: str = 'full') -> Tuple[bool, str]:
        """Validate imported data structure."""
        try:
            if data_type == 'full':
                required_keys = ['transactions', 'accounts', 'categories']
                for key in required_keys:
                    if key not in data:
                        return False, f"Missing required key: {key}"
            
            elif data_type == 'transactions':
                if not isinstance(data, list):
                    return False, "Transactions data must be a list"
                
                required_fields = ['transaction_type', 'amount', 'date']
                for trans in data:
                    for field in required_fields:
                        if field not in trans:
                            return False, f"Transaction missing required field: {field}"
            
            return True, "Data validation successful"
        except Exception as e:
            return False, f"Validation error: {e}"

