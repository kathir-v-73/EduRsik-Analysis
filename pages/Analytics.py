# pages/4_📈_Analytics.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import load_data, calculate_metrics
from model import StudentPredictor

def main():
    st.markdown("""
    <div class='main-header'>
        <h1>📈 Advanced Analytics</h1>
        <p>PowerBI-like Dashboards with Interactive Visualizations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    data = load_data()
    
    if data.empty:
        st.info("No data available for analytics. Please import or generate data first.")
        return
    
    # Initialize ML model
    predictor = StudentPredictor()
    
    # Analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview Analytics", "🎯 Risk Analysis", "🤖 ML Predictions", "📈 Trend Analysis"
    ])
    
    with tab1:
        render_overview_analytics(data)
    
    with tab2:
        render_risk_analysis(data)
    
    with tab3:
        render_ml_predictions(data, predictor)
    
    with tab4:
        render_trend_analysis(data)

def render_overview_analytics(data):
    """Render overview analytics dashboard"""
    st.markdown("### 📊 Comprehensive Overview Analytics")
    
    # Key metrics
    metrics = calculate_metrics(data)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", metrics['total_students'])
    
    with col2:
        st.metric("Average Marks", f"{metrics['average_marks']:.1f}")
    
    with col3:
        at_risk = metrics.get('high_risk', 0) + metrics.get('failure_risk', 0)
        st.metric("At-Risk Students", at_risk, delta_color="inverse")
    
    with col4:
        st.metric("Courses", metrics['courses_count'])
    
    # Main charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Course distribution
        if 'course_name' in data.columns:
            course_counts = data['course_name'].value_counts()
            fig = px.pie(
                values=course_counts.values,
                names=course_counts.index,
                title="Student Distribution by Course",
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Marks distribution
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
    
    # Detailed analysis row
    st.markdown("#### 📈 Detailed Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gender performance
        if 'gender' in data.columns and 'total_internal_marks' in data.columns:
            gender_performance = data.groupby('gender')['total_internal_marks'].agg(['mean', 'std', 'count']).round(2)
            fig = px.bar(
                gender_performance.reset_index(),
                x='gender',
                y='mean',
                error_y='std',
                title="Average Marks by Gender",
                color='gender'
            )
            fig.update_layout(xaxis_title="Gender", yaxis_title="Average Marks")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Age distribution
        if 'age' in data.columns:
            age_counts = data['age'].value_counts().sort_index()
            fig = px.bar(
                x=age_counts.index,
                y=age_counts.values,
                title="Student Age Distribution",
                labels={'x': 'Age', 'y': 'Number of Students'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Course-wise detailed analysis
    if 'course_name' in data.columns and 'total_internal_marks' in data.columns:
        st.markdown("#### 🎓 Course-wise Detailed Analysis")
        
        course_analysis = data.groupby('course_name').agg({
            'total_internal_marks': ['mean', 'median', 'std', 'min', 'max', 'count'],
            'risk_level': lambda x: (x.isin(['High', 'Failure'])).sum()
        }).round(2)
        
        course_analysis.columns = ['avg_marks', 'median_marks', 'std_marks', 'min_marks', 'max_marks', 'student_count', 'at_risk_count']
        course_analysis['at_risk_percent'] = (course_analysis['at_risk_count'] / course_analysis['student_count'] * 100).round(1)
        
        # Display course analysis table
        st.dataframe(course_analysis, use_container_width=True)

def render_risk_analysis(data):
    """Render risk analysis dashboard"""
    st.markdown("### 🎯 Advanced Risk Analysis")
    
    if 'risk_level' not in data.columns:
        st.warning("Risk level data not available. Please ensure your data includes academic marks.")
        return
    
    # Risk distribution metrics
    risk_counts = data['risk_level'].value_counts()
    
    col1, col2, col3, col4 = st.columns(4)
    
    risk_colors = {'Low': '#28a745', 'Medium': '#ffc107', 'High': '#fd7e14', 'Failure': '#dc3545'}
    
    for i, (risk_level, count) in enumerate(risk_counts.items()):
        with [col1, col2, col3, col4][i]:
            percentage = (count / len(data)) * 100
            st.metric(
                f"{risk_level} Risk", 
                count, 
                delta=f"{percentage:.1f}%",
                delta_color="normal" if risk_level in ['Low', 'Medium'] else "inverse"
            )
    
    # Risk analysis charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Risk distribution pie chart
        fig = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            title="Risk Level Distribution",
            color=risk_counts.index,
            color_discrete_map=risk_colors
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Risk by course
        if 'course_name' in data.columns:
            risk_by_course = pd.crosstab(data['course_name'], data['risk_level'])
            fig = px.bar(
                risk_by_course.reset_index().melt(id_vars='course_name'),
                x='course_name',
                y='value',
                color='risk_level',
                title="Risk Distribution by Course",
                color_discrete_map=risk_colors
            )
            fig.update_layout(xaxis_title="Course", yaxis_title="Number of Students")
            st.plotly_chart(fig, use_container_width=True)
    
    # Detailed risk factors analysis
    st.markdown("#### 🔍 Risk Factors Analysis")
    
    # Correlation analysis
    numerical_columns = data.select_dtypes(include=[np.number]).columns
    if len(numerical_columns) > 1:
        st.markdown("##### Correlation Heatmap")
        
        # Calculate correlation matrix
        corr_matrix = data[numerical_columns].corr()
        
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu_r',
            title="Correlation Matrix of Numerical Features"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Risk threshold analysis
    st.markdown("##### Risk Threshold Analysis")
    
    threshold = st.slider(
        "Set Risk Threshold (Total Marks)",
        min_value=0,
        max_value=60,
        value=35,
        help="Students below this threshold are considered at risk"
    )
    
    at_risk_count = (data['total_internal_marks'] < threshold).sum() if 'total_internal_marks' in data.columns else 0
    at_risk_percentage = (at_risk_count / len(data)) * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            f"Students Below {threshold} Marks",
            at_risk_count,
            delta=f"{at_risk_percentage:.1f}%",
            delta_color="inverse"
        )
    
    with col2:
        safe_count = len(data) - at_risk_count
        safe_percentage = 100 - at_risk_percentage
        st.metric(
            f"Students Above {threshold} Marks",
            safe_count,
            delta=f"{safe_percentage:.1f}%"
        )
    
    # Individual component impact on risk
    st.markdown("##### Component-wise Impact on Risk")
    
    marks_components = ['cat1_marks', 'cat2_marks', 'assignment_marks', 'attendance_marks', 'quiz_marks']
    available_components = [col for col in marks_components if col in data.columns]
    
    if available_components:
        component_corr = {}
        for component in available_components:
            if component in data.columns and 'total_internal_marks' in data.columns:
                corr = data[component].corr(data['total_internal_marks'])
                component_corr[component] = corr
        
        if component_corr:
            corr_df = pd.DataFrame({
                'Component': list(component_corr.keys()),
                'Correlation with Total Marks': list(component_corr.values())
            }).sort_values('Correlation with Total Marks', ascending=False)
            
            fig = px.bar(
                corr_df,
                x='Component',
                y='Correlation with Total Marks',
                title="Component Correlation with Total Marks",
                color='Correlation with Total Marks',
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig, use_container_width=True)

def render_ml_predictions(data, predictor):
    """Render machine learning predictions dashboard"""
    st.markdown("### 🤖 Machine Learning Predictions")
    
    # Model training section
    st.markdown("#### 🎯 Train Prediction Model")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Train ML Model", use_container_width=True):
            with st.spinner("Training machine learning model..."):
                success = predictor.train_model(data)
                if success:
                    predictor.save_model()
    
    with col2:
        if st.button("📥 Load Saved Model", use_container_width=True):
            if predictor.load_model():
                st.success("✅ Model loaded successfully!")
            else:
                st.warning("No saved model found. Please train a model first.")
    
    # Model status
    st.markdown("#### 📊 Model Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        status_color = "🟢" if predictor.is_trained else "🔴"
        st.metric("Model Status", f"{status_color} {'Trained' if predictor.is_trained else 'Not Trained'}")
    
    with col2:
        if predictor.is_trained and predictor.feature_importance is not None:
            top_feature = predictor.feature_importance.iloc[0]
            st.metric("Most Important Feature", f"{top_feature['feature']} ({top_feature['importance']:.3f})")
    
    # Feature importance visualization
    if predictor.is_trained and predictor.feature_importance is not None:
        st.markdown("##### Feature Importance")
        
        fig = px.bar(
            predictor.feature_importance,
            x='importance',
            y='feature',
            orientation='h',
            title="Feature Importance in Risk Prediction",
            color='importance',
            color_continuous_scale='viridis'
        )
        fig.update_layout(yaxis_title="Feature", xaxis_title="Importance Score")
        st.plotly_chart(fig, use_container_width=True)
    
    # Interactive prediction
    st.markdown("#### 🔮 Interactive Risk Prediction")
    
    st.info("Enter student marks to predict their risk level using the trained ML model")
    
    if not predictor.is_trained:
        st.warning("Please train the ML model first to enable predictions.")
        return
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        cat1 = st.number_input("CAT 1 Marks", 0.0, 10.0, 7.0, 0.5)
    
    with col2:
        cat2 = st.number_input("CAT 2 Marks", 0.0, 10.0, 7.0, 0.5)
    
    with col3:
        assignment = st.number_input("Assignment Marks", 0.0, 15.0, 12.0, 0.5)
    
    with col4:
        attendance = st.number_input("Attendance Marks", 0.0, 5.0, 4.5, 0.1)
    
    with col5:
        quiz = st.number_input("Quiz Marks", 0.0, 10.0, 7.0, 0.5)
    
    if st.button("🎯 Predict Risk Level", type="primary", use_container_width=True):
        features = {
            'cat1_marks': cat1,
            'cat2_marks': cat2,
            'assignment_marks': assignment,
            'attendance_marks': attendance,
            'quiz_marks': quiz
        }
        
        risk_level, confidence = predictor.predict_risk(features)
        
        # Display prediction results
        col1, col2 = st.columns(2)
        
        with col1:
            risk_color_map = {
                "Low": "🟢",
                "Medium": "🟡", 
                "High": "🟠",
                "Failure": "🔴"
            }
            risk_icon = risk_color_map.get(risk_level, "⚪")
            st.metric("Predicted Risk Level", f"{risk_icon} {risk_level}")
        
        with col2:
            st.metric("Prediction Confidence", f"{confidence:.1f}%")
        
        # Show comparison with traditional method
        total_marks = cat1 + cat2 + assignment + attendance + quiz
        traditional_risk = "Low" if total_marks >= 45 else "Medium" if total_marks >= 35 else "High" if total_marks >= 25 else "Failure"
        
        st.info(f"**Traditional method:** {total_marks}/60 = {traditional_risk} risk")
        
        if risk_level != traditional_risk:
            st.warning(f"⚠️ ML prediction differs from traditional method. This could indicate nuanced patterns in the data.")

def render_trend_analysis(data):
    """Render trend analysis dashboard"""
    st.markdown("### 📈 Trend Analysis")
    
    # Time-based analysis (if date data available)
    st.markdown("#### 📅 Performance Trends")
    
    # Since we don't have actual time data, we'll create synthetic trends
    # based on course progression or other available dimensions
    
    if 'course_name' in data.columns and 'total_internal_marks' in data.columns:
        # Course performance trends
        course_trends = data.groupby('course_name').agg({
            'total_internal_marks': ['mean', 'std', 'count']
        }).round(2)
        
        course_trends.columns = ['avg_marks', 'std_marks', 'student_count']
        course_trends = course_trends.sort_values('avg_marks', ascending=False)
        
        # Performance comparison chart
        fig = px.bar(
            course_trends.reset_index(),
            x='course_name',
            y='avg_marks',
            error_y='std_marks',
            title="Course Performance Comparison",
            color='avg_marks',
            color_continuous_scale='viridis'
        )
        fig.update_layout(xaxis_title="Course", yaxis_title="Average Marks")
        st.plotly_chart(fig, use_container_width=True)
    
    # Risk progression analysis
    st.markdown("#### 📊 Risk Progression Analysis")
    
    # Create synthetic risk progression data
    if 'total_internal_marks' in data.columns:
        # Analyze how small changes in marks affect risk levels
        mark_ranges = [
            (0, 25, "Failure"),
            (25, 35, "High"),
            (35, 45, "Medium"), 
            (45, 60, "Low")
        ]
        
        range_data = []
        for min_marks, max_marks, risk_level in mark_ranges:
            count = ((data['total_internal_marks'] >= min_marks) & 
                    (data['total_internal_marks'] < max_marks)).sum()
            range_data.append({
                'Marks Range': f"{min_marks}-{max_marks}",
                'Risk Level': risk_level,
                'Student Count': count,
                'Percentage': (count / len(data)) * 100
            })
        
        range_df = pd.DataFrame(range_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                range_df,
                x='Marks Range',
                y='Student Count',
                color='Risk Level',
                title="Student Distribution by Marks Range",
                color_discrete_map={
                    'Low': '#28a745',
                    'Medium': '#ffc107', 
                    'High': '#fd7e14',
                    'Failure': '#dc3545'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.pie(
                range_df,
                values='Student Count',
                names='Risk Level',
                title="Risk Level Distribution",
                color='Risk Level',
                color_discrete_map={
                    'Low': '#28a745',
                    'Medium': '#ffc107', 
                    'High': '#fd7e14',
                    'Failure': '#dc3545'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Comparative analysis
    st.markdown("#### ⚖️ Comparative Analysis")
    
    if 'course_name' in data.columns and 'risk_level' in data.columns:
        # Course-wise risk comparison
        risk_comparison = pd.crosstab(data['course_name'], data['risk_level'], normalize='index') * 100
        
        fig = px.bar(
            risk_comparison.reset_index().melt(id_vars='course_name'),
            x='course_name',
            y='value',
            color='risk_level',
            title="Risk Level Distribution by Course (%)",
            barmode='stack',
            color_discrete_map={
                'Low': '#28a745',
                'Medium': '#ffc107', 
                'High': '#fd7e14',
                'Failure': '#dc3545'
            }
        )
        fig.update_layout(
            xaxis_title="Course",
            yaxis_title="Percentage (%)",
            legend_title="Risk Level"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Export analytics
    st.markdown("#### 📥 Export Analytics")
    
    if st.button("📊 Generate Analytics Report", use_container_width=True):
        # Create comprehensive analytics report
        report_data = {
            'Total Students': len(data),
            'Average Marks': data['total_internal_marks'].mean() if 'total_internal_marks' in data.columns else 'N/A',
            'Courses': data['course_name'].nunique() if 'course_name' in data.columns else 'N/A'
        }
        
        if 'risk_level' in data.columns:
            risk_summary = data['risk_level'].value_counts().to_dict()
            report_data.update(risk_summary)
        
        report_df = pd.DataFrame(list(report_data.items()), columns=['Metric', 'Value'])
        
        st.success("✅ Analytics report generated!")
        st.dataframe(report_df, use_container_width=True, hide_index=True)
        
        # Download option
        csv_report = report_df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Analytics Report",
            data=csv_report,
            file_name=f"analytics_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

if __name__ == "__main__":
    main()