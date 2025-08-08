"""
Keyword Generator Module
Generates and expands keywords from seed keywords and competitor analysis.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any
import itertools
from pathlib import Path

class KeywordGenerator:
    """Generates keywords from various sources."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.brand_name = config['brand']['name'].lower()
        self.competitor_name = config['competitor']['name'].lower()
        self.locations = [loc.lower() for loc in config['service_locations']]
        self.seed_keywords = [kw.lower().strip() for kw in config['seed_keywords']]
        
        # Set random seed for reproducible results
        np.random.seed(42)
    
    def generate_keywords(self) -> pd.DataFrame:
        """
        Generate comprehensive keyword list from all sources.
        
        Returns:
            DataFrame with columns: keyword, source, estimated_volume, 
            estimated_cpc_low, estimated_cpc_high, estimated_competition
        """
        all_keywords = []
        
        # Generate from different sources
        all_keywords.extend(self._generate_from_seeds())
        all_keywords.extend(self._generate_location_variants())
        all_keywords.extend(self._generate_commercial_variants())
        all_keywords.extend(self._generate_brand_variants())
        all_keywords.extend(self._generate_competitor_variants())
        all_keywords.extend(self._generate_long_tail_variants())
        
        # Convert to DataFrame and add simulated metrics
        df = pd.DataFrame(all_keywords)
        df = self._add_simulated_metrics(df)
        df = self._clean_and_deduplicate(df)
        
        return df
    
    def _generate_from_seeds(self) -> List[Dict[str, str]]:
        """Generate keywords directly from seed keywords."""
        keywords = []
        for seed in self.seed_keywords:
            keywords.append({
                'keyword': seed,
                'source': 'seed_direct'
            })
        return keywords
    
    def _generate_location_variants(self) -> List[Dict[str, str]]:
        """Generate location-based keyword variants."""
        keywords = []
        location_patterns = [
            "{keyword} {location}",
            "{keyword} in {location}",
            "best {keyword} {location}",
            "{keyword} near {location}",
            "{location} {keyword}",
            "{keyword} delivery {location}"
        ]
        
        for seed in self.seed_keywords:
            for location in self.locations:
                for pattern in location_patterns:
                    keyword = pattern.format(keyword=seed, location=location)
                    keywords.append({
                        'keyword': keyword,
                        'source': 'location_variant'
                    })
        
        return keywords
    
    def _generate_commercial_variants(self) -> List[Dict[str, str]]:
        """Generate commercial intent keyword variants."""
        keywords = []
        commercial_patterns = [
            "buy {keyword}",
            "{keyword} price",
            "{keyword} cost",
            "{keyword} online",
            "best {keyword}",
            "{keyword} review",
            "{keyword} reviews",
            "cheap {keyword}",
            "{keyword} discount",
            "{keyword} deals",
            "{keyword} offers",
            "order {keyword}",
            "{keyword} purchase",
            "where to buy {keyword}",
            "{keyword} for sale"
        ]
        
        for seed in self.seed_keywords:
            for pattern in commercial_patterns:
                keyword = pattern.format(keyword=seed)
                keywords.append({
                    'keyword': keyword,
                    'source': 'commercial_variant'
                })
        
        return keywords
    
    def _generate_brand_variants(self) -> List[Dict[str, str]]:
        """Generate brand-related keyword variants."""
        keywords = []
        brand_patterns = [
            "{brand} {keyword}",
            "{keyword} {brand}",
            "{brand}",
            "{brand} official",
            "{brand} website",
            "{brand} store",
            "{brand} products",
            "{brand} reviews",
            "{brand} price",
            "{brand} contact",
            "{brand} support"
        ]
        
        for pattern in brand_patterns:
            if "{keyword}" in pattern:
                for seed in self.seed_keywords:
                    keyword = pattern.format(brand=self.brand_name, keyword=seed)
                    keywords.append({
                        'keyword': keyword,
                        'source': 'brand_variant'
                    })
            else:
                keyword = pattern.format(brand=self.brand_name)
                keywords.append({
                    'keyword': keyword,
                    'source': 'brand_variant'
                })
        
        return keywords
    
    def _generate_competitor_variants(self) -> List[Dict[str, str]]:
        """Generate competitor-related keyword variants."""
        keywords = []
        competitor_patterns = [
            "{competitor} alternative",
            "alternative to {competitor}",
            "{competitor} vs {brand}",
            "{brand} vs {competitor}",
            "{competitor} competitor",
            "better than {competitor}",
            "{competitor} replacement",
            "like {competitor} but better"
        ]
        
        for pattern in competitor_patterns:
            keyword = pattern.format(
                competitor=self.competitor_name, 
                brand=self.brand_name
            )
            keywords.append({
                'keyword': keyword,
                'source': 'competitor_variant'
            })
        
        return keywords
    
    def _generate_long_tail_variants(self) -> List[Dict[str, str]]:
        """Generate long-tail informational keyword variants."""
        keywords = []
        longtail_patterns = [
            "how to use {keyword}",
            "what is {keyword}",
            "{keyword} benefits",
            "{keyword} side effects",
            "{keyword} dosage",
            "best time to take {keyword}",
            "{keyword} for beginners",
            "{keyword} vs protein powder",
            "natural {keyword}",
            "organic {keyword}",
            "{keyword} guide",
            "{keyword} tips",
            "why use {keyword}",
            "{keyword} ingredients",
            "{keyword} nutrition facts"
        ]
        
        for seed in self.seed_keywords:
            for pattern in longtail_patterns:
                keyword = pattern.format(keyword=seed)
                keywords.append({
                    'keyword': keyword,
                    'source': 'longtail_variant'
                })
        
        return keywords
    
    def _add_simulated_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add simulated search volume and CPC metrics."""
        
        def get_volume_estimate(keyword, source):
            """Estimate search volume based on keyword characteristics."""
            base_volume = np.random.randint(500, 5000)
            
            # Adjust based on keyword characteristics
            if source == 'seed_direct':
                base_volume *= 1.5
            elif source == 'brand_variant':
                if self.brand_name in keyword:
                    base_volume *= 0.3  # Brand searches are typically lower volume
            elif source == 'location_variant':
                base_volume *= 0.8
            elif source == 'commercial_variant':
                if any(word in keyword for word in ['buy', 'price', 'best']):
                    base_volume *= 1.2
            elif source == 'longtail_variant':
                base_volume *= 0.6  # Long-tail typically has lower volume
            
            # Add some randomness
            volume_multiplier = np.random.uniform(0.7, 1.3)
            final_volume = int(base_volume * volume_multiplier)
            
            # Ensure minimum volume constraint
            min_volume = self.config['campaign_constraints']['min_search_volume']
            return max(final_volume, min_volume)
        
        def get_competition_estimate(keyword, source):
            """Estimate competition level."""
            if source == 'brand_variant' and self.brand_name in keyword:
                return 'Low'
            elif source == 'competitor_variant':
                return 'Medium'
            elif source == 'commercial_variant':
                if any(word in keyword for word in ['buy', 'price', 'best']):
                    return 'High'
            
            return np.random.choice(['Low', 'Medium', 'High'], p=[0.3, 0.5, 0.2])
        
        def get_cpc_estimate(competition, keyword_length):
            """Estimate CPC based on competition and keyword characteristics."""
            base_cpc = {
                'Low': (0.25, 0.75),
                'Medium': (0.50, 1.25),
                'High': (0.80, 2.00)
            }
            
            cpc_low, cpc_high = base_cpc.get(competition, (0.50, 1.00))
            
            # Adjust for keyword length (longer keywords typically cheaper)
            if keyword_length > 4:
                cpc_low *= 0.8
                cpc_high *= 0.8
            
            # Add randomness
            cpc_low *= np.random.uniform(0.8, 1.2)
            cpc_high *= np.random.uniform(0.9, 1.1)
            
            return round(cpc_low, 2), round(cpc_high, 2)
        
        # Apply estimations
        df['estimated_volume'] = df.apply(
            lambda row: get_volume_estimate(row['keyword'], row['source']), axis=1
        )
        
        df['estimated_competition'] = df.apply(
            lambda row: get_competition_estimate(row['keyword'], row['source']), axis=1
        )
        
        df['keyword_length'] = df['keyword'].str.split().str.len()
        
        cpc_estimates = df.apply(
            lambda row: get_cpc_estimate(row['estimated_competition'], row['keyword_length']), 
            axis=1
        )
        
        df['estimated_cpc_low'] = [cpc[0] for cpc in cpc_estimates]
        df['estimated_cpc_high'] = [cpc[1] for cpc in cpc_estimates]
        
        # Drop intermediate column
        df = df.drop('keyword_length', axis=1)
        
        return df
    
    def _clean_and_deduplicate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and deduplicate keywords."""
        
        # Clean keywords
        df['keyword'] = df['keyword'].str.strip().str.lower()
        
        # Remove duplicates (keep first occurrence)
        df = df.drop_duplicates(subset=['keyword'], keep='first')
        
        # Remove keywords that are too short or too long
        min_length = self.config['campaign_constraints']['min_keyword_length']
        max_length = self.config['campaign_constraints']['max_keyword_length']
        
        df = df[
            (df['keyword'].str.len() >= min_length) & 
            (df['keyword'].str.len() <= max_length)
        ]
        
        # Remove keywords with special characters (except spaces and hyphens)
        df = df[df['keyword'].str.match(r'^[a-zA-Z0-9\s\-]+$')]
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def get_generation_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get summary statistics of keyword generation.
        
        Args:
            df: Generated keywords DataFrame
            
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'total_keywords': len(df),
            'keywords_by_source': df['source'].value_counts().to_dict(),
            'avg_volume': df['estimated_volume'].mean(),
            'competition_distribution': df['estimated_competition'].value_counts().to_dict(),
            'avg_cpc_range': {
                'low': df['estimated_cpc_low'].mean(),
                'high': df['estimated_cpc_high'].mean()
            }
        }
        
        return summary