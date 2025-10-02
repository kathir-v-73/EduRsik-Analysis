# model.py - Machine Learning Model
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import streamlit as st
import joblib
import os

class StudentPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        self.is_trained = False
        self.label_encoders = {}
        self.feature_importance = None
    
    def train_model(self, data):
        """Train the machine learning model for risk prediction"""
        try:
            if data.empty or len(data) < 10:
                st.warning("Not enough data to train the model. Need at least 10 records.")
                return False
            
            # Prepare features - use all available academic marks
            feature_columns = ['cat1_marks', 'cat2_marks', 'assignment_marks', 'attendance_marks', 'quiz_marks']
            available_features = [col for col in feature_columns if col in data.columns]
            
            if len(available_features) < 3:
                st.error(f"Need at least 3 academic mark columns. Found: {available_features}")
                return False
            
            if 'risk_level' not in data.columns:
                st.error("Risk level column not found in data")
                return False
            
            X = data[available_features]
            y = data['risk_level']
            
            # Remove any rows with missing values
            mask = X.notna().all(axis=1) & y.notna()
            X = X[mask]
            y = y[mask]
            
            if len(X) < 10:
                st.warning("Not enough complete records after cleaning missing values")
                return False
            
            # Encode target variable
            le = LabelEncoder()
            y_encoded = le.fit_transform(y)
            self.label_encoders['risk_level'] = le
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
            )
            
            # Train model
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Feature importance
            self.feature_importance = pd.DataFrame({
                'feature': available_features,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            self.is_trained = True
            
            st.success(f"✅ Model trained successfully! Accuracy: {accuracy:.2f}")
            st.info(f"Feature importance: {', '.join(self.feature_importance['feature'].head(3).tolist())}")
            
            return True
            
        except Exception as e:
            st.error(f"Error training model: {str(e)}")
            return False
    
    def predict_risk(self, features_dict):
        """Predict risk level for new student data"""
        if not self.is_trained:
            return "Model not trained", 0
        
        try:
            # Convert features to array in correct order
            feature_columns = self.feature_importance['feature'].tolist()
            features_array = [features_dict.get(col, 0) for col in feature_columns]
            
            prediction_encoded = self.model.predict([features_array])[0]
            prediction_proba = self.model.predict_proba([features_array])[0]
            
            risk_level = self.label_encoders['risk_level'].inverse_transform([prediction_encoded])[0]
            confidence = max(prediction_proba) * 100
            
            return risk_level, confidence
            
        except Exception as e:
            return f"Prediction error: {e}", 0
    
    def save_model(self, filename='model/student_predictor.joblib'):
        """Save trained model to file"""
        try:
            os.makedirs('model', exist_ok=True)
            joblib.dump({
                'model': self.model,
                'label_encoders': self.label_encoders,
                'feature_importance': self.feature_importance,
                'is_trained': self.is_trained
            }, filename)
            return True
        except Exception as e:
            st.error(f"Error saving model: {e}")
            return False
    
    def load_model(self, filename='model/student_predictor.joblib'):
        """Load trained model from file"""
        try:
            if os.path.exists(filename):
                model_data = joblib.load(filename)
                self.model = model_data['model']
                self.label_encoders = model_data['label_encoders']
                self.feature_importance = model_data['feature_importance']
                self.is_trained = model_data['is_trained']
                return True
            return False
        except Exception as e:
            st.error(f"Error loading model: {e}")
            return False