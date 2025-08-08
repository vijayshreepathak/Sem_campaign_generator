"""
Data Processor Module
Handles filtering, scoring, and classification of keyword data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class DataProcessor:
    """Processes and analyzes keyword data."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.brand_name = config['brand']['name'].lower()
        self.competitor_name = config['competitor']['name'].lower()
        self.constraints = config['campaign_constraints']
    
    def process_keywords(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Complete processing pipeline for keywords.
        
        Args:
            df: Raw keywords DataFrame
            
        Returns:
            Processed keywords DataFrame with scores and classifications
        """
        # Apply filters
        df_filtered = self._apply_filters(df)
        
        # Add scores
        df_scored = self._add_performance_scores(df_filtered)
        
        # Add intent classification
        df_intent = self._classify_search_intent(df_scored)
        
        # Add theme clustering
        df_themed = self._cluster_themes(df_intent)
        
        # Calculate final composite scores
        df_final = self._calculate_final_scores(df_themed)
        
        return df_final
    
    def _apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply various filters to clean the keyword data."""
        
        print("  🔍 Applying volume filter...")
        initial_count = len(df)
        
        # Filter by minimum search volume
        min_volume = self.constraints['min_search_volume']
        df = df[df['estimated_volume'] >= min_volume]
        
        print(f"    Volume filter: {initial_count} → {len(df)} keywords")
        
        # Filter by maximum CPC
        max_cpc = self.constraints['max_cpc']
        df = df[df['estimated_cpc_high'] <= max_cpc]
        
        print(f"    CPC filter: Applied max CPC ${max_cpc}")
        
        # Remove irrelevant keywords
        df = self._filter_relevance(df)
        
        print(f"    Final filtered count: {len(df)} keywords")
        
        return df.reset_index(drop=True)
    
    def _filter_relevance(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter out irrelevant keywords."""
        
        # Define irrelevant patterns
        irrelevant_patterns = [
            r'\b(free|download|torrent|crack|pirate)\b',
            r'\b(jobs|career|hiring|salary|interview)\b',
            r'\b(course|training|education|class|school)\b',
            r'\b(porn|sex|adult|xxx)\b',
            r'\b(illegal|fake|scam|fraud)\b'
        ]
        
        # Create combined pattern
        combined_pattern = '|'.join(irrelevant_patterns)
        
        # Filter out matches
        initial_count = len(df)
        df = df[~df['keyword'].str.contains(combined_pattern, case=False, na=False)]
        
        print(f"    Relevance filter: {initial_count} → {len(df)} keywords")
        
        return df
    
    def _add_performance_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add performance scores for each keyword."""
        
        df = df.copy()
        
        # Volume score (0-10 scale)
        df['volume_score'] = df['estimated_volume'].apply(self._calculate_volume_score)
        
        # Competition score (0-10 scale, lower competition = higher score)
        df['competition_score'] = df['estimated_competition'].apply(self._calculate_competition_score)
        
        # CPC efficiency score (0-10 scale, lower CPC = higher score)
        df['cpc_efficiency_score'] = df['estimated_cpc_high'].apply(self._calculate_cpc_score)
        
        # Relevance score (0-10 scale)
        df['relevance_score'] = df['keyword'].apply(self._calculate_relevance_score)
        
        return df
    
    def _calculate_volume_score(self, volume: float) -> float:
        """Calculate volume score on 0-10 scale."""
        if volume < 500:
            return 1.0
        elif volume < 1000:
            return 3.0
        elif volume < 2000:
            return 5.0
        elif volume < 5000:
            return 7.0
        elif volume < 10000:
            return 9.0
        else:
            return 10.0
    
    def _calculate_competition_score(self, competition: str) -> float:
        """Calculate competition score (lower competition = higher score)."""
        competition_scores = {
            'Low': 9.0,
            'Medium': 6.0,
            'High': 3.0
        }
        return competition_scores.get(competition, 5.0)
    
    def _calculate_cpc_score(self, cpc: float) -> float:
        """Calculate CPC efficiency score (lower CPC = higher score)."""
        if cpc <= 0.5:
            return 10.0
        elif cpc <= 1.0:
            return 8.0
        elif cpc <= 1.5:
            return 6.0
        elif cpc <= 2.0:
            return 4.0
        else:
            return 2.0
    
    def _calculate_relevance_score(self, keyword: str) -> float:
        """Calculate relevance score based on keyword content."""
        keyword_lower = keyword.lower()
        
        # Brand keywords get high relevance
        if self.brand_name in keyword_lower:
            return 10.0
        
        # High-intent commercial keywords
        if any(term in keyword_lower for term in ['buy', 'price', 'best', 'review']):
            return 9.0
        
        # Core product terms
        core_terms = ['protein', 'supplement', 'shake', 'powder', 'nutrition']
        if any(term in keyword_lower for term in core_terms):
            return 8.0
        
        # Location-based terms
        locations = [loc.lower() for loc in self.config['service_locations']]
        if any(loc in keyword_lower for loc in locations):
            return 7.0
        
        # Fitness-related terms
        fitness_terms = ['gym', 'workout', 'fitness', 'muscle', 'health', 'recovery']
        if any(term in keyword_lower for term in fitness_terms):
            return 6.0
        
        return 5.0  # Default relevance
    
    def _classify_search_intent(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classify search intent for each keyword."""
        
        df = df.copy()
        
        def classify_intent(keyword):
            keyword_lower = keyword.lower()
            
            # Transactional intent
            transactional_patterns = [
                r'\b(buy|purchase|order|price|cost|shop|store)\b',
                r'\b(cheap|discount|deal|sale|offer)\b',
                r'\b(near me|delivery|shipping)\b'
            ]
            
            if any(re.search(pattern, keyword_lower) for pattern in transactional_patterns):
                return 'transactional'
            
            # Navigational intent (brand searches)
            if self.brand_name in keyword_lower:
                return 'navigational'
            
            # Commercial investigation
            commercial_patterns = [
                r'\b(best|top|review|compare|vs)\b',
                r'\b(alternative|option|choice)\b'
            ]
            
            if any(re.search(pattern, keyword_lower) for pattern in commercial_patterns):
                return 'commercial'
            
            # Informational intent
            informational_patterns = [
                r'\b(how to|what is|why|guide|tips)\b',
                r'\b(benefits|side effects|ingredients)\b'
            ]
            
            if any(re.search(pattern, keyword_lower) for pattern in informational_patterns):
                return 'informational'
            
            # Default based on keyword structure
            if len(keyword_lower.split()) >= 4:
                return 'informational'
            else:
                return 'commercial'
        
        df['search_intent'] = df['keyword'].apply(classify_intent)
        
        # Add intent scores
        intent_scores = {
            'transactional': 10.0,
            'commercial': 8.0,
            'navigational': 6.0,
            'informational': 4.0
        }
        
        df['intent_score'] = df['search_intent'].map(intent_scores)
        
        return df
    
    def _cluster_themes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cluster keywords into thematic groups."""
        
        df = df.copy()
        
        def classify_theme(keyword):
            keyword_lower = keyword.lower()
            locations = [loc.lower() for loc in self.config['service_locations']]
            
            # Brand terms
            if self.brand_name in keyword_lower:
                return 'Brand Terms'
            
            # Competitor terms
            if (self.competitor_name in keyword_lower or 
                'alternative' in keyword_lower or 
                'vs' in keyword_lower):
                return 'Competitor Terms'
            
            # Location-based queries
            if any(location in keyword_lower for location in locations):
                return 'Location-based Queries'
            
            # Long-tail informational
            if (len(keyword_lower.split()) >= 4 or
                any(term in keyword_lower for term in ['how to', 'what is', 'guide', 'tips'])):
                return 'Long-Tail Informational'
            
            # Default to category terms
            return 'Category Terms'
        
        df['theme'] = df['keyword'].apply(classify_theme)
        
        return df
    
    def _calculate_final_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate final composite scores."""
        
        df = df.copy()
        
        # Define weights for scoring components
        weights = {
            'volume': 0.25,
            'competition': 0.20,
            'cpc_efficiency': 0.20,
            'relevance': 0.20,
            'intent': 0.15
        }
        
        # Calculate weighted composite score
        df['composite_score'] = (
            df['volume_score'] * weights['volume'] +
            df['competition_score'] * weights['competition'] +
            df['cpc_efficiency_score'] * weights['cpc_efficiency'] +
            df['relevance_score'] * weights['relevance'] +
            df['intent_score'] * weights['intent']
        ).round(2)
        
        # Add ranking
        df['performance_rank'] = df['composite_score'].rank(method='dense', ascending=False).astype(int)
        
        # Add priority classification
        def classify_priority(score):
            if score >= 8.0:
                return 'High'
            elif score >= 6.0:
                return 'Medium'
            else:
                return 'Low'
        
        df['priority'] = df['composite_score'].apply(classify_priority)
        
        return df
    
    def get_processing_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate processing summary statistics."""
        
        summary = {
            'total_processed_keywords': len(df),
            'intent_distribution': df['search_intent'].value_counts().to_dict(),
            'theme_distribution': df['theme'].value_counts().to_dict(),
            'priority_distribution': df['priority'].value_counts().to_dict(),
            'average_scores': {
                'volume': df['volume_score'].mean(),
                'competition': df['competition_score'].mean(),
                'cpc_efficiency': df['cpc_efficiency_score'].mean(),
                'relevance': df['relevance_score'].mean(),
                'intent': df['intent_score'].mean(),
                'composite': df['composite_score'].mean()
            },
            'top_performing_keywords': df.nlargest(10, 'composite_score')['keyword'].tolist()
        }
        
        return summary
