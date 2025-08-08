"""
Utility Functions Module
Common utility functions used across the project.
"""

import os
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

def ensure_directory(path: str) -> None:
    """
    Ensure that a directory exists, create it if it doesn't.
    
    Args:
        path: Directory path to ensure exists
    """
    Path(path).mkdir(parents=True, exist_ok=True)

def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate configuration dictionary.
    
    Args:
        config: Configuration dictionary to validate
        
    Raises:
        ValueError: If configuration is invalid
    """
    # Check required top-level keys
    required_keys = ['brand', 'competitor', 'budgets', 'campaign_constraints']
    missing_keys = [key for key in required_keys if key not in config]
    
    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {missing_keys}")
    
    # Validate budget values
    budgets = config['budgets']
    budget_keys = ['search_ads', 'shopping_ads', 'pmax_ads', 'total_monthly']
    
    for key in budget_keys:
        if key not in budgets:
            raise ValueError(f"Missing budget key: {key}")
        
        if not isinstance(budgets[key], (int, float)) or budgets[key] < 0:
            raise ValueError(f"Budget {key} must be a positive number")
    
    # Validate constraint values
    constraints = config['campaign_constraints']
    constraint_keys = ['min_search_volume', 'target_conversion_rate', 'target_cpa', 'max_cpc']
    
    for key in constraint_keys:
        if key not in constraints:
            raise ValueError(f"Missing constraint key: {key}")
        
        if not isinstance(constraints[key], (int, float)) or constraints[key] <= 0:
            raise ValueError(f"Constraint {key} must be a positive number")
    
    # Validate conversion rate is reasonable (between 0 and 1)
    if not 0 < constraints['target_conversion_rate'] <= 1:
        raise ValueError("target_conversion_rate must be between 0 and 1")

def format_currency(amount: float) -> str:
    """
    Format number as currency string.
    
    Args:
        amount: Amount to format
        
    Returns:
        Formatted currency string
    """
    return f"${amount:,.2f}"

def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format number as percentage string.
    
    Args:
        value: Value to format (as decimal, e.g., 0.02 for 2%)
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    percentage = value * 100
    return f"{percentage:.{decimal_places}f}%"

def clean_keyword(keyword: str) -> str:
    """
    Clean and normalize a keyword string.
    
    Args:
        keyword: Raw keyword string
        
    Returns:
        Cleaned keyword string
    """
    if not isinstance(keyword, str):
        return str(keyword).lower().strip()
    
    # Convert to lowercase and strip whitespace
    cleaned = keyword.lower().strip()
    
    # Remove multiple spaces
    cleaned = ' '.join(cleaned.split())
    
    # Remove special characters except hyphens and spaces
    import re
    cleaned = re.sub(r'[^a-zA-Z0-9\s\-]', '', cleaned)
    
    return cleaned

def calculate_cpc_from_cpa(target_cpa: float, conversion_rate: float) -> float:
    """
    Calculate target CPC from target CPA and conversion rate.
    
    Args:
        target_cpa: Target cost per acquisition
        conversion_rate: Expected conversion rate (as decimal)
        
    Returns:
        Target CPC
    """
    return round(target_cpa * conversion_rate, 2)

def estimate_budget_distribution(total_budget: float, priorities: List[str]) -> Dict[str, float]:
    """
    Distribute budget based on priority levels.
    
    Args:
        total_budget: Total budget to distribute
        priorities: List of priority levels ('High', 'Medium', 'Low')
        
    Returns:
        Dictionary mapping priorities to budget amounts
    """
    priority_weights = {'High': 1.5, 'Medium': 1.0, 'Low': 0.7}
    
    # Calculate total weight
    total_weight = sum(priority_weights.get(priority, 1.0) for priority in priorities)
    
    # Distribute budget proportionally
    budget_distribution = {}
    for priority in set(priorities):
        weight = priority_weights.get(priority, 1.0)
        count = priorities.count(priority)
        budget_distribution[priority] = round((weight * count / total_weight) * total_budget, 0)
    
    return budget_distribution

def validate_dataframe_columns(df: pd.DataFrame, required_columns: List[str], df_name: str = "DataFrame") -> None:
    """
    Validate that DataFrame contains required columns.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        df_name: Name of DataFrame for error messages
        
    Raises:
        ValueError: If required columns are missing
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"{df_name} missing required columns: {missing_columns}")

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator  
        default: Default value to return if denominator is zero
        
    Returns:
        Result of division or default value
    """
    if denominator == 0:
        return default
    return numerator / denominator

def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate string to maximum length with optional suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def get_file_size_mb(filepath: str) -> float:
    """
    Get file size in megabytes.
    
    Args:
        filepath: Path to file
        
    Returns:
        File size in MB
    """
    try:
        size_bytes = os.path.getsize(filepath)
        return round(size_bytes / (1024 * 1024), 2)
    except OSError:
        return 0.0

def create_backup_filename(original_path: str) -> str:
    """
    Create backup filename with timestamp.
    
    Args:
        original_path: Original file path
        
    Returns:
        Backup file path with timestamp
    """
    from datetime import datetime
    
    path = Path(original_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    backup_name = f"{path.stem}_backup_{timestamp}{path.suffix}"
    return str(path.parent / backup_name)

def log_performance_metrics(df: pd.DataFrame, operation_name: str) -> None:
    """
    Log performance metrics for DataFrame operations.
    
    Args:
        df: DataFrame to analyze
        operation_name: Name of operation for logging
    """
    print(f"📊 {operation_name} Performance Metrics:")
    print(f"   Rows: {len(df):,}")
    print(f"   Columns: {len(df.columns)}")
    print(f"   Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    if 'composite_score' in df.columns:
        print(f"   Avg Composite Score: {df['composite_score'].mean():.2f}")
        print(f"   Score Range: {df['composite_score'].min():.2f} - {df['composite_score'].max():.2f}")
