"""Category and subcategory models for organizing transactions."""
from typing import Optional, Dict


class Category:
    """Represents a transaction category."""
    
    def __init__(self, category_id: Optional[int] = None,
                 name: str = "",
                 category_type: str = "Expense",
                 icon: str = "tag",
                 color: str = "#757575"):
        self.id = category_id
        self.name = name
        self.category_type = category_type  # Expense or Income
        self.icon = icon
        self.color = color
        
    def to_dict(self) -> Dict:
        """Convert category to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'category_type': self.category_type,
            'icon': self.icon,
            'color': self.color
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Category':
        """Create category from dictionary."""
        return Category(
            category_id=data.get('id'),
            name=data.get('name', ''),
            category_type=data.get('category_type', 'Expense'),
            icon=data.get('icon', 'tag'),
            color=data.get('color', '#757575')
        )


class Subcategory:
    """Represents a subcategory under a category."""
    
    def __init__(self, subcategory_id: Optional[int] = None,
                 name: str = "",
                 category_id: Optional[int] = None):
        self.id = subcategory_id
        self.name = name
        self.category_id = category_id
        
    def to_dict(self) -> Dict:
        """Convert subcategory to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'category_id': self.category_id
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Subcategory':
        """Create subcategory from dictionary."""
        return Subcategory(
            subcategory_id=data.get('id'),
            name=data.get('name', ''),
            category_id=data.get('category_id')
        )

