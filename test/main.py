import streamlit as st
import pandas as pd
import numpy as np
import pickle
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(page_title="AQI Forecasting App", layout="wide")

# Add custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.5rem;
        margin-bottom: 2rem;
    }
    .prediction {
        padding: 1.5rem;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="title">Port Dickson AQI Prediction</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Forecast air quality using Prophet model</div>', unsafe_allow_html=True)

# Load the model
@st.cache_resource
def load_model():
    try:
        with open('prophet_aqi_model.pkl', 'rb') as file:
            model_data = pickle.load(file)
        return model_data
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

model_data = load_model()

# If model is loaded successfully
if model_data:
    model = model_data['model']
    last_date = model_data['last_date']
    historical_data = model_data['historical_data']
    target_month_avg_temps = model_data['target_month_avg_temps']
    
    # Display model info
    st.info(f"Model loaded successfully. Historical data up to: {last_date.strftime('%Y-%m-%d')}")
    
    # Date input
    min_date = last_date + timedelta(days=1)
    max_date = last_date + timedelta(days=365)  # Allow predictions up to 1 year in the future
    
    st.subheader("Select Forecast Date")
    target_date = st.date_input(
        "Choose a date to predict AQI:", 
        min_value=min_date,
        max_value=max_date,
        value=min_date + timedelta(days=7)
    )
    
    # Optional temperature input
    st.subheader("Temperature Information")
    use_custom_temp = st.checkbox("Use custom temperature value")
    
    # Get historical average temperature for the selected date
    target_month = target_date.month
    target_day = target_date.day
    
    # Try to find exact month/day combination in historical data
    historical_temps = historical_data[
        (historical_data['ds'].dt.month == target_month) &
        (historical_data['ds'].dt.day == target_day)
    ]['temperature']
    
    if len(historical_temps) > 0:
        avg_temp = historical_temps.mean()
    else:
        # Fallback to month average if specific day not found
        monthly_temps = historical_data[historical_data['ds'].dt.month == target_month]['temperature']
        avg_temp = monthly_temps.mean() if len(monthly_temps) > 0 else 28.0  # Default if no data
    
    if use_custom_temp:
        temperature = st.number_input("Enter expected temperature (°C):", 
                                       min_value=15.0, max_value=40.0, 
                                       value=float(avg_temp), step=0.1)
    else:
        temperature = avg_temp
        st.write(f"Using historical average temperature for {target_date.strftime('%B %d')}: {avg_temp:.2f}°C")
    
    # Prediction button
    if st.button("Generate Prediction"):
        with st.spinner("Generating forecast..."):
            # Convert to pandas datetime
            pd_target_date = pd.to_datetime(target_date)
            
            # Calculate days needed for forecast
            days_needed = (pd_target_date - last_date).days
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=days_needed + 1, freq='D')
            
            # Add temperature data
            future = future.merge(historical_data[['ds', 'temperature']], on='ds', how='left')
            
            # Set temperature for target date
            mask = (future['ds'] == pd_target_date)
            future.loc[mask, 'temperature'] = temperature
            
            # Fill any missing temperatures with historical averages
            for idx, row in future[future['temperature'].isna()].iterrows():
                month = row['ds'].month
                day = row['ds'].day
                # Try to find month/day combination in historical averages
                if (month, day) in target_month_avg_temps.index:
                    future.loc[idx, 'temperature'] = target_month_avg_temps.loc[(month, day)]
                else:
                    # Fallback to month average
                    month_avg = historical_data[historical_data['ds'].dt.month == month]['temperature'].mean()
                    future.loc[idx, 'temperature'] = month_avg if not np.isnan(month_avg) else avg_temp
            
            # Ensure no NaN values remain
            future['temperature'] = future['temperature'].fillna(avg_temp)
            
            # Make predictions
            forecast = model.predict(future)
            
            # Extract prediction for target date
            target_forecast = forecast[forecast['ds'] == pd_target_date]
            
            if not target_forecast.empty:
                predicted_aqi = target_forecast['yhat'].values[0]
                lower_bound = target_forecast['yhat_lower'].values[0]
                upper_bound = target_forecast['yhat_upper'].values[0]
                
                # Display prediction
                st.markdown('<div class="prediction">', unsafe_allow_html=True)
                st.subheader(f"AQI Prediction for {target_date.strftime('%B %d, %Y')}")
                
                # Create columns for results
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Predicted AQI", f"{predicted_aqi:.1f}")
                with col2:
                    st.metric("Lower Bound (95%)", f"{lower_bound:.1f}")
                with col3:
                    st.metric("Upper Bound (95%)", f"{upper_bound:.1f}")
                
                # Determine AQI category
                if predicted_aqi <= 50:
                    category = "Good"
                    color = "green"
                elif predicted_aqi <= 100:
                    category = "Moderate"
                    color = "yellow"
                elif predicted_aqi <= 150:
                    category = "Unhealthy for Sensitive Groups"
                    color = "orange"
                elif predicted_aqi <= 200:
                    category = "Unhealthy"
                    color = "red"
                elif predicted_aqi <= 300:
                    category = "Very Unhealthy"
                    color = "purple"
                else:
                    category = "Hazardous"
                    color = "maroon"
                
                st.markdown(f"<h3 style='color:{color}'>Air Quality: {category}</h3>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Optional: Show forecast for the next few days
                st.subheader("Forecast Trend")
                
                # Get forecast for a week around the target date (3 days before and 3 after)
                start_date = pd_target_date - pd.Timedelta(days=3)
                end_date = pd_target_date + pd.Timedelta(days=3)
                
                trend_forecast = forecast[
                    (forecast['ds'] >= start_date) & 
                    (forecast['ds'] <= end_date)
                ]
                
                # Create the plot
                fig = go.Figure()
                
                # Add main forecast line
                fig.add_trace(go.Scatter(
                    x=trend_forecast['ds'],
                    y=trend_forecast['yhat'],
                    mode='lines+markers',
                    name='Predicted AQI',
                    line=dict(color='blue', width=2),
                    marker=dict(size=8)
                ))
                
                # Add confidence interval
                fig.add_trace(go.Scatter(
                    x=trend_forecast['ds'],
                    y=trend_forecast['yhat_upper'],
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False
                ))
                
                fig.add_trace(go.Scatter(
                    x=trend_forecast['ds'],
                    y=trend_forecast['yhat_lower'],
                    mode='lines',
                    line=dict(width=0),
                    fill='tonexty',
                    fillcolor='rgba(0, 0, 255, 0.2)',
                    name='95% Confidence Interval'
                ))
                
                # Highlight target date
                fig.add_trace(go.Scatter(
                    x=[pd_target_date],
                    y=[predicted_aqi],
                    mode='markers',
                    marker=dict(color='red', size=12, symbol='star'),
                    name='Selected Date'
                ))
                
                # Update layout
                fig.update_layout(
                    title="AQI Forecast Trend",
                    xaxis_title="Date",
                    yaxis_title="AQI Value",
                    legend=dict(y=0.99, x=0.01),
                    margin=dict(l=40, r=40, t=40, b=40),
                    height=400,
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.error("Could not generate prediction for the selected date.")
else:
    st.error("Failed to load the model. Please ensure the model file exists and is correctly formatted.")
    st.info("Please run the model training script first to generate the pickle file.")