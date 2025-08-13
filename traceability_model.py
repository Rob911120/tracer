# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set
from datetime import datetime
import pandas as pd
from pathlib import Path
import sys

# Ensure UTF-8 encoding for Windows compatibility
if sys.platform == 'win32':
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'sv_SE.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')  
        except locale.Error:
            pass  # Use system default


@dataclass
class TraceabilityItem:
    artikelnummer: str
    artikelbenaming: Optional[str] = None
    batchnummer: Optional[str] = None
    chargenummer: Optional[str] = None
    serienummer: Optional[str] = None
    ordernummer: Optional[str] = None
    source_file: Optional[str] = None
    source_type: Optional[str] = None  # 'spårbarhet', 'lagerlogg', 'nivålista'
    # Hierarchical structure fields
    parent_artikel: Optional[str] = None  # Parent article in BOM structure
    level: int = 0  # Hierarchy level (0 = top level)
    artikeltyp: Optional[str] = None  # From nivålista: 'Tillverkad: Orderstyrd', 'Köpt', etc.
    kvantitet: Optional[float] = None  # Quantity from nivålista
    grundtyp: Optional[str] = None  # Grundtyp from nivålista P51959
    
    def __hash__(self):
        return hash((self.artikelnummer, self.batchnummer, self.chargenummer))
    
    def __eq__(self, other):
        if not isinstance(other, TraceabilityItem):
            return False
        return (self.artikelnummer == other.artikelnummer and 
                self.batchnummer == other.batchnummer and 
                self.chargenummer == other.chargenummer)


@dataclass
class ArticleTraceability:
    artikelnummer: str
    artikelbenaming: Optional[str] = None
    items: List[TraceabilityItem] = field(default_factory=list)
    # Hierarchical structure
    children: List['ArticleTraceability'] = field(default_factory=list)
    parent: Optional['ArticleTraceability'] = None
    level: int = 0
    artikeltyp: Optional[str] = None
    kvantitet: Optional[float] = None
    
    def add_item(self, item: TraceabilityItem):
        if item not in self.items:
            self.items.append(item)
            # Update article metadata from item if available
            if item.artikeltyp and not self.artikeltyp:
                self.artikeltyp = item.artikeltyp
            if item.kvantitet and not self.kvantitet:
                self.kvantitet = item.kvantitet
    
    def add_child(self, child: 'ArticleTraceability'):
        if child not in self.children:
            self.children.append(child)
            child.parent = self
            child.level = self.level + 1
    
    def get_unique_batch_numbers(self) -> Set[str]:
        return {item.batchnummer for item in self.items if item.batchnummer}
    
    def get_unique_charge_numbers(self) -> Set[str]:
        return {item.chargenummer for item in self.items if item.chargenummer}


class TraceabilityDatabase:
    def __init__(self):
        self.articles: Dict[str, ArticleTraceability] = {}
        self.loaded_files: Set[str] = set()
        self.original_order: List[str] = []  # Keep track of original article order
        self.all_items_in_order: List[TraceabilityItem] = []  # Keep ALL items in original order
    
    def add_item(self, item: TraceabilityItem):
        if item.artikelnummer not in self.articles:
            self.articles[item.artikelnummer] = ArticleTraceability(
                artikelnummer=item.artikelnummer,
                artikelbenaming=item.artikelbenaming
            )
        
        # Update artikelbenaming if not set and available in item
        if not self.articles[item.artikelnummer].artikelbenaming and item.artikelbenaming:
            self.articles[item.artikelnummer].artikelbenaming = item.artikelbenaming
        
        self.articles[item.artikelnummer].add_item(item)
        
        if item.source_file:
            self.loaded_files.add(item.source_file)
    
    def add_item_with_hierarchy(self, item: TraceabilityItem):
        """Add item with hierarchical structure from nivålista"""
        # Store ALL items in original order (including duplicates)
        self.all_items_in_order.append(item)
        
        # First add the item normally (this creates unique articles)
        self.add_item(item)
        
        # Track original order for export (unique articles only)
        if item.artikelnummer not in self.original_order:
            self.original_order.append(item.artikelnummer)
        
        # Set up hierarchical relationships
        article = self.articles[item.artikelnummer]
        article.level = item.level
        article.artikeltyp = item.artikeltyp
        article.kvantitet = item.kvantitet
        
        # Store parent relationship for later processing if parent doesn't exist yet
        if hasattr(article, '_pending_parent'):
            article._pending_parent = item.parent_artikel
        else:
            article._pending_parent = item.parent_artikel
        
        # Establish parent-child relationship if parent exists
        if item.parent_artikel and item.parent_artikel in self.articles:
            parent = self.articles[item.parent_artikel]
            parent.add_child(article)
        
        # Check if this item can be a parent to any pending children
        self._resolve_pending_relationships(item.artikelnummer)
        
    def _resolve_pending_relationships(self, parent_artikelnummer: str):
        """Resolve any pending parent-child relationships for this parent"""
        parent_article = self.articles.get(parent_artikelnummer)
        if not parent_article:
            return
            
        # Look for articles that are waiting for this parent
        for article in self.articles.values():
            if (hasattr(article, '_pending_parent') and 
                article._pending_parent == parent_artikelnummer and
                article.parent is None):  # Not already assigned
                parent_article.add_child(article)
                article._pending_parent = None  # Clear pending status
    
    def get_article(self, artikelnummer: str) -> Optional[ArticleTraceability]:
        return self.articles.get(artikelnummer)
    
    def get_all_articles(self) -> List[ArticleTraceability]:
        return list(self.articles.values())
    
    def export_to_dataframe(self) -> pd.DataFrame:
        """Export to DataFrame for Excel export (flattened structure)"""
        rows = []
        
        # Get top-level articles (those without parents)
        top_level_articles = [art for art in self.articles.values() if art.level == 0]
        
        # If no hierarchical structure, fall back to old behavior
        if not top_level_articles:
            top_level_articles = list(self.articles.values())
        
        for article in top_level_articles:
            self._add_article_to_export(article, rows)
        
        return pd.DataFrame(rows)
    
    def _add_article_to_export(self, article: ArticleTraceability, rows: List[Dict], indent_level: int = 0, is_last_sibling: bool = True, parent_prefixes: List[str] = None):
        """Recursively add article and its children to export rows"""
        if parent_prefixes is None:
            parent_prefixes = []
            
        batch_numbers = list(article.get_unique_batch_numbers())
        charge_numbers = list(article.get_unique_charge_numbers())
        
        # Create hierarchy visualization using Excel-like symbols
        if indent_level == 0:
            display_name = article.artikelnummer
            prefix = ""
            current_prefix = ""  # No prefix for top level
        else:
            # Build the prefix from parent levels
            prefix = "".join(parent_prefixes)
            
            # Add the current level's symbol
            if is_last_sibling:
                prefix += "└─ "
                current_prefix = "   "  # Three spaces for continuation
            else:
                prefix += "├─ "
                current_prefix = "│  "  # Vertical line with space for continuation
            
            display_name = f"{prefix}{article.artikelnummer}"
        
        if not batch_numbers and not charge_numbers:
            rows.append({
                'Artikelnummer': display_name,
                'Artikelbenämning': article.artikelbenaming,
                'Artikeltyp': article.artikeltyp,
                'Kvantitet': article.kvantitet,
                'Batchnummer': '',
                'Chargenummer': '',
                'Antal källor': len(article.items),
                'Nivå': indent_level
            })
        else:
            max_len = max(len(batch_numbers), len(charge_numbers), 1)
            for i in range(max_len):
                rows.append({
                    'Artikelnummer': display_name if i == 0 else '',
                    'Artikelbenämning': article.artikelbenaming if i == 0 else '',
                    'Artikeltyp': article.artikeltyp if i == 0 else '',
                    'Kvantitet': article.kvantitet if i == 0 else '',
                    'Batchnummer': batch_numbers[i] if i < len(batch_numbers) else '',
                    'Chargenummer': charge_numbers[i] if i < len(charge_numbers) else '',
                    'Antal källor': len(article.items) if i == 0 else '',
                    'Nivå': indent_level if i == 0 else ''
                })
        
        # Add children recursively
        for i, child in enumerate(article.children):
            is_last_child = (i == len(article.children) - 1)
            
            # Calculate new parent prefixes for this child
            new_parent_prefixes = parent_prefixes.copy()
            if indent_level > 0:
                new_parent_prefixes.append(current_prefix)
            
            self._add_article_to_export(child, rows, indent_level + 1, is_last_child, new_parent_prefixes)
    
    def clear(self):
        self.articles.clear()
        self.loaded_files.clear()
        self.all_items_in_order.clear()
        self.original_order.clear()