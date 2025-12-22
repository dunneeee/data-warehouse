import streamlit as st
import altair as alt
import pandas as pd
from datetime import datetime


def render_revenue_analysis(revenue_analysis, start_date, end_date):
    st.header("Bảng điều khiển Phân tích Doanh thu")
    st.info(f"Hiển thị dữ liệu từ {start_date} đến {end_date}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Xu hướng Doanh thu theo Ngày")
        df = revenue_analysis.get_daily_revenue_trend()
        if not df.empty:
            df['full_date'] = df['full_date'].astype(str)
            df = df[(df['full_date'] >= str(start_date)) & (df['full_date'] <= str(end_date))]
        if not df.empty:
            chart = alt.Chart(df).mark_line(point=True).encode(
                x=alt.X('full_date:T', title='Ngày'),
                y=alt.Y('total_revenue:Q', title='Doanh thu (VND)', axis=alt.Axis(format=',.0f')),
                tooltip=[
                    alt.Tooltip('full_date:T', title='Ngày'),
                    alt.Tooltip('total_revenue:Q', title='Doanh thu', format=',.0f'),
                    alt.Tooltip('tickets_sold:Q', title='Số vé', format=','),
                    alt.Tooltip('net_profit:Q', title='Lợi nhuận', format=',.0f')
                ]
            ).properties(height=400)
            st.altair_chart(chart, width="stretch")
        else:
            st.info("Không có dữ liệu")
    
    with col2:
        st.subheader("Tổng hợp Doanh thu theo Tháng")
        df = revenue_analysis.get_monthly_revenue_summary()
        if not df.empty:
            start_month = str(start_date)[:7]
            end_month = str(end_date)[:7]
            df = df[(df['year_month'] >= start_month) & (df['year_month'] <= end_month)]
        if not df.empty:
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('year_month:N', title='Tháng'),
                y=alt.Y('total_revenue:Q', title='Doanh thu (VND)', axis=alt.Axis(format=',.0f')),
                color=alt.value('#1f77b4'),
                tooltip=[
                    alt.Tooltip('year_month:N', title='Tháng'),
                    alt.Tooltip('total_revenue:Q', title='Doanh thu', format=',.0f'),
                    alt.Tooltip('tickets_sold:Q', title='Số vé', format=',')
                ]
            ).properties(height=400)
            st.altair_chart(chart, width="stretch")
        else:
            st.info("Không có dữ liệu")
    
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Doanh thu theo Đài")
        df = revenue_analysis.get_revenue_by_station()
        if not df.empty:
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('total_revenue:Q', title='Tổng Doanh thu (VND)', axis=alt.Axis(format=',.0f')),
                y=alt.Y('station_name:N', title='Đài', sort='-x'),
                color=alt.Color('region:N', title='Khu vực'),
                tooltip=[
                    alt.Tooltip('station_name:N', title='Đài'),
                    alt.Tooltip('region:N', title='Khu vực'),
                    alt.Tooltip('total_revenue:Q', title='Doanh thu', format=',.0f'),
                    alt.Tooltip('active_days:Q', title='Số ngày hoạt động')
                ]
            ).properties(height=400)
            st.altair_chart(chart, width="stretch")
        else:
            st.info("Không có dữ liệu")
    
    with col4:
        st.subheader("Doanh thu theo Ngày trong Tuần")
        df = revenue_analysis.get_revenue_by_day_of_week()
        if not df.empty:
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('day_of_week:N', title='Ngày', sort=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']),
                y=alt.Y('total_revenue:Q', title='Tổng Doanh thu (VND)', axis=alt.Axis(format=',.0f')),
                color=alt.condition(
                    alt.datum.is_weekend == 1,
                    alt.value('#ff7f0e'),
                    alt.value('#1f77b4')
                ),
                tooltip=[
                    alt.Tooltip('day_of_week:N', title='Ngày'),
                    alt.Tooltip('total_revenue:Q', title='Doanh thu', format=',.0f'),
                    alt.Tooltip('transactions:Q', title='Giao dịch', format=',')
                ]
            ).properties(height=400)
            st.altair_chart(chart, width="stretch")
        else:
            st.info("Không có dữ liệu")
    
    st.markdown("---")
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.subheader("Top Đại lý theo Doanh thu")
        df = revenue_analysis.get_revenue_by_agency()
        if not df.empty:
            top_agencies = df.head(10)
            chart = alt.Chart(top_agencies).mark_bar().encode(
                x=alt.X('total_revenue:Q', title='Tổng Doanh thu (VND)', axis=alt.Axis(format=',.0f')),
                y=alt.Y('agency_name:N', title='Đại lý', sort='-x'),
                color=alt.Color('agency_type:N', title='Loại'),
                tooltip=[
                    alt.Tooltip('agency_name:N', title='Đại lý'),
                    alt.Tooltip('agency_type:N', title='Loại'),
                    alt.Tooltip('total_revenue:Q', title='Doanh thu', format=',.0f'),
                    alt.Tooltip('total_commission:Q', title='Hoa hồng', format=',.0f')
                ]
            ).properties(height=400)
            st.altair_chart(chart, width="stretch")
        else:
            st.info("Không có dữ liệu")
    
    with col6:
        st.subheader("Tỷ lệ Tăng trưởng Doanh thu (Tháng)")
        df = revenue_analysis.get_revenue_growth_rate(period='month')
        if not df.empty:
            start_month = str(start_date)[:7]
            end_month = str(end_date)[:7]
            df = df[(df['period'] >= start_month) & (df['period'] <= end_month)]
        if not df.empty:
            chart = alt.Chart(df).mark_line(point=True).encode(
                x=alt.X('period:N', title='Tháng'),
                y=alt.Y('growth_rate_percent:Q', title='Tỷ lệ Tăng trưởng (%)'),
                color=alt.condition(
                    alt.datum.growth_rate_percent > 0,
                    alt.value('green'),
                    alt.value('red')
                ),
                tooltip=[
                    alt.Tooltip('period:N', title='Tháng'),
                    alt.Tooltip('total_revenue:Q', title='Doanh thu', format=',.0f'),
                    alt.Tooltip('growth_rate_percent:Q', title='Tăng trưởng %', format='.2f')
                ]
            ).properties(height=400)
            st.altair_chart(chart, width="stretch")
        else:
            st.info("Không có dữ liệu")
    
    st.markdown("---")
    
    st.subheader("So sánh Cuối tuần vs Ngày thường")
    df = revenue_analysis.get_weekend_vs_weekday_comparison()
    if not df.empty:
        col7, col8 = st.columns(2)
        
        with col7:
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('period_type:N', title='Loại'),
                y=alt.Y('total_revenue:Q', title='Tổng Doanh thu (VND)', axis=alt.Axis(format=',.0f')),
                color=alt.Color('period_type:N', legend=None),
                tooltip=[
                    alt.Tooltip('period_type:N', title='Loại'),
                    alt.Tooltip('days:Q', title='Số ngày'),
                    alt.Tooltip('total_revenue:Q', title='Doanh thu', format=',.0f')
                ]
            ).properties(height=300)
            st.altair_chart(chart, width="stretch")
        
        with col8:
            st.dataframe(df[['period_type', 'days', 'transactions', 'total_revenue', 'avg_revenue']], width="stretch")
