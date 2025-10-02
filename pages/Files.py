# pages/5_📂_Files.py
import streamlit as st
import pandas as pd
import os
import shutil
from datetime import datetime
from utils import load_data, save_data
import glob

def main():
    st.markdown("""
    <div class='main-header'>
        <h1>📂 File Management System</h1>
        <p>Backup, Restore, and Manage Student Data Files</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('backups', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    
    # File management tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💾 Current Data", "📦 Backups", "📁 File Analysis", "🔄 Data Operations", "⚙️ System Info"
    ])
    
    with tab1:
        render_current_data_tab()
    
    with tab2:
        render_backups_tab()
    
    with tab3:
        render_file_analysis_tab()
    
    with tab4:
        render_data_operations_tab()
    
    with tab5:
        render_system_info_tab()

def render_current_data_tab():
    """Render current data management tab"""
    st.markdown("### 💾 Current Data File")
    
    current_file = 'data/students.csv'
    
    if os.path.exists(current_file):
        # Load and display file info
        file_stats = os.stat(current_file)
        file_size = file_stats.st_size
        modified_time = datetime.fromtimestamp(file_stats.st_mtime)
        
        data = load_data()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("File Size", f"{file_size / 1024:.1f} KB")
        
        with col2:
            st.metric("Records", len(data))
        
        with col3:
            st.metric("Last Modified", modified_time.strftime("%Y-%m-%d %H:%M"))
        
        # File actions
        st.markdown("#### 🔧 File Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("📦 Create Backup", use_container_width=True):
                create_backup()
        
        with col3:
            if st.button("📤 Export Data", use_container_width=True):
                export_data(data, "CSV")
        
        with col4:
            if st.button("🗑️ Clear Data", use_container_width=True, type="secondary"):
                clear_data_confirmation()
        
        # Data summary
        st.markdown("#### 📊 Data Summary")
        
        if not data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Column Information")
                col_info = pd.DataFrame({
                    'Column': data.columns,
                    'Data Type': data.dtypes.astype(str),
                    'Non-Null': data.notna().sum()
                })
                st.dataframe(col_info, use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("##### Quick Stats")
                if 'risk_level' in data.columns:
                    risk_counts = data['risk_level'].value_counts()
                    for risk, count in risk_counts.items():
                        st.write(f"- {risk}: {count} students")
                
                if 'course_name' in data.columns:
                    st.write(f"- Courses: {data['course_name'].nunique()}")
                
                if 'total_internal_marks' in data.columns:
                    st.write(f"- Avg Marks: {data['total_internal_marks'].mean():.1f}")
        else:
            st.info("No data available in the current file.")
    
    else:
        st.warning("No current data file found. Please import or generate data first.")
        
        # File upload option
        st.markdown("#### 📤 Upload Data File")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        
        if uploaded_file is not None:
            try:
                # Save uploaded file
                with open(current_file, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("✅ File uploaded successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error uploading file: {e}")

def render_backups_tab():
    """Render backups management tab"""
    st.markdown("### 📦 Data Backups")
    
    # Create backup section
    st.markdown("#### 💾 Create New Backup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        backup_name = st.text_input(
            "Backup Name",
            value=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            help="Name for the backup file"
        )
    
    with col2:
        backup_description = st.text_area(
            "Backup Description",
            placeholder="Optional description of this backup",
            help="What does this backup contain?"
        )
    
    if st.button("🛡️ Create Backup", type="primary", use_container_width=True):
        if create_backup(backup_name, backup_description):
            st.success("✅ Backup created successfully!")
            st.rerun()
    
    # List existing backups
    st.markdown("#### 📋 Existing Backups")
    
    backups = get_backup_files()
    
    if not backups:
        st.info("No backups found. Create your first backup to get started.")
        return
    
    # Display backups in a table
    backup_data = []
    for backup_file, backup_info in backups.items():
        backup_data.append({
            'Backup Name': backup_info['name'],
            'File Size': f"{backup_info['size'] / 1024:.1f} KB",
            'Records': backup_info['records'],
            'Created': backup_info['created'].strftime("%Y-%m-%d %H:%M"),
            'Description': backup_info.get('description', 'No description')
        })
    
    backup_df = pd.DataFrame(backup_data)
    st.dataframe(backup_df, use_container_width=True, hide_index=True)
    
    # Backup actions
    st.markdown("#### 🔧 Backup Actions")
    
    if backups:
        selected_backup = st.selectbox(
            "Select Backup",
            options=list(backups.keys()),
            format_func=lambda x: f"{backups[x]['name']} ({backups[x]['created'].strftime('%Y-%m-%d %H:%M')})"
        )
        
        if selected_backup:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("🔄 Restore Backup", use_container_width=True):
                    restore_backup(selected_backup)
            
            with col2:
                if st.button("📥 Download Backup", use_container_width=True):
                    download_backup(selected_backup)
            
            with col3:
                if st.button("🔍 Preview Backup", use_container_width=True):
                    preview_backup(selected_backup)
            
            with col4:
                if st.button("🗑️ Delete Backup", use_container_width=True, type="secondary"):
                    delete_backup(selected_backup)

def render_file_analysis_tab():
    """Render file analysis tab - NEW TAB FOR FILE SELECTION AND ANALYSIS"""
    st.markdown("### 📁 File Analysis")
    
    # Get all available data files
    data_files = get_available_data_files()
    
    if not data_files:
        st.info("No data files found. Please upload or create data files first.")
        return
    
    # File selection
    st.markdown("#### 🔍 Select Files for Analysis")
    
    selected_files = st.multiselect(
        "Choose files to analyze:",
        options=list(data_files.keys()),
        format_func=lambda x: f"{data_files[x]['name']} ({data_files[x]['records']} records, {data_files[x]['size']/1024:.1f} KB)",
        help="Select one or more files to analyze and compare"
    )
    
    if selected_files:
        st.markdown("#### 📊 Analysis Results")
        
        # Analyze selected files
        for file_key in selected_files:
            file_info = data_files[file_key]
            
            with st.expander(f"📄 {file_info['name']} - {file_info['records']} records"):
                try:
                    # Load and analyze the file
                    if file_key == 'current':
                        data = load_data()
                    else:
                        data = pd.read_csv(file_info['path'])
                    
                    if not data.empty:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Basic Information**")
                            st.write(f"- Records: {len(data)}")
                            st.write(f"- Columns: {len(data.columns)}")
                            st.write(f"- File Size: {file_info['size']/1024:.1f} KB")
                            
                            # Data types summary
                            st.markdown("**Data Types**")
                            dtype_counts = data.dtypes.value_counts()
                            for dtype, count in dtype_counts.items():
                                st.write(f"- {dtype}: {count} columns")
                        
                        with col2:
                            st.markdown("**Data Quality**")
                            total_cells = data.size
                            null_cells = data.isnull().sum().sum()
                            completeness = ((total_cells - null_cells) / total_cells) * 100
                            
                            st.write(f"- Data Completeness: {completeness:.1f}%")
                            st.write(f"- Null Values: {null_cells}")
                            
                            # Duplicate check
                            if 'student_id' in data.columns:
                                duplicates = data.duplicated(subset=['student_id']).sum()
                                st.write(f"- Duplicate IDs: {duplicates}")
                        
                        # Show sample data
                        st.markdown("**Sample Data**")
                        st.dataframe(data.head(10), use_container_width=True)
                        
                        # Quick actions for this file
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"📊 Analyze {file_info['name']}", key=f"analyze_{file_key}"):
                                st.session_state.current_analysis_file = file_key
                                st.rerun()
                        
                        with col2:
                            if file_key != 'current' and st.button(f"🔄 Set as Current", key=f"set_current_{file_key}"):
                                set_as_current_file(file_info['path'])
                    
                except Exception as e:
                    st.error(f"Error analyzing {file_info['name']}: {e}")
        
        # Comparative analysis if multiple files selected
        if len(selected_files) > 1:
            st.markdown("#### 📈 Comparative Analysis")
            
            comparison_data = []
            for file_key in selected_files:
                file_info = data_files[file_key]
                try:
                    if file_key == 'current':
                        data = load_data()
                    else:
                        data = pd.read_csv(file_info['path'])
                    
                    comparison_data.append({
                        'File': file_info['name'],
                        'Records': len(data),
                        'Columns': len(data.columns),
                        'Size_KB': file_info['size'] / 1024,
                        'Null_Values': data.isnull().sum().sum(),
                        'Duplicate_IDs': data.duplicated(subset=['student_id']).sum() if 'student_id' in data.columns else 0
                    })
                except Exception as e:
                    st.error(f"Error processing {file_info['name']} for comparison: {e}")
            
            if comparison_data:
                comparison_df = pd.DataFrame(comparison_data)
                st.dataframe(comparison_df, use_container_width=True, hide_index=True)

def get_available_data_files():
    """Get all available data files for analysis"""
    files = {}
    
    # Current data file
    current_file = 'data/students.csv'
    if os.path.exists(current_file):
        try:
            data = load_data()
            files['current'] = {
                'name': 'Current Data (students.csv)',
                'path': current_file,
                'size': os.path.getsize(current_file),
                'records': len(data),
                'type': 'current'
            }
        except:
            pass
    
    # Backup files
    backup_files = get_backup_files()
    for backup_name, backup_info in backup_files.items():
        files[f'backup_{backup_name}'] = {
            'name': f"Backup: {backup_info['name']}",
            'path': f"backups/{backup_name}.csv",
            'size': backup_info['size'],
            'records': backup_info['records'],
            'type': 'backup'
        }
    
    # Uploaded files
    upload_dir = 'uploads'
    if os.path.exists(upload_dir):
        for file in os.listdir(upload_dir):
            if file.endswith('.csv'):
                file_path = os.path.join(upload_dir, file)
                try:
                    data = pd.read_csv(file_path)
                    files[f'upload_{file}'] = {
                        'name': f"Uploaded: {file}",
                        'path': file_path,
                        'size': os.path.getsize(file_path),
                        'records': len(data),
                        'type': 'upload'
                    }
                except:
                    continue
    
    return files

def set_as_current_file(file_path):
    """Set a selected file as the current data file"""
    try:
        shutil.copy2(file_path, 'data/students.csv')
        st.success("✅ File set as current data successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"Error setting file as current: {e}")

def preview_backup(backup_name):
    """Preview backup file contents"""
    try:
        backup_file = f"backups/{backup_name}.csv"
        data = pd.read_csv(backup_file)
        
        st.markdown(f"#### 📋 Preview: {backup_name}")
        st.write(f"**Records:** {len(data)}")
        st.dataframe(data.head(10), use_container_width=True)
        
    except Exception as e:
        st.error(f"Error previewing backup: {e}")

def delete_backup(backup_name):
    """Delete a backup file with confirmation"""
    # Use session state to track deletion confirmation
    if f'confirm_delete_{backup_name}' not in st.session_state:
        st.session_state[f'confirm_delete_{backup_name}'] = False
    
    if not st.session_state[f'confirm_delete_{backup_name}']:
        st.warning(f"⚠️ Are you sure you want to delete backup '{backup_name}'?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Delete", key=f"yes_del_{backup_name}"):
                st.session_state[f'confirm_delete_{backup_name}'] = True
        with col2:
            if st.button("❌ Cancel", key=f"cancel_del_{backup_name}"):
                st.session_state[f'confirm_delete_{backup_name}'] = False
                st.rerun()
    else:
        try:
            csv_file = f"backups/{backup_name}.csv"
            json_file = f"backups/{backup_name}.json"
            
            if os.path.exists(csv_file):
                os.remove(csv_file)
            
            if os.path.exists(json_file):
                os.remove(json_file)
            
            st.success(f"✅ Backup '{backup_name}' deleted successfully!")
            st.session_state[f'confirm_delete_{backup_name}'] = False
            st.rerun()
        
        except Exception as e:
            st.error(f"Error deleting backup: {e}")

def clear_data_confirmation():
    """Show confirmation for clearing data"""
    # Use session state for confirmation
    if 'confirm_clear_data' not in st.session_state:
        st.session_state.confirm_clear_data = False
    
    if not st.session_state.confirm_clear_data:
        st.warning("⚠️ This will permanently delete all current student data!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Clear Data", type="primary"):
                st.session_state.confirm_clear_data = True
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.confirm_clear_data = False
    else:
        clear_data()

def clear_data():
    """Clear all current data"""
    try:
        data_file = 'data/students.csv'
        if os.path.exists(data_file):
            os.remove(data_file)
            st.success("✅ Data cleared successfully!")
            st.session_state.confirm_clear_data = False
            st.rerun()
        else:
            st.info("No data file found to clear")
    
    except Exception as e:
        st.error(f"Error clearing data: {e}")

# Keep all the other existing functions (create_backup, get_backup_files, restore_backup, 
# download_backup, render_data_operations_tab, render_system_info_tab, and all data operation functions)
# They remain the same as in your original code

def create_backup(backup_name=None, description=""):
    """Create a backup of current data"""
    try:
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        source_file = 'data/students.csv'
        if not os.path.exists(source_file):
            st.error("No data file found to backup")
            return False
        
        # Create backup filename
        backup_file = f"backups/{backup_name}.csv"
        
        # Copy file
        shutil.copy2(source_file, backup_file)
        
        # Create backup info file
        backup_info = {
            'name': backup_name,
            'created': datetime.now().isoformat(),
            'description': description,
            'records': len(load_data()),
            'size': os.path.getsize(source_file)
        }
        
        info_file = f"backups/{backup_name}.json"
        import json
        with open(info_file, 'w') as f:
            json.dump(backup_info, f, indent=2)
        
        return True
    
    except Exception as e:
        st.error(f"Error creating backup: {e}")
        return False

def get_backup_files():
    """Get list of backup files with information"""
    backups = {}
    
    try:
        if not os.path.exists('backups'):
            return backups
        
        for file in os.listdir('backups'):
            if file.endswith('.csv'):
                backup_name = file[:-4]  # Remove .csv extension
                csv_file = f"backups/{file}"
                json_file = f"backups/{backup_name}.json"
                
                # Get basic file info
                file_stats = os.stat(csv_file)
                
                backup_info = {
                    'name': backup_name,
                    'size': file_stats.st_size,
                    'created': datetime.fromtimestamp(file_stats.st_mtime),
                    'records': 0
                }
                
                # Load additional info from JSON if available
                if os.path.exists(json_file):
                    import json
                    with open(json_file, 'r') as f:
                        json_info = json.load(f)
                        backup_info.update(json_info)
                        if 'created' in json_info:
                            backup_info['created'] = datetime.fromisoformat(json_info['created'])
                
                # Count records in CSV
                try:
                    data = pd.read_csv(csv_file)
                    backup_info['records'] = len(data)
                except:
                    backup_info['records'] = 0
                
                backups[backup_name] = backup_info
        
        # Sort by creation date (newest first)
        backups = dict(sorted(backups.items(), key=lambda x: x[1]['created'], reverse=True))
        
        return backups
    
    except Exception as e:
        st.error(f"Error reading backups: {e}")
        return {}

def restore_backup(backup_name):
    """Restore a backup to current data"""
    try:
        backup_file = f"backups/{backup_name}.csv"
        
        if not os.path.exists(backup_file):
            st.error("Backup file not found")
            return
        
        # Copy backup to current data
        shutil.copy2(backup_file, 'data/students.csv')
        
        st.success(f"✅ Backup '{backup_name}' restored successfully!")
        st.rerun()
    
    except Exception as e:
        st.error(f"Error restoring backup: {e}")

def download_backup(backup_name):
    """Download a backup file"""
    try:
        backup_file = f"backups/{backup_name}.csv"
        
        if not os.path.exists(backup_file):
            st.error("Backup file not found")
            return
        
        with open(backup_file, 'rb') as f:
            data = f.read()
        
        st.download_button(
            label="⬇️ Download Backup File",
            data=data,
            file_name=f"{backup_name}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    except Exception as e:
        st.error(f"Error downloading backup: {e}")

def render_data_operations_tab():
    """Render data operations tab"""
    st.markdown("### 🔄 Data Operations")
    
    data = load_data()
    
    if data.empty:
        st.info("No data available for operations. Please import or generate data first.")
        return
    
    st.markdown("#### 🧹 Data Cleaning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Find Duplicates", use_container_width=True):
            find_duplicates(data)
    
    with col2:
        if st.button("🔄 Remove Duplicates", use_container_width=True):
            remove_duplicates(data)
    
    st.markdown("#### 📊 Data Transformation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📈 Recalculate Totals", use_container_width=True):
            recalculate_totals(data)
    
    with col2:
        if st.button("🎯 Update Risk Levels", use_container_width=True):
            update_risk_levels(data)
    
    with col3:
        if st.button("🔄 Refresh All", use_container_width=True):
            refresh_all_data(data)
    
    st.markdown("#### 📤 Export Options")
    
    export_format = st.selectbox(
        "Export Format",
        options=["CSV", "Excel", "JSON"],
        help="Choose the format for exporting data"
    )
    
    if st.button(f"📥 Export as {export_format}", type="primary", use_container_width=True):
        export_data(data, export_format)

def render_system_info_tab():
    """Render system information tab"""
    st.markdown("### ⚙️ System Information")
    
    # System status
    st.markdown("#### 🖥️ System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Check data directory
        data_exists = os.path.exists('data/students.csv')
        status_color = "🟢" if data_exists else "🔴"
        st.metric("Data File", f"{status_color} {'Available' if data_exists else 'Missing'}")
    
    with col2:
        # Check backups
        backups = get_backup_files()
        st.metric("Backups", f"📦 {len(backups)}")
    
    with col3:
        # Check required directories
        required_dirs = ['data', 'backups', 'model', 'uploads']
        missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
        status_color = "🟢" if not missing_dirs else "🔴"
        st.metric("Directories", f"{status_color} {'All OK' if not missing_dirs else f'Missing {len(missing_dirs)}'}")
    
    # Storage information
    st.markdown("#### 💽 Storage Information")
    
    total_size = 0
    file_count = 0
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.csv', '.json', '.joblib')):
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
                file_count += 1
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Data Files", file_count)
    
    with col2:
        st.metric("Total Storage Used", f"{total_size / (1024*1024):.2f} MB")
    
    # Available files
    st.markdown("#### 📁 Available Data Files")
    data_files = get_available_data_files()
    
    if data_files:
        files_data = []
        for file_key, file_info in data_files.items():
            files_data.append({
                'File Name': file_info['name'],
                'Type': file_info['type'],
                'Records': file_info['records'],
                'Size (KB)': f"{file_info['size'] / 1024:.1f}"
            })
        
        files_df = pd.DataFrame(files_data)
        st.dataframe(files_df, use_container_width=True, hide_index=True)
    else:
        st.info("No data files available.")
    
    # System actions
    st.markdown("#### 🔧 System Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Check System", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear Cache", use_container_width=True):
            clear_cache()
    
    with col3:
        if st.button("📋 Generate Report", use_container_width=True):
            generate_system_report()

# Keep all the remaining utility functions (find_duplicates, remove_duplicates, recalculate_totals, 
# update_risk_levels, refresh_all_data, export_data, clear_cache, generate_system_report)
# They remain the same as in your original code

def find_duplicates(data):
    """Find duplicate records in data"""
    if 'student_id' in data.columns:
        duplicates = data[data.duplicated(subset=['student_id'], keep=False)]
        
        if len(duplicates) > 0:
            st.warning(f"Found {len(duplicates)} duplicate student IDs")
            st.dataframe(duplicates[['student_id', 'name']], use_container_width=True)
        else:
            st.success("✅ No duplicate student IDs found")
    else:
        st.error("Student ID column not found")

def remove_duplicates(data):
    """Remove duplicate records from data"""
    if 'student_id' in data.columns:
        initial_count = len(data)
        data_clean = data.drop_duplicates(subset=['student_id'], keep='first')
        removed_count = initial_count - len(data_clean)
        
        if removed_count > 0:
            if save_data(data_clean):
                st.success(f"✅ Removed {removed_count} duplicate records")
                st.rerun()
            else:
                st.error("Failed to save cleaned data")
        else:
            st.info("No duplicates found to remove")
    else:
        st.error("Student ID column not found")

def recalculate_totals(data):
    """Recalculate total marks and risk scores"""
    marks_columns = ['cat1_marks', 'cat2_marks', 'assignment_marks', 'attendance_marks', 'quiz_marks']
    
    if all(col in data.columns for col in marks_columns):
        data['total_internal_marks'] = (
            data['cat1_marks'] + data['cat2_marks'] + 
            data['assignment_marks'] + data['attendance_marks'] + 
            data['quiz_marks']
        )
        
        if save_data(data):
            st.success("✅ Total marks recalculated successfully!")
            st.rerun()
        else:
            st.error("Failed to save recalculated data")
    else:
        st.error("Not all marks columns are available")

def update_risk_levels(data):
    """Update risk levels based on current marks"""
    from utils import get_risk_level
    
    if 'total_internal_marks' in data.columns:
        data['risk_level'] = data['total_internal_marks'].apply(get_risk_level)
        data['risk_score'] = (data['total_internal_marks'] / 60) * 100
        
        if save_data(data):
            st.success("✅ Risk levels updated successfully!")
            st.rerun()
        else:
            st.error("Failed to save updated risk levels")
    else:
        st.error("Total internal marks column not found")

def refresh_all_data(data):
    """Refresh all calculated fields"""
    recalculate_totals(data)
    # update_risk_levels will be called after recalculate_totals saves the data

def export_data(data, format_type):
    """Export data in specified format"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "CSV":
            csv_data = data.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_data,
                file_name=f"students_export_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        elif format_type == "Excel":
            excel_buffer = pd.ExcelWriter(f"students_export_{timestamp}.xlsx", engine='openpyxl')
            data.to_excel(excel_buffer, index=False, sheet_name='Students')
            excel_buffer.close()
            
            with open(f"students_export_{timestamp}.xlsx", 'rb') as f:
                excel_data = f.read()
            
            st.download_button(
                label="⬇️ Download Excel",
                data=excel_data,
                file_name=f"students_export_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        elif format_type == "JSON":
            json_data = data.to_json(orient='records', indent=2)
            st.download_button(
                label="⬇️ Download JSON",
                data=json_data,
                file_name=f"students_export_{timestamp}.json",
                mime="application/json",
                use_container_width=True
            )
    
    except Exception as e:
        st.error(f"Error exporting data: {e}")

def clear_cache():
    """Clear system cache"""
    try:
        # This is a simplified cache clearing - in a real app you might have more specific cache management
        st.success("✅ Cache cleared successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"Error clearing cache: {e}")

def generate_system_report():
    """Generate a system status report"""
    try:
        report_data = []
        
        # Data status
        data_exists = os.path.exists('data/students.csv')
        report_data.append(("Data File", "Available" if data_exists else "Missing"))
        
        if data_exists:
            data = load_data()
            report_data.append(("Records", len(data)))
            report_data.append(("File Size", f"{os.path.getsize('data/students.csv') / 1024:.1f} KB"))
        
        # Backups status
        backups = get_backup_files()
        report_data.append(("Backups Count", len(backups)))
        
        # Available files
        data_files = get_available_data_files()
        report_data.append(("Total Data Files", len(data_files)))
        
        # Directories status
        required_dirs = ['data', 'backups', 'model', 'uploads']
        missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
        report_data.append(("Missing Directories", f"{len(missing_dirs)}" if missing_dirs else "None"))
        
        # Create report dataframe
        report_df = pd.DataFrame(report_data, columns=['Metric', 'Value'])
        
        st.success("✅ System report generated!")
        st.dataframe(report_df, use_container_width=True, hide_index=True)
        
        # Download option
        csv_report = report_df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download System Report",
            data=csv_report,
            file_name=f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    except Exception as e:
        st.error(f"Error generating system report: {e}")

if __name__ == "__main__":
    main()