import streamlit as st
import altair as alt
import pandas as pd
from datetime import datetime


def render_forecasting(db):
    st.header("Dự đoán Doanh thu")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Cài đặt")
        
        current_year = datetime.now().year
        forecast_year = st.selectbox(
            "Năm dự đoán",
            options=range(current_year, current_year + 6),
            index=1
        )
        
        retrain = st.checkbox("Train lại model", value=False)
        
        if st.button("Chạy dự đoán", type="primary"):
            st.session_state['run_forecast'] = True
            st.session_state['forecast_year'] = forecast_year
            st.session_state['retrain'] = retrain
    
    with col2:
        st.subheader("Kết quả")
        
        if st.session_state.get('run_forecast', False):
            with st.spinner("Đang xử lý..."):
                from src.forecasting import train_revenue_model, RevenueForecasting
                from src.analysis.revenue import RevenueAnalysis
                from pathlib import Path
                
                project_root = Path(__file__).parent.parent.parent
                model_path = project_root / "database" / "revenue_model.pkl"
                
                try:
                    if st.session_state.get('retrain', False) or not model_path.exists():
                        st.info("🤖 Đang train model...")
                        forecaster, _ = train_revenue_model(db)
                        forecaster.save_model(str(model_path))
                        st.success("✅ Model đã train và lưu thành công")
                    else:
                        st.info("📥 Đang load model có sẵn...")
                        forecaster = RevenueForecasting()
                        forecaster.load_model(str(model_path))
                        st.success("✅ Model đã load thành công")
                    
                    revenue_analysis = RevenueAnalysis(db)
                    historical_data = revenue_analysis.get_monthly_revenue_summary()
                    
                    current_year = datetime.now().year
                    forecast_year = st.session_state.get('forecast_year', current_year + 1)
                    months_needed = (forecast_year - current_year) * 12
                    
                    forecast_result = forecaster.forecast_next_months(historical_data, months=max(12, months_needed))
                    
                    st.session_state['forecaster'] = forecaster
                    st.session_state['forecast_result'] = forecast_result
                    st.session_state['historical_data'] = historical_data
                    
                except Exception as e:
                    st.error(f"❌ Lỗi: {str(e)}")
                    return
    
    if 'forecast_result' in st.session_state:
        st.markdown("---")
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("📊 Metrics")
            metrics = st.session_state['forecaster'].get_metrics()
            
            if metrics:
                metric_col1, metric_col2 = st.columns(2)
                with metric_col1:
                    st.metric("R² Score", f"{metrics.get('R2', 0):.4f}")
                    st.metric("MAE", f"{metrics.get('MAE', 0):,.0f} VND")
                with metric_col2:
                    st.metric("MAPE", f"{metrics.get('MAPE', 0):.2f}%")
                    st.metric("RMSE", f"{metrics.get('RMSE', 0):,.0f} VND")
        
        with col4:
            st.subheader("🎯 Top Features")
            importance = st.session_state['forecaster'].get_feature_importance()
            if importance is not None and not importance.empty:
                st.dataframe(
                    importance[['feature', 'coefficient']].head(5),
                    width="stretch",
                    hide_index=True
                )
        
        st.markdown("---")
        st.subheader("📈 Biểu đồ Dự đoán")
        
        historical = st.session_state['historical_data'].copy()
        forecast = st.session_state['forecast_result'].copy()
        
        historical['type'] = 'Thực tế'
        historical['revenue'] = historical['total_revenue']
        historical = historical[['year_month', 'revenue', 'type']]
        
        forecast['type'] = 'Dự đoán'
        forecast['revenue'] = forecast['predicted_revenue']
        forecast = forecast[['year_month', 'revenue', 'type']]
        
        selected_year = st.session_state.get('forecast_year', datetime.now().year + 1)
        forecast_year_data = forecast[forecast['year_month'].str.startswith(str(selected_year))]
        
        last_12_months = historical.tail(12)
        
        combined = pd.concat([last_12_months, forecast_year_data], ignore_index=True)
        
        chart = alt.Chart(combined).mark_line(point=True).encode(
            x=alt.X('year_month:N', title='Tháng'),
            y=alt.Y('revenue:Q', title='Doanh thu (VND)', axis=alt.Axis(format=',.0f')),
            color=alt.Color('type:N', 
                scale=alt.Scale(
                    domain=['Thực tế', 'Dự đoán'],
                    range=['#1f77b4', '#ff7f0e']
                ),
                title='Loại'
            ),
            strokeDash=alt.StrokeDash('type:N',
                scale=alt.Scale(
                    domain=['Thực tế', 'Dự đoán'],
                    range=[[1, 0], [5, 5]]
                ),
                legend=None
            ),
            tooltip=[
                alt.Tooltip('year_month:N', title='Tháng'),
                alt.Tooltip('revenue:Q', title='Doanh thu', format=',.0f'),
                alt.Tooltip('type:N', title='Loại')
            ]
        ).properties(height=400)
        
        st.altair_chart(chart, width="stretch")
        
        st.markdown("---")
        st.subheader("📋 Chi tiết Dự đoán")
        
        display_df = forecast_year_data.copy()
        display_df['Tháng'] = display_df['year_month']
        display_df['Doanh thu dự đoán (VND)'] = display_df['revenue'].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(
            display_df[['Tháng', 'Doanh thu dự đoán (VND)']],
            width="stretch",
            hide_index=True
        )
