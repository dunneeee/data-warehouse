import streamlit as st
import altair as alt
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import DatabaseConnection
from src.analysis.revenue import RevenueAnalysis
from src.analysis.lottery import LotteryAnalysis


st.set_page_config(
    page_title="Kho Dữ liệu - Phân tích Xổ số và Doanh thu",
    page_icon="📊",
    layout="wide"
)

@st.cache_resource
def get_database_connection():
    db_path = project_root / "database" / "lottery_warehouse.db"
    db = DatabaseConnection(str(db_path))
    db.connect()
    return db

def get_revenue_analysis(db):
    return RevenueAnalysis(db)

def get_lottery_analysis(db):
    return LotteryAnalysis(db)


def main():
    st.title("Kho Dữ liệu - Phân tích Xổ số và Doanh thu")
    
    # Sidebar filters
    with st.sidebar:
        st.header("Bộ lọc")
        
        # Get date range from database
        db = get_database_connection()
        date_query = "SELECT MIN(full_date) as min_date, MAX(full_date) as max_date FROM Dim_Date"
        date_range = db.fetchone(date_query)
        
        if date_range:
            import datetime
            min_date = datetime.datetime.strptime(date_range['min_date'], '%Y-%m-%d').date()
            max_date = datetime.datetime.strptime(date_range['max_date'], '%Y-%m-%d').date()
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Từ ngày",
                    value=min_date,
                    min_value=min_date,
                    max_value=max_date
                )
            with col2:
                end_date = st.date_input(
                    "Đến ngày",
                    value=max_date,
                    min_value=min_date,
                    max_value=max_date
                )
            
            if start_date > end_date:
                st.error("Ngày bắt đầu phải nhỏ hơn ngày kết thúc")
                start_date = min_date
                end_date = max_date
        else:
            import datetime
            start_date = datetime.date(2015, 1, 1)
            end_date = datetime.date.today()
    
    st.markdown("---")
    
    revenue_analysis = get_revenue_analysis(db)
    lottery_analysis = get_lottery_analysis(db)
    
    tab1, tab2, tab3 = st.tabs(["Phân tích Doanh thu", "Phân tích Xổ số", "Thông tin Tổng hợp"])
    
    with tab1:
        render_revenue_analysis(revenue_analysis, start_date, end_date)
    
    with tab2:
        render_lottery_analysis(lottery_analysis, start_date, end_date)
    
    with tab3:
        render_combined_insights(revenue_analysis, lottery_analysis, start_date, end_date)


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


def render_lottery_analysis(lottery_analysis, start_date, end_date):
    st.header("Bảng điều khiển Phân tích Xổ số")
    st.info(f"Hiển thị dữ liệu từ {start_date} đến {end_date}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 10 Số xuất hiện Nhiều nhất (2 chữ số)")
        df = lottery_analysis.get_number_frequency(digit_length=2, limit=10)
        if not df.empty:
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('frequency:Q', title='Tần suất'),
                y=alt.Y('number_part:N', title='Số', sort='-x'),
                color=alt.value('#2ca02c'),
                tooltip=[
                    alt.Tooltip('number_part:N', title='Số'),
                    alt.Tooltip('frequency:Q', title='Tần suất', format=','),
                    alt.Tooltip('appeared_on_days:Q', title='Số ngày', format=',')
                ]
            ).properties(height=400)
            st.altair_chart(chart, width="stretch")
        else:
            st.info("Không có dữ liệu")
    
    with col2:
        st.subheader("Phân bố Giải thưởng")
        df = lottery_analysis.get_prize_distribution()
        if not df.empty:
            chart = alt.Chart(df).mark_arc().encode(
                theta=alt.Theta('total_count:Q', title='Số lượng'),
                color=alt.Color('prize_name:N', title='Giải'),
                tooltip=[
                    alt.Tooltip('prize_name:N', title='Giải'),
                    alt.Tooltip('total_count:Q', title='Số lượng', format=','),
                    alt.Tooltip('days_appeared:Q', title='Số ngày', format=',')
                ]
            ).properties(height=400)
            st.altair_chart(chart, width="stretch")
        else:
            st.info("Không có dữ liệu")
    
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Số Nóng và Số Lạnh (30 ngày gần đây)")
        df = lottery_analysis.get_hot_cold_numbers(digit_length=2, period_days=30)
        if not df.empty:
            chart = alt.Chart(df.head(20)).mark_bar().encode(
                x=alt.X('frequency:Q', title='Tần suất'),
                y=alt.Y('number:N', title='Số', sort='-x'),
                color=alt.Color('status:N', 
                    scale=alt.Scale(
                        domain=['Hot', 'Normal', 'Cold'],
                        range=['#d62728', '#7f7f7f', '#1f77b4']
                    ),
                    title='Trạng thái'
                ),
                tooltip=[
                    alt.Tooltip('number:N', title='Số'),
                    alt.Tooltip('frequency:Q', title='Tần suất'),
                    alt.Tooltip('status:N', title='Trạng thái')
                ]
            ).properties(height=400)
            st.altair_chart(chart, width="stretch")
        else:
            st.info("Không có dữ liệu")
    
    with col4:
        st.subheader("Kết quả theo Ngày trong Tuần")
        df = lottery_analysis.get_results_by_day_of_week()
        if not df.empty:
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('day_of_week:N', title='Ngày', sort=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']),
                y=alt.Y('draw_days:Q', title='Số ngày quay'),
                color=alt.condition(
                    alt.datum.is_weekend == 1,
                    alt.value('#ff7f0e'),
                    alt.value('#2ca02c')
                ),
                tooltip=[
                    alt.Tooltip('day_of_week:N', title='Ngày'),
                    alt.Tooltip('draw_days:Q', title='Số ngày quay'),
                    alt.Tooltip('active_stations:Q', title='Số đài')
                ]
            ).properties(height=400)
            st.altair_chart(chart, width="stretch")
        else:
            st.info("Không có dữ liệu")
    
    st.markdown("---")
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.subheader("Kết quả Xổ số theo Đài")
        df = lottery_analysis.get_lottery_results_by_station()
        if not df.empty:
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('draw_days:Q', title='Số ngày quay'),
                y=alt.Y('station_name:N', title='Đài', sort='-x'),
                color=alt.Color('region:N', title='Khu vực'),
                tooltip=[
                    alt.Tooltip('station_name:N', title='Đài'),
                    alt.Tooltip('region:N', title='Khu vực'),
                    alt.Tooltip('draw_days:Q', title='Số ngày quay'),
                    alt.Tooltip('total_results:Q', title='Tổng kết quả', format=',')
                ]
            ).properties(height=400)
            st.altair_chart(chart, width="stretch")
        else:
            st.info("Không có dữ liệu")
    
    with col6:
        st.subheader("Phân tích Tần suất Chữ số (Vị trí cuối)")
        df = lottery_analysis.get_digit_frequency_analysis(position=-1)
        if not df.empty:
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('digit:N', title='Chữ số', sort=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']),
                y=alt.Y('frequency:Q', title='Tần suất'),
                color=alt.value('#9467bd'),
                tooltip=[
                    alt.Tooltip('digit:N', title='Chữ số'),
                    alt.Tooltip('frequency:Q', title='Tần suất', format=','),
                    alt.Tooltip('percentage:Q', title='Tỷ lệ %', format='.2f')
                ]
            ).properties(height=400)
            st.altair_chart(chart, width="stretch")
        else:
            st.info("Không có dữ liệu")
    
    st.markdown("---")
    
    st.subheader("Lịch sử Giải Đặc biệt")
    df = lottery_analysis.get_special_prize_history(limit=1000)
    if not df.empty:
        df['full_date'] = df['full_date'].astype(str)
        df = df[(df['full_date'] >= str(start_date)) & (df['full_date'] <= str(end_date))]
    if not df.empty:
        st.dataframe(
            df[['full_date', 'station_name', 'result_number']],
            width="stretch",
            height=400
        )
    else:
        st.info("Không có dữ liệu")


def render_combined_insights(revenue_analysis, lottery_analysis, start_date, end_date):
    st.header("Thông tin Tổng hợp")
    st.info(f"Hiển thị dữ liệu từ {start_date} đến {end_date}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tổng hợp theo Tháng")
        revenue_monthly = revenue_analysis.get_monthly_revenue_summary()
        lottery_monthly = lottery_analysis.get_monthly_lottery_summary()
        
        if not revenue_monthly.empty and not lottery_monthly.empty:
            import pandas as pd
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
            import pandas as pd
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


if __name__ == "__main__":
    main()
