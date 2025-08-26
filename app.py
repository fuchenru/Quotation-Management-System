import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Quotation System",
    page_icon="💾",
    layout="wide"
)

# Initialize session state for authentication and data storage
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'username' not in st.session_state:
    st.session_state.username = None

if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.esd_data = None
    st.session_state.cmf_data = None
    st.session_state.transistor_data = None
    st.session_state.mos_data = None
    st.session_state.last_refresh = None
    st.session_state.sky_data = None
    st.session_state.zener_data = None
    st.session_state.ps_data = None
    st.session_state.tvs_data = None
    st.session_state.quote_usd_data = None
    st.session_state.quote_rmb_data = None

def authenticate_user(username, password):
    """Authenticate user with credentials from secrets"""
    try:
        # Get all auth sections from secrets
        auth_config = st.secrets["auth"]
        
        # Check each user in the auth config
        for user_key, user_config in auth_config.items():
            if user_config["username"] == username and user_config["password"] == password:
                # Store the username in session state
                st.session_state.username = username
                return True
        
        return False
        
    except KeyError as e:
        st.error(f"Authentication credentials not configured in secrets: {str(e)}")
        return False
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return False

def login_page():
    """Display login page"""
    st.title("🔐 Login")
    st.markdown("---")
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Please enter your credentials")
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            login_button = st.form_submit_button("🔑 Login", type="primary", use_container_width=True)
            
            if login_button:
                if username and password:
                    if authenticate_user(username, password):
                        st.session_state.authenticated = True
                        st.success("✅ Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please enter both username and password")
        


def logout():
    """Logout function"""
    st.session_state.authenticated = False
    st.session_state.username = None  # Clear username on logout
    st.session_state.data_loaded = False
    st.session_state.esd_data = None
    st.session_state.cmf_data = None
    st.session_state.transistor_data = None
    st.session_state.mos_data = None
    st.session_state.last_refresh = None
    st.session_state.sky_data = None
    st.session_state.zener_data = None
    st.session_state.ps_data = None
    st.session_state.tvs_data = None
    st.session_state.quote_usd_data = None
    st.session_state.quote_rmb_data = None
    st.rerun()

def load_google_sheet(worksheet_name):
    """Load data from specific Google Sheets worksheet"""
    try:
        creds_info = st.secrets["connections"]["gsheets"]
        
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        credentials = Credentials.from_service_account_info(creds_info, scopes=scope)
        gc = gspread.authorize(credentials)
        sheet = gc.open_by_url(creds_info["spreadsheet"])
        worksheet = sheet.worksheet(worksheet_name)
        data = worksheet.get_all_records()
        
        if data:
            df = pd.DataFrame(data)
            # Convert Quote Date to datetime with flexible parsing for both formats
            if 'Quote Date' in df.columns:
                # Handle both 'YYYY.MM.DD' and 'YYYY-MM-DD' formats
                df['Quote Date'] = df['Quote Date'].apply(lambda x: 
                    pd.to_datetime(str(x).replace('.', '-'), errors='coerce') if x else None)
            return df
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error loading {worksheet_name} sheet: {str(e)}")
        return None

def update_google_sheet(worksheet_name, data_dict, row_index=None):
    """Update Google Sheets with new/modified data"""
    try:
        creds_info = st.secrets["connections"]["gsheets"]
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        credentials = Credentials.from_service_account_info(creds_info, scopes=scope)
        gc = gspread.authorize(credentials)
        sheet = gc.open_by_url(creds_info["spreadsheet"])
        worksheet = sheet.worksheet(worksheet_name)
        
        if row_index is None:
            # Add new row
            worksheet.append_row(list(data_dict.values()))
            return True, "Row added successfully"
        else:
            # Update existing row (row_index + 2 because gspread is 1-indexed and row 1 is headers)
            for col_index, value in enumerate(data_dict.values(), start=1):
                worksheet.update_cell(row_index + 2, col_index, value)
            return True, "Row updated successfully"
            
    except Exception as e:
        return False, f"Error updating sheet: {str(e)}"

def get_column_names(category):
    """Get column names for each category"""
    if category == "ESD":
        return [
            'Quote Date', 'Product Name', 'Package', 'FG Supplier', 'FG Supplier P/N', 
            'Parts RMB Price', 'Parts USD Price', 'Wafer Supplier', 'Wafer Supplier P/N', 
            'Magnias Wafer P/N', 'Wafer Price (RMB)', 'Distributor RMB Price', 
            'Distributor USD Price', 'Notes'
        ]
    elif category == "CMF":
        return [
            'Quote Date', 'Magnias P/N', 'FG Supplier', 'FG Supplier P/N', 'Parts RMB Price', 'Parts USD Price', 'Notes'
        ]
    elif category == "Transistor":
        return [
            'Quote Date', 'Magnias P/N', 'Package', 'FG Supplier', 'FG Supplier P/N', 'Parts RMB Price', 'Parts USD Price', 'Polarity', 'Notes'
        ]
    elif category == "MOS":
        return [
            'Quote Date', 'Magnias P/N', 'Package', 'Type', 'VDS (V)', 'ID (A)', 'FG Supplier', 'FG Supplier P/N',
            'Parts RMB Price', 'Parts USD Price', 'Wafer Supplier', 'Wafer Supplier P/N', 'Magnias Wafer P/N', 'Wafer Price (RMB)'
        ]
    elif category == "SKY":
        return [
            'Quote Date', 'Magnias P/N', 'FG Supplier', 'FG Supplier P/N', 'Parts RMB Price', 'Parts USD Price', 'Notes', 'IF (mA)',
            'IFSM (A)',	'VRRM (V)',	'Vf @ If= 1mA'
        ]
    elif category == "Zener":
        return [
            'Quote Date', 'Magnias P/N', 'Package', 'FG Supplier', 'FG Supplier P/N', 'Parts RMB Price', 'Parts USD Price', 'Notes'
        ]  
    elif category == "PS":
        return [
            'Quote Date', 'Magnias P/N', 'Package', 'FG Supplier', 'FG Supplier P/N', 'Parts RMB Price', 'Parts USD Price'
        ]
    elif category == "TVS":
        return [
            'Finished product supplier', 'Finished Product Supplier Material Name' , 'Parts RMB Price', 'Parts USD Price', 'Quote Date', 'Product Name', 'Package', 'PPK @ 10/1000us (W)', 'Distributor RMB Price', 'Distributor USD Price', 'Notes'
        ]
    return []

def display_data_management():
    """Display data management interface for CRUD operations"""
    st.title("⚙️ Data Management")
    st.markdown("---")
    
    # Category selection
    category = st.selectbox("Select Product Category:", ["ESD", "CMF", "Transistor", "MOS", "SKY", "Zener", "PS", "TVS"], key="mgmt_category")

    # Get cached data
    df = get_cached_data(category)
    
    if df is None:
        st.warning(f"No data available for {category} category")
        return
    
    # Operation selection
    operation = st.radio("Select Operation:", ["Add New Quote"], horizontal=True)

    if operation == "Add New Quote":
        display_add_product_form(category)

def display_add_product_form(category):
    """Display form to add new product"""
    st.subheader(f"➕ Add New {category} Product")
    
    columns = get_column_names(category)
    
    with st.form(f"add_{category}_form"):
        st.markdown("**Basic Information**")
        col1, col2 = st.columns(2)
        
        form_data = {}
        
        # Essential fields in first column
    with col1:
        if category in ["MOS", "CMF", "Transistor", "SKY", "Zener", "PS"]:  
            form_data['Magnias P/N'] = st.text_input("Magnias P/N*", key="add_magnias_pn")
            if category == "MOS":
                form_data['Package'] = st.text_input("Package", key="add_package")
                form_data['Type'] = st.selectbox("Type", ["N-Channel", "P-Channel", "Enhancement", "Depletion", "N/A"], key="add_mos_type")
            elif category == "Transistor":
                form_data['Package'] = st.text_input("Package", key="add_package")
                form_data['Polarity'] = st.selectbox("Polarity", ["NPN", "PNP", "N/A"], key="add_polarity")
        else:  # ESD and TVS
            form_data['Product Name'] = st.text_input("Product Name*", key="add_product_name")
            form_data['Package'] = st.text_input("Package", key="add_package")
        
    with col2:
        if category in ["MOS", "CMF", "Transistor", "SKY", "Zener", "PS"]:
            form_data['FG Supplier'] = st.text_input("FG Supplier", key="add_fg_supplier")
            form_data['FG Supplier P/N'] = st.text_input("FG Supplier P/N", key="add_fg_supplier_pn")
        elif category == "ESD":
            form_data['FG Supplier'] = st.text_input("FG Supplier", key="add_fg_supplier")
            form_data['FG Supplier P/N'] = st.text_input("FG Supplier P/N", key="add_fg_supplier_pn")
        elif category in ["TVS"]:
            form_data["Finished product supplier"] = st.text_input("Finished product supplier", key="add_fp_supplier")
            form_data["Finished Product Supplier Material Name"] = st.text_input("Finished Product Supplier Material Name", key="add_fpm_supplier")
        
        # Remove the Technical Specifications section for Transistor since it's now simplified
        # Only show Technical Specifications for ESD and MOS
        if category in ["MOS"]:
            st.markdown("**Technical Specifications**")
                    
            if category == "MOS":
                col1, col2 = st.columns(2)
                with col1:
                    form_data['VDS (V)'] = st.number_input("VDS (V)", step=0.1, key="add_vds")
                with col2:
                    form_data['ID (A)'] = st.number_input("ID (A)", step=0.1, key="add_id")
        
        st.markdown("**Pricing Information**")
        col1, col2 = st.columns(2)
        with col1:
            form_data['Parts RMB Price'] = st.number_input("Parts RMB Price", step=0.01, key="add_parts_rmb")
        with col2:
            form_data['Parts USD Price'] = st.number_input("Parts USD Price", step=0.01, key="add_parts_usd")


        # Additional fields - only for ESD and MOS
        if category == "ESD":
            st.markdown("**Wafer Information**")
            col1, col2 = st.columns(2)
            with col1:
                form_data['Wafer Supplier'] = st.text_input("Wafer Supplier", key="add_esd_wafer_supplier")
                form_data['Wafer Supplier P/N'] = st.text_input("Wafer Supplier P/N", key="add_esd_wafer_supplier_pn")
            with col2:
                form_data['Magnias Wafer P/N'] = st.text_input("Magnias Wafer P/N", key="add_esd_magnias_wafer_pn")
                form_data['Wafer Price (RMB)'] = st.number_input("Wafer Price (RMB)", step=0.01, key="add_esd_wafer_price")
            
            st.markdown("**Distributor Pricing**")
            col1, col2 = st.columns(2)
            with col1:
                form_data['Distributor RMB Price'] = st.number_input("Distributor RMB Price", step=0.01, key="add_dist_rmb")
            with col2:
                form_data['Distributor USD Price'] = st.number_input("Distributor USD Price", step=0.01, key="add_dist_usd")
                
        elif category == "MOS":
            col1, col2 = st.columns(2)
            with col1:
                form_data['Wafer Supplier'] = st.text_input("Wafer Supplier", key="add_mos_wafer_supplier")
                form_data['Wafer Supplier P/N'] = st.text_input("Wafer Supplier P/N", key="add_mos_wafer_supplier_pn")
            with col2:
                form_data['Magnias Wafer P/N'] = st.text_input("Magnias Wafer P/N", key="add_mos_magnias_wafer_pn")
                form_data['Wafer Price (RMB)'] = st.number_input("Wafer Price (RMB)", step=0.01, key="add_mos_wafer_price")
        
        form_data['Quote Date'] = st.date_input("Quote Date", value=datetime.now().date(), key="add_quote_date")
        form_data['Notes'] = st.text_area("Notes", key="add_notes")
        
        submitted = st.form_submit_button("➕ Add Product", type="primary")
        
        if submitted:
            required_field = 'Magnias P/N' if category in ["MOS", "CMF", "Transistor", "SKY", "Zener", "PS", "TVS"] else 'Product Name'  
            if form_data[required_field]:
                # Convert date to string
                form_data['Quote Date'] = form_data['Quote Date'].strftime('%Y.%m.%d')
                # Ensure all columns are present with empty values if not filled
                ordered_data = {}
                for col in columns:
                    ordered_data[col] = form_data.get(col, '')
                
                success, message = update_google_sheet(category, ordered_data)
                
                if success:
                    st.success(message)
                    st.session_state.data_loaded = False  # Force refresh
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error(f"{required_field} is required!")

def load_all_data():
    """Load all data from Google Sheets and store in session state"""
    with st.spinner("Loading data from Google Sheets..."):
        st.session_state.esd_data = load_google_sheet("ESD")
        st.session_state.cmf_data = load_google_sheet("CMF")
        st.session_state.transistor_data = load_google_sheet("Transistor")
        st.session_state.mos_data = load_google_sheet("MOS")
        st.session_state.sky_data = load_google_sheet("SKY")
        st.session_state.zener_data = load_google_sheet("Zener")
        st.session_state.ps_data = load_google_sheet("PS")
        st.session_state.tvs_data = load_google_sheet("TVS")
        st.session_state.quote_usd_data = load_google_sheet("QuoteUSD")
        st.session_state.quote_rmb_data = load_google_sheet("QuoteRMB")
        st.session_state.data_loaded = True
        st.session_state.last_refresh = datetime.now()

def get_cached_data(category):
    """Get cached data for specific category"""
    if not st.session_state.data_loaded:
        load_all_data()
    
    if category == "ESD":
        return st.session_state.esd_data
    elif category == "CMF":
        return st.session_state.cmf_data
    elif category == "Transistor":
        return st.session_state.transistor_data
    elif category == "MOS":
        return st.session_state.mos_data
    elif category == "SKY":
        return st.session_state.sky_data
    elif category == "Zener":
        return st.session_state.zener_data
    elif category == "PS":
        return st.session_state.ps_data
    elif category == "TVS":
        return st.session_state.tvs_data
    elif category == "QuoteUSD":
        return st.session_state.quote_usd_data
    elif category == "QuoteRMB":
        return st.session_state.quote_rmb_data
    else:
        return None

def get_latest_quotes(product_category, product_name):
    """Get latest quotes for a specific product from both USD and RMB sheets"""
    usd_data = get_cached_data("QuoteUSD")
    rmb_data = get_cached_data("QuoteRMB")
    
    quotes = []
    
    # Process USD quotes
    if usd_data is not None and not usd_data.empty:
        usd_quotes = usd_data[
            (usd_data['Products'].str.contains(product_category, case=False, na=False)) &
            (usd_data['Product Name'].str.contains(product_name, case=False, na=False))
        ]
        
        for _, row in usd_quotes.iterrows():
            for i in range(1, 5):  # DC-1 to DC-4
                dc_col = f'DC-{i}'
                date_col = f'Quote Date {i}'
                
                # Handle the inconsistent column naming for End Customer
                if i == 3:
                    customer_col = f'End Customers {i}'  # Note: "Customers" (plural) for column 3
                elif i == 4:
                    customer_col = f'End Customers {i}'  # Note: "Customers" (plural) for column 4
                else:
                    customer_col = f'End Customer {i}'   # Note: "Customer" (singular) for columns 1 & 2
                
                # Check if the customer column exists in the dataframe, if not try the other variant
                if customer_col not in row:
                    # Try the alternative naming
                    if i in [3, 4]:
                        customer_col = f'End Customer {i}'  # Try singular
                    else:
                        customer_col = f'End Customers {i}'  # Try plural
                
                if (dc_col in row and customer_col in row and date_col in row and 
                    pd.notna(row[dc_col]) and pd.notna(row[customer_col]) and pd.notna(row[date_col])):
                    
                    quotes.append({
                        'Currency': 'USD',
                        'Price': row[dc_col],
                        'Customer': row[customer_col],
                        'Quote_Date': pd.to_datetime(row[date_col], errors='coerce'),
                        'Raw_Date': row[date_col],
                        'DC_Column': dc_col
                    })
    
    # Process RMB quotes
    if rmb_data is not None and not rmb_data.empty:
        rmb_quotes = rmb_data[
            (rmb_data['Products'].str.contains(product_category, case=False, na=False)) &
            (rmb_data['Product Name'].str.contains(product_name, case=False, na=False))
        ]
        
        for _, row in rmb_quotes.iterrows():
            for i in range(1, 5):  # DC-1 to DC-4
                dc_col = f'DC-{i}'
                date_col = f'Quote Date {i}'
                
                # Handle the inconsistent column naming for End Customer
                if i == 3:
                    customer_col = f'End Customers {i}'  # Note: "Customers" (plural) for column 3
                elif i == 4:
                    customer_col = f'End Customers {i}'  # Note: "Customers" (plural) for column 4
                else:
                    customer_col = f'End Customer {i}'   # Note: "Customer" (singular) for columns 1 & 2
                
                # Check if the customer column exists in the dataframe, if not try the other variant
                if customer_col not in row:
                    # Try the alternative naming
                    if i in [3, 4]:
                        customer_col = f'End Customer {i}'  # Try singular
                    else:
                        customer_col = f'End Customers {i}'  # Try plural
                
                if (dc_col in row and customer_col in row and date_col in row and 
                    pd.notna(row[dc_col]) and pd.notna(row[customer_col]) and pd.notna(row[date_col])):
                    
                    quotes.append({
                        'Currency': 'RMB',
                        'Price': row[dc_col],
                        'Customer': row[customer_col],
                        'Quote_Date': pd.to_datetime(row[date_col], errors='coerce'),
                        'Raw_Date': row[date_col],
                        'DC_Column': dc_col
                    })
    
    # Sort by date descending (most recent first)
    quotes.sort(key=lambda x: x['Quote_Date'] if pd.notna(x['Quote_Date']) else pd.Timestamp.min, reverse=True)
    
    return quotes

def display_dashboard():
    """Display main dashboard with key metrics"""
    st.title("💾 Quotation Management System")
    st.markdown("---")
    
    # Get cached data
    esd_data = get_cached_data("ESD")
    cmf_data = get_cached_data("CMF")
    transistor_data = get_cached_data("Transistor")
    mos_data = get_cached_data("MOS")
    sky_data = get_cached_data("SKY")
    zener_data = get_cached_data("Zener")
    ps_data = get_cached_data("PS")
    tvs_data = get_cached_data("TVS")
    quote_usd_data = get_cached_data("QuoteUSD")
    quote_rmb_data = get_cached_data("QuoteRMB")

    # Dashboard metrics - First Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        esd_count = len(esd_data) if esd_data is not None else 0
        st.metric("ESD Products", esd_count)
    
    with col2:
        cmf_count = len(cmf_data) if cmf_data is not None else 0
        st.metric("CMF Products", cmf_count)
    
    with col3:
        transistor_count = len(transistor_data) if transistor_data is not None else 0
        st.metric("Transistor Products", transistor_count)
    
    with col4:
        mos_count = len(mos_data) if mos_data is not None else 0
        st.metric("MOS Products", mos_count)

    # Dashboard metrics - Second Row
    col5, col6, col7, col8, col9 = st.columns(5)

    with col5:
        sky_count = len(sky_data) if sky_data is not None else 0
        st.metric("SKY Products", sky_count)

    with col6:
        zener_count = len(zener_data) if zener_data is not None else 0
        st.metric("Zener Products", zener_count)

    with col7:
        ps_count = len(ps_data) if ps_data is not None else 0
        st.metric("PS Products", ps_count)

    with col8:
        tvs_count = len(tvs_data) if tvs_data is not None else 0
        st.metric("TVS Products", tvs_count)

    with col9:
        total_count = esd_count + cmf_count + transistor_count + mos_count + sky_count + zener_count + ps_count + tvs_count
        st.metric("Total Products", total_count)
    
    # Quotes Analysis Section
    st.markdown("---")
    st.subheader("💰 Quotes Analysis")
    
    # Process quotes data for analysis
    all_quotes = []
    
    # Process USD quotes
    if quote_usd_data is not None and not quote_usd_data.empty:
        for _, row in quote_usd_data.iterrows():
            for i in range(1, 5):  # DC-1 to DC-4
                dc_col = f'DC-{i}'
                date_col = f'Quote Date {i}'
                
                # Handle the inconsistent column naming for End Customer
                if i == 3:
                    customer_col = f'End Customers {i}'  # Note: "Customers" (plural) for column 3
                elif i == 4:
                    customer_col = f'End Customers {i}'  # Note: "Customers" (plural) for column 4
                else:
                    customer_col = f'End Customer {i}'   # Note: "Customer" (singular) for columns 1 & 2
                
                # Check if the customer column exists in the dataframe, if not try the other variant
                if customer_col not in row:
                    # Try the alternative naming
                    if i in [3, 4]:
                        customer_col = f'End Customer {i}'  # Try singular
                    else:
                        customer_col = f'End Customers {i}'  # Try plural
                
                if (dc_col in row and customer_col in row and date_col in row and 
                    pd.notna(row[dc_col]) and pd.notna(row[customer_col]) and pd.notna(row[date_col])):
                    
                    all_quotes.append({
                        'Product_Category': row.get('Products', 'N/A'),
                        'Product_Name': row.get('Product Name', 'N/A'),
                        'Currency': 'USD',
                        'Price': row[dc_col],
                        'Customer': row[customer_col],
                        'Quote_Date': pd.to_datetime(row[date_col], errors='coerce'),
                        'Distributor': row.get('Distributor', 'N/A')
                    })
    
    # Process RMB quotes
    if quote_rmb_data is not None and not quote_rmb_data.empty:
        for _, row in quote_rmb_data.iterrows():
            for i in range(1, 5):  # DC-1 to DC-4
                dc_col = f'DC-{i}'
                date_col = f'Quote Date {i}'
                
                # Handle the inconsistent column naming for End Customer
                if i == 3:
                    customer_col = f'End Customers {i}'  # Note: "Customers" (plural) for column 3
                elif i == 4:
                    customer_col = f'End Customers {i}'  # Note: "Customers" (plural) for column 4
                else:
                    customer_col = f'End Customer {i}'   # Note: "Customer" (singular) for columns 1 & 2
                
                # Check if the customer column exists in the dataframe, if not try the other variant
                if customer_col not in row:
                    # Try the alternative naming
                    if i in [3, 4]:
                        customer_col = f'End Customer {i}'  # Try singular
                    else:
                        customer_col = f'End Customers {i}'  # Try plural
                
                if (dc_col in row and customer_col in row and date_col in row and 
                    pd.notna(row[dc_col]) and pd.notna(row[customer_col]) and pd.notna(row[date_col])):
                    
                    all_quotes.append({
                        'Product_Category': row.get('Products', 'N/A'),
                        'Product_Name': row.get('Product Name', 'N/A'),
                        'Currency': 'RMB',
                        'Price': row[dc_col],
                        'Customer': row[customer_col],
                        'Quote_Date': pd.to_datetime(row[date_col], errors='coerce'),
                        'Distributor': row.get('Distributor', 'N/A')
                    })
    
    if all_quotes:
        quotes_df = pd.DataFrame(all_quotes)
        quotes_df = quotes_df.dropna(subset=['Quote_Date'])
        
        # Quotes metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_quotes = len(quotes_df)
            st.metric("Total Quotes", total_quotes)
        
        with col2:
            usd_quotes = len(quotes_df[quotes_df['Currency'] == 'USD'])
            st.metric("USD Quotes", usd_quotes)
        
        with col3:
            rmb_quotes = len(quotes_df[quotes_df['Currency'] == 'RMB'])
            st.metric("RMB Quotes", rmb_quotes)
        
        with col4:
            unique_customers = quotes_df['Customer'].nunique()
            st.metric("Unique Customers", unique_customers)
        
        # Charts Row
        col1, col2 = st.columns(2)
        
        with col1:
            # Quotes by Product Category
            if not quotes_df.empty:
                category_counts = quotes_df['Product_Category'].value_counts()
                fig_category = px.pie(
                    values=category_counts.values, 
                    names=category_counts.index,
                    title="Quotes Distribution by Product Category"
                )
                st.plotly_chart(fig_category, use_container_width=True)
        
        with col2:
            # Quotes by Currency
            if not quotes_df.empty:
                currency_counts = quotes_df['Currency'].value_counts()
                fig_currency = px.bar(
                    x=currency_counts.index,
                    y=currency_counts.values,
                    title="Quotes by Currency",
                    labels={'x': 'Currency', 'y': 'Number of Quotes'}
                )
                st.plotly_chart(fig_currency, use_container_width=True)
        
        # Recent Quotes Activity
        st.subheader("📈 Recent Quotes Activity")
        
        # Filter last 6 months for better visualization
        six_months_ago = pd.Timestamp.now() - pd.DateOffset(months=6)
        recent_quotes = quotes_df[quotes_df['Quote_Date'] >= six_months_ago]
        
        if not recent_quotes.empty:
            # Group by month and currency
            recent_quotes['Month'] = recent_quotes['Quote_Date'].dt.to_period('M')
            monthly_counts = recent_quotes.groupby(['Month', 'Currency']).size().reset_index(name='Count')
            monthly_counts['Month'] = monthly_counts['Month'].astype(str)
            
            fig_timeline = px.line(
                monthly_counts, 
                x='Month', 
                y='Count', 
                color='Currency',
                title="Monthly Quotes Activity (Last 6 Months)",
                markers=True
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Top Customers
        st.subheader("🏆 Top Customers by Quote Volume")
        top_customers = quotes_df['Customer'].value_counts().head(10)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            fig_customers = px.bar(
                x=top_customers.values,
                y=top_customers.index,
                orientation='h',
                title="Top 10 Customers",
                labels={'x': 'Number of Quotes', 'y': 'Customer'}
            )
            st.plotly_chart(fig_customers, use_container_width=True)
        
        with col2:
            # Recent Quotes Table
            st.write("**Recent Quotes (Last 10)**")
            recent_quotes_display = quotes_df.sort_values('Quote_Date', ascending=False).head(10)
            display_quotes = recent_quotes_display[['Product_Category', 'Product_Name', 'Currency', 'Price', 'Customer', 'Quote_Date']].copy()
            display_quotes['Quote_Date'] = display_quotes['Quote_Date'].dt.strftime('%Y-%m-%d')
            st.dataframe(display_quotes, use_container_width=True, hide_index=True)
    
    else:
        st.info("No quotes data available for analysis")

def display_price_lookup():
    """Display price lookup interface"""
    st.title("🔍 Price Lookup & Recommendations")
    st.markdown("---")
    
    # Product category selection - Add "All Products" as first option
    category = st.selectbox("Select Product Category:", ["All Products", "ESD", "CMF", "Transistor", "MOS", "SKY", "Zener", "PS", "TVS"])

    # Get cached data - handle "All Products" selection
    if category == "All Products":
        # Combine all product data
        all_dfs = []
        for cat in ["ESD", "CMF", "Transistor", "MOS", "SKY", "Zener", "PS", "TVS"]:
            cat_df = get_cached_data(cat)
            if cat_df is not None and not cat_df.empty:
                cat_df_copy = cat_df.copy()
                cat_df_copy['Category'] = cat  # Add category column
                all_dfs.append(cat_df_copy)
        
        if all_dfs:
            df = pd.concat(all_dfs, ignore_index=True, sort=False)
        else:
            df = pd.DataFrame()
    else:
        df = get_cached_data(category)
    
    if df is None or df.empty:
        st.warning(f"No data available for {category}")
        return
    
    # Search functionality
    if category == "All Products":
        search_label = "🔍 Search Product Name/Magnias P/N:"
        search_placeholder = "Enter product name or part number"
    else:
        search_label = "🔍 Search Magnias P/N:" if category in ["MOS", "CMF", "Transistor", "SKY", "Zener", "PS", "TVS"] else "🔍 Search Product Name:"  
        search_placeholder = "Enter Magnias P/N" if category in ["MOS", "CMF", "Transistor", "SKY", "Zener", "PS", "TVS"] else "Enter product name or part number"
    
    search_term = st.text_input(search_label, placeholder=search_placeholder)
    
    # Filter data based on search
    if search_term:
        if category == "All Products":
            # Search in both Product Name and Magnias P/N columns
            mask = pd.Series([False] * len(df))
            if 'Product Name' in df.columns:
                mask |= df['Product Name'].str.contains(search_term, case=False, na=False)
            if 'Magnias P/N' in df.columns:
                mask |= df['Magnias P/N'].str.contains(search_term, case=False, na=False)
            filtered_df = df[mask]
        else:
            # Try to find in Product Name or Magnias P/N columns
            if category in ["MOS", "CMF", "Transistor", "SKY", "Zener", "PS", "TVS"]:  
                search_column = 'Magnias P/N'
            else:
                search_column = 'Product Name' if 'Product Name' in df.columns else 'Product'
            
            filtered_df = df[df[search_column].str.contains(search_term, case=False, na=False)]
    else:
        filtered_df = df
    
    # Display results
    st.subheader(f"📋 {category}")
    
    # Key columns to display
    if category == "All Products":
        # Show category, product identifier, and prices
        display_columns = ['Category']
        if 'Product Name' in df.columns:
            display_columns.append('Product Name')
        if 'Magnias P/N' in df.columns:
            display_columns.append('Magnias P/N')
        display_columns.extend(['Parts RMB Price', 'Parts USD Price', 'Quote Date'])
    elif category in ["MOS", "CMF", "Transistor", "SKY", "Zener", "PS"]:
        display_columns = ['Quote Date', 'Magnias P/N', 'Parts RMB Price', 'Parts USD Price']
    else:
        display_columns = ['Product Name' if 'Product Name' in df.columns else 'Product',  
                          'Parts RMB Price', 'Parts USD Price', 'Quote Date']
    
    display_columns = [col for col in display_columns if col in df.columns]
    
    st.dataframe(filtered_df[display_columns], use_container_width=True)
    
    # Add Latest Quotes section - only show if there's a search term and not "All Products"
    if search_term and category != "All Products":
        st.markdown("---")
        st.subheader("💰 Latest Quotes")
        
        # Get the product name to search for quotes
        if category in ["MOS", "CMF", "Transistor", "SKY", "Zener", "PS", "TVS"]:
            # For these categories, use the search term as product name
            product_name_for_quotes = search_term
        else:
            # For ESD, use the Product Name from the filtered results
            if not filtered_df.empty and 'Product Name' in filtered_df.columns:
                product_name_for_quotes = filtered_df['Product Name'].iloc[0]
            else:
                product_name_for_quotes = search_term
        
        # Get latest quotes
        quotes = get_latest_quotes(category, product_name_for_quotes)
        
        if quotes:
            st.success(f"Found {len(quotes)} quotes for {category} - {product_name_for_quotes}")
            
            # Display quotes in a table format instead of expanders
            quote_data = []
            for i, quote in enumerate(quotes, 1):
                quote_data.append({
                    'Quote #': i,
                    'Currency': quote['Currency'],
                    'Price': quote['Price'],
                    'Customer': quote['Customer'],
                    'Date': quote['Raw_Date'],
                })
            
            quote_df = pd.DataFrame(quote_data)
            st.dataframe(quote_df, use_container_width=True)
        else:
            st.info(f"No quotes found for {category} - {product_name_for_quotes}")
    elif search_term and category == "All Products":
        st.info("💡 Latest Quotes are only available when searching within a specific product category.")


def display_product_details():
    """Display detailed product information"""
    st.title("📋 Product Details & Specifications")
    st.markdown("---")
    
    # Category and product selection
    category = st.selectbox("Select Product Category:", ["ESD", "CMF", "Transistor", "MOS", "SKY", "Zener", "PS", "TVS"], key="details_category")

    # Get cached data
    df = get_cached_data(category)
    
    if df is None or df.empty:
        st.warning(f"No data available for {category} category")
        return
    
    # Product selection
    if category in ["MOS", "CMF", "Transistor", "SKY", "Zener", "PS"]:
        product_col = 'Magnias P/N'
        products = sorted(df[product_col].dropna().unique())
        selected_product = st.selectbox("Select Magnias P/N:", products, key="details_product")
    else:
        product_col = 'Product Name' if 'Product Name' in df.columns else 'Product'
        products = sorted(df[product_col].dropna().unique())
        selected_product = st.selectbox("Select Product:", products, key="details_product")
    
    if selected_product:
        # Filter data for selected product
        product_data = df[df[product_col] == selected_product]
        
        if not product_data.empty:
            
            # FG Supplier Information (for all categories)
            st.subheader("🏪 FG Supplier Information")
            fg_specs = {
                'FG Supplier': product_data['FG Supplier'].iloc[0] if 'FG Supplier' in product_data.columns else 'N/A',
                'FG Supplier P/N': product_data['FG Supplier P/N'].iloc[0] if 'FG Supplier P/N' in product_data.columns else 'N/A',
            }
            
            # Display FG supplier specifications in columns with smaller font
            cols = st.columns(3)
            for i, (key, value) in enumerate(fg_specs.items()):
                with cols[i % 3]:
                    st.markdown(f"<div style='font-size: 0.9rem;'><strong>{key}:</strong><br>{value}</div>", unsafe_allow_html=True)
            
            # Wafer supplier information (only for ESD and MOS)
            if category in ["ESD", "MOS"]:
                st.subheader("📟 Wafer Supplier")
                wafer_specs = {
                    'Wafer Supplier': product_data['Wafer Supplier'].iloc[0] if 'Wafer Supplier' in product_data.columns else 'N/A',
                }
                
                if category == ["ESD", "MOS"]:
                    wafer_specs['Magnias Wafer P/N'] = product_data['Magnias Wafer P/N'].iloc[0] if 'Magnias Wafer P/N' in product_data.columns else 'N/A'
                
                # Display wafer specifications in columns with smaller font
                cols = st.columns(3)
                for i, (key, value) in enumerate(wafer_specs.items()):
                    with cols[i % 3]:
                        st.markdown(f"<div style='font-size: 0.9rem;'><strong>{key}:</strong><br>{value}</div>", unsafe_allow_html=True)
            


def authenticated_main():
    """Main application function for authenticated users"""
    
    # Sidebar navigation
    with st.sidebar:
        st.sidebar.image("https://i.postimg.cc/j5G8ytbC/cropped-logo.png")
        st.header("Navigation")
        
        # Show current user
        if st.session_state.username:
            st.info(f"👤 Logged in as: {st.session_state.username}")
        
        # Add logout button at the top
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            logout()
        
        st.markdown("---")
        
        # Create navigation options based on user role
        nav_options = ["Dashboard", "Price Lookup", "Product Details"]
        
        # Only add Data Management for admin users
        if st.session_state.username == "admin":
            nav_options.append("Data Management")
        
        page = st.radio("Select Page:", nav_options)
        
        # Show a message if user is not admin and tries to access data management features
        if st.session_state.username != "admin":
            st.markdown("---")
            st.info("💡 **Note:** Data Management is only available for admin users")
        
        st.markdown("---")
        
        # Data status
        if st.session_state.data_loaded and st.session_state.last_refresh:
            st.success("✅ Data Loaded")
            st.caption(f"Last refresh: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.warning("⚠️ Data not loaded")
        
        # Refresh button
        if st.button("🔄 Refresh Data", type="primary"):
            load_all_data()
            st.success("Data refreshed!")
            st.rerun()
        
        # Force reload button (for debugging)
        if st.button("🔄 Force Reload", help="Clear cache and reload all data"):
            st.session_state.data_loaded = False
            st.session_state.esd_data = None
            st.session_state.cmf_data = None
            st.session_state.transistor_data = None
            st.session_state.mos_data = None
            st.session_state.last_refresh = None
            st.session_state.sky_data = None
            st.session_state.zener_data = None
            st.session_state.ps_data = None
            st.session_state.tvs_data = None
            st.session_state.quote_usd_data = None
            st.session_state.quote_rmb_data = None
            load_all_data()
            st.success("Data force reloaded!")
            st.rerun()
        
        st.markdown("---")
        st.info("💡 **Tip:** Data is cached in memory. Only refresh when you need latest updates from Google Sheets")
        
        # Quick stats
        st.subheader("Quick Stats")
        if st.session_state.data_loaded:
            esd_count = len(st.session_state.esd_data) if st.session_state.esd_data is not None else 0
            cmf_count = len(st.session_state.cmf_data) if st.session_state.cmf_data is not None else 0
            transistor_count = len(st.session_state.transistor_data) if st.session_state.transistor_data is not None else 0
            mos_count = len(st.session_state.mos_data) if st.session_state.mos_data is not None else 0
            sky_count = len(st.session_state.sky_data) if st.session_state.sky_data is not None else 0
            zener_count = len(st.session_state.zener_data) if st.session_state.zener_data is not None else 0
            ps_count = len(st.session_state.ps_data) if st.session_state.ps_data is not None else 0
            tvs_count = len(st.session_state.tvs_data) if st.session_state.tvs_data is not None else 0

            st.write(f"ESD: {esd_count}")
            st.write(f"CMF: {cmf_count}")
            st.write(f"Transistor: {transistor_count}")
            st.write(f"MOS: {mos_count}")
            st.write(f"SKY: {sky_count}")
            st.write(f"Zener: {zener_count}")
            st.write(f"PS: {ps_count}")
            st.write(f"TVS: {tvs_count}")
            st.write(f"**Total: {esd_count + cmf_count + transistor_count + mos_count + sky_count + zener_count + ps_count + tvs_count}**")
        else:
            st.write("Loading...")
    
    # Load data on first run
    if not st.session_state.data_loaded:
        load_all_data()
    
    # Main content based on page selection
    if page == "Dashboard":
        display_dashboard()
    elif page == "Price Lookup":
        display_price_lookup()
    elif page == "Product Details":
        display_product_details()
    elif page == "Data Management":
        # Double-check admin access before showing data management
        if st.session_state.username == "admin":
            display_data_management()
        else:
            st.error("🚫 Access Denied: Data Management is only available for admin users")
            st.info("Please contact your administrator if you need access to this feature.")

def main():
    """Main application function with authentication check"""
    
    # Check if user is authenticated
    if not st.session_state.authenticated:
        login_page()
    else:
        authenticated_main()

if __name__ == "__main__":
    main()
