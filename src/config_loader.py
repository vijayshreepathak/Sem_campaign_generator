
"""
Configuration Loader Module
Handles loading and validation of YAML configuration files.
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any

class ConfigLoader:
    """Handles configuration loading and validation."""
    
    def __init__(self):
        self.required_sections = [
            'brand', 'competitor', 'budgets', 'campaign_constraints', 'seed_keywords'
        ]
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to the YAML configuration file
            
        Returns:
            Dictionary containing configuration data
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
            ValueError: If required sections are missing
        """
        if not Path(config_path).exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML in config file: {e}")
        
        # Validate required sections
        self._validate_required_sections(config)
        
        # Set defaults for optional sections
        config = self._set_defaults(config)
        
        return config
    
    def _validate_required_sections(self, config: Dict[str, Any]) -> None:
        """Validate that all required sections are present."""
        missing_sections = [
            section for section in self.required_sections 
            if section not in config
        ]
        
        if missing_sections:
            raise ValueError(f"Missing required config sections: {missing_sections}")
    
    def _set_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Set default values for optional configuration sections."""
        
        # Default output settings
        config.setdefault('output_settings', {})
        config['output_settings'].setdefault('directory', 'output')
        config['output_settings'].setdefault('file_formats', ['xlsx', 'csv'])
        config['output_settings'].setdefault('include_charts', False)
        
        # Default execution settings
        config.setdefault('execution_settings', {})
        config['execution_settings'].setdefault('verbose_logging', True)
        config['execution_settings'].setdefault('save_intermediate_files', True)
        config['execution_settings'].setdefault('parallel_processing', False)
        
        # Default data source settings
        config.setdefault('data_sources', {})
        config['data_sources'].setdefault('use_simulated_data', True)
        config['data_sources'].setdefault('planner_csv_path', '')
        config['data_sources'].setdefault('external_api_enabled', False)
        
        # Default service locations if not provided
        config.setdefault('service_locations', ['Mumbai', 'Delhi', 'Bengaluru'])
        
        return config
    
    def validate_budget_allocation(self, config: Dict[str, Any]) -> bool:
        """
        Validate that budget allocation is reasonable.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if budget allocation is valid, False otherwise
        """
        budgets = config['budgets']
        
        allocated_budget = (
            budgets.get('search_ads', 0) + 
            budgets.get('shopping_ads', 0) + 
            budgets.get('pmax_ads', 0)
        )
        
        total_budget = budgets.get('total_monthly', allocated_budget)
        
        if allocated_budget > total_budget * 1.05:  # 5% tolerance
            print(f"⚠️  Warning: Allocated budget (${allocated_budget:,}) exceeds total budget (${total_budget:,})")
            return False
        
        return True
    
    def get_config_summary(self, config: Dict[str, Any]) -> str:
        """
        Generate a summary of the configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            String summary of configuration
        """
        summary = []
        summary.append(f"Brand: {config['brand']['name']}")
        summary.append(f"Competitor: {config['competitor']['name']}")
        summary.append(f"Locations: {len(config['service_locations'])} cities")
        summary.append(f"Total Budget: ${config['budgets']['total_monthly']:,}")
        summary.append(f"Seed Keywords: {len(config['seed_keywords'])}")
        summary.append(f"Min Search Volume: {config['campaign_constraints']['min_search_volume']:,}")
        
        return "\n".join(summary)