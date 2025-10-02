# pages/6_🔔_Notifications.py
import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
from datetime import datetime
from utils import load_data, get_email_config, save_email_config

def main():
    st.markdown("""
    <div class='main-header'>
        <h1>🔔 Email Notification System</h1>
        <p>Send Alerts, Reports, and Communications to Students</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    data = load_data()
    
    # Notification system tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "⚙️ Email Setup", "📧 Send Notifications", "📋 Email Templates", "📊 Notification History"
    ])
    
    with tab1:
        render_email_setup_tab()
    
    with tab2:
        render_send_notifications_tab(data)
    
    with tab3:
        render_email_templates_tab()
    
    with tab4:
        render_notification_history_tab()

def render_email_setup_tab():
    """Render email configuration tab"""
    st.markdown("### ⚙️ Email Configuration")
    
    st.info("""
    **Configure your email settings to enable notifications:**
    - For Gmail: Use app password (2-factor authentication required)
    - For Outlook: Use app password or enable less secure apps
    - For other providers: Check your email provider's SMTP settings
    """)
    
    # Load existing configuration
    config = get_email_config()
    
    with st.form("email_config_form"):
        st.markdown("#### 🔧 SMTP Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            smtp_server = st.text_input(
                "SMTP Server *",
                value=config.get('smtp_server', 'smtp.gmail.com'),
                placeholder="e.g., smtp.gmail.com",
                help="Your email provider's SMTP server"
            )
            smtp_port = st.number_input(
                "SMTP Port *",
                min_value=1,
                max_value=65535,
                value=config.get('smtp_port', 587),
                help="Typically 587 for TLS, 465 for SSL"
            )
        
        with col2:
            sender_email = st.text_input(
                "Sender Email *",
                value=config.get('sender_email', ''),
                placeholder="e.g., your.email@gmail.com",
                help="The email address that will send notifications"
            )
            sender_name = st.text_input(
                "Sender Name",
                value=config.get('sender_name', 'EduRisk System'),
                placeholder="e.g., EduRisk Analytics",
                help="Display name for sent emails"
            )
        
        st.markdown("#### 🔐 Authentication")
        
        email_password = st.text_input(
            "Email Password/App Password *",
            type="password",
            value=config.get('email_password', ''),
            help="Your email password or app-specific password"
        )
        
        # Test connection
        st.markdown("#### 🧪 Test Connection")
        
        test_email = st.text_input(
            "Test Email Address",
            placeholder="Enter an email to test configuration",
            help="Send a test email to verify your settings"
        )
        
        # Form actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            save_config = st.form_submit_button(
                "💾 Save Configuration",
                type="primary",
                use_container_width=True
            )
        
        with col2:
            test_config = st.form_submit_button(
                "🧪 Test Configuration",
                use_container_width=True
            )
        
        with col3:
            clear_config = st.form_submit_button(
                "🗑️ Clear Configuration",
                use_container_width=True
            )
        
        if save_config:
            if not all([smtp_server, smtp_port, sender_email, email_password]):
                st.error("❌ Please fill in all required fields")
                return
            
            new_config = {
                'smtp_server': smtp_server,
                'smtp_port': smtp_port,
                'sender_email': sender_email,
                'sender_name': sender_name,
                'email_password': email_password,
                'configured': True
            }
            
            save_email_config(new_config)
            st.success("✅ Email configuration saved successfully!")
        
        if test_config:
            if not test_email:
                st.error("❌ Please enter a test email address")
                return
            
            if test_email_config(smtp_server, smtp_port, sender_email, email_password, test_email, sender_name):
                st.success("✅ Test email sent successfully! Configuration is working.")
            else:
                st.error("❌ Failed to send test email. Please check your configuration.")
        
        if clear_config:
            if os.path.exists('config/email_config.json'):
                os.remove('config/email_config.json')
            st.success("✅ Configuration cleared successfully!")
            st.rerun()

def render_send_notifications_tab(data):
    """Render send notifications tab"""
    st.markdown("### 📧 Send Notifications")
    
    # Check if email is configured
    config = get_email_config()
    if not config.get('configured', False):
        st.warning("⚠️ Please configure your email settings first in the 'Email Setup' tab.")
        return
    
    if data.empty:
        st.info("No student data available. Please import or generate data first.")
        return
    
    # Notification type selection
    st.markdown("#### 🎯 Notification Type")
    
    notification_type = st.radio(
        "Select Notification Type",
        options=[
            "Risk Alerts", 
            "Performance Reports", 
            "Custom Message",
            "Course Announcements"
        ],
        horizontal=True
    )
    
    # Recipient selection
    st.markdown("#### 👥 Recipient Selection")
    
    recipient_option = st.radio(
        "Send to",
        options=["All Students", "At-Risk Students", "Specific Course", "Custom Selection"],
        horizontal=True
    )
    
    recipients = data.copy()
    
    if recipient_option == "At-Risk Students":
        if 'risk_level' in recipients.columns:
            recipients = recipients[recipients['risk_level'].isin(['High', 'Failure'])]
            st.info(f"Selected {len(recipients)} at-risk students")
        else:
            st.warning("Risk level data not available")
    
    elif recipient_option == "Specific Course":
        if 'course_name' in recipients.columns:
            selected_course = st.selectbox("Select Course", recipients['course_name'].unique())
            recipients = recipients[recipients['course_name'] == selected_course]
            st.info(f"Selected {len(recipients)} students from {selected_course}")
        else:
            st.warning("Course data not available")
    
    elif recipient_option == "Custom Selection":
        st.info("Select specific students to notify")
        selected_students = st.multiselect(
            "Choose Students",
            options=data.apply(lambda x: f"{x['student_id']} - {x['name']} ({x['email']})", axis=1).tolist(),
            help="Select individual students to receive notifications"
        )
        
        if selected_students:
            selected_ids = [s.split(' - ')[0] for s in selected_students]
            recipients = recipients[recipients['student_id'].isin(selected_ids)]
            st.info(f"Selected {len(recipients)} students")
        else:
            recipients = pd.DataFrame()
    
    # Message configuration based on type
    st.markdown("#### ✉️ Message Configuration")
    
    if notification_type == "Risk Alerts":
        subject = st.text_input(
            "Email Subject",
            value="Important: Academic Risk Alert",
            help="Subject line for the risk alert email"
        )
        
        message_template = st.text_area(
            "Message Template",
            value="""Dear {name},

This is an important alert regarding your academic performance.

Current Status:
- Student ID: {student_id}
- Course: {course_name}
- Total Internal Marks: {total_internal_marks}/60
- Risk Level: {risk_level}

We recommend that you meet with your academic advisor to discuss strategies for improvement.

Best regards,
Academic Support Team""",
            height=200,
            help="Use placeholders like {name}, {student_id}, {course_name}, {total_internal_marks}, {risk_level}"
        )
    
    elif notification_type == "Performance Reports":
        subject = st.text_input(
            "Email Subject",
            value="Your Academic Performance Report",
            help="Subject line for the performance report"
        )
        
        message_template = st.text_area(
            "Message Template",
            value="""Dear {name},

Here is your academic performance report:

Student Information:
- ID: {student_id}
- Course: {course_name}

Academic Performance:
- CAT 1: {cat1_marks}/10
- CAT 2: {cat2_marks}/10
- Assignments: {assignment_marks}/15
- Attendance: {attendance_marks}/5
- Quizzes: {quiz_marks}/10
- Total: {total_internal_marks}/60
- Risk Level: {risk_level}

Keep up the good work or consider seeking academic support if needed.

Best regards,
Academic Department""",
            height=200,
            help="Use placeholders for student data and marks"
        )
    
    elif notification_type == "Course Announcements":
        subject = st.text_input(
            "Email Subject",
            value="Course Announcement",
            help="Subject line for the course announcement"
        )
        
        message_template = st.text_area(
            "Message Template",
            value="""Dear {name},

This is an important announcement regarding your course: {course_name}

[Your announcement message here]

Best regards,
Course Instructor""",
            height=200,
            help="Customize the announcement message"
        )
    
    else:  # Custom Message
        subject = st.text_input(
            "Email Subject",
            value="Message from Academic Department",
            help="Subject line for your custom message"
        )
        
        message_template = st.text_area(
            "Message Template",
            value="""Dear {name},

[Your custom message here]

You can include student-specific information like:
- Student ID: {student_id}
- Course: {course_name}
- Current performance: {total_internal_marks}/60

Best regards,
Academic Team""",
            height=200,
            help="Write your custom message with available placeholders"
        )
    
    # Send options
    st.markdown("#### 🚀 Send Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        send_test = st.checkbox("Send test email first", value=True)
        test_email = st.text_input("Test email address", placeholder="your.email@example.com")
    
    with col2:
        batch_size = st.slider("Emails per batch", 1, 50, 10, 
                             help="Send emails in batches to avoid rate limiting")
        delay = st.slider("Delay between batches (seconds)", 1, 30, 5,
                         help="Wait time between sending batches")
    
    # Send actions
    if len(recipients) == 0:
        st.warning("No recipients selected. Please adjust your recipient filters.")
        return
    
    st.info(f"📧 Ready to send to {len(recipients)} recipients")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧪 Send Test Email", use_container_width=True):
            if not test_email:
                st.error("Please enter a test email address")
                return
            
            # Send test with sample data
            sample_student = recipients.iloc[0] if len(recipients) > 0 else {}
            test_message = format_message(message_template, sample_student.to_dict())
            
            if send_email(config, test_email, subject, test_message):
                st.success("✅ Test email sent successfully!")
                log_notification("Test", test_email, subject, "Success")
            else:
                st.error("❌ Failed to send test email")
    
    with col2:
        if st.button("📤 Send to All Recipients", type="primary", use_container_width=True):
            send_bulk_emails(config, recipients, subject, message_template, 
                           batch_size, delay, send_test, test_email)
            st.rerun()

def render_email_templates_tab():
    """Render email templates management tab"""
    st.markdown("### 📋 Email Templates")
    
    st.info("""
    **Manage your email templates for different notification types:**
    - Create and save templates for reuse
    - Use placeholders for dynamic content
    - Templates are saved locally in your system
    """)
    
    # Load existing templates
    templates = load_email_templates()
    
    # Template management
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💾 Save New Template")
        
        with st.form("save_template_form"):
            template_name = st.text_input(
                "Template Name",
                placeholder="e.g., Risk Alert v2",
                help="Unique name for this template"
            )
            
            template_subject = st.text_input(
                "Subject Template",
                placeholder="e.g., Academic Alert for {name}",
                help="Email subject with placeholders"
            )
            
            template_body = st.text_area(
                "Body Template",
                height=300,
                placeholder="Dear {name},\n\nYour current risk level is {risk_level}...",
                help="Email body with placeholders for dynamic content"
            )
            
            save_template = st.form_submit_button(
                "💾 Save Template",
                type="primary",
                use_container_width=True
            )
            
            if save_template:
                if not all([template_name, template_subject, template_body]):
                    st.error("❌ Please fill in all template fields")
                    return
                
                if save_email_template(template_name, template_subject, template_body):
                    st.success(f"✅ Template '{template_name}' saved successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to save template")
    
    with col2:
        st.markdown("#### 📂 Existing Templates")
        
        if not templates:
            st.info("No templates saved yet. Create your first template!")
            return
        
        selected_template = st.selectbox(
            "Select Template",
            options=list(templates.keys()),
            help="Choose a template to view or manage"
        )
        
        if selected_template:
            template = templates[selected_template]
            
            st.text_area(
                "Subject",
                value=template['subject'],
                key="view_subject",
                disabled=True
            )
            
            st.text_area(
                "Body",
                value=template['body'],
                height=200,
                key="view_body",
                disabled=True
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📝 Use This Template", use_container_width=True):
                    # Set the template in session state for use in send tab
                    st.session_state.selected_template = template
                    st.success("✅ Template loaded! Switch to 'Send Notifications' tab to use it.")
            
            with col2:
                if st.button("🗑️ Delete Template", use_container_width=True):
                    if delete_email_template(selected_template):
                        st.success(f"✅ Template '{selected_template}' deleted!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete template")

def render_notification_history_tab():
    """Render notification history tab"""
    st.markdown("### 📊 Notification History")
    
    # Load notification history
    history = load_notification_history()
    
    if not history:
        st.info("No notification history found. Send your first email to see history here.")
        return
    
    # Convert history to dataframe for display
    history_data = []
    for record in history:
        history_data.append({
            'Date': record.get('timestamp', 'Unknown'),
            'Type': record.get('type', 'Unknown'),
            'Recipient': record.get('recipient', 'Unknown'),
            'Subject': record.get('subject', 'Unknown'),
            'Status': record.get('status', 'Unknown')
        })
    
    history_df = pd.DataFrame(history_data)
    
    # Filters
    st.markdown("#### 🔍 Filter History")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All"] + list(history_df['Status'].unique())
        )
    
    with col2:
        type_filter = st.selectbox(
            "Filter by Type",
            options=["All"] + list(history_df['Type'].unique())
        )
    
    with col3:
        search_term = st.text_input("Search in Subject/Recipient")
    
    # Apply filters
    filtered_history = history_df.copy()
    
    if status_filter != "All":
        filtered_history = filtered_history[filtered_history['Status'] == status_filter]
    
    if type_filter != "All":
        filtered_history = filtered_history[filtered_history['Type'] == type_filter]
    
    if search_term:
        mask = (
            filtered_history['Subject'].str.contains(search_term, case=False, na=False) |
            filtered_history['Recipient'].str.contains(search_term, case=False, na=False)
        )
        filtered_history = filtered_history[mask]
    
    # Display history
    st.markdown(f"#### 📋 Notification Records ({len(filtered_history)} found)")
    
    st.dataframe(
        filtered_history.sort_values('Date', ascending=False),
        use_container_width=True,
        hide_index=True
    )
    
    # History actions
    st.markdown("#### 🔧 History Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh History", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            if clear_notification_history():
                st.success("✅ History cleared successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to clear history")

def test_email_config(smtp_server, smtp_port, sender_email, password, test_email, sender_name):
    """Test email configuration by sending a test email"""
    try:
        # Create message
        message = MIMEMultipart()
        message['From'] = f"{sender_name} <{sender_email}>"
        message['To'] = test_email
        message['Subject'] = "EduRisk Pro - Test Email"
        
        body = """
        <html>
        <body>
            <h2>🎉 Test Email Successful!</h2>
            <p>This is a test email from your EduRisk Pro system.</p>
            <p>Your email configuration is working correctly.</p>
            <br>
            <p><strong>System:</strong> EduRisk Analyzer Pro</p>
            <p><strong>Time:</strong> {}</p>
        </body>
        </html>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        message.attach(MIMEText(body, 'html'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(message)
        
        return True
    
    except Exception as e:
        st.error(f"Email test failed: {str(e)}")
        return False

def send_email(config, recipient, subject, message):
    """Send a single email"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"{config.get('sender_name', 'EduRisk System')} <{config['sender_email']}>"
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # Attach message body
        msg.attach(MIMEText(message, 'html'))
        
        # Send email
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['sender_email'], config['email_password'])
            server.send_message(msg)
        
        return True
    
    except Exception as e:
        st.error(f"Failed to send email to {recipient}: {str(e)}")
        return False

def format_message(template, student_data):
    """Format message template with student data"""
    try:
        formatted = template
        
        # Replace all placeholders with actual data
        for key, value in student_data.items():
            if pd.notna(value):
                placeholder = f"{{{key}}}"
                formatted = formatted.replace(placeholder, str(value))
        
        # Convert to HTML for better formatting
        html_message = formatted.replace('\n', '<br>')
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            {html_message}
            <br><br>
            <hr>
            <p style="color: #666; font-size: 0.9em;">
                This email was sent automatically by EduRisk Analyzer Pro.<br>
                Please do not reply to this email.
            </p>
        </body>
        </html>
        """
    
    except Exception as e:
        st.error(f"Error formatting message: {e}")
        return template

def send_bulk_emails(config, recipients, subject_template, message_template, batch_size, delay, send_test, test_email):
    """Send emails to multiple recipients in batches"""
    import time
    
    total_recipients = len(recipients)
    successful = 0
    failed = 0
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Send test email if requested
    if send_test and test_email:
        test_student = recipients.iloc[0] if len(recipients) > 0 else {}
        test_subject = format_message(subject_template, test_student.to_dict())
        test_message = format_message(message_template, test_student.to_dict())
        
        if send_email(config, test_email, test_subject, test_message):
            st.success("✅ Test email sent successfully!")
        else:
            st.error("❌ Test email failed. Stopping bulk send.")
            return
    
    # Send in batches
    for i in range(0, total_recipients, batch_size):
        batch = recipients.iloc[i:i + batch_size]
        
        for _, student in batch.iterrows():
            student_data = student.to_dict()
            
            # Format subject and message
            subject = format_message(subject_template, student_data)
            message = format_message(message_template, student_data)
            
            # Send email
            if send_email(config, student['email'], subject, message):
                successful += 1
                log_notification("Bulk", student['email'], subject, "Success")
            else:
                failed += 1
                log_notification("Bulk", student['email'], subject, "Failed")
            
            # Update progress
            progress = (successful + failed) / total_recipients
            progress_bar.progress(progress)
            status_text.text(f"Progress: {successful + failed}/{total_recipients} | Successful: {successful} | Failed: {failed}")
        
        # Delay between batches
        if i + batch_size < total_recipients:
            time.sleep(delay)
    
    # Final status
    if failed == 0:
        st.success(f"✅ All {successful} emails sent successfully!")
    else:
        st.warning(f"⚠️ Sent {successful} emails, {failed} failed")

def load_email_templates():
    """Load email templates from file"""
    try:
        if os.path.exists('config/email_templates.json'):
            with open('config/email_templates.json', 'r') as f:
                return json.load(f)
        return {}
    except:
        return {}

def save_email_template(name, subject, body):
    """Save an email template"""
    try:
        os.makedirs('config', exist_ok=True)
        
        templates = load_email_templates()
        templates[name] = {
            'subject': subject,
            'body': body,
            'created': datetime.now().isoformat()
        }
        
        with open('config/email_templates.json', 'w') as f:
            json.dump(templates, f, indent=2)
        
        return True
    except Exception as e:
        st.error(f"Error saving template: {e}")
        return False

def delete_email_template(name):
    """Delete an email template"""
    try:
        templates = load_email_templates()
        
        if name in templates:
            del templates[name]
            
            with open('config/email_templates.json', 'w') as f:
                json.dump(templates, f, indent=2)
            
            return True
        
        return False
    except Exception as e:
        st.error(f"Error deleting template: {e}")
        return False

def load_notification_history():
    """Load notification history from file"""
    try:
        if os.path.exists('config/notification_history.json'):
            with open('config/notification_history.json', 'r') as f:
                return json.load(f)
        return []
    except:
        return []

def log_notification(notification_type, recipient, subject, status):
    """Log a notification to history"""
    try:
        os.makedirs('config', exist_ok=True)
        
        history = load_notification_history()
        
        history.append({
            'timestamp': datetime.now().isoformat(),
            'type': notification_type,
            'recipient': recipient,
            'subject': subject,
            'status': status
        })
        
        # Keep only last 1000 records
        history = history[-1000:]
        
        with open('config/notification_history.json', 'w') as f:
            json.dump(history, f, indent=2)
        
        return True
    except:
        return False

def clear_notification_history():
    """Clear notification history"""
    try:
        if os.path.exists('config/notification_history.json'):
            os.remove('config/notification_history.json')
        return True
    except:
        return False

if __name__ == "__main__":
    main()