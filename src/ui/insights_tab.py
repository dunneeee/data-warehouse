import streamlit as st
import altair as alt
import pandas as pd


def render_combined_insights(revenue_analysis, lottery_analysis, start_date, end_date):
    st.header("Thông tin Tổng hợp")
    st.info(f"Hiển thị dữ liệu từ {start_date} đến {end_date}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tổng hợp theo Tháng")
        revenue_monthly = revenue_analysis.get_monthly_revenue_summary()
        lottery_monthly = lottery_analysis.get_monthly_lottery_summary()
        
        if not revenue_monthly.empty and not lottery_monthly.empty:
            start_month = str(start_date)[:7]
            end_month = str(end_date)[:7]
            revenue_monthly = revenue_monthly[(revenue_monthly['year_month'] >= start_month) & (revenue_monthly['year_month'] <= end_month)]
            lottery_monthly = lottery_monthly[(lottery_monthly['year_month'] >= start_month) & (lottery_monthly['year_month'] <= end_month)]
            
            combined = pd.merge(
                revenue_monthly[['year_month', 'total_revenue', 'tickets_sold']],
                lottery_monthly[['year_month', 'draw_days']],
                on='year_month',
                how='inner'
            )
            
            recent = combined
            
            base = alt.Chart(recent).encode(
                x=alt.X('year_month:N', title='Tháng')
            )
            
            revenue_line = base.mark_line(color='blue', point=True).encode(
                y=alt.Y('total_revenue:Q', title='Doanh thu (VND)', axis=alt.Axis(format=',.0f')),
                tooltip=[
                    alt.Tooltip('year_month:N', title='Tháng'),
                    alt.Tooltip('total_revenue:Q', title='Doanh thu', format=',.0f')
                ]
            )
            
            draw_line = base.mark_line(color='green', point=True).encode(
                y=alt.Y('draw_days:Q', title='Số ngày quay'),
                tooltip=[
                    alt.Tooltip('year_month:N', title='Tháng'),
                    alt.Tooltip('draw_days:Q', title='Số ngày quay')
                ]
            )
            
            chart = alt.layer(revenue_line, draw_line).resolve_scale(y='independent').properties(height=400)
            st.altair_chart(chart, width="stretch")
        else:
            st.info("Không có dữ liệu")
    
    with col2:
        st.subheader("Tổng quan Hiệu suất Đài")
        revenue_station = revenue_analysis.get_revenue_by_station()
        lottery_station = lottery_analysis.get_lottery_results_by_station()
        
        if not revenue_station.empty and not lottery_station.empty:
            combined = pd.merge(
                revenue_station[['station_name', 'total_revenue', 'region']],
                lottery_station[['station_name', 'draw_days']],
                on='station_name',
                how='inner'
            )
            
            chart = alt.Chart(combined).mark_circle(size=200).encode(
                x=alt.X('draw_days:Q', title='Số ngày quay'),
                y=alt.Y('total_revenue:Q', title='Tổng Doanh thu (VND)', axis=alt.Axis(format=',.0f')),
                color=alt.Color('region:N', title='Khu vực'),
                size=alt.Size('total_revenue:Q', legend=None),
                tooltip=[
                    alt.Tooltip('station_name:N', title='Đài'),
                    alt.Tooltip('region:N', title='Khu vực'),
                    alt.Tooltip('draw_days:Q', title='Số ngày quay'),
                    alt.Tooltip('total_revenue:Q', title='Doanh thu', format=',.0f')
                ]
            ).properties(height=400)
            st.altair_chart(chart, width="stretch")
        else:
            st.info("Không có dữ liệu")
