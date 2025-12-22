import streamlit as st
import altair as alt


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
