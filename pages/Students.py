# pages/2_👥_Students.py
import streamlit as st
import pandas as pd
import numpy as np
from utils import load_data, save_data, get_risk_level
from model import StudentPredictor
import re

def main():
    st.markdown("""
    <div class='main-header'>
        <h1>👥 Student Management</h1>
        <p>Comprehensive Student Records Management System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load current data
    data = load_data()
    predictor = StudentPredictor()
    
    # Tabs for different student operations
    tab1, tab2, tab3 = st.tabs([
        "➕ Add Student", "👀 View Students", "✏️ Edit Students"
    ])
    
    with tab1:
        render_add_student_tab(data, predictor)
    
    with tab2:
        render_view_students_tab(data)
    
    with tab3:
        render_edit_students_tab(data, predictor)

def render_add_student_tab(data, predictor):
    """Render add student form tab"""
    st.markdown("### ➕ Add New Student")
    
    with st.form("add_student_form"):
        st.markdown("#### 🏷️ Basic Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            student_id = st.text_input(
                "Student ID *",
                placeholder="e.g., STU1001",
                help="Unique identifier for the student"
            )
            name = st.text_input(
                "Full Name *",
                placeholder="e.g., John Smith",
                help="Student's full name"
            )
            email = st.text_input(
                "Email Address *",
                placeholder="e.g., john.smith@university.edu",
                help="Student's email address"
            )
        
        with col2:
            phone = st.text_input(
                "Phone Number",
                placeholder="e.g., +1-555-0100",
                help="Student's contact number"
            )
            age = st.number_input(
                "Age",
                min_value=16,
                max_value=30,
                value=18,
                help="Student's age"
            )
            gender = st.selectbox(
                "Gender",
                options=["Male", "Female", "Other", "Prefer not to say"],
                help="Student's gender"
            )
        
        st.markdown("#### 📚 Academic Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            course_name = st.text_input(
                "Course Name *",
                placeholder="e.g., Computer Science Engineering",
                help="Name of the course or program"
            )
            course_code = st.text_input(
                "Course Code",
                placeholder="e.g., CS101",
                help="Course code or identifier"
            )
        
        with col2:
            # Generate a new student ID if not provided
            if not student_id and not data.empty and 'student_id' in data.columns:
                try:
                    last_id = data['student_id'].str.extract(r'(\d+)').astype(float).max().iloc[0]
                    new_id = f"STU{int(last_id) + 1}" if not pd.isna(last_id) else "STU1001"
                    student_id = st.text_input(
                        "Generated Student ID",
                        value=new_id,
                        disabled=True,
                        help="Auto-generated student ID"
                    )
                except:
                    student_id = st.text_input("Student ID *", placeholder="e.g., STU1001")
        
        st.markdown("#### 📊 Academic Marks")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            cat1_marks = st.number_input(
                "CAT 1 Marks (0-10)",
                min_value=0.0,
                max_value=10.0,
                value=7.0,
                step=0.5,
                help="Continuous Assessment Test 1 marks"
            )
        
        with col2:
            cat2_marks = st.number_input(
                "CAT 2 Marks (0-10)",
                min_value=0.0,
                max_value=10.0,
                value=7.0,
                step=0.5,
                help="Continuous Assessment Test 2 marks"
            )
        
        with col3:
            assignment_marks = st.number_input(
                "Assignment Marks (0-15)",
                min_value=0.0,
                max_value=15.0,
                value=12.0,
                step=0.5,
                help="Assignment/project marks"
            )
        
        with col4:
            attendance_marks = st.number_input(
                "Attendance Marks (0-5)",
                min_value=0.0,
                max_value=5.0,
                value=4.5,
                step=0.1,
                help="Attendance and participation marks"
            )
        
        with col5:
            quiz_marks = st.number_input(
                "Quiz Marks (0-10)",
                min_value=0.0,
                max_value=10.0,
                value=7.0,
                step=0.5,
                help="Quiz marks"
            )
        
        # Calculate total and risk
        total_marks = cat1_marks + cat2_marks + assignment_marks + attendance_marks + quiz_marks
        risk_level = get_risk_level(total_marks)
        risk_score = (total_marks / 60) * 100
        
        # ML Prediction if model is trained
        ml_risk_level = "N/A"
        ml_confidence = 0
        
        if predictor.is_trained:
            features = {
                'cat1_marks': cat1_marks,
                'cat2_marks': cat2_marks,
                'assignment_marks': assignment_marks,
                'attendance_marks': attendance_marks,
                'quiz_marks': quiz_marks
            }
            ml_risk_level, ml_confidence = predictor.predict_risk(features)
        
        # Display calculated values
        st.markdown("#### 📈 Risk Assessment")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Internal Marks", f"{total_marks:.1f}/60")
        
        with col2:
            risk_color_map = {
                "Low": "risk-low",
                "Medium": "risk-medium", 
                "High": "risk-high",
                "Failure": "risk-failure"
            }
            risk_class = risk_color_map.get(risk_level, "")
            st.markdown(f"**Risk Level:** <span class='{risk_class}'>{risk_level}</span>", unsafe_allow_html=True)
            
            if predictor.is_trained and ml_risk_level not in ["N/A", "Model not trained"]:
                ml_class = risk_color_map.get(ml_risk_level, "")
                st.markdown(f"**ML Prediction:** <span class='{ml_class}'>{ml_risk_level}</span> ({ml_confidence:.1f}%)", unsafe_allow_html=True)
        
        with col3:
            st.metric("Risk Score", f"{risk_score:.1f}%")
        
        # Submit button - FIXED: Added inside the form
        submitted = st.form_submit_button(
            "➕ Add Student",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if not student_id or not name or not email or not course_name:
                st.error("❌ Please fill in all required fields (marked with *)")
                return
            
            # Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                st.error("❌ Please enter a valid email address")
                return
            
            # Check for duplicate student ID
            if not data.empty and 'student_id' in data.columns and student_id in data['student_id'].values:
                st.error(f"❌ Student ID '{student_id}' already exists")
                return
            
            # Create new student record
            new_student = {
                'student_id': student_id,
                'name': name,
                'email': email,
                'phone': phone,
                'age': age,
                'gender': gender,
                'course_name': course_name,
                'course_code': course_code,
                'cat1_marks': cat1_marks,
                'cat2_marks': cat2_marks,
                'assignment_marks': assignment_marks,
                'attendance_marks': attendance_marks,
                'quiz_marks': quiz_marks,
                'total_internal_marks': total_marks,
                'risk_level': risk_level,
                'risk_score': risk_score
            }
            
            # Add to dataframe
            if data.empty:
                data = pd.DataFrame([new_student])
            else:
                data = pd.concat([data, pd.DataFrame([new_student])], ignore_index=True)
            
            # Save data
            if save_data(data):
                st.success(f"✅ Student '{name}' added successfully!")
                st.balloons()
                
                # Clear form by rerunning
                st.rerun()
            else:
                st.error("❌ Failed to save student data")

def render_view_students_tab(data):
    """Render view students tab"""
    st.markdown("### 👀 View Students")
    
    if data.empty:
        st.info("No student records available. Add some students to get started!")
        return
    
    # Filters
    st.markdown("#### 🔍 Filter Students")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        course_filter = st.selectbox(
            "Filter by Course",
            options=["All"] + list(data['course_name'].unique()) if 'course_name' in data.columns else ["All"]
        )
    
    with col2:
        risk_filter = st.selectbox(
            "Filter by Risk Level",
            options=["All"] + list(data['risk_level'].unique()) if 'risk_level' in data.columns else ["All"]
        )
    
    with col3:
        search_term = st.text_input("Search by Name/ID")
    
    with col4:
        min_marks = st.number_input(
            "Min Marks",
            min_value=0,
            max_value=60,
            value=0,
            help="Filter by minimum total marks"
        )
    
    # Apply filters
    filtered_data = data.copy()
    
    if course_filter != "All" and 'course_name' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['course_name'] == course_filter]
    
    if risk_filter != "All" and 'risk_level' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['risk_level'] == risk_filter]
    
    if search_term:
        mask = (
            filtered_data['name'].str.contains(search_term, case=False, na=False) |
            filtered_data['student_id'].str.contains(search_term, case=False, na=False)
        )
        filtered_data = filtered_data[mask]
    
    if 'total_internal_marks' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['total_internal_marks'] >= min_marks]
    
    # Display results
    st.markdown(f"#### 📋 Student Records ({len(filtered_data)} found)")
    
    if len(filtered_data) > 0:
        # Select columns to display
        display_columns = ['student_id', 'name', 'course_name']
        if 'risk_level' in filtered_data.columns:
            display_columns.append('risk_level')
        if 'total_internal_marks' in filtered_data.columns:
            display_columns.append('total_internal_marks')
        if 'email' in filtered_data.columns:
            display_columns.append('email')
        
        # Format risk levels with colors
        def format_risk_level(val):
            color_map = {
                "Low": "🟢",
                "Medium": "🟡", 
                "High": "🟠",
                "Failure": "🔴"
            }
            return f"{color_map.get(val, '⚪')} {val}"
        
        display_data = filtered_data[display_columns].copy()
        if 'risk_level' in display_data.columns:
            display_data['risk_level'] = display_data['risk_level'].apply(format_risk_level)
        
        st.dataframe(
            display_data,
            use_container_width=True,
            height=400
        )
        
        # Export option
        if st.button("📥 Export Filtered Data", use_container_width=True):
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"students_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.warning("No students match the current filters")

def render_edit_students_tab(data, predictor):
    """Render edit students tab"""
    st.markdown("### ✏️ Edit Students")
    
    if data.empty:
        st.info("No student records available to edit.")
        return
    
    # Student selection
    student_options = data[['student_id', 'name']].apply(lambda x: f"{x['student_id']} - {x['name']}", axis=1).tolist()
    selected_student = st.selectbox(
        "Select Student to Edit",
        options=student_options,
        help="Choose a student to edit their details"
    )
    
    if selected_student:
        student_id = selected_student.split(" - ")[0]
        student_data = data[data['student_id'] == student_id].iloc[0]
        
        with st.form("edit_student_form"):  # FIXED: Added form context
            st.markdown(f"#### ✏️ Editing: {student_data['name']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input(
                    "Full Name *",
                    value=student_data.get('name', ''),
                    help="Student's full name"
                )
                new_email = st.text_input(
                    "Email Address *",
                    value=student_data.get('email', ''),
                    help="Student's email address"
                )
                new_phone = st.text_input(
                    "Phone Number",
                    value=student_data.get('phone', ''),
                    help="Student's contact number"
                )
            
            with col2:
                new_age = st.number_input(
                    "Age",
                    min_value=16,
                    max_value=30,
                    value=int(student_data.get('age', 18)),
                    help="Student's age"
                )
                new_gender = st.selectbox(
                    "Gender",
                    options=["Male", "Female", "Other", "Prefer not to say"],
                    index=["Male", "Female", "Other", "Prefer not to say"].index(student_data.get('gender', 'Male')),
                    help="Student's gender"
                )
                new_course = st.text_input(
                    "Course Name *",
                    value=student_data.get('course_name', ''),
                    help="Name of the course or program"
                )
            
            st.markdown("#### 📊 Academic Marks")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                # Get current value safely
                current_cat1 = student_data.get('cat1_marks', 7.0)
                new_cat1 = st.number_input(
                    "CAT 1 Marks (0-10)",
                    min_value=0.0,
                    max_value=10.0,
                    value=float(min(current_cat1, 10.0)),  # FIXED: Ensure value doesn't exceed max
                    step=0.5
                )
            
            with col2:
                current_cat2 = student_data.get('cat2_marks', 7.0)
                new_cat2 = st.number_input(
                    "CAT 2 Marks (0-10)",
                    min_value=0.0,
                    max_value=10.0,
                    value=float(min(current_cat2, 10.0)),  # FIXED: Ensure value doesn't exceed max
                    step=0.5
                )
            
            with col3:
                current_assignment = student_data.get('assignment_marks', 12.0)
                new_assignment = st.number_input(
                    "Assignment Marks (0-15)",
                    min_value=0.0,
                    max_value=15.0,
                    value=float(min(current_assignment, 15.0)),  # FIXED: Ensure value doesn't exceed max
                    step=0.5
                )
            
            with col4:
                current_attendance = student_data.get('attendance_marks', 4.5)
                new_attendance = st.number_input(
                    "Attendance Marks (0-5)",
                    min_value=0.0,
                    max_value=5.0,
                    value=float(min(current_attendance, 5.0)),  # FIXED: Ensure value doesn't exceed max
                    step=0.1
                )
            
            with col5:
                current_quiz = student_data.get('quiz_marks', 7.0)
                new_quiz = st.number_input(
                    "Quiz Marks (0-10)",
                    min_value=0.0,
                    max_value=10.0,
                    value=float(min(current_quiz, 10.0)),  # FIXED: Ensure value doesn't exceed max
                    step=0.5
                )
            
            # Calculate updated values
            new_total = new_cat1 + new_cat2 + new_assignment + new_attendance + new_quiz
            new_risk = get_risk_level(new_total)
            new_score = (new_total / 60) * 100
            
            # Display updated assessment
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Updated Total Marks", f"{new_total:.1f}/60")
            
            with col2:
                risk_color_map = {
                    "Low": "risk-low",
                    "Medium": "risk-medium", 
                    "High": "risk-high",
                    "Failure": "risk-failure"
                }
                risk_class = risk_color_map.get(new_risk, "")
                st.markdown(f"**Updated Risk Level:** <span class='{risk_class}'>{new_risk}</span>", unsafe_allow_html=True)
            
            # FIXED: Added submit button inside the form
            updated = st.form_submit_button(
                "💾 Update Student",
                type="primary",
                use_container_width=True
            )
            
            if updated:
                if not new_name or not new_email or not new_course:
                    st.error("❌ Please fill in all required fields")
                    return
                
                # Validate marks are within bounds
                marks_validation = [
                    (new_cat1, 0, 10, "CAT 1"),
                    (new_cat2, 0, 10, "CAT 2"),
                    (new_assignment, 0, 15, "Assignment"),
                    (new_attendance, 0, 5, "Attendance"),
                    (new_quiz, 0, 10, "Quiz")
                ]
                
                for mark, min_val, max_val, mark_name in marks_validation:
                    if mark < min_val or mark > max_val:
                        st.error(f"❌ {mark_name} marks must be between {min_val} and {max_val}")
                        return
                
                # Update student data
                update_data = {
                    'name': new_name,
                    'email': new_email,
                    'phone': new_phone,
                    'age': new_age,
                    'gender': new_gender,
                    'course_name': new_course,
                    'cat1_marks': new_cat1,
                    'cat2_marks': new_cat2,
                    'assignment_marks': new_assignment,
                    'attendance_marks': new_attendance,
                    'quiz_marks': new_quiz,
                    'total_internal_marks': new_total,
                    'risk_level': new_risk,
                    'risk_score': new_score
                }
                
                # Update the dataframe
                for key, value in update_data.items():
                    if key in data.columns:
                        data.loc[data['student_id'] == student_id, key] = value
                
                # Save updated data
                if save_data(data):
                    st.success(f"✅ Student '{new_name}' updated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to update student data")

if __name__ == "__main__":
    main()