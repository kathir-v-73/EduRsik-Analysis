# utils.py - Enhanced Utility Functions
import pandas as pd
import numpy as np
import streamlit as st
import os
import json
from datetime import datetime
import re

def load_data():
    """Load student data from CSV file"""
    try:
        if os.path.exists('data/students.csv'):
            data = pd.read_csv('data/students.csv')
            return data
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def save_data(data, filename='data/students.csv'):
    """Save student data to CSV file"""
    try:
        if not os.path.exists('data'):
            os.makedirs('data')
        data.to_csv(filename, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def get_risk_level(total_marks):
    """Determine risk level based on total marks"""
    if total_marks >= 45:
        return "Low"
    elif total_marks >= 35:
        return "Medium"
    elif total_marks >= 25:
        return "High"
    else:
        return "Failure"

def calculate_metrics(data):
    """Calculate various metrics from student data"""
    if data.empty:
        return {}
    
    metrics = {
        'total_students': len(data),
        'average_marks': data['total_internal_marks'].mean() if 'total_internal_marks' in data.columns else 0,
        'courses_count': data['course_name'].nunique() if 'course_name' in data.columns else 0,
        'risk_distribution': {}
    }
    
    if 'risk_level' in data.columns:
        risk_counts = data['risk_level'].value_counts()
        metrics.update({
            'low_risk': risk_counts.get('Low', 0),
            'medium_risk': risk_counts.get('Medium', 0),
            'high_risk': risk_counts.get('High', 0),
            'failure_risk': risk_counts.get('Failure', 0)
        })
        metrics['risk_distribution'] = risk_counts.to_dict()
    
    return metrics

def get_active_file():
    """Get the currently active data file"""
    return st.session_state.get('active_file', 'data/students.csv')

def set_active_file(filename):
    """Set the active data file"""
    st.session_state.active_file = filename

def generate_sample_data(num_students=50):
    """Generate comprehensive sample student data"""
    np.random.seed(42)
    
    courses = {
        "Computer Science Engineering": 30,
        "Electrical Engineering": 25, 
        "Mechanical Engineering": 20,
        "Civil Engineering": 15,
        "Information Technology": 10
    }
    
    # Generate student IDs and names
    student_ids = [f'STU{1000 + i}' for i in range(num_students)]
    first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa', 'William', 'Maria']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
    
    names = [f"{np.random.choice(first_names)} {np.random.choice(last_names)}" for _ in range(num_students)]
    
    # Generate course distribution
    course_list = []
    for course, percentage in courses.items():
        count = int(num_students * percentage / 100)
        course_list.extend([course] * count)
    
    # Adjust for rounding
    while len(course_list) < num_students:
        course_list.append(np.random.choice(list(courses.keys())))
    
    course_list = course_list[:num_students]
    np.random.shuffle(course_list)
    
    sample_data = {
        'student_id': student_ids,
        'name': names,
        'email': [f"student{i}@university.edu" for i in range(num_students)],
        'phone': [f"+1-555-{1000 + i:04d}" for i in range(num_students)],
        'age': np.random.randint(18, 25, num_students),
        'gender': np.random.choice(['Male', 'Female'], num_students, p=[0.55, 0.45]),
        'course_name': course_list,
        'course_code': [f"{course[:2].upper()}{np.random.randint(100, 500)}" for course in course_list],
        'cat1_marks': np.random.normal(7.5, 1.5, num_students).clip(0, 10).round(1),
        'cat2_marks': np.random.normal(7.0, 1.8, num_students).clip(0, 10).round(1),
        'assignment_marks': np.random.normal(12.5, 1.2, num_students).clip(0, 15).round(1),
        'attendance_marks': np.random.normal(4.2, 0.5, num_students).clip(0, 5).round(1),
        'quiz_marks': np.random.normal(7.8, 1.3, num_students).clip(0, 10).round(1)
    }
    
    df = pd.DataFrame(sample_data)
    
    # Calculate totals and risk
    df['total_internal_marks'] = (
        df['cat1_marks'] + df['cat2_marks'] + 
        df['assignment_marks'] + df['attendance_marks'] + 
        df['quiz_marks']
    )
    df['risk_level'] = df['total_internal_marks'].apply(get_risk_level)
    df['risk_score'] = (df['total_internal_marks'] / 60) * 100
    
    return df

def validate_student_data(df):
    """Validate student data structure and content"""
    required_columns = ['student_id', 'name', 'email']
    
    # Check required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    # Check for duplicate student IDs
    if df['student_id'].duplicated().any():
        return False, "Duplicate student IDs found"
    
    # Validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    invalid_emails = df[~df['email'].astype(str).str.match(email_pattern, na=False)]
    if not invalid_emails.empty:
        return False, f"Invalid email format for {len(invalid_emails)} records"
    
    return True, "Data validation successful"

def get_email_config():
    """Get email configuration"""
    config_file = 'config/email_config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}

def save_email_config(config):
    """Save email configuration"""
    os.makedirs('config', exist_ok=True)
    with open('config/email_config.json', 'w') as f:
        json.dump(config, f, indent=2)