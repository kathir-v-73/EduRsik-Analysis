# app.py - Main Entry Point
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="EduRisk Analyzer Pro",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS
def apply_custom_css():
    st.markdown("""
    <style>
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        margin: 20px;
        padding: 30px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Glass Morphism Header */
    .glass-header {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 3rem 2rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .glass-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
    }
    
    .glass-header h1 {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .glass-header p {
        font-size: 1.3rem;
        color: #6c757d;
        font-weight: 300;
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        background: linear-gradient(135deg, #00b09b, #96c93d);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 176, 155, 0.3);
    }
    
    /* Welcome Card */
    .welcome-card {
        background: white;
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
        border-left: 5px solid #667eea;
        position: relative;
        overflow: hidden;
    }
    
    .welcome-card::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 100px;
        height: 100px;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 0 0 0 100px;
    }
    
    .welcome-card h2 {
        color: #343a40;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .welcome-card p {
        color: #6c757d;
        font-size: 1.1rem;
        line-height: 1.7;
        margin-bottom: 0;
    }
    
    /* Metric Cards - 3D Effect */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .metric-card-3d {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 
            0 10px 30px rgba(0, 0, 0, 0.1),
            0 1px 8px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.5);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        transform-style: preserve-3d;
        perspective: 1000px;
    }
    
    .metric-card-3d::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .metric-card-3d:hover {
        transform: translateY(-10px) rotateX(5deg);
        box-shadow: 
            0 25px 50px rgba(0, 0, 0, 0.15),
            0 15px 35px rgba(102, 126, 234, 0.2);
    }
    
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-title {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2.8rem;
        font-weight: 800;
        color: #343a40;
        margin-bottom: 0.5rem;
        line-height: 1;
    }
    
    .metric-subtitle {
        color: #6c757d;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    /* Progress Ring */
    .progress-ring {
        position: absolute;
        top: 1rem;
        right: 1rem;
        width: 60px;
        height: 60px;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #343a40;
        margin: 3rem 0 1.5rem 0;
        text-align: center;
        position: relative;
    }
    
    .section-header::after {
        content: '';
        display: block;
        width: 60px;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        margin: 0.5rem auto;
        border-radius: 2px;
    }
    
    /* Floating Elements */
    .floating-element {
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Hide sidebar */
    .css-1d391kg {
        display: none;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .glass-header h1 {
            font-size: 2.5rem;
        }
        
        .metric-value {
            font-size: 2.2rem;
        }
        
        .main-container {
            margin: 10px;
            padding: 20px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def create_progress_ring(progress, color):
    """Create a circular progress ring"""
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode = "gauge+number",
        value = progress,
        number = {'suffix': "%", 'font': {'size': 20}},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': 'lightgray'},
                {'range': [50, 100], 'color': 'lightgray'}],
        }
    ))
    
    fig.update_layout(
        height=100,
        width=100,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "gray", 'family': "Arial"}
    )
    
    return fig

def main():
    apply_custom_css()
    
    # Main container with glass morphism effect
    st.markdown("""
    <div class='main-container'>
        <div class='glass-header floating-element'>
            <h1>🎓 EduRisk Analyzer Pro</h1>
            <p>Advanced Student Risk Assessment & Analytics Platform</p>
            <div class='status-badge'>
                ✅ System Operational • Data Loaded Successfully
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Welcome card
    st.markdown("""
    <div class='welcome-card'>
        <h2>Welcome to EduRisk Analyzer Pro</h2>
        <p>Your comprehensive platform for identifying at-risk students and improving educational outcomes through data-driven insights. Leverage advanced analytics to transform student success rates.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats if data exists
    from utils import load_data
    data = load_data()
    
    if not data.empty:
        # System Overview section
        st.markdown('<div class="section-header">System Overview</div>', unsafe_allow_html=True)
        
        # Calculate metrics
        total_students = len(data)
        at_risk = (data['risk_level'].isin(['High', 'Failure'])).sum() if 'risk_level' in data.columns else 0
        avg_marks = data['total_internal_marks'].mean() if 'total_internal_marks' in data.columns else 0
        courses = data['course_name'].nunique() if 'course_name' in data.columns else 0
        
        # Calculate progress percentages
        risk_percentage = min(100, (at_risk / total_students) * 100) if total_students > 0 else 0
        marks_percentage = min(100, (avg_marks / 100) * 100) if avg_marks > 0 else 0
        
        # Create metric cards with 3D effects
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class='metric-card-3d floating-element'>
                <div class='metric-icon'>👥</div>
                <div class='metric-title'>Total Students</div>
                <div class='metric-value'>{total_students}</div>
                <div class='metric-subtitle'>Registered in System</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='metric-card-3d floating-element'>
                <div class='metric-icon'>⚠️</div>
                <div class='metric-title'>At Risk Students</div>
                <div class='metric-value'>{at_risk}</div>
                <div class='metric-subtitle'>Requiring Immediate Attention</div>
                <div class='progress-ring'>
            """, unsafe_allow_html=True)
            st.plotly_chart(create_progress_ring(risk_percentage, "#ff6b6b"), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='metric-card-3d floating-element'>
                <div class='metric-icon'>📊</div>
                <div class='metric-title'>Average Marks</div>
                <div class='metric-value'>{avg_marks:.1f}</div>
                <div class='metric-subtitle'>Across All Courses</div>
                <div class='progress-ring'>
            """, unsafe_allow_html=True)
            st.plotly_chart(create_progress_ring(marks_percentage, "#4ecdc4"), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class='metric-card-3d floating-element'>
                <div class='metric-icon'>📚</div>
                <div class='metric-title'>Active Courses</div>
                <div class='metric-value'>{courses}</div>
                <div class='metric-subtitle'>Being Actively Monitored</div>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # No data state with enhanced design
        st.markdown("""
        <div class='welcome-card'>
            <div class='status-badge' style='background: linear-gradient(135deg, #ff6b6b, #ee5a24);'>
                ⚠️ No Data Available
            </div>
            <h2>Ready to Get Started?</h2>
            <p>Begin your journey with EduRisk Analyzer Pro by importing student data or generating sample data to explore the platform's powerful analytics capabilities.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Close main container
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()