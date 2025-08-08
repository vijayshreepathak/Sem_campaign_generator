"""
Campaign Builder Module
Builds Search, Shopping, and Performance Max campaign structures.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple

class CampaignBuilder:
    """Builds complete campaign structures from processed keywords."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.budgets = config['budgets']
        self.constraints = config['campaign_constraints']
        
        # Match type strategies by theme
        self.match_type_strategy = {
            'Brand Terms': ['Exact', 'Phrase'],
            'Category Terms': ['Phrase', 'Broad'],
            'Competitor Terms': ['Phrase', 'Exact'],
            'Location-based Queries': ['Phrase'],
            'Long-Tail Informational': ['Broad', 'Phrase']
        }
        
        # Bidding strategies by theme
        self.bidding_strategy = {
            'Brand Terms': {'multiplier': 1.2, 'priority': 'High'},
            'Category Terms': {'multiplier': 1.0, 'priority': 'Medium'},
            'Competitor Terms': {'multiplier': 0.9, 'priority': 'Medium'},
            'Location-based Queries': {'multiplier': 0.8, 'priority': 'High'},
            'Long-Tail Informational': {'multiplier': 0.7, 'priority': 'Low'}
        }
    
    def build_search_campaigns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Build search campaign ad groups with keywords, match types, and bids.
        
        Args:
            df: Processed keywords DataFrame
            
        Returns:
            DataFrame with search campaign structure
        """
        print("  🎪 Building search campaign ad groups...")
        
        search_campaigns = []
        
        for theme, group_df in df.groupby('theme'):
            print(f"    Processing {theme}: {len(group_df)} keywords")
            
            # Sort by composite score and take top keywords
            sorted_group = group_df.sort_values('composite_score', ascending=False)
            top_keywords = sorted_group.head(25)  # Limit per ad group
            
            for _, row in top_keywords.iterrows():
                # Determine match types
                match_types = self._get_match_types(theme, row['search_intent'])
                
                # Calculate suggested CPCs
                cpc_low, cpc_high = self._calculate_suggested_cpc(row, theme)
                
                # Calculate expected performance
                expected_clicks, expected_conversions = self._calculate_expected_performance(
                    row, cpc_high
                )
                
                search_campaigns.append({
                    'campaign_type': 'Search',
                    'ad_group': theme,
                    'keyword': row['keyword'],
                    'match_types': match_types,
                    'suggested_cpc_low': cpc_low,
                    'suggested_cpc_high': cpc_high,
                    'estimated_volume': row['estimated_volume'],
                    'competition': row['estimated_competition'],
                    'search_intent': row['search_intent'],
                    'composite_score': row['composite_score'],
                    'priority': self.bidding_strategy.get(theme, {}).get('priority', 'Medium'),
                    'expected_monthly_clicks': expected_clicks,
                    'expected_monthly_conversions': expected_conversions,
                    'source': row['source']
                })
        
        search_df = pd.DataFrame(search_campaigns)
        
        # Add budget allocations
        search_df = self._add_search_budget_allocation(search_df)
        
        print(f"    ✅ Created {len(search_df)} search ad group entries")
        return search_df
    
    def build_pmax_campaigns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Build Performance Max campaign themes.
        
        Args:
            df: Processed keywords DataFrame
            
        Returns:
            DataFrame with Performance Max themes
        """
        print("  🎨 Building Performance Max themes...")
        
        # Define theme templates
        pmax_themes = [
            {
                'theme_type': 'Product Category',
                'theme_name': 'Premium Protein Solutions',
                'description': 'High-quality protein products and supplements',
                'target_keywords': self._get_theme_keywords(df, 'product'),
                'primary_intent': 'Purchase',
                'audience_signals': 'Health-conscious consumers; Fitness enthusiasts; Nutrition-focused individuals',
                'budget_allocation': 0.35
            },
            {
                'theme_type': 'Use-case Based',
                'theme_name': 'Post-Workout Recovery',
                'description': 'Recovery and muscle-building focused solutions',
                'target_keywords': self._get_theme_keywords(df, 'recovery'),
                'primary_intent': 'Solution-seeking',
                'audience_signals': 'Active lifestyle; Gym members; Athletes; Fitness trainers',
                'budget_allocation': 0.30
            },
            {
                'theme_type': 'Demographic',
                'theme_name': 'Nutrition for Professionals',
                'description': 'Convenient nutrition for busy professionals',
                'target_keywords': self._get_theme_keywords(df, 'professional'),
                'primary_intent': 'Convenience',
                'audience_signals': 'Working professionals; High income; Time-conscious; Career-focused',
                'budget_allocation': 0.20
            },
            {
                'theme_type': 'Seasonal',
                'theme_name': 'Fitness Resolution Goals',
                'description': 'Supporting fitness and health goals',
                'target_keywords': self._get_theme_keywords(df, 'seasonal'),
                'primary_intent': 'Goal-achievement',
                'audience_signals': 'New Year resolutions; Fitness goals; Health improvement; Summer prep',
                'budget_allocation': 0.15
            }
        ]
        
        # Calculate metrics for each theme
        pmax_df = pd.DataFrame(pmax_themes)
        pmax_df['monthly_budget'] = pmax_df['budget_allocation'] * self.budgets['pmax_ads']
        
        # Add performance expectations
        for idx, row in pmax_df.iterrows():
            keywords = row['target_keywords']
            performance = self._calculate_pmax_performance(df, keywords, row['monthly_budget'])
            
            pmax_df.at[idx, 'expected_impressions'] = performance['impressions']
            pmax_df.at[idx, 'expected_clicks'] = performance['clicks']
            pmax_df.at[idx, 'expected_conversions'] = performance['conversions']
            pmax_df.at[idx, 'target_roas'] = performance['target_roas']
        
        # Add asset requirements
        pmax_df['asset_requirements'] = pmax_df.apply(self._generate_asset_requirements, axis=1)
        
        print(f"    ✅ Created {len(pmax_df)} Performance Max themes")
        return pmax_df
    
    def build_shopping_campaigns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Build Shopping campaign bid recommendations.
        
        Args:
            df: Processed keywords DataFrame
            
        Returns:
            DataFrame with shopping campaign structure
        """
        print("  🛒 Building shopping campaign recommendations...")
        
        # Define product categories based on keyword analysis
        product_categories = self._identify_product_categories(df)
        
        shopping_campaigns = []
        
        for category in product_categories:
            # Get relevant keywords for this category
            category_keywords = self._get_category_keywords(df, category['name'])
            
            if category_keywords.empty:
                continue
            
            # Calculate metrics
            avg_volume = category_keywords['estimated_volume'].mean()
            avg_competition = category_keywords['estimated_competition'].mode().iloc[0] if len(category_keywords) > 0 else 'Medium'
            avg_cpc_low = category_keywords['estimated_cpc_low'].mean()
            avg_cpc_high = category_keywords['estimated_cpc_high'].mean()
            
            # Calculate target CPC using formula: Target CPC = Target CPA × Conversion Rate
            target_cpa = self.constraints['target_cpa']
            conversion_rate = self.constraints['target_conversion_rate']
            target_cpc = round(target_cpa * conversion_rate, 2)
            
            # Apply category-specific adjustments
            adjusted_cpc = self._adjust_cpc_for_category(target_cpc, category, avg_competition)
            
            shopping_campaigns.append({
                'product_category': category['name'],
                'category_description': category['description'],
                'avg_monthly_volume': round(avg_volume, 0),
                'competition_level': avg_competition,
                'top_of_page_bid_low': round(avg_cpc_low, 2),
                'top_of_page_bid_high': round(avg_cpc_high, 2),
                'target_cpc_formula': target_cpc,
                'suggested_cpc': adjusted_cpc,
                'priority_level': category['priority'],
                'margin_factor': category['margin_factor'],
                'bidding_strategy': self._get_shopping_bidding_strategy(category, avg_competition),
                'budget_allocation': category['budget_weight']
            })
        
        shopping_df = pd.DataFrame(shopping_campaigns)
        
        # Calculate budget allocations
        total_weight = shopping_df['budget_allocation'].sum()
        shopping_df['monthly_budget'] = (shopping_df['budget_allocation'] / total_weight * self.budgets['shopping_ads']).round(0)
        
        # Add performance projections
        shopping_df = self._add_shopping_performance_projections(shopping_df)
        
        print(f"    ✅ Created {len(shopping_df)} shopping product categories")
        return shopping_df
    
    def _get_match_types(self, theme: str, intent: str) -> str:
        """Determine optimal match types based on theme and intent."""
        base_match_types = self.match_type_strategy.get(theme, ['Phrase'])
        
        # Adjust based on search intent
        if intent == 'transactional':
            if 'Exact' not in base_match_types:
                base_match_types = ['Exact'] + base_match_types
        elif intent == 'informational':
            if 'Broad' not in base_match_types:
                base_match_types.append('Broad')
        
        return ', '.join(base_match_types[:2])
    
    def _calculate_suggested_cpc(self, row: pd.Series, theme: str) -> Tuple[float, float]:
        """Calculate suggested CPC range with theme-based adjustments."""
        base_cpc_low = row['estimated_cpc_low']
        base_cpc_high = row['estimated_cpc_high']
        
        # Apply theme-based multiplier
        strategy = self.bidding_strategy.get(theme, {'multiplier': 1.0})
        multiplier = strategy['multiplier']
        
        suggested_low = round(base_cpc_low * multiplier, 2)
        suggested_high = round(base_cpc_high * multiplier, 2)
        
        # Ensure reasonable bounds
        max_cpc = self.constraints['max_cpc']
        suggested_low = max(0.25, min(suggested_low, max_cpc))
        suggested_high = max(suggested_low + 0.1, min(suggested_high, max_cpc))
        
        return suggested_low, suggested_high
    
    def _calculate_expected_performance(self, row: pd.Series, cpc: float) -> Tuple[int, float]:
        """Calculate expected clicks and conversions."""
        volume = row['estimated_volume']
        
        # Estimate impression share based on competition
        competition = row['estimated_competition']
        impression_share = {'Low': 0.8, 'Medium': 0.6, 'High': 0.4}.get(competition, 0.6)
        
        # Estimate CTR based on intent
        intent = row['search_intent']
        ctr = {'transactional': 0.05, 'commercial': 0.03, 'navigational': 0.08, 'informational': 0.02}.get(intent, 0.03)
        
        # Calculate expected clicks
        expected_impressions = volume * impression_share
        expected_clicks = round(expected_impressions * ctr, 0)
        
        # Calculate expected conversions
        conversion_rate = self.constraints['target_conversion_rate']
        expected_conversions = round(expected_clicks * conversion_rate, 1)
        
        return int(expected_clicks), expected_conversions
    
    def _add_search_budget_allocation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add budget allocation for search campaigns."""
        total_search_budget = self.budgets['search_ads']
        
        # Calculate budget weights by theme priority
        theme_weights = {}
        for theme in df['ad_group'].unique():
            strategy = self.bidding_strategy.get(theme, {'priority': 'Medium'})
            priority = strategy['priority']
            
            if priority == 'High':
                weight = 1.5
            elif priority == 'Low':
                weight = 0.7
            else:
                weight = 1.0
            
            theme_weights[theme] = weight
        
        # Normalize and calculate budgets
        total_weight = sum(theme_weights.values())
        theme_budgets = {
            theme: round((weight / total_weight) * total_search_budget, 0)
            for theme, weight in theme_weights.items()
        }
        
        df['theme_monthly_budget'] = df['ad_group'].map(theme_budgets)
        
        return df
    
    def _get_theme_keywords(self, df: pd.DataFrame, theme_type: str) -> List[str]:
        """Get representative keywords for PMax themes."""
        if theme_type == 'product':
            keywords = df[
                (df['theme'] == 'Category Terms') | 
                (df['search_intent'] == 'transactional')
            ].nlargest(8, 'composite_score')['keyword'].tolist()
        
        elif theme_type == 'recovery':
            keywords = df[
                df['keyword'].str.contains('recovery|workout|post|muscle', case=False, na=False)
            ].nlargest(6, 'composite_score')['keyword'].tolist()
        
        elif theme_type == 'professional':
            keywords = df[
                df['keyword'].str.contains('professional|busy|office|work', case=False, na=False)
            ].nlargest(5, 'composite_score')['keyword'].tolist()
            
            if not keywords:
                keywords = ['protein for professionals', 'busy lifestyle nutrition', 'office wellness']
        
        elif theme_type == 'seasonal':
            keywords = df[
                df['keyword'].str.contains('new year|summer|winter|resolution', case=False, na=False)
            ].nlargest(5, 'composite_score')['keyword'].tolist()
            
            if not keywords:
                keywords = ['fitness goals', 'health resolutions', 'seasonal nutrition']
        
        else:
            keywords = df.nlargest(5, 'composite_score')['keyword'].tolist()
        
        return keywords[:8]
    
    def _calculate_pmax_performance(self, df: pd.DataFrame, keywords: List[str], budget: float) -> Dict[str, Any]:
        """Calculate expected Performance Max performance."""
        
        # Get metrics for theme keywords
        theme_keywords_df = df[df['keyword'].isin(keywords)]
        
        if theme_keywords_df.empty:
            avg_cpc = 1.0
            total_volume = 10000
        else:
            avg_cpc = theme_keywords_df['estimated_cpc_high'].mean()
            total_volume = theme_keywords_df['estimated_volume'].sum()
        
        # Performance Max typically has higher reach but lower CTR
        pmax_multiplier = 1.5  # Higher reach
        pmax_ctr = 0.02  # Lower CTR than search
        
        expected_clicks = min(budget / avg_cpc, total_volume * pmax_multiplier * pmax_ctr)
        expected_conversions = expected_clicks * self.constraints['target_conversion_rate']
        
        # Calculate target ROAS
        target_cpa = self.constraints['target_cpa']
        implied_aov = target_cpa / self.constraints['target_conversion_rate']
        target_roas = round(implied_aov / target_cpa, 1)
        
        return {
            'impressions': round(total_volume * pmax_multiplier, 0),
            'clicks': round(expected_clicks, 0),
            'conversions': round(expected_conversions, 1),
            'target_roas': max(target_roas, 3.0)  # Minimum 3:1 ROAS
        }
    
    def _generate_asset_requirements(self, row: pd.Series) -> str:
        """Generate asset requirements for PMax themes."""
        return f"Headlines: 15 (focus on {row['theme_name'].lower()}); Descriptions: 4-5; Images: 20+ high-quality; Videos: 2-3 demonstrating value; Landing pages: Optimized for {row['primary_intent'].lower()}"
    
    def _identify_product_categories(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify product categories for shopping campaigns."""
        
        categories = [
            {
                'name': 'Vegan Protein Products',
                'description': 'Plant-based protein powders and supplements',
                'keywords': ['vegan', 'plant', 'organic'],
                'priority': 'High',
                'margin_factor': 1.2,
                'budget_weight': 1.5
            },
            {
                'name': 'Recovery Supplements',
                'description': 'Post-workout and muscle recovery products',
                'keywords': ['recovery', 'post', 'muscle'],
                'priority': 'High',
                'margin_factor': 1.1,
                'budget_weight': 1.3
            },
            {
                'name': 'Womens Nutrition',
                'description': 'Nutrition products specifically for women',
                'keywords': ['women', 'female', 'ladies'],
                'priority': 'Medium',
                'margin_factor': 1.0,
                'budget_weight': 1.0
            },
            {
                'name': 'General Protein Supplements',
                'description': 'Standard protein powders and supplements',
                'keywords': ['protein', 'supplement', 'powder'],
                'priority': 'Medium',
                'margin_factor': 0.9,
                'budget_weight': 0.8
            }
        ]
        
        return categories
    
    def _get_category_keywords(self, df: pd.DataFrame, category_name: str) -> pd.DataFrame:
        """Get keywords relevant to a product category."""
        category_map = {
            'Vegan Protein Products': ['vegan', 'plant', 'organic'],
            'Recovery Supplements': ['recovery', 'post', 'muscle'],
            'Womens Nutrition': ['women', 'female', 'ladies'],
            'General Protein Supplements': ['protein', 'supplement', 'powder']
        }
        
        keywords = category_map.get(category_name, [])
        if not keywords:
            return pd.DataFrame()
        
        # Create pattern for regex search
        pattern = '|'.join(keywords)
        return df[df['keyword'].str.contains(pattern, case=False, na=False)]
    
    def _adjust_cpc_for_category(self, base_cpc: float, category: Dict[str, Any], competition: str) -> float:
        """Adjust CPC based on category characteristics."""
        adjusted_cpc = base_cpc * category['margin_factor']
        
        # Further adjust based on competition
        competition_adjustments = {'Low': 0.9, 'Medium': 1.0, 'High': 1.1}
        adjusted_cpc *= competition_adjustments.get(competition, 1.0)
        
        return round(adjusted_cpc, 2)
    
    def _get_shopping_bidding_strategy(self, category: Dict[str, Any], competition: str) -> str:
        """Get bidding strategy recommendation for shopping."""
        priority = category['priority']
        
        if priority == 'High' and competition == 'Low':
            return 'Aggressive bidding to maximize market share'
        elif priority == 'High':
            return 'Target CPA bidding with volume focus'
        elif competition == 'High':
            return 'Conservative Target ROAS bidding'
        else:
            return 'Balanced Target CPA approach'
    
    def _add_shopping_performance_projections(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add performance projections for shopping campaigns."""
        
        def calculate_projections(row):
            budget = row['monthly_budget']
            cpc = row['suggested_cpc']
            conversion_rate = self.constraints['target_conversion_rate']
            
            clicks = round(budget / cpc, 0)
            conversions = round(clicks * conversion_rate, 1)
            
            return pd.Series({
                'expected_monthly_clicks': clicks,
                'expected_monthly_conversions': conversions
            })
        
        projections = df.apply(calculate_projections, axis=1)
        return pd.concat([df, projections], axis=1)