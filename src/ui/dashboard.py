import streamlit as st
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import DatabaseConnection
from src.analysis.revenue import RevenueAnalysis
from src.analysis.lottery import LotteryAnalysis
from src.ui.revenue_tab import render_revenue_analysis
from src.ui.lottery_tab import render_lottery_analysis
from src.ui.insights_tab import render_combined_insights
from src.ui.forecasting_tab import render_forecasting


st.set_page_config(
    page_title="Kho Dữ liệu - Phân tích Xổ số và Doanh thu",
    page_icon="📊",
    layout="wide"
)

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
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Phân tích Doanh thu", 
        "Phân tích Xổ số", 
        "Thông tin Tổng hợp",
        "Dự đoán Doanh thu"
    ])
    
    with tab1:
        render_revenue_analysis(revenue_analysis, start_date, end_date)
    
    with tab2:
        render_lottery_analysis(lottery_analysis, start_date, end_date)
    
    with tab3:
        render_combined_insights(revenue_analysis, lottery_analysis, start_date, end_date)
    
    with tab4:
        render_forecasting(db)




if __name__ == "__main__":
    main()
