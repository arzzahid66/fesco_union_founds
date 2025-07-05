import streamlit as st
import pandas as pd
from datetime import datetime
import google_sheets_api as gsa
import excel_export as excel

st.set_page_config(page_title="Union Funds Management", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    .logo-img {
        height: 60px;
        width: auto;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .section-header {
        background: #f0f2f6;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .success-msg {
        background: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    @media (max-width: 768px) {
        .main-header {
            flex-direction: column;
            gap: 10px;
        }
        .main-header h1 {
            font-size: 2rem;
        }
        .logo-img {
            height: 50px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Main header with logo
try:
    # Try to display logo using Streamlit's method
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.image("hydrounion.png", width=150)
    
    # Alternative: Use base64 encoding for the logo
    import base64
    
    def get_base64_image(image_path):
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except:
            return None
    
    logo_base64 = get_base64_image("hydrounion.png")
    
    if logo_base64:
        st.markdown(f"""
        <div class="main-header">
            <img src="data:image/png;base64,{logo_base64}" alt="Company Logo" class="logo-img">
            <h1> Union Funds Management System</h1>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Fallback without logo
        st.markdown("""
        <div class="main-header">
            <h1> Union Funds Management System</h1>
        </div>
        """, unsafe_allow_html=True)
        
except Exception as e:
    # Fallback if logo loading fails
    st.markdown("""
    <div class="main-header">
        <h1> Union Funds Management System</h1>
    </div>
    """, unsafe_allow_html=True)

def auto_load_data_on_start():
    """Automatically load data from Google Sheets when the app starts"""
    try:
        # Check if data is already loaded in this session
        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = False
        
        # Load data if not already loaded or if explicitly requested
        if not st.session_state.data_loaded:
            income_df = gsa.read_sheet_data('Income')
            expense_df = gsa.read_sheet_data('Expenses')
            
            if not income_df.empty:
                # Clean the data and handle NaN values
                income_df = income_df.fillna('')
                # Ensure proper column order
                if len(income_df.columns) >= 4:
                    income_df.columns = ['Sr', 'Date', 'Name', 'Amount']
                st.session_state.income_data = income_df
            else:
                st.session_state.income_data = pd.DataFrame(columns=['Sr', 'Date', 'Name', 'Amount'])
            
            if not expense_df.empty:
                # Clean the data and handle NaN values
                expense_df = expense_df.fillna('')
                # Ensure proper column order
                if len(expense_df.columns) >= 4:
                    expense_df.columns = ['Sr', 'Date', 'Name', 'Amount']
                st.session_state.expense_data = expense_df
            else:
                st.session_state.expense_data = pd.DataFrame(columns=['Sr', 'Date', 'Name', 'Amount'])
            
            st.session_state.data_loaded = True
            return True
    except Exception as e:
        st.error(f"Error auto-loading data from Google Sheets: {str(e)}")
        # Initialize empty dataframes if loading fails
        if 'income_data' not in st.session_state:
            st.session_state.income_data = pd.DataFrame(columns=['Sr', 'Date', 'Name', 'Amount'])
        if 'expense_data' not in st.session_state:
            st.session_state.expense_data = pd.DataFrame(columns=['Sr', 'Date', 'Name', 'Amount'])
        return False
    
# Initialize session state
if 'income_data' not in st.session_state:
    st.session_state.income_data = pd.DataFrame(columns=['Sr', 'Date', 'Name', 'Amount'])
if 'expense_data' not in st.session_state:
    st.session_state.expense_data = pd.DataFrame(columns=['Sr', 'Date', 'Name', 'Amount'])


auto_load_data_on_start()


# Sidebar navigation
st.sidebar.header("📊 Navigation")
page = st.sidebar.selectbox("Choose Section", ["Add Income", "Add Expense", "View Data", "Monthly Summary", "Download Data"])

# Helper functions
# Updated load_data_from_sheets function (replace the existing one)
def load_data_from_sheets():
    """Manual data loading function"""
    try:
        income_df = gsa.read_sheet_data('Income')
        expense_df = gsa.read_sheet_data('Expenses')
        
        if not income_df.empty:
            # Clean the data and handle NaN values
            income_df = income_df.fillna('')
            # Ensure proper column order
            if len(income_df.columns) >= 4:
                income_df.columns = ['Sr', 'Date', 'Name', 'Amount']
            st.session_state.income_data = income_df
        else:
            st.session_state.income_data = pd.DataFrame(columns=['Sr', 'Date', 'Name', 'Amount'])
        
        if not expense_df.empty:
            # Clean the data and handle NaN values
            expense_df = expense_df.fillna('')
            # Ensure proper column order
            if len(expense_df.columns) >= 4:
                expense_df.columns = ['Sr', 'Date', 'Name', 'Amount']
            st.session_state.expense_data = expense_df
        else:
            st.session_state.expense_data = pd.DataFrame(columns=['Sr', 'Date', 'Name', 'Amount'])
        
        st.session_state.data_loaded = True
        return True
    except Exception as e:
        st.error(f"Error loading data from Google Sheets: {str(e)}")
        return False

def clean_dataframe_for_sheets(df):
    """Clean DataFrame to remove NaN values and prepare for Google Sheets"""
    if df.empty:
        return df
    
    # Make a copy to avoid modifying the original
    clean_df = df.copy()
    
    # Replace NaN values with empty strings
    clean_df = clean_df.fillna('')
    
    # Convert all columns to string to avoid type issues
    for col in clean_df.columns:
        clean_df[col] = clean_df[col].astype(str)
    
    return clean_df

def save_data_to_sheets():
    try:
        # Save income data
        if not st.session_state.income_data.empty:
            # Clean the data first
            clean_income = clean_dataframe_for_sheets(st.session_state.income_data)
            
            # Prepare data with headers - convert DataFrame to list format
            headers = [['Sr', 'Date', 'Name', 'Amount']]
            data_rows = clean_income.values.tolist()
            
            # Combine headers and data
            all_data = headers + data_rows
            
            # Write to sheets using the list format
            gsa.write_sheet_data('Income', all_data)
        
        # Save expense data
        if not st.session_state.expense_data.empty:
            # Clean the data first
            clean_expense = clean_dataframe_for_sheets(st.session_state.expense_data)
            
            # Prepare data with headers - convert DataFrame to list format
            headers = [['Sr', 'Date', 'Name', 'Amount']]
            data_rows = clean_expense.values.tolist()
            
            # Combine headers and data
            all_data = headers + data_rows
            
            # Write to sheets using the list format
            gsa.write_sheet_data('Expenses', all_data)
        
        return True
    except Exception as e:
        st.error(f"Error saving data to Google Sheets: {str(e)}")
        return False

# Load data on app start
if st.sidebar.button("🔄 Load Data from Google Sheets"):
    if load_data_from_sheets():
        st.sidebar.success("Data loaded successfully!")
    else:
        st.sidebar.error("Failed to load data")

# Page content based on selection
if page == "Add Income":
    st.markdown('<div class="section-header"><h2>💵 Add Incoming Amount</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        income_date = st.date_input("Date", datetime.now())
        income_name = st.text_input("Name/Description")
    
    with col2:
        income_amount = st.number_input("Amount", min_value=0.0, step=0.01)
        
    if st.button("➕ Add Income", type="primary"):
        if income_name and income_amount > 0:
            new_sr = len(st.session_state.income_data) + 1
            new_row = pd.DataFrame({
                'Sr': [str(new_sr)],
                'Date': [income_date.strftime('%Y-%m-%d')],
                'Name': [income_name],
                'Amount': [str(income_amount)]
            })
            st.session_state.income_data = pd.concat([st.session_state.income_data, new_row], ignore_index=True)
            
            if save_data_to_sheets():
                st.markdown('<div class="success-msg">✅ Income added successfully and saved to Google Sheets!</div>', unsafe_allow_html=True)
            else:
                st.warning("Income added locally but failed to save to Google Sheets")
        else:
            st.error("Please fill in all fields with valid data")

elif page == "Add Expense":
    st.markdown('<div class="section-header"><h2>💸 Add Spending</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        expense_date = st.date_input("Date", datetime.now())
        expense_name = st.text_input("Name/Description")
    
    with col2:
        expense_amount = st.number_input("Amount", min_value=0.0, step=0.01)
        
    if st.button("➕ Add Expense", type="primary"):
        if expense_name and expense_amount > 0:
            new_sr = len(st.session_state.expense_data) + 1
            new_row = pd.DataFrame({
                'Sr': [str(new_sr)],
                'Date': [expense_date.strftime('%Y-%m-%d')],
                'Name': [expense_name],
                'Amount': [str(expense_amount)]
            })
            st.session_state.expense_data = pd.concat([st.session_state.expense_data, new_row], ignore_index=True)
            
            if save_data_to_sheets():
                st.markdown('<div class="success-msg">✅ Expense added successfully and saved to Google Sheets!</div>', unsafe_allow_html=True)
            else:
                st.warning("Expense added locally but failed to save to Google Sheets")
        else:
            st.error("Please fill in all fields with valid data")

elif page == "View Data":
    st.markdown('<div class="section-header"><h2>📋 View All Data</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💵 Income Records")
        if not st.session_state.income_data.empty:
            st.dataframe(st.session_state.income_data, use_container_width=True)
        else:
            st.info("No income records found")
    
    with col2:
        st.subheader("💸 Expense Records")
        if not st.session_state.expense_data.empty:
            st.dataframe(st.session_state.expense_data, use_container_width=True)
        else:
            st.info("No expense records found")

elif page == "Monthly Summary":
    st.markdown('<div class="section-header"><h2>📊 Monthly Summary</h2></div>', unsafe_allow_html=True)
    
    # Calculate totals with proper type conversion
    total_income = 0
    total_expenses = 0
    
    if not st.session_state.income_data.empty:
        try:
            total_income = pd.to_numeric(st.session_state.income_data['Amount'], errors='coerce').fillna(0).sum()
        except:
            total_income = 0
    
    if not st.session_state.expense_data.empty:
        try:
            total_expenses = pd.to_numeric(st.session_state.expense_data['Amount'], errors='coerce').fillna(0).sum()
        except:
            total_expenses = 0
    
    net_balance = total_income - total_expenses
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💵 Total Income", f"Rs {total_income:,.2f}")
    
    with col2:
        st.metric("💸 Total Expenses", f"Rs {total_expenses:,.2f}")
    
    with col3:
        st.metric("💰 Net Balance", f"Rs {net_balance:,.2f}", delta=f"{net_balance:,.2f}")
    
    # Monthly breakdown
    if not st.session_state.income_data.empty or not st.session_state.expense_data.empty:
        st.subheader("📅 Monthly Breakdown")
        
        # Prepare data for monthly analysis
        income_monthly = pd.DataFrame()
        expense_monthly = pd.DataFrame()
        
        if not st.session_state.income_data.empty:
            try:
                income_copy = st.session_state.income_data.copy()
                income_copy['Date'] = pd.to_datetime(income_copy['Date'], errors='coerce')
                income_copy['Amount'] = pd.to_numeric(income_copy['Amount'], errors='coerce').fillna(0)
                income_copy = income_copy.dropna(subset=['Date'])
                if not income_copy.empty:
                    income_copy['Month'] = income_copy['Date'].dt.to_period('M')
                    income_monthly = income_copy.groupby('Month')['Amount'].sum().reset_index()
                    income_monthly.columns = ['Month', 'Income']
            except Exception as e:
                st.warning(f"Error processing income data for monthly breakdown: {str(e)}")
        
        if not st.session_state.expense_data.empty:
            try:
                expense_copy = st.session_state.expense_data.copy()
                expense_copy['Date'] = pd.to_datetime(expense_copy['Date'], errors='coerce')
                expense_copy['Amount'] = pd.to_numeric(expense_copy['Amount'], errors='coerce').fillna(0)
                expense_copy = expense_copy.dropna(subset=['Date'])
                if not expense_copy.empty:
                    expense_copy['Month'] = expense_copy['Date'].dt.to_period('M')
                    expense_monthly = expense_copy.groupby('Month')['Amount'].sum().reset_index()
                    expense_monthly.columns = ['Month', 'Expenses']
            except Exception as e:
                st.warning(f"Error processing expense data for monthly breakdown: {str(e)}")
        
        # Merge and display
        if not income_monthly.empty and not expense_monthly.empty:
            monthly_summary = pd.merge(income_monthly, expense_monthly, on='Month', how='outer').fillna(0)
            monthly_summary['Net'] = monthly_summary['Income'] - monthly_summary['Expenses']
            st.dataframe(monthly_summary, use_container_width=True)
        elif not income_monthly.empty:
            st.dataframe(income_monthly, use_container_width=True)
        elif not expense_monthly.empty:
            st.dataframe(expense_monthly, use_container_width=True)

elif page == "Download Data":
    st.markdown('<div class="section-header"><h2>📥 Download Data</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Excel Downloads")
        
        # Complete Excel file with all data
        if st.button("📋 Download Complete Excel File", type="primary"):
            if not st.session_state.income_data.empty or not st.session_state.expense_data.empty:
                # Convert data properly for Excel export
                income_for_excel = st.session_state.income_data.copy()
                expense_for_excel = st.session_state.expense_data.copy()
                
                # Convert Amount columns to numeric
                if not income_for_excel.empty:
                    income_for_excel['Amount'] = pd.to_numeric(income_for_excel['Amount'], errors='coerce').fillna(0)
                if not expense_for_excel.empty:
                    expense_for_excel['Amount'] = pd.to_numeric(expense_for_excel['Amount'], errors='coerce').fillna(0)
                
                excel_data = excel.create_excel_file(income_for_excel, expense_for_excel)
                st.download_button(
                    label="💾 Download Excel File",
                    data=excel_data,
                    file_name=f"union_funds_complete_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("No data available to download")
        
        # Individual CSV downloads
        if st.button("📊 Download Income CSV"):
            if not st.session_state.income_data.empty:
                csv_data = st.session_state.income_data.to_csv(index=False)
                st.download_button(
                    label="💾 Download Income CSV",
                    data=csv_data,
                    file_name=f"income_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No income data to download")
        
        if st.button("📊 Download Expenses CSV"):
            if not st.session_state.expense_data.empty:
                csv_data = st.session_state.expense_data.to_csv(index=False)
                st.download_button(
                    label="💾 Download Expenses CSV",
                    data=csv_data,
                    file_name=f"expense_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No expense data to download")
    
    with col2:
        st.subheader("📋 Combined Downloads")
        
        # Combined CSV
        if st.button("📊 Download Combined CSV"):
            if not st.session_state.income_data.empty or not st.session_state.expense_data.empty:
                # Convert data properly for CSV export
                income_for_csv = st.session_state.income_data.copy()
                expense_for_csv = st.session_state.expense_data.copy()
                
                # Convert Amount columns to numeric
                if not income_for_csv.empty:
                    income_for_csv['Amount'] = pd.to_numeric(income_for_csv['Amount'], errors='coerce').fillna(0)
                if not expense_for_csv.empty:
                    expense_for_csv['Amount'] = pd.to_numeric(expense_for_csv['Amount'], errors='coerce').fillna(0)
                
                combined_csv = excel.create_combined_csv(income_for_csv, expense_for_csv)
                st.download_button(
                    label="💾 Download Combined CSV",
                    data=combined_csv,
                    file_name=f"union_funds_combined_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No data available to download")
        
        # Data summary
        st.subheader("📈 Data Summary")
        
        # Calculate totals safely
        total_income = 0
        total_expenses = 0
        
        if not st.session_state.income_data.empty:
            try:
                total_income = pd.to_numeric(st.session_state.income_data['Amount'], errors='coerce').fillna(0).sum()
            except:
                total_income = 0
        
        if not st.session_state.expense_data.empty:
            try:
                total_expenses = pd.to_numeric(st.session_state.expense_data['Amount'], errors='coerce').fillna(0).sum()
            except:
                total_expenses = 0
        
        st.write(f"**Income Records:** {len(st.session_state.income_data)}")
        st.write(f"**Expense Records:** {len(st.session_state.expense_data)}")
        st.write(f"**Total Income:** Rs {total_income:,.2f}")
        st.write(f"**Total Expenses:** Rs {total_expenses:,.2f}")
        st.write(f"**Net Balance:** Rs {total_income - total_expenses:,.2f}")

# Footer
st.markdown("---")
st.markdown("**Union Funds Management System** - Manage your union's finances efficiently with Google Sheets integration.")