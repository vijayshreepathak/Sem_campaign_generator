"""
SEM Campaign Generator Package

A comprehensive tool for building structured SEM campaigns including
Search, Shopping, and Performance Max campaigns.

Author: Vijayshree Vaibhav (Ex-Snapchat, Cube)
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Vijayshree Vaibhav"
__email__ = "vijayshree@example.com"

# Package-level imports
from .config_loader import ConfigLoader
from .keyword_generator import KeywordGenerator
from .data_processor import DataProcessor
from .campaign_builder import CampaignBuilder
from .export_manager import ExportManager

__all__ = [
    'ConfigLoader',
    'KeywordGenerator', 
    'DataProcessor',
    'CampaignBuilder',
    'ExportManager'
]