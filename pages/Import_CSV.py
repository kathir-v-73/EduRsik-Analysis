# pages/3_📤_Import_CSV.py
import streamlit as st
import pandas as pd
import numpy as np
import os
from utils import load_data, save_data, generate_sample_data, validate_student_data, get_risk_level

def main():
    st.markdown("""
    <div class='main-header'>
        <h1>📤 Data Import & Management</h1>
        <p>Import, Validate, and Manage Student Data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different import methods
    tab1, tab2, tab3, tab4 = st.tabs([
        "📁 Import CSV", "🎯 Generate Sample", "🔄 Data Validation", "📊 Data Preview"
    ])
    
    with tab1:
        render_import_csv_tab()
    
    with tab2:
        render_generate_sample_tab()
    
    with tab3:
        render_data_validation_tab()
    
    with tab4:
        render_data_preview_tab()

def render_import_csv_tab():
    """Render CSV import tab"""
    st.markdown("### 📁 Import CSV File")
    
    st.info("""
    **Supported CSV Format:**
    - Must include: student_id, name, email
    - Optional: phone, age, gender, course_name, course_code, cat1_marks, cat2_marks, assignment_marks, attendance_marks, quiz_marks
    - File encoding: UTF-8 recommended
    """)
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload your student data CSV file"
    )
    
    if uploaded_file is not None:
        try:
            # Read the uploaded file
            df = pd.read_csv(uploaded_file)
            
            st.success(f"✅ File loaded successfully! Found {len(df)} records")
            
            # Show preview
            st.markdown("#### 📋 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Data validation
            is_valid, validation_message = validate_student_data(df)
            
            if not is_valid:
                st.error(f"❌ Validation Error: {validation_message}")
                return
            
            # Calculate additional fields if needed
            if all(col in df.columns for col in ['cat1_marks', 'cat2_marks', 'assignment_marks', 'attendance_marks', 'quiz_marks']):
                if 'total_internal_marks' not in df.columns:
                    df['total_internal_marks'] = (
                        df['cat1_marks'] + df['cat2_marks'] + 
                        df['assignment_marks'] + df['attendance_marks'] + 
                        df['quiz_marks']
                    )
                
                if 'risk_level' not in df.columns:
                    df['risk_level'] = df['total_internal_marks'].apply(get_risk_level)
                
                if 'risk_score' not in df.columns:
                    df['risk_score'] = (df['total_internal_marks'] / 60) * 100
            
            # Import options
            st.markdown("#### ⚙️ Import Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                import_action = st.radio(
                    "Import Action",
                    options=["Replace Existing Data", "Merge with Existing Data"],
                    help="Choose how to handle existing data"
                )
            
            with col2:
                if st.button("🚀 Import Data", type="primary", use_container_width=True):
                    current_data = load_data()
                    
                    if import_action == "Replace Existing Data" or current_data.empty:
                        final_data = df
                    else:
                        # Merge data, keeping the uploaded version for duplicates
                        final_data = pd.concat([current_data, df]).drop_duplicates(
                            subset=['student_id'], 
                            keep='last'
                        ).reset_index(drop=True)
                    
                    # Save the data
                    if save_data(final_data):
                        st.success(f"✅ Data imported successfully! Total records: {len(final_data)}")
                        st.balloons()
                        
                        # Show import summary
                        st.markdown("#### 📈 Import Summary")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Total Records", len(final_data))
                        
                        with col2:
                            new_records = len(df) if import_action == "Replace Existing Data" else len(df[~df['student_id'].isin(current_data['student_id'])])
                            st.metric("New Records", new_records)
                        
                        with col3:
                            if 'risk_level' in final_data.columns:
                                high_risk = (final_data['risk_level'].isin(['High', 'Failure'])).sum()
                                st.metric("At-Risk Students", high_risk, delta_color="inverse")
                    else:
                        st.error("❌ Failed to save imported data")
        
        except Exception as e:
            st.error(f"❌ Error reading CSV file: {str(e)}")

def render_generate_sample_tab():
    """Render sample data generation tab"""
    st.markdown("### 🎯 Generate Sample Data")
    
    st.info("""
    **Sample Data Includes:**
    - 50 realistic student records
    - Complete academic performance data
    - Pre-calculated risk assessments
    - Multiple courses and demographics
    - Perfect for testing and demonstration
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_students = st.number_input(
            "Number of Students",
            min_value=10,
            max_value=500,
            value=50,
            help="Number of sample student records to generate"
        )
    
    with col2:
        action = st.radio(
            "Action",
            options=["Replace Existing Data", "Add to Existing Data"],
            help="Choose how to handle existing data"
        )
    
    if st.button("🎲 Generate Sample Data", type="primary", use_container_width=True):
        with st.spinner("Generating realistic sample data..."):
            sample_data = generate_sample_data(num_students)
            
            current_data = load_data()
            
            if action == "Replace Existing Data" or current_data.empty:
                final_data = sample_data
            else:
                final_data = pd.concat([current_data, sample_data]).drop_duplicates(
                    subset=['student_id'], 
                    keep='last'
                ).reset_index(drop=True)
            
            if save_data(final_data):
                st.success(f"✅ Sample data generated! Total records: {len(final_data)}")
                st.balloons()
                
                # Show sample data preview
                st.markdown("#### 📋 Sample Data Preview")
                st.dataframe(final_data.head(10), use_container_width=True)
                
                # Show statistics
                st.markdown("#### 📊 Sample Data Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Students", len(final_data))
                
                with col2:
                    courses = final_data['course_name'].nunique() if 'course_name' in final_data.columns else 0
                    st.metric("Courses", courses)
                
                with col3:
                    if 'risk_level' in final_data.columns:
                        low_risk = (final_data['risk_level'] == 'Low').sum()
                        st.metric("Low Risk", low_risk)
                
                with col4:
                    if 'risk_level' in final_data.columns:
                        high_risk = (final_data['risk_level'].isin(['High', 'Failure'])).sum()
                        st.metric("At Risk", high_risk, delta_color="inverse")
            else:
                st.error("❌ Failed to save sample data")

def render_data_validation_tab():
    """Render data validation tab"""
    st.markdown("### 🔄 Data Validation")
    
    data = load_data()
    
    if data.empty:
        st.info("No data available for validation. Please import or generate data first.")
        return
    
    st.markdown(f"#### 📊 Validating {len(data)} Student Records")
    
    # Run validation
    is_valid, validation_message = validate_student_data(data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if is_valid:
            st.success("✅ Data Validation Passed")
        else:
            st.error(f"❌ Data Validation Failed: {validation_message}")
    
    with col2:
        st.metric("Total Records", len(data))
    
    # Detailed validation report
    st.markdown("#### 📋 Detailed Validation Report")
    
    validation_results = []
    
    # Check required columns
    required_columns = ['student_id', 'name', 'email']
    missing_columns = [col for col in required_columns if col not in data.columns]
    validation_results.append({
        "Check": "Required Columns",
        "Status": "✅ Pass" if not missing_columns else "❌ Fail",
        "Details": "All required columns present" if not missing_columns else f"Missing: {', '.join(missing_columns)}"
    })
    
    # Check duplicate student IDs
    if 'student_id' in data.columns:
        duplicate_ids = data['student_id'].duplicated().sum()
        validation_results.append({
            "Check": "Unique Student IDs",
            "Status": "✅ Pass" if duplicate_ids == 0 else "❌ Fail",
            "Details": f"All student IDs are unique" if duplicate_ids == 0 else f"Found {duplicate_ids} duplicate IDs"
        })
    
    # Check email format
    if 'email' in data.columns:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        invalid_emails = data[~data['email'].astype(str).str.match(email_pattern, na=False)]
        validation_results.append({
            "Check": "Email Format",
            "Status": "✅ Pass" if len(invalid_emails) == 0 else "⚠️ Warning",
            "Details": f"All emails valid" if len(invalid_emails) == 0 else f"{len(invalid_emails)} invalid email formats"
        })
    
    # Check marks range
    marks_columns = ['cat1_marks', 'cat2_marks', 'assignment_marks', 'attendance_marks', 'quiz_marks']
    for col in marks_columns:
        if col in data.columns:
            out_of_range = data[(data[col] < 0) | (data[col] > {
                'cat1_marks': 10, 'cat2_marks': 10, 'assignment_marks': 15, 
                'attendance_marks': 5, 'quiz_marks': 10
            }[col])].shape[0]
            validation_results.append({
                "Check": f"{col} Range",
                "Status": "✅ Pass" if out_of_range == 0 else "⚠️ Warning",
                "Details": f"All values in range" if out_of_range == 0 else f"{out_of_range} values out of range"
            })
    
    # Display validation results
    validation_df = pd.DataFrame(validation_results)
    st.dataframe(validation_df, use_container_width=True, hide_index=True)
    
    # Data cleaning options
    st.markdown("#### 🧹 Data Cleaning Options")
    
    if st.button("🔄 Clean Data Automatically", use_container_width=True):
        cleaned_data = data.copy()
        
        # Remove duplicate student IDs (keep first occurrence)
        if 'student_id' in cleaned_data.columns:
            cleaned_data = cleaned_data.drop_duplicates(subset=['student_id'], keep='first')
        
        # Fix marks range issues
        for col in marks_columns:
            if col in cleaned_data.columns:
                max_val = {'cat1_marks': 10, 'cat2_marks': 10, 'assignment_marks': 15, 
                          'attendance_marks': 5, 'quiz_marks': 10}[col]
                cleaned_data[col] = cleaned_data[col].clip(0, max_val)
        
        # Recalculate totals if marks were cleaned
        if all(col in cleaned_data.columns for col in marks_columns):
            cleaned_data['total_internal_marks'] = (
                cleaned_data['cat1_marks'] + cleaned_data['cat2_marks'] + 
                cleaned_data['assignment_marks'] + cleaned_data['attendance_marks'] + 
                cleaned_data['quiz_marks']
            )
            cleaned_data['risk_level'] = cleaned_data['total_internal_marks'].apply(get_risk_level)
            cleaned_data['risk_score'] = (cleaned_data['total_internal_marks'] / 60) * 100
        
        if save_data(cleaned_data):
            st.success("✅ Data cleaned successfully!")
            st.rerun()
        else:
            st.error("❌ Failed to save cleaned data")

def render_data_preview_tab():
    """Render data preview tab"""
    st.markdown("### 📊 Data Preview & Statistics")
    
    data = load_data()
    
    if data.empty:
        st.info("No data available for preview. Please import or generate data first.")
        return
    
    st.markdown(f"#### 📋 Complete Dataset ({len(data)} records)")
    
    # Show full data with pagination
    page_size = st.slider("Records per page", 10, 100, 20)
    
    total_pages = max(1, len(data) // page_size)
    page_number = st.number_input("Page", 1, total_pages, 1)
    
    start_idx = (page_number - 1) * page_size
    end_idx = start_idx + page_size
    
    st.dataframe(data.iloc[start_idx:end_idx], use_container_width=True)
    
    st.markdown(f"**Showing records {start_idx + 1} to {min(end_idx, len(data))} of {len(data)}**")
    
    # Data statistics
    st.markdown("#### 📈 Data Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Column Information")
        col_info = pd.DataFrame({
            'Column': data.columns,
            'Data Type': data.dtypes.astype(str),
            'Non-Null Count': data.notna().sum(),
            'Null Count': data.isna().sum()
        })
        st.dataframe(col_info, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("##### Numerical Statistics")
        if data.select_dtypes(include=[np.number]).shape[1] > 0:
            st.dataframe(data.describe(), use_container_width=True)
        else:
            st.info("No numerical columns for statistics")
    
    # Export options
    st.markdown("#### 📥 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Export to CSV", use_container_width=True):
            csv = data.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"students_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        if st.button("📊 Export Statistics", use_container_width=True):
            stats = data.describe(include='all').T
            csv_stats = stats.to_csv()
            st.download_button(
                label="⬇️ Download Stats",
                data=csv_stats,
                file_name=f"students_stats_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col3:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

if __name__ == "__main__":
    main()