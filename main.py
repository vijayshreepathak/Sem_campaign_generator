"""
SEM Campaign Generator - Complete Project
Author: Vijayshree Vaibhav (Ex-Snapchat, Cube)
Version: 1.0.0
"""

import sys
import os
import argparse
from pathlib import Path
from colorama import init, Fore, Style
import traceback

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def print_banner():
    """Print project banner."""
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("=" * 60)
    print("  SEM CAMPAIGN GENERATOR")
    print("  Author: Vijayshree Vaibhav (Ex-Snapchat, Cube)")
    print("  Version: 1.0.0")
    print("=" * 60)
    print(f"{Style.RESET_ALL}")

def print_step(step_num, description):
    """Print step information."""
    print(f"\n{Fore.YELLOW}📋 Step {step_num}: {description}{Style.RESET_ALL}")

def print_success(message):
    """Print success message."""
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")

def print_error(message):
    """Print error message."""
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="SEM Campaign Generator - Build complete SEM strategies"
    )
    parser.add_argument(
        "--config", 
        default="config.yaml", 
        help="Path to configuration file"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )
    parser.add_argument(
        "--output-dir", 
        default=None, 
        help="Override output directory"
    )
    
    args = parser.parse_args()
    
    try:
        print_banner()
        
        # Import modules after path setup
        from config_loader import ConfigLoader
        from keyword_generator import KeywordGenerator
        from data_processor import DataProcessor
        from campaign_builder import CampaignBuilder
        from export_manager import ExportManager
        from utils import ensure_directory, validate_config
        
        print_step(1, "Loading Configuration")
        config_loader = ConfigLoader()
        config = config_loader.load_config(args.config)
        
        if args.output_dir:
            config['output_settings']['directory'] = args.output_dir
        
        validate_config(config)
        print_success(f"Configuration loaded from: {args.config}")
        
        print_step(2, "Setting Up Output Directory")
        output_dir = config['output_settings']['directory']
        ensure_directory(output_dir)
        print_success(f"Output directory ready: {output_dir}")
        
        print_step(3, "Generating Keywords")
        keyword_gen = KeywordGenerator(config)
        raw_keywords = keyword_gen.generate_keywords()
        print_success(f"Generated {len(raw_keywords)} raw keywords")
        
        print_step(4, "Processing and Filtering Keywords")
        processor = DataProcessor(config)
        processed_keywords = processor.process_keywords(raw_keywords)
        print_success(f"Processed to {len(processed_keywords)} filtered keywords")
        
        print_step(5, "Building Campaign Structures")
        campaign_builder = CampaignBuilder(config)
        
        # Build all campaign components
        search_adgroups = campaign_builder.build_search_campaigns(processed_keywords)
        pmax_themes = campaign_builder.build_pmax_campaigns(processed_keywords)
        shopping_bids = campaign_builder.build_shopping_campaigns(processed_keywords)
        
        print_success(f"Built {len(search_adgroups)} search ad groups")
        print_success(f"Built {len(pmax_themes)} Performance Max themes")
        print_success(f"Built {len(shopping_bids)} shopping bid recommendations")
        
        print_step(6, "Exporting Results")
        export_manager = ExportManager(config)
        
        # Export all deliverables
        export_files = export_manager.export_all_deliverables(
            raw_keywords=raw_keywords,
            processed_keywords=processed_keywords,
            search_adgroups=search_adgroups,
            pmax_themes=pmax_themes,
            shopping_bids=shopping_bids
        )
        
        print_success("All deliverables exported successfully")
        
        # Print summary
        print(f"\n{Fore.CYAN}{Style.BRIGHT}📊 CAMPAIGN SUMMARY{Style.RESET_ALL}")
        print(f"Total Keywords Processed: {len(processed_keywords)}")
        print(f"Search Ad Groups: {search_adgroups['ad_group'].nunique()}")
        print(f"Performance Max Themes: {len(pmax_themes)}")
        print(f"Shopping Products: {len(shopping_bids)}")
        print(f"Total Budget: ${config['budgets']['total_monthly']:,}")
        
        print(f"\n{Fore.CYAN}📁 Output Files:{Style.RESET_ALL}")
        for file_path in export_files:
            print(f"  • {file_path}")
        
        print(f"\n{Fore.GREEN}{Style.BRIGHT}🎉 SEM Campaign Generation Complete!{Style.RESET_ALL}")
        
    except ImportError as e:
        print_error(f"Import Error: {e}")
        print("Please install required packages: pip install -r requirements.txt")
        sys.exit(1)
        
    except FileNotFoundError as e:
        print_error(f"File not found: {e}")
        print("Please ensure all required files exist")
        sys.exit(1)
        
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if args.verbose:
            print(f"\n{Fore.RED}Full traceback:{Style.RESET_ALL}")
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()