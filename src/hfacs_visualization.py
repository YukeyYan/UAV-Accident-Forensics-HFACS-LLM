"""
HFACS Visualization System
Professional visualization for HFACS 8.0 analysis results
Based on LLM-generated classifications with clear activation indicators
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Set, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# HFACS 8.0 Standard Definitions
HFACS_CATEGORIES = [
    "UNSAFE ACTS—Errors—Performance/Skill-Based",
    "UNSAFE ACTS—Errors—Judgement & Decision-Making",
    "UNSAFE ACTS—Known Deviations",
    "PRECONDITIONS—Physical Environment",
    "PRECONDITIONS—Technological Environment",
    "PRECONDITIONS—Team Coordination/Communication",
    "PRECONDITIONS—Training Conditions",
    "PRECONDITIONS—Mental Awareness (Attention)",
    "PRECONDITIONS—State of Mind",
    "PRECONDITIONS—Adverse Physiological",
    "SUPERVISION/LEADERSHIP—Unit Safety Culture",
    "SUPERVISION/LEADERSHIP—Supervisory Known Deviations",
    "SUPERVISION/LEADERSHIP—Ineffective Supervision",
    "SUPERVISION/LEADERSHIP—Ineffective Planning & Coordination",
    "ORGANIZATIONAL INFLUENCES—Climate/Culture",
    "ORGANIZATIONAL INFLUENCES—Policy/Procedures/Process",
    "ORGANIZATIONAL INFLUENCES—Resource Support",
    "ORGANIZATIONAL INFLUENCES—Training Program Issues"
]

HFACS_LAYERS = [
    "UNSAFE ACTS",
    "PRECONDITIONS", 
    "SUPERVISION/LEADERSHIP",
    "ORGANIZATIONAL INFLUENCES"
]

# Layer color scheme
LAYER_COLORS = {
    'UNSAFE ACTS': '#E74C3C',                    # Red - Direct actions
    'PRECONDITIONS': '#F39C12',                  # Orange - Enabling conditions  
    'SUPERVISION/LEADERSHIP': '#3498DB',         # Blue - Management oversight
    'ORGANIZATIONAL INFLUENCES': '#9B59B6'       # Purple - System factors
}

# Category to layer mapping
CATEGORY_TO_LAYER = {}
for category in HFACS_CATEGORIES:
    for layer in HFACS_LAYERS:
        if category.startswith(layer):
            CATEGORY_TO_LAYER[category] = layer
            break

class HFACSVisualizer:
    """Professional HFACS visualization system"""
    
    def __init__(self):
        self.active_color = '#2ECC71'      # Green for activated
        self.inactive_color = '#BDC3C7'   # Gray for not activated
        self.font_family = 'Arial, sans-serif'
        
    def create_activation_matrix(self, hfacs_result) -> go.Figure:
        """
        Create HFACS activation matrix showing identified categories with enhanced highlighting
        
        Args:
            hfacs_result: HFACSAnalysisResult object from LLM analysis
            
        Returns:
            Plotly figure showing activation matrix with proper highlighting
        """
        logger.info("Creating HFACS activation matrix")
        
        # Extract data from LLM results
        activated_categories = set()
        confidence_data = {}
        reasoning_data = {}
        
        if hasattr(hfacs_result, 'classifications') and hfacs_result.classifications:
            for classification in hfacs_result.classifications:
                activated_categories.add(classification.category)
                confidence_data[classification.category] = classification.confidence
                reasoning_data[classification.category] = classification.reasoning
                
        logger.info(f"Found {len(activated_categories)} activated categories")
        
        # Create matrix data
        matrix_data = []
        category_labels = []
        layer_labels = []
        colors = []
        hover_texts = []
        text_annotations = []
        
        for layer in HFACS_LAYERS:
            layer_categories = [cat for cat in HFACS_CATEGORIES if cat.startswith(layer)]
            
            for category in layer_categories:
                category_labels.append(self._format_category_name(category))
                layer_labels.append(layer)
                
                if category in activated_categories:
                    confidence = confidence_data.get(category, 0.8)
                    reasoning = reasoning_data.get(category, "Identified by LLM analysis")
                    matrix_data.append(confidence)
                    
                    # Enhanced highlighting with confidence-based intensity
                    base_color = LAYER_COLORS[layer]
                    # Make color more intense for higher confidence
                    if confidence >= 0.8:
                        colors.append(base_color)  # Full intensity
                        text_annotations.append("★★★")  # High confidence indicator
                    elif confidence >= 0.6:
                        colors.append(self._adjust_color_opacity(base_color, 0.8))
                        text_annotations.append("★★")  # Medium confidence
                    else:
                        colors.append(self._adjust_color_opacity(base_color, 0.6))
                        text_annotations.append("★")  # Lower confidence
                    
                    status = f"<span style='color: green; font-weight: bold;'>ACTIVATED</span>"
                    confidence_text = f"Confidence: {confidence:.1%}"
                    hover_texts.append(f"<b>{category}</b><br>Layer: {layer}<br>Status: {status}<br>{confidence_text}<br>Reasoning: {reasoning[:100]}...")
                else:
                    matrix_data.append(0.05)  # Very small value to show inactive bar
                    colors.append(self.inactive_color)
                    text_annotations.append("")
                    status = "Not Activated"
                    hover_texts.append(f"<b>{category}</b><br>Layer: {layer}<br>Status: {status}<br>Not identified in analysis")
        
        # Create the visualization with enhanced highlighting
        fig = go.Figure()
        
        # Add bars with highlighting
        fig.add_trace(go.Bar(
            x=category_labels,
            y=matrix_data,
            marker=dict(
                color=colors,
                line=dict(
                    color=['#2c3e50' if val > 0.05 else '#95a5a6' for val in matrix_data],
                    width=[3 if val > 0.05 else 1 for val in matrix_data]
                )
            ),
            text=text_annotations,
            textposition='outside',
            textfont=dict(size=14, color='gold'),
            hovertemplate='%{customdata}<extra></extra>',
            customdata=hover_texts,
            showlegend=False
        ))
        
        # Add layer separator lines
        layer_positions = self._get_layer_positions()
        for pos in layer_positions[1:]:  # Skip first position
            fig.add_vline(x=pos-0.5, line_dash="dash", line_color="gray", opacity=0.5)
        
        # Update layout with enhanced styling
        fig.update_layout(
            title={
                'text': f'<b>HFACS Analysis Results - {len(activated_categories)}/18 Categories Identified</b>',
                'x': 0.5,
                'font': {'size': 20, 'family': self.font_family, 'color': '#2c3e50'}
            },
            xaxis_title="HFACS Categories",
            yaxis_title="Confidence Level",
            xaxis_tickangle=-45,
            yaxis=dict(
                range=[0, 1.1],  # Fixed range to make differences more visible
                tickformat='.0%',
                dtick=0.2
            ),
            height=650,
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(b=150, t=100),
            font=dict(family=self.font_family, size=12),
            annotations=[
                dict(
                    text=f"★★★ High Confidence (≥80%)  ★★ Medium Confidence (≥60%)  ★ Lower Confidence (<60%)",
                    x=0.5, y=1.05, xref='paper', yref='paper',
                    showarrow=False, font=dict(size=12, color='gray')
                )
            ]
        )
        
        return fig
        
    def create_layer_summary(self, hfacs_result) -> go.Figure:
        """
        Create layer-based summary visualization
        
        Args:
            hfacs_result: HFACSAnalysisResult object from LLM analysis
            
        Returns:
            Plotly figure showing layer activation summary
        """
        logger.info("Creating HFACS layer summary")
        
        # Calculate layer statistics
        layer_stats = {}
        for layer in HFACS_LAYERS:
            layer_categories = [cat for cat in HFACS_CATEGORIES if cat.startswith(layer)]
            layer_stats[layer] = {
                'total': len(layer_categories),
                'activated': 0,
                'avg_confidence': 0.0,
                'categories': []
            }
        
        # Process LLM results
        if hasattr(hfacs_result, 'classifications') and hfacs_result.classifications:
            for classification in hfacs_result.classifications:
                layer = classification.layer
                if layer in layer_stats:
                    layer_stats[layer]['activated'] += 1
                    layer_stats[layer]['categories'].append({
                        'category': classification.category,
                        'confidence': classification.confidence,
                        'reasoning': classification.reasoning
                    })
            
            # Calculate average confidence per layer
            for layer in layer_stats:
                if layer_stats[layer]['categories']:
                    confidences = [cat['confidence'] for cat in layer_stats[layer]['categories']]
                    layer_stats[layer]['avg_confidence'] = sum(confidences) / len(confidences)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Layer Activation Count',
                'Average Confidence by Layer', 
                'Activation Rate by Layer',
                'Layer Distribution'
            ],
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "pie"}]]
        )
        
        layers = list(layer_stats.keys())
        activated_counts = [layer_stats[layer]['activated'] for layer in layers]
        total_counts = [layer_stats[layer]['total'] for layer in layers]
        avg_confidences = [layer_stats[layer]['avg_confidence'] for layer in layers]
        activation_rates = [layer_stats[layer]['activated'] / layer_stats[layer]['total'] * 100 for layer in layers]
        
        # 1. Activation count
        fig.add_trace(
            go.Bar(
                x=layers,
                y=activated_counts,
                name='Activated',
                marker_color=[LAYER_COLORS[layer] for layer in layers],
                text=activated_counts,
                textposition='auto'
            ),
            row=1, col=1
        )
        
        # 2. Average confidence
        fig.add_trace(
            go.Bar(
                x=layers,
                y=avg_confidences,
                name='Avg Confidence',
                marker_color=[LAYER_COLORS[layer] for layer in layers],
                text=[f"{conf:.1%}" for conf in avg_confidences],
                textposition='auto'
            ),
            row=1, col=2
        )
        
        # 3. Activation rate
        fig.add_trace(
            go.Bar(
                x=layers,
                y=activation_rates,
                name='Activation Rate (%)',
                marker_color=[LAYER_COLORS[layer] for layer in layers],
                text=[f"{rate:.1f}%" for rate in activation_rates],
                textposition='auto'
            ),
            row=2, col=1
        )
        
        # 4. Pie chart
        pie_labels = []
        pie_values = []
        pie_colors = []
        
        for layer in layers:
            if activated_counts[layers.index(layer)] > 0:
                pie_labels.append(f"{layer} ({activated_counts[layers.index(layer)]})")
                pie_values.append(activated_counts[layers.index(layer)])
                pie_colors.append(LAYER_COLORS[layer])
        
        if not pie_values:
            pie_labels = ['No Activations']
            pie_values = [1]
            pie_colors = [self.inactive_color]
        
        fig.add_trace(
            go.Pie(
                labels=pie_labels,
                values=pie_values,
                marker_colors=pie_colors,
                textinfo='label+percent'
            ),
            row=2, col=2
        )
        
        # Update layout with enhanced styling
        fig.update_layout(
            title={
                'text': f'<b>HFACS Layer Analysis Summary - {sum(activated_counts)} Total Activations</b>',
                'x': 0.5,
                'font': {'size': 18, 'family': self.font_family, 'color': '#2c3e50'}
            },
            height=800,
            showlegend=False,
            font=dict(family=self.font_family, size=11),
            plot_bgcolor='white',
            paper_bgcolor='white',
            annotations=[
                dict(
                    text="Enhanced visualization showing HFACS layer activation patterns and confidence levels",
                    x=0.5, y=0.02, xref='paper', yref='paper',
                    showarrow=False, font=dict(size=10, color='gray')
                )
            ]
        )
        
        return fig
        
    def create_hierarchy_tree(self, hfacs_result) -> go.Figure:
        """
        Create hierarchical tree visualization
        
        Args:
            hfacs_result: HFACSAnalysisResult object from LLM analysis
            
        Returns:
            Plotly figure showing HFACS hierarchy with activations
        """
        logger.info("Creating HFACS hierarchy tree")
        
        # Extract activated categories
        activated_categories = set()
        confidence_data = {}
        
        if hasattr(hfacs_result, 'classifications') and hfacs_result.classifications:
            for classification in hfacs_result.classifications:
                activated_categories.add(classification.category)
                confidence_data[classification.category] = classification.confidence
        
        fig = go.Figure()
        
        # Define positions for tree layout
        positions = self._calculate_tree_positions()
        
        # Draw connections
        self._add_tree_connections(fig, positions, activated_categories)
        
        # Add nodes
        self._add_tree_nodes(fig, positions, activated_categories, confidence_data)
        
        # Update layout with enhanced styling
        fig.update_layout(
            title={
                'text': f'<b>HFACS Hierarchy Tree - {len(activated_categories)}/18 Categories Activated</b>',
                'x': 0.5,
                'font': {'size': 18, 'family': self.font_family, 'color': '#2c3e50'}
            },
            xaxis=dict(range=[-10, 10], showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(range=[0, 5], showgrid=False, showticklabels=False, zeroline=False),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=700,
            margin=dict(t=100, b=80, l=60, r=60),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            annotations=[
                dict(
                    text="★ High Confidence (≥80%)  ● Medium Confidence (≥60%)  ◆ Lower Confidence (<60%)  ○ Not Activated",
                    x=0.5, y=-0.05, xref='paper', yref='paper',
                    showarrow=False, font=dict(size=11, color='gray')
                )
            ]
        )
        
        return fig
        
    def create_detailed_analysis(self, hfacs_result) -> go.Figure:
        """
        Create detailed analysis view with classification details
        
        Args:
            hfacs_result: HFACSAnalysisResult object from LLM analysis
            
        Returns:
            Plotly figure showing detailed classification information
        """
        logger.info("Creating detailed HFACS analysis view")
        
        if not hasattr(hfacs_result, 'classifications') or not hfacs_result.classifications:
            # Return empty state figure
            fig = go.Figure()
            fig.add_annotation(
                x=0.5, y=0.5,
                text="No HFACS classifications found in analysis",
                showarrow=False,
                font=dict(size=16, family=self.font_family),
                xref="paper", yref="paper"
            )
            fig.update_layout(
                title="HFACS Detailed Analysis",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )
            return fig
        
        # Prepare data for table with enhanced highlighting
        table_data = []
        cell_colors = []
        
        for classification in hfacs_result.classifications:
            # Determine confidence level and color
            confidence = classification.confidence
            if confidence >= 0.8:
                confidence_color = '#d5f4e6'  # Light green for high confidence
                confidence_label = f"★★★ {confidence:.1%}"
            elif confidence >= 0.6:
                confidence_color = '#fff2cc'  # Light yellow for medium confidence  
                confidence_label = f"★★ {confidence:.1%}"
            else:
                confidence_color = '#fde2e4'  # Light red for low confidence
                confidence_label = f"★ {confidence:.1%}"
            
            table_data.append({
                'Category': self._format_category_name(classification.category),
                'Layer': classification.layer,
                'Confidence': confidence_label,
                'Reasoning': classification.reasoning[:100] + "..." if len(classification.reasoning) > 100 else classification.reasoning,
                'Evidence Count': len(classification.evidence) if classification.evidence else 0
            })
            
            # Store colors for this row
            cell_colors.append([
                '#ECF0F1',  # Category
                LAYER_COLORS.get(classification.layer, '#ECF0F1'),  # Layer with layer color
                confidence_color,  # Confidence with confidence-based color
                '#ECF0F1',  # Reasoning
                '#ECF0F1'   # Evidence Count
            ])
        
        df = pd.DataFrame(table_data)
        
        # Transpose colors for Plotly table format
        transposed_colors = list(map(list, zip(*cell_colors))) if cell_colors else ['#ECF0F1'] * len(df.columns)
        
        # Create enhanced table visualization
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['<b>' + col + '</b>' for col in df.columns],
                fill_color='#34495E',
                font=dict(color='white', size=12, family=self.font_family),
                align='left',
                height=50
            ),
            cells=dict(
                values=[df[col] for col in df.columns],
                fill_color=transposed_colors,
                align='left',
                font=dict(size=11, family=self.font_family),
                height=45,
                line=dict(color='white', width=2)
            )
        )])
        
        fig.update_layout(
            title={
                'text': f'<b>HFACS Classification Details - {len(table_data)} Items</b>',
                'x': 0.5,
                'font': {'size': 16, 'family': self.font_family}
            },
            height=max(400, len(table_data) * 50 + 150),
            margin=dict(t=80, b=20, l=20, r=20)
        )
        
        return fig
        
    def _format_category_name(self, category: str) -> str:
        """Format category name for display"""
        if '—' in category:
            parts = category.split('—')
            return parts[-1] if parts else category
        return category
    
    def _adjust_color_opacity(self, hex_color: str, opacity: float) -> str:
        """Adjust the opacity of a hex color"""
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            
            # Convert to RGB
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Return RGBA string
            return f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {opacity})'
        except (ValueError, IndexError):
            # Fallback to original color
            return hex_color
    
    def _get_layer_positions(self) -> List[int]:
        """Get the starting positions of each layer in the category list"""
        positions = [0]
        current_pos = 0
        
        for layer in HFACS_LAYERS:
            layer_categories = [cat for cat in HFACS_CATEGORIES if cat.startswith(layer)]
            current_pos += len(layer_categories)
            positions.append(current_pos)
        
        return positions[:-1]  # Remove the last position
        
    def _calculate_tree_positions(self) -> Dict[str, Tuple[float, float]]:
        """Calculate positions for tree nodes"""
        positions = {
            'HFACS Framework': (0, 4),
            
            # Layer nodes
            'UNSAFE ACTS': (-6, 3),
            'PRECONDITIONS': (-2, 3),
            'SUPERVISION/LEADERSHIP': (2, 3),
            'ORGANIZATIONAL INFLUENCES': (6, 3)
        }
        
        # Add category positions
        layer_x_centers = {
            'UNSAFE ACTS': -6,
            'PRECONDITIONS': -2,
            'SUPERVISION/LEADERSHIP': 2,
            'ORGANIZATIONAL INFLUENCES': 6
        }
        
        for layer in HFACS_LAYERS:
            categories = [cat for cat in HFACS_CATEGORIES if cat.startswith(layer)]
            x_center = layer_x_centers[layer]
            
            if len(categories) == 1:
                positions[categories[0]] = (x_center, 1.5)
            else:
                spacing = 2.0 / (len(categories) - 1) if len(categories) > 1 else 0
                start_x = x_center - 1
                
                for i, category in enumerate(categories):
                    x = start_x + (i * spacing)
                    y = 1.5 if i < 4 else 0.5  # Two rows if many categories
                    positions[category] = (x, y)
        
        return positions
        
    def _add_tree_connections(self, fig: go.Figure, positions: Dict, activated_categories: Set[str]):
        """Add connection lines to tree"""
        # Root to layers
        root_pos = positions['HFACS Framework']
        for layer in HFACS_LAYERS:
            layer_pos = positions[layer]
            fig.add_trace(go.Scatter(
                x=[root_pos[0], layer_pos[0]],
                y=[root_pos[1], layer_pos[1]],
                mode='lines',
                line=dict(color='#7F8C8D', width=2),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Layers to categories
        for layer in HFACS_LAYERS:
            layer_pos = positions[layer]
            categories = [cat for cat in HFACS_CATEGORIES if cat.startswith(layer)]
            
            for category in categories:
                if category in positions:
                    cat_pos = positions[category]
                    
                    # Highlight if activated
                    if category in activated_categories:
                        line_color = LAYER_COLORS[layer]
                        line_width = 3
                    else:
                        line_color = '#BDC3C7'
                        line_width = 1
                    
                    fig.add_trace(go.Scatter(
                        x=[layer_pos[0], cat_pos[0]],
                        y=[layer_pos[1], cat_pos[1]],
                        mode='lines',
                        line=dict(color=line_color, width=line_width),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
        
    def _add_tree_nodes(self, fig: go.Figure, positions: Dict, activated_categories: Set[str], confidence_data: Dict):
        """Add nodes to tree"""
        # Root node
        root_pos = positions['HFACS Framework']
        fig.add_trace(go.Scatter(
            x=[root_pos[0]],
            y=[root_pos[1]],
            mode='markers+text',
            marker=dict(size=30, color='#2C3E50', symbol='diamond'),
            text=['HFACS<br>Framework'],
            textposition='bottom center',
            textfont=dict(size=12, color='white', family=self.font_family),
            name='Framework',
            showlegend=False
        ))
        
        # Layer nodes
        for layer in HFACS_LAYERS:
            layer_pos = positions[layer]
            fig.add_trace(go.Scatter(
                x=[layer_pos[0]],
                y=[layer_pos[1]],
                mode='markers+text',
                marker=dict(size=25, color=LAYER_COLORS[layer], symbol='square'),
                text=[layer.replace('/', '/<br>')],
                textposition='bottom center',
                textfont=dict(size=10, color='white', family=self.font_family),
                name=layer,
                showlegend=True
            ))
        
        # Category nodes
        for layer in HFACS_LAYERS:
            categories = [cat for cat in HFACS_CATEGORIES if cat.startswith(layer)]
            
            x_coords = []
            y_coords = []
            colors = []
            sizes = []
            texts = []
            hover_texts = []
            
            for category in categories:
                if category in positions:
                    pos = positions[category]
                    x_coords.append(pos[0])
                    y_coords.append(pos[1])
                    
                    if category in activated_categories:
                        confidence = confidence_data.get(category, 0.0)
                        colors.append(LAYER_COLORS[layer])
                        
                        # Enhanced highlighting based on confidence
                        if confidence >= 0.8:
                            sizes.append(25)
                            texts.append("★")  # High confidence star
                        elif confidence >= 0.6:
                            sizes.append(22)
                            texts.append("●")  # Medium confidence dot
                        else:
                            sizes.append(20)
                            texts.append("◆")  # Lower confidence diamond
                        
                        status = f"<span style='color: green; font-weight: bold;'>ACTIVATED</span>"
                        hover_texts.append(f"<b>{self._format_category_name(category)}</b><br>Status: {status}<br>Confidence: {confidence:.1%}<br>Layer: {layer}")
                    else:
                        colors.append(self.inactive_color)
                        sizes.append(15)
                        texts.append("○")
                        hover_texts.append(f"<b>{self._format_category_name(category)}</b><br>Status: Not Activated<br>Layer: {layer}")
            
            if x_coords:
                fig.add_trace(go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    mode='markers+text',
                    marker=dict(
                        size=sizes,
                        color=colors,
                        symbol='circle',
                        line=dict(color='white', width=2)
                    ),
                    text=texts,
                    textposition='middle center',
                    textfont=dict(size=10, color='white', family=self.font_family),
                    hovertext=hover_texts,
                    hoverinfo='text',
                    name=f'{layer} Categories',
                    showlegend=False
                ))

def create_hfacs_visualizations(hfacs_result) -> Dict[str, go.Figure]:
    """
    Create all HFACS visualizations
    
    Args:
        hfacs_result: HFACSAnalysisResult object from LLM analysis
        
    Returns:
        Dictionary containing all visualization figures
    """
    logger.info("Creating comprehensive HFACS visualizations")
    
    visualizer = HFACSVisualizer()
    
    visualizations = {
        'matrix': visualizer.create_activation_matrix(hfacs_result),
        'summary': visualizer.create_layer_summary(hfacs_result),
        'tree': visualizer.create_hierarchy_tree(hfacs_result),
        'details': visualizer.create_detailed_analysis(hfacs_result)
    }
    
    logger.info(f"Created {len(visualizations)} HFACS visualizations")
    return visualizations

# Test function
def test_hfacs_visualization():
    """Test the visualization system"""
    from dataclasses import dataclass
    from typing import List
    
    @dataclass
    class MockClassification:
        category: str
        layer: str
        confidence: float
        reasoning: str
        evidence: List[str]
    
    @dataclass  
    class MockResult:
        classifications: List[MockClassification]
        primary_factors: List[str]
        contributing_factors: List[str]
        recommendations: List[str]
        analysis_summary: str
        confidence_score: float
        analysis_timestamp: str
        visualization_data: dict
    
    # Create mock data
    mock_result = MockResult(
        classifications=[
            MockClassification(
                category="UNSAFE ACTS—Errors—Judgement & Decision-Making",
                layer="UNSAFE ACTS",
                confidence=0.85,
                reasoning="Poor decision making during critical phase",
                evidence=["Decision errors mentioned in report"]
            ),
            MockClassification(
                category="PRECONDITIONS—Training Conditions", 
                layer="PRECONDITIONS",
                confidence=0.70,
                reasoning="Inadequate training on procedures",
                evidence=["Training deficiencies noted"]
            )
        ],
        primary_factors=["Decision making errors"],
        contributing_factors=["Training issues"],
        recommendations=["Improve training"],
        analysis_summary="Test analysis",
        confidence_score=0.75,
        analysis_timestamp="2024-01-01",
        visualization_data={}
    )
    
    # Test visualizations 
    viz = create_hfacs_visualizations(mock_result)
    print(f"Created {len(viz)} test visualizations")
    
    return viz

if __name__ == "__main__":
    test_viz = test_hfacs_visualization()