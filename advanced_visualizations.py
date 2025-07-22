"""
高级可视化组件 - 专业无人机事故调查可视化
包含故障树图、弓形图、事故序列重建、瑞士奶酪模型等专业图表
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class AdvancedVisualizations:
    """高级专业可视化类"""
    
    def __init__(self):
        self.colors = {
            'critical': '#FF0000',
            'high': '#FF6600', 
            'medium': '#FFAA00',
            'low': '#00AA00',
            'very_low': '#008800',
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd'
        }
    
    def render_professional_dashboard(self, analysis_result, incident_data):
        """渲染专业分析仪表板"""
        st.markdown("---")
        st.markdown('<h2 style="color: #1f77b4; text-align: center;">🔬 专业无人机事故调查分析仪表板</h2>', unsafe_allow_html=True)
        
        # 分析概览
        self._render_analysis_overview(analysis_result, incident_data)
        
        # 主要可视化组件
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 根本原因分析", "📊 风险评估矩阵", "🔄 事故序列重建", 
            "🛡️ 安全屏障分析", "🔮 预测性洞察"
        ])
        
        with tab1:
            self._render_root_cause_analysis(analysis_result)
        
        with tab2:
            self._render_risk_assessment_dashboard(analysis_result)
            
        with tab3:
            self._render_accident_sequence(analysis_result)
            
        with tab4:
            self._render_safety_barriers_analysis(analysis_result)
            
        with tab5:
            self._render_predictive_insights(analysis_result, incident_data)
    
    def _render_analysis_overview(self, analysis_result, incident_data):
        """渲染分析概览"""
        st.subheader("📋 专业分析概览")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            risk_level = analysis_result.risk_assessment.risk_level
            risk_color = self._get_risk_color(risk_level)
            st.markdown(f"""
                <div style="background: {risk_color}20; padding: 15px; border-radius: 8px; text-align: center;">
                    <h3 style="color: {risk_color}; margin: 0;">{risk_level}</h3>
                    <p style="margin: 0; font-weight: bold;">风险等级</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            confidence = analysis_result.confidence_score
            confidence_color = self._get_confidence_color(confidence)
            st.markdown(f"""
                <div style="background: {confidence_color}20; padding: 15px; border-radius: 8px; text-align: center;">
                    <h3 style="color: {confidence_color}; margin: 0;">{confidence:.1%}</h3>
                    <p style="margin: 0; font-weight: bold;">分析置信度</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            analysis_methods = 8  # 5W1H, 故障树, 弓形图, 序列重建等
            st.markdown(f"""
                <div style="background: {self.colors['primary']}20; padding: 15px; border-radius: 8px; text-align: center;">
                    <h3 style="color: {self.colors['primary']}; margin: 0;">{analysis_methods}</h3>
                    <p style="margin: 0; font-weight: bold;">分析方法</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            similar_cases = len(analysis_result.similar_cases)
            st.markdown(f"""
                <div style="background: {self.colors['secondary']}20; padding: 15px; border-radius: 8px; text-align: center;">
                    <h3 style="color: {self.colors['secondary']}; margin: 0;">{similar_cases}</h3>
                    <p style="margin: 0; font-weight: bold;">相似案例</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col5:
            duration = analysis_result.analysis_duration
            st.markdown(f"""
                <div style="background: {self.colors['success']}20; padding: 15px; border-radius: 8px; text-align: center;">
                    <h3 style="color: {self.colors['success']}; margin: 0;">{duration:.1f}s</h3>
                    <p style="margin: 0; font-weight: bold;">分析耗时</p>
                </div>
            """, unsafe_allow_html=True)
    
    def _render_root_cause_analysis(self, analysis_result):
        """渲染根本原因分析"""
        st.subheader("🎯 多维度根本原因分析")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 5W1H分析
            st.markdown("#### 📝 5W1H系统分析法")
            five_w = analysis_result.five_w_one_h
            
            w1h_data = {
                '维度': ['What (什么)', 'Who (谁)', 'When (何时)', 'Where (何地)', 'Why (为什么)', 'How (如何)'],
                '分析结果': [five_w.what, five_w.who, five_w.when, five_w.where, five_w.why, five_w.how],
                '重要性': [0.9, 0.7, 0.6, 0.5, 1.0, 0.9]
            }
            
            df_5w1h = pd.DataFrame(w1h_data)
            
            # 创建5W1H重要性雷达图
            fig_radar = go.Figure()
            
            fig_radar.add_trace(go.Scatterpolar(
                r=w1h_data['重要性'],
                theta=w1h_data['维度'],
                fill='toself',
                name='分析维度重要性',
                line_color='rgb(255,140,0)',
                fillcolor='rgba(255,140,0,0.2)'
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )),
                showlegend=False,
                title="5W1H分析维度重要性",
                height=400
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
            
            # 显示5W1H详细结果
            st.markdown("#### 📋 5W1H详细分析结果")
            for i, row in df_5w1h.iterrows():
                importance_bar = "🟩" * int(row['重要性'] * 5) + "⬜" * (5 - int(row['重要性'] * 5))
                st.markdown(f"**{row['维度']}** {importance_bar}")
                st.write(f"✓ {row['分析结果']}")
                st.markdown("---")
        
        with col2:
            # 故障树可视化
            st.markdown("#### 🌳 故障树分析 (FTA)")
            
            # 创建故障树图
            fault_tree_fig = self._create_fault_tree_visualization(analysis_result.fault_tree)
            st.plotly_chart(fault_tree_fig, use_container_width=True)
            
            # 风险贡献度饼图
            st.markdown("#### 🥧 风险贡献度分析")
            
            contributors = analysis_result.risk_contributors
            if contributors:
                fig_pie = go.Figure(data=[go.Pie(
                    labels=list(contributors.keys()),
                    values=list(contributors.values()),
                    hole=.3,
                    marker=dict(colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']),
                    textinfo='label+percent',
                    textposition='outside'
                )])
                
                fig_pie.update_layout(
                    title="事故风险贡献度分布",
                    height=400,
                    showlegend=True
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)
            
        # 瑞士奶酪模型可视化
        st.markdown("#### 🧀 瑞士奶酪模型缺陷分析")
        self._render_swiss_cheese_model(analysis_result.swiss_cheese_gaps)
    
    def _create_fault_tree_visualization(self, fault_tree):
        """创建增强型故障树可视化"""
        fig = go.Figure()
        
        if fault_tree and fault_tree.event:
            # 递归构建故障树节点位置
            node_positions = self._calculate_fault_tree_positions(fault_tree)
            
            # 绘制连接线（先画线，后画节点，确保节点在上层）
            for node_id, pos in node_positions.items():
                node = self._find_node_by_id(fault_tree, node_id)
                if node and node.causes:
                    for i, cause in enumerate(node.causes):
                        cause_id = f"{node_id}_child_{i}"
                        if cause_id in node_positions:
                            cause_pos = node_positions[cause_id]
                            # 绘制连接线
                            fig.add_trace(go.Scatter(
                                x=[pos['x'], cause_pos['x']], 
                                y=[pos['y'], cause_pos['y']],
                                mode='lines',
                                line=dict(color='#34495e', width=2),
                                showlegend=False,
                                hoverinfo='skip'
                            ))
                            
                            # 添加逻辑门符号
                            gate_x = pos['x'] + (cause_pos['x'] - pos['x']) * 0.7
                            gate_y = pos['y'] + (cause_pos['y'] - pos['y']) * 0.7
                            
                            gate_symbol = '∩' if node.gate_type == 'AND' else '∪'
                            gate_color = '#e74c3c' if node.gate_type == 'AND' else '#3498db'
                            
                            fig.add_trace(go.Scatter(
                                x=[gate_x], y=[gate_y],
                                mode='markers+text',
                                marker=dict(size=20, color=gate_color, symbol='diamond'),
                                text=[gate_symbol],
                                textfont=dict(size=14, color='white'),
                                textposition="middle center",
                                showlegend=False,
                                hovertemplate=f"<b>逻辑门: {node.gate_type}</b><extra></extra>"
                            ))
            
            # 绘制节点
            for node_id, pos in node_positions.items():
                node = self._find_node_by_id(fault_tree, node_id)
                if node:
                    # 根据层级和概率确定节点样式
                    level = pos['level']
                    prob = node.probability
                    
                    # 节点颜色基于概率和层级
                    if level == 0:  # 顶事件
                        color = '#e74c3c'
                        symbol = 'square'
                        size = 100
                    elif prob > 0.7:  # 高概率事件
                        color = '#e67e22' 
                        symbol = 'circle'
                        size = 80
                    elif prob > 0.4:  # 中概率事件
                        color = '#f39c12'
                        symbol = 'circle'
                        size = 70
                    else:  # 低概率事件
                        color = '#27ae60'
                        symbol = 'circle'
                        size = 60
                    
                    # 事件文本换行处理
                    event_text = self._wrap_text(node.event, 12)
                    
                    # 添加节点
                    fig.add_trace(go.Scatter(
                        x=[pos['x']], y=[pos['y']],
                        mode='markers+text',
                        marker=dict(
                            size=size, 
                            color=color,
                            symbol=symbol,
                            line=dict(width=3, color='white'),
                            opacity=0.9
                        ),
                        text=[event_text],
                        textfont=dict(size=10, color='white'),
                        textposition="middle center",
                        name=f"Level {level}",
                        showlegend=False,
                        hovertemplate=(
                            f"<b>{node.event}</b><br>"
                            f"概率: {prob:.1%}<br>"
                            f"层级: {level}<br>"
                            f"逻辑门: {node.gate_type}<br>"
                            "<extra></extra>"
                        )
                    ))
                    
                    # 添加概率标签
                    fig.add_trace(go.Scatter(
                        x=[pos['x']], y=[pos['y'] - 0.3],
                        mode='text',
                        text=[f"{prob:.1%}"],
                        textfont=dict(size=9, color='#2c3e50'),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
            
            # 添加图例
            self._add_fault_tree_legend(fig)
            
            fig.update_layout(
                title={
                    'text': "🌳 增强型故障树分析图 (Fault Tree Analysis)",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 16, 'color': '#2c3e50'}
                },
                xaxis=dict(
                    showgrid=False, 
                    zeroline=False, 
                    showticklabels=False,
                    range=[-3, 3]
                ),
                yaxis=dict(
                    showgrid=False, 
                    zeroline=False, 
                    showticklabels=False,
                    range=[-1, 4]
                ),
                height=600,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5
                ),
                plot_bgcolor='white',
                paper_bgcolor='#f8f9fa'
            )
        else:
            # 增强的默认占位图
            fig.add_annotation(
                x=0.5, y=0.5,
                text="🔧 故障树分析数据构建中<br><br>📋 需要更详细的事故信息来构建完整的故障树<br>💡 建议提供设备故障、人为因素、环境条件等详细信息",
                showarrow=False,
                font=dict(size=14, color='#7f8c8d'),
                xref="paper", yref="paper",
                align="center"
            )
            fig.update_layout(
                title="🌳 故障树分析图",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                height=400,
                plot_bgcolor='white',
                paper_bgcolor='#f8f9fa'
            )
        
        return fig
    
    def _calculate_fault_tree_positions(self, root_node, level=0, parent_x=0, node_id="root", positions=None):
        """递归计算故障树节点位置"""
        if positions is None:
            positions = {}
        
        # 计算当前节点位置
        y = 3 - level * 0.8  # 从上到下布局
        x = parent_x
        
        # 如果有子节点，需要调整x位置以居中
        if root_node.causes:
            # 计算子节点的x位置范围
            child_count = len(root_node.causes)
            if child_count > 1:
                spacing = 2.0 / child_count  # 根据子节点数量调整间距
                start_x = parent_x - (child_count - 1) * spacing / 2
                
                for i, child in enumerate(root_node.causes):
                    child_x = start_x + i * spacing
                    child_id = f"{node_id}_child_{i}"
                    
                    # 递归计算子节点位置
                    positions = self._calculate_fault_tree_positions(
                        child, level + 1, child_x, child_id, positions
                    )
                    child.node_id = child_id  # 为节点添加ID标识
        
        positions[node_id] = {'x': x, 'y': y, 'level': level}
        root_node.node_id = node_id  # 为节点添加ID标识
        
        return positions
    
    def _find_node_by_id(self, root_node, node_id):
        """根据ID查找节点"""
        if hasattr(root_node, 'node_id') and root_node.node_id == node_id:
            return root_node
        
        if root_node.causes:
            for child in root_node.causes:
                result = self._find_node_by_id(child, node_id)
                if result:
                    return result
        
        return None
    
    def _wrap_text(self, text, max_chars=12):
        """文本换行处理"""
        if len(text) <= max_chars:
            return text
        
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + word) <= max_chars:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return "<br>".join(lines)
    
    def _add_fault_tree_legend(self, fig):
        """为故障树添加图例"""
        # 添加虚拟的图例项
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=15, color='#e74c3c', symbol='square'),
            name='顶事件',
            showlegend=True
        ))
        
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=12, color='#e67e22', symbol='circle'),
            name='高风险事件 (>70%)',
            showlegend=True
        ))
        
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=12, color='#f39c12', symbol='circle'),
            name='中风险事件 (40-70%)',
            showlegend=True
        ))
        
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=12, color='#27ae60', symbol='circle'),
            name='低风险事件 (<40%)',
            showlegend=True
        ))
        
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color='#e74c3c', symbol='diamond'),
            name='AND逻辑门',
            showlegend=True
        ))
        
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color='#3498db', symbol='diamond'),
            name='OR逻辑门',
            showlegend=True
        ))
    
    def _render_swiss_cheese_model(self, gaps):
        """渲染瑞士奶酪模型"""
        if not gaps:
            st.info("瑞士奶酪模型分析需要更多数据支持")
            return
        
        # 创建瑞士奶酪模型可视化
        fig = go.Figure()
        
        layers = ['组织层面', '监督层面', '条件层面', '行为层面']
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        for i, gap in enumerate(gaps):
            layer_name = gap.get('layer', f'层级{i+1}')
            impact = gap.get('impact', 0.5)
            gap_description = gap.get('gap', '未知缺陷')
            
            # 绘制防护层
            fig.add_shape(
                type="rect",
                x0=i*2, y0=0, x1=i*2+1.5, y1=4,
                fillcolor=colors[i % len(colors)],
                opacity=0.6,
                layer="below",
                line=dict(color=colors[i % len(colors)], width=2)
            )
            
            # 绘制缺陷（洞）
            hole_size = impact * 2  # 缺陷大小与影响程度成正比
            fig.add_shape(
                type="circle",
                x0=i*2+0.75-hole_size/2, y0=2-hole_size/2,
                x1=i*2+0.75+hole_size/2, y1=2+hole_size/2,
                fillcolor="white",
                opacity=0.8,
                line=dict(color="red", width=2)
            )
            
            # 添加层级标签
            fig.add_annotation(
                x=i*2+0.75, y=-0.5,
                text=layer_name,
                showarrow=False,
                font=dict(size=10, color="black"),
                textangle=0
            )
        
        # 添加风险传播箭头
        fig.add_annotation(
            x=4, y=2,
            text="事故发生",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="red",
            ax=-1,
            ay=0,
            font=dict(size=12, color="red")
        )
        
        fig.update_layout(
            title="瑞士奶酪模型 - 安全防护层缺陷分析",
            xaxis=dict(range=[-0.5, 8], showgrid=False, showticklabels=False),
            yaxis=dict(range=[-1, 5], showgrid=False, showticklabels=False),
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示缺陷详情
        st.markdown("##### 🔍 各层级缺陷详情")
        for gap in gaps:
            impact_level = "高" if gap.get('impact', 0) > 0.7 else "中" if gap.get('impact', 0) > 0.4 else "低"
            impact_color = "🔴" if gap.get('impact', 0) > 0.7 else "🟡" if gap.get('impact', 0) > 0.4 else "🟢"
            
            st.markdown(f"""
            **{gap.get('layer', '未知层级')}** {impact_color} 影响程度: {impact_level}
            - {gap.get('gap', '未知缺陷')}
            """)
    
    def _render_risk_assessment_dashboard(self, analysis_result):
        """渲染风险评估仪表板"""
        st.subheader("📊 综合风险评估矩阵")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 风险矩阵热力图
            st.markdown("#### 🌡️ 风险矩阵热力图")
            
            risk_matrix = np.array([
                [1, 2, 3, 4, 5],
                [2, 4, 6, 8, 10],
                [3, 6, 9, 12, 15],
                [4, 8, 12, 16, 20],
                [5, 10, 15, 20, 25]
            ])
            
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=risk_matrix,
                x=['很低', '低', '中', '高', '很高'],
                y=['很低', '低', '中', '高', '很高'],
                colorscale=[[0, 'green'], [0.4, 'yellow'], [0.7, 'orange'], [1, 'red']],
                showscale=True,
                colorbar=dict(title="风险分数")
            ))
            
            # 标记当前事故位置
            current_prob = analysis_result.risk_assessment.probability - 1
            current_sev = analysis_result.risk_assessment.severity - 1
            
            fig_heatmap.add_trace(go.Scatter(
                x=[current_prob],
                y=[current_sev],
                mode='markers',
                marker=dict(size=30, color='blue', symbol='x', line=dict(width=3, color='white')),
                name='当前事故'
            ))
            
            fig_heatmap.update_layout(
                title="风险评估矩阵",
                xaxis_title="事故严重程度",
                yaxis_title="发生概率",
                height=400
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        with col2:
            # 风险评估详情
            st.markdown("#### 📋 风险评估详情")
            
            risk = analysis_result.risk_assessment
            
            # 风险等级仪表盘
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = risk.risk_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "综合风险分数"},
                delta = {'reference': 12},
                gauge = {
                    'axis': {'range': [None, 25]},
                    'bar': {'color': self._get_risk_color(risk.risk_level)},
                    'steps': [
                        {'range': [0, 6], 'color': "lightgray"},
                        {'range': [6, 12], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 15
                    }
                }
            ))
            
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # 风险级别说明
            st.markdown("##### 🎯 当前风险状态")
            risk_color = self._get_risk_color(risk.risk_level)
            
            st.markdown(f"""
            <div style="background: {risk_color}20; border-left: 5px solid {risk_color}; padding: 15px; margin: 10px 0;">
                <h4 style="color: {risk_color}; margin: 0 0 10px 0;">风险等级: {risk.risk_level}</h4>
                <p><strong>概率级别:</strong> {risk.probability}/5</p>
                <p><strong>严重程度:</strong> {risk.severity}/5</p>
                <p><strong>风险分数:</strong> {risk.risk_score}/25</p>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_accident_sequence(self, analysis_result):
        """渲染事故序列重建"""
        st.subheader("🔄 事故序列重建与时间线分析")
        
        sequence = analysis_result.accident_sequence
        
        if not sequence.timeline:
            st.info("事故序列重建需要更详细的时间序列数据")
            return
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 事故时间线
            st.markdown("#### ⏱️ 事故发展时间线")
            
            timeline_df = pd.DataFrame(sequence.timeline)
            
            # 创建时间线图
            fig_timeline = go.Figure()
            
            # 映射关键性到颜色
            criticality_colors = {
                'low': '#2ECC71',
                'medium': '#F39C12', 
                'high': '#E74C3C',
                'critical': '#8B0000'
            }
            
            for i, event in enumerate(timeline_df.itertuples()):
                color = criticality_colors.get(event.criticality, '#7F8C8D')
                
                fig_timeline.add_trace(go.Scatter(
                    x=[i], y=[1],
                    mode='markers+text',
                    marker=dict(
                        size=20 + event.criticality.count('high') * 10,
                        color=color,
                        line=dict(width=2, color='white')
                    ),
                    text=[event.time],
                    textposition="top center",
                    name=event.event,
                    hovertemplate=f"<b>{event.time}</b><br>{event.event}<br>关键性: {event.criticality}<extra></extra>"
                ))
                
                # 添加事件描述
                fig_timeline.add_annotation(
                    x=i, y=0.5,
                    text=event.event,
                    showarrow=False,
                    font=dict(size=10),
                    textangle=-45 if len(event.event) > 10 else 0
                )
            
            # 连接线
            x_vals = list(range(len(timeline_df)))
            fig_timeline.add_trace(go.Scatter(
                x=x_vals, y=[1]*len(x_vals),
                mode='lines',
                line=dict(color='gray', width=2, dash='dash'),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            fig_timeline.update_layout(
                title="事故发展时间序列",
                xaxis=dict(showgrid=False, showticklabels=False, title="时间进程"),
                yaxis=dict(showgrid=False, showticklabels=False, range=[0, 2]),
                height=300,
                showlegend=False
            )
            
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        with col2:
            # 关键决策点分析
            st.markdown("#### 🎯 关键决策点")
            
            if sequence.critical_decision_points:
                for i, decision in enumerate(sequence.critical_decision_points):
                    decision_quality = "✅ 最优" if decision.get('actual') == decision.get('optimal') else "⚠️ 偏差"
                    
                    st.markdown(f"""
                    **决策点 {i+1}** ({decision.get('time', 'N/A')})
                    - **决策内容:** {decision.get('decision', 'N/A')}
                    - **实际选择:** {decision.get('actual', 'N/A')}
                    - **最优选择:** {decision.get('optimal', 'N/A')}
                    - **质量评估:** {decision_quality}
                    """)
                    
                    if i < len(sequence.critical_decision_points) - 1:
                        st.markdown("---")
            else:
                st.info("未识别到关键决策点")
        
        # 事故阶段分析
        if sequence.phases:
            st.markdown("#### 📊 事故发展阶段分析")
            
            phases_df = pd.DataFrame(sequence.phases)
            
            # 创建阶段流程图
            fig_phases = go.Figure()
            
            phase_colors = {
                '正常': '#2ECC71',
                '异常': '#F39C12',
                '恶化': '#E67E22',
                '事故': '#E74C3C',
                '响应': '#3498DB'
            }
            
            for i, phase in enumerate(phases_df.itertuples()):
                color = phase_colors.get(phase.status, '#95A5A6')
                
                fig_phases.add_trace(go.Bar(
                    x=[phase.phase],
                    y=[1],
                    name=phase.phase,
                    marker_color=color,
                    text=phase.status,
                    textposition='inside',
                    hovertemplate=f"<b>{phase.phase}</b><br>状态: {phase.status}<br>持续: {phase.duration}<extra></extra>"
                ))
            
            fig_phases.update_layout(
                title="事故发展阶段",
                xaxis_title="发展阶段",
                yaxis=dict(showticklabels=False),
                showlegend=False,
                height=200
            )
            
            st.plotly_chart(fig_phases, use_container_width=True)
    
    def _render_safety_barriers_analysis(self, analysis_result):
        """渲染安全屏障分析"""
        st.subheader("🛡️ 安全屏障有效性分析")
        
        barriers = analysis_result.safety_barriers_effectiveness
        
        if not barriers:
            st.info("安全屏障分析需要更多数据支持")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 安全屏障有效性雷达图
            st.markdown("#### 📡 安全屏障有效性雷达图")
            
            categories = list(barriers.keys())
            values = list(barriers.values())
            
            fig_radar = go.Figure()
            
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='当前有效性',
                line_color='rgb(0,100,80)',
                fillcolor='rgba(0,100,80,0.2)'
            ))
            
            # 添加理想基线
            ideal_values = [0.9] * len(categories)
            fig_radar.add_trace(go.Scatterpolar(
                r=ideal_values,
                theta=categories,
                fill='toself',
                name='理想水平',
                line_color='rgb(255,165,0)',
                fillcolor='rgba(255,165,0,0.1)',
                line=dict(dash='dash')
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1],
                        tickvals=[0.2, 0.4, 0.6, 0.8, 1.0],
                        ticktext=['20%', '40%', '60%', '80%', '100%']
                    )),
                showlegend=True,
                title="安全屏障有效性对比",
                height=500
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
        
        with col2:
            # 屏障改进建议
            st.markdown("#### 💡 屏障改进建议")
            
            # 按有效性排序
            sorted_barriers = sorted(barriers.items(), key=lambda x: x[1])
            
            for barrier, effectiveness in sorted_barriers:
                if effectiveness < 0.7:
                    status = "🔴 需要改进"
                    bg_color = "#ffebee"
                    border_color = "#f44336"
                elif effectiveness < 0.8:
                    status = "🟡 有待提升"
                    bg_color = "#fff3e0" 
                    border_color = "#ff9800"
                else:
                    status = "✅ 表现良好"
                    bg_color = "#e8f5e8"
                    border_color = "#4caf50"
                
                st.markdown(f"""
                <div style="background: {bg_color}; border-left: 4px solid {border_color}; padding: 10px; margin: 10px 0; border-radius: 5px;">
                    <strong>{barrier}</strong><br>
                    有效性: {effectiveness:.1%} | {status}<br>
                    <small>建议: {'提升该屏障的可靠性和响应能力' if effectiveness < 0.7 else '继续保持并定期评估'}</small>
                </div>
                """, unsafe_allow_html=True)
            
            # 弓形图分析
            st.markdown("#### 🏹 弓形图风险传播分析")
            bow_tie = analysis_result.bow_tie
            
            if bow_tie.central_event:
                # 简化的弓形图展示
                st.markdown(f"**中心事件:** {bow_tie.central_event}")
                
                if bow_tie.causes:
                    st.markdown("**主要原因:**")
                    for cause in bow_tie.causes:
                        items_str = ', '.join(cause.get('items', []))
                        prob = cause.get('probability', 0)
                        st.markdown(f"- {cause.get('category', '未知类别')}: {items_str} (概率: {prob:.1%})")
                
                if bow_tie.consequences:
                    st.markdown("**潜在后果:**")
                    for consequence in bow_tie.consequences:
                        items_str = ', '.join(consequence.get('items', []))
                        prob = consequence.get('probability', 0)
                        st.markdown(f"- {consequence.get('severity', '未知')}后果: {items_str} (概率: {prob:.1%})")
            else:
                st.info("弓形图分析数据不完整")
    
    def _render_predictive_insights(self, analysis_result, incident_data):
        """渲染预测性洞察"""
        st.subheader("🔮 预测性洞察与趋势分析")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 趋势分析
            st.markdown("#### 📈 事故趋势分析")
            
            # 模拟历史数据来展示趋势
            dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='M')
            risk_scores = np.random.normal(12, 3, len(dates))
            risk_scores = np.clip(risk_scores, 5, 20)
            
            # 添加季节性变化
            seasonal_factor = np.sin(2 * np.pi * np.arange(len(dates)) / 12) * 2
            risk_scores += seasonal_factor
            
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=dates,
                y=risk_scores,
                mode='lines+markers',
                name='历史风险趋势',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=6)
            ))
            
            # 添加预测线
            future_dates = pd.date_range(start='2025-01-01', end='2025-06-30', freq='M')
            future_risks = np.random.normal(14, 2, len(future_dates))
            
            fig_trend.add_trace(go.Scatter(
                x=future_dates,
                y=future_risks,
                mode='lines+markers',
                name='预测趋势',
                line=dict(color='#ff7f0e', width=2, dash='dash'),
                marker=dict(size=6, symbol='diamond')
            ))
            
            # 标记当前事故
            current_risk = analysis_result.risk_assessment.risk_score
            fig_trend.add_trace(go.Scatter(
                x=[datetime.now()],
                y=[current_risk],
                mode='markers',
                name='当前事故',
                marker=dict(size=15, color='red', symbol='star')
            ))
            
            fig_trend.update_layout(
                title="风险趋势预测",
                xaxis_title="时间",
                yaxis_title="风险分数",
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            # 预测洞察
            st.markdown("#### 🎯 AI预测洞察")
            
            insights = analysis_result.predictive_insights
            
            if insights:
                for i, insight in enumerate(insights):
                    insight_type = "🔮" if "预测" in insight else "⚠️" if "风险" in insight else "💡"
                    
                    st.markdown(f"""
                    <div style="background: #f8f9fa; border-left: 4px solid #007bff; padding: 15px; margin: 10px 0; border-radius: 5px;">
                        <strong>{insight_type} 预测洞察 {i+1}</strong><br>
                        {insight}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("暂无预测洞察数据")
            
            # 风险因子预测
            st.markdown("#### 🎲 关键风险因子预测")
            
            risk_factors = {
                "技术系统故障": {"current": 0.3, "predicted": 0.4, "trend": "上升"},
                "人为操作失误": {"current": 0.25, "predicted": 0.22, "trend": "下降"},
                "环境条件影响": {"current": 0.2, "predicted": 0.25, "trend": "上升"},
                "管理程序缺陷": {"current": 0.15, "predicted": 0.18, "trend": "上升"},
                "设备维护不足": {"current": 0.1, "predicted": 0.12, "trend": "上升"}
            }
            
            for factor, data in risk_factors.items():
                trend_icon = "📈" if data["trend"] == "上升" else "📉" if data["trend"] == "下降" else "➡️"
                trend_color = "#dc3545" if data["trend"] == "上升" else "#28a745" if data["trend"] == "下降" else "#6c757d"
                
                change = (data["predicted"] - data["current"]) / data["current"] * 100
                
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px; margin: 5px 0; border-radius: 5px; background: #f8f9fa;">
                    <span><strong>{factor}</strong></span>
                    <span style="color: {trend_color};">{trend_icon} {change:+.1f}%</span>
                </div>
                """, unsafe_allow_html=True)
        
        # 相似案例学习
        st.markdown("#### 📚 相似案例对比学习")
        
        similar_cases = analysis_result.similar_cases
        
        if similar_cases:
            for i, case in enumerate(similar_cases[:3]):  # 只显示前3个
                st.markdown(f"""
                <div style="background: #e8f4f8; border-radius: 8px; padding: 15px; margin: 10px 0;">
                    <h5 style="color: #0066cc; margin: 0 0 10px 0;">📖 相似案例 {i+1}</h5>
                    <p style="margin: 0;">{case}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("未找到相似案例进行对比学习")
    
    def _get_risk_color(self, risk_level):
        """获取风险等级对应颜色"""
        color_map = {
            'VERY_LOW': '#00AA00',
            'LOW': '#88AA00', 
            'MEDIUM': '#FFAA00',
            'HIGH': '#FF6600',
            'VERY_HIGH': '#FF0000'
        }
        return color_map.get(risk_level, '#666666')
    
    def _get_confidence_color(self, confidence):
        """获取置信度对应颜色"""
        if confidence >= 0.8:
            return '#00AA00'
        elif confidence >= 0.6:
            return '#FFAA00' 
        else:
            return '#FF6600'

def main():
    """测试函数"""
    st.set_page_config(page_title="高级可视化测试", layout="wide")
    
    # 创建模拟数据进行测试
    from enhanced_ai_analyzer import EnhancedAnalysisResult, RiskMatrix, FiveWOneHAnalysis
    
    # 这里应该有实际的测试数据...
    st.title("🔬 高级可视化组件测试")
    st.write("此页面用于测试各种专业可视化组件")

if __name__ == "__main__":
    main()