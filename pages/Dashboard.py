# pages/1_🏠_Dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import load_data, calculate_metrics
import numpy as np

def main():
    st.markdown("""
    <div class='main-header'>
        <h1>📊 Executive Dashboard</h1>
        <p>Comprehensive Overview of Student Performance & Risk Analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    data = load_data()
    
    if data.empty:
        st.info("""
        ## 🚀 Welcome to EduRisk Analyzer Pro!
        
        No student data available yet. Get started by:
        
        - **Generating sample data** for demonstration
        - **Importing your CSV file** with student records
        - **Adding students manually** through the Students page
        
        Use the sidebar navigation to explore all features!
        """)
        return
    
    # Calculate metrics
    metrics = calculate_metrics(data)
    
    # Key Metrics Row
    st.markdown("### 🎯 Key Performance Indicators")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Students", metrics['total_students'])
    
    with col2:
        st.metric("Low Risk", metrics.get('low_risk', 0), 
                 delta=f"{metrics.get('low_risk', 0)/metrics['total_students']*100:.1f}%" if metrics['total_students'] > 0 else "0%")
    
    with col3:
        st.metric("High Risk", metrics.get('high_risk', 0) + metrics.get('failure_risk', 0),
                 delta=f"{(metrics.get('high_risk', 0) + metrics.get('failure_risk', 0))/metrics['total_students']*100:.1f}%" if metrics['total_students'] > 0 else "0%",
                 delta_color="inverse")
    
    with col4:
        st.metric("Avg Marks", f"{metrics['average_marks']:.1f}/60")
    
    with col5:
        st.metric("Courses", metrics['courses_count'])
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Risk Distribution")
        if 'risk_level' in data.columns:
            risk_counts = data['risk_level'].value_counts()
            fig = px.pie(
                values=risk_counts.values,
                names=risk_counts.index,
                title="Student Risk Level Distribution",
                color=risk_counts.index,
                color_discrete_map={
                    'Low': '#28a745',
                    'Medium': '#ffc107', 
                    'High': '#fd7e14',
                    'Failure': '#dc3545'
                }
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No risk level data available")
    
    with col2:
        st.markdown("#### 📈 Performance Overview")
        if 'total_internal_marks' in data.columns:
            fig = px.histogram(
                data, 
                x='total_internal_marks',
                nbins=20,
                title="Distribution of Total Internal Marks",
                color_discrete_sequence=['#667eea']
            )
            fig.update_layout(
                xaxis_title="Total Internal Marks",
                yaxis_title="Number of Students"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No marks data available")
    
    # Course Performance
    st.markdown("#### 🎓 Course-wise Analysis")
    
    if 'course_name' in data.columns and 'total_internal_marks' in data.columns:
        course_performance = data.groupby('course_name').agg({
            'total_internal_marks': ['mean', 'std', 'count'],
            'risk_level': lambda x: (x.isin(['High', 'Failure'])).sum()
        }).round(2)
        
        course_performance.columns = ['avg_marks', 'std_dev', 'student_count', 'at_risk_count']
        course_performance['at_risk_percent'] = (course_performance['at_risk_count'] / course_performance['student_count'] * 100).round(1)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart for average marks by course
            fig = px.bar(
                course_performance.reset_index(),
                x='course_name',
                y='avg_marks',
                title="Average Marks by Course",
                color='avg_marks',
                color_continuous_scale='viridis'
            )
            fig.update_layout(xaxis_title="Course", yaxis_title="Average Marks")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Risk percentage by course
            fig = px.bar(
                course_performance.reset_index(),
                x='course_name', 
                y='at_risk_percent',
                title="At-Risk Students Percentage by Course",
                color='at_risk_percent',
                color_continuous_scale='reds'
            )
            fig.update_layout(xaxis_title="Course", yaxis_title="At-Risk Students (%)")
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent Activity
    st.markdown("#### 📋 Recent Student Records")
    
    display_cols = ['student_id', 'name', 'course_name']
    if 'risk_level' in data.columns:
        display_cols.append('risk_level')
    if 'total_internal_marks' in data.columns:
        display_cols.append('total_internal_marks')
    
    available_cols = [col for col in display_cols if col in data.columns]
    if available_cols:
        st.dataframe(
            data[available_cols].tail(10),
            use_container_width=True,
            height=400
        )
    
    # Quick Actions
    st.markdown("#### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("📈 View Detailed Analytics", use_container_width=True):
            st.switch_page("pages/Analytics.py")
    
    with col3:
        if st.button("🔔 Check Alerts", use_container_width=True):
            st.switch_page("pages/Notifications.py")

if __name__ == "__main__":
    main()