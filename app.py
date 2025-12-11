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
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_custom_css():
    """Inject professional CRM/SaaS styling with light theme"""
    st.markdown("""
    <style>
    /* Import Professional Fonts */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* ═══ COLOR SYSTEM ═══ */
    :root {
        --primary: #2563eb;
        --primary-hover: #1d4ed8;
        --secondary: #64748b;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --bg-tertiary: #f1f5f9;
        --text-primary: #0f172a;
        --text-secondary: #334155;
        --text-muted: #64748b;
        --border: #e2e8f0;
    }
    
    /* ═══ GLOBAL STYLES ═══ */
    .stApp {
        background: var(--bg-primary);
        font-family: 'IBM Plex Sans', -apple-system, sans-serif;
        color: var(--text-primary);
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    
    /* ═══ TYPOGRAPHY ═══ */
    h1 {
        font-size: 2.25rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.025em !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin: 2rem 0 1rem !important;
    }
    
    h3 {
        font-size: 1.125rem !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        font-size: 0.875rem !important;
        margin: 1.5rem 0 1rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 1px solid var(--border) !important;
    }
    
    /* ═══ SIDEBAR ═══ */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border) !important;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background: var(--bg-primary);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 0.625rem 1rem;
        font-weight: 500;
        transition: all 0.15s ease;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: var(--primary);
        color: white;
        border-color: var(--primary);
        transform: translateY(-1px);
    }
    
    /* ═══ METRIC CARDS ═══ */
    [data-testid="stMetric"] {
        background: var(--bg-secondary);
        padding: 1.25rem;
        border-radius: 8px;
        border: 1px solid var(--border);
        transition: all 0.2s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        border-color: var(--primary);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        font-family: 'JetBrains Mono', monospace !important;
        color: var(--text-primary) !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    /* ═══ INPUTS ═══ */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea textarea,
    .stDateInput > div > div > input,
    .stSelectbox > div > div {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        transition: all 0.15s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea textarea:focus,
    .stDateInput > div > div > input:focus,
    .stSelectbox > div > div:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }
    
    /* ═══ BUTTONS ═══ */
    .stButton > button {
        background: var(--primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.625rem 1.25rem !important;
        font-weight: 600 !important;
        transition: all 0.15s ease !important;
    }
    
    .stButton > button:hover {
        background: var(--primary-hover) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }
    
    /* ═══ DATA TABLES ═══ */
    [data-testid="stDataFrame"] {
        background: var(--bg-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stDataFrame"] thead tr th {
        background: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.05em !important;
    }
    
    [data-testid="stDataFrame"] tbody tr:hover {
        background: rgba(37, 99, 235, 0.05) !important;
    }
    
    /* ═══ FORMS ═══ */
    [data-testid="stForm"] {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 1.5rem !important;
    }
    
    /* ═══ ALERTS ═══ */
    .stSuccess {
        background: rgba(16, 185, 129, 0.1) !important;
        border-left: 4px solid var(--success) !important;
        color: #047857 !important;
        border-radius: 6px !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border-left: 4px solid var(--danger) !important;
        color: #b91c1c !important;
        border-radius: 6px !important;
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.1) !important;
        border-left: 4px solid var(--warning) !important;
        color: #c2410c !important;
        border-radius: 6px !important;
    }
    
    .stInfo {
        background: rgba(37, 99, 235, 0.1) !important;
        border-left: 4px solid var(--primary) !important;
        color: var(--text-secondary) !important;
        border-radius: 6px !important;
    }
    
    /* ═══ RADIO BUTTONS ═══ */
    .stRadio label {
        background: var(--bg-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        padding: 0.625rem 1rem !important;
        transition: all 0.15s ease !important;
    }
    
    .stRadio label:hover {
        background: var(--bg-tertiary) !important;
        border-color: var(--primary) !important;
    }
    
    /* ═══ SCROLLBAR ═══ */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }
    
    /* ═══ ANIMATIONS ═══ */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .block-container > div {
        animation: fadeIn 0.3s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

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
    st.session_state.PowerSwitch_data = None
    st.session_state.Misc_data = None
    st.session_state.SDOthers_data = None
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
    """Display professional login page"""
    
    # Additional login styling
    st.markdown("""
    <style>
    .login-container {
        max-width: 450px;
        margin: 5rem auto;
        padding: 3rem;
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 12px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.3);
    }
    
    .login-icon {
        width: 64px;
        height: 64px;
        background: linear-gradient(135deg, var(--primary), var(--primary-hover));
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1.5rem;
        font-size: 2rem;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
    }
    
    .login-title {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .login-subtitle {
        text-align: center;
        color: var(--text-secondary);
        font-size: 0.9375rem;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-icon">💼</div>
        <div class="login-title">Quotation CRM</div>
        <div class="login-subtitle">Sign in to access your account</div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_a, col_b = st.columns([1, 1])
            with col_a:
                login_button = st.form_submit_button("🔐 Sign In", type="primary", use_container_width=True)
            with col_b:
                help_button = st.form_submit_button("Need Help?", type="secondary", use_container_width=True)
            
            if login_button:
                if username and password:
                    if authenticate_user(username, password):
                        st.session_state.authenticated = True
                        st.success("✓ Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("✗ Invalid username or password")
                else:
                    st.warning("⚠ Please enter both username and password")
            
            if help_button:
                st.info("📧 Contact your system administrator for assistance")

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
    st.session_state.PowerSwitch_data = None
    st.session_state.Misc_data = None
    st.session_state.SDOthers_data = None
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
            
            # Get the row number of the newly added row
            new_row_number = len(worksheet.get_all_values())
            num_columns = len(data_dict)
            
            # Apply left alignment to the new row
            # Format the range for the entire new row
            range_name = f"A{new_row_number}:{chr(ord('A') + num_columns - 1)}{new_row_number}"
            
            worksheet.format(range_name, {
                "horizontalAlignment": "LEFT",
                "textFormat": {
                    "bold": False
                }
            })
            
            return True, "Row added successfully with left alignment"
        else:
            # Update existing row (row_index + 2 because gspread is 1-indexed and row 1 is headers)
            target_row = row_index + 2
            for col_index, value in enumerate(data_dict.values(), start=1):
                worksheet.update_cell(target_row, col_index, value)
            
            # Apply left alignment to the updated row
            num_columns = len(data_dict)
            range_name = f"A{target_row}:{chr(ord('A') + num_columns - 1)}{target_row}"
            
            worksheet.format(range_name, {
                "horizontalAlignment": "LEFT",
                "textFormat": {
                    "bold": False
                }
            })
            
            return True, "Row updated successfully with left alignment"
            
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
    elif category == "PowerSwitch":
        return [
            'Quote Date', 'Magnias P/N', 'Package', 'FG Supplier', 'FG Supplier P/N', 'Parts RMB Price', 'Parts USD Price'
        ]
    elif category == "Misc":
            return [
                'Quote Date', 'Magnias P/N', 'Package', 'FG Supplier', 'FG Supplier P/N', 'Parts RMB Price', 'Parts USD Price'
            ]
    elif category == "SDOthers":
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
    category = st.selectbox("Select Product Category:", ["ESD", "CMF", "Transistor", "MOS", "SKY", "Zener", "PowerSwitch", "Misc", "SDOthers", "TVS"], key="mgmt_category")

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
            if category in ["MOS", "CMF", "Transistor", "SKY", "Zener", "PowerSwitch", "Misc", "SDOthers"]:  
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
            if category in ["MOS", "CMF", "Transistor", "SKY", "Zener", "PowerSwitch", "Misc", "SDOthers"]:
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
            # Use text input for direct entry, then validate and format
            parts_rmb_input = st.text_input("Parts RMB Price", placeholder="Enter price (e.g., 1.23456)", key="add_parts_rmb")
        with col2:
            parts_usd_input = st.text_input("Parts USD Price", placeholder="Enter price (e.g., 0.17501)", key="add_parts_usd")

        # Additional fields - only for ESD and MOS
        if category == "ESD":
            st.markdown("**Wafer Information**")
            col1, col2 = st.columns(2)
            with col1:
                form_data['Wafer Supplier'] = st.text_input("Wafer Supplier", key="add_esd_wafer_supplier")
                form_data['Wafer Supplier P/N'] = st.text_input("Wafer Supplier P/N", key="add_esd_wafer_supplier_pn")
            with col2:
                form_data['Magnias Wafer P/N'] = st.text_input("Magnias Wafer P/N", key="add_esd_magnias_wafer_pn")
                wafer_price_input = st.text_input("Wafer Price (RMB)", placeholder="Enter price (e.g., 25.00000)", key="add_esd_wafer_price")
            
            st.markdown("**Distributor Pricing**")
            col1, col2 = st.columns(2)
            with col1:
                dist_rmb_input = st.text_input("Distributor RMB Price", placeholder="Enter price (e.g., 2.50000)", key="add_dist_rmb")
            with col2:
                dist_usd_input = st.text_input("Distributor USD Price", placeholder="Enter price (e.g., 0.35000)", key="add_dist_usd")
                
        elif category == "MOS":
            col1, col2 = st.columns(2)
            with col1:
                form_data['Wafer Supplier'] = st.text_input("Wafer Supplier", key="add_mos_wafer_supplier")
                form_data['Wafer Supplier P/N'] = st.text_input("Wafer Supplier P/N", key="add_mos_wafer_supplier_pn")
            with col2:
                form_data['Magnias Wafer P/N'] = st.text_input("Magnias Wafer P/N", key="add_mos_magnias_wafer_pn")
                wafer_price_input = st.text_input("Wafer Price (RMB)", placeholder="Enter price (e.g., 25.00000)", key="add_mos_wafer_price")
        
        form_data['Quote Date'] = st.date_input("Quote Date", value=datetime.now().date(), key="add_quote_date")
        form_data['Notes'] = st.text_area("Notes", key="add_notes")
        
        submitted = st.form_submit_button("➕ Add Product", type="primary")
        
        if submitted:
            required_field = 'Magnias P/N' if category in ["MOS", "CMF", "Transistor", "SKY", "Zener", "PowerSwitch", "TVS", "Misc", "SDOthers"] else 'Product Name'  
            if form_data[required_field]:
                # Process and format price inputs
                try:
                    # Format Parts RMB Price
                    if parts_rmb_input.strip():
                        form_data['Parts RMB Price'] = f"{float(parts_rmb_input):.5f}"
                    else:
                        form_data['Parts RMB Price'] = "0.00000"
                    
                    # Format Parts USD Price
                    if parts_usd_input.strip():
                        form_data['Parts USD Price'] = f"{float(parts_usd_input):.5f}"
                    else:
                        form_data['Parts USD Price'] = "0.00000"
                    
                    # Format category-specific prices
                    if category == "ESD":
                        if wafer_price_input.strip():
                            form_data['Wafer Price (RMB)'] = f"{float(wafer_price_input):.5f}"
                        else:
                            form_data['Wafer Price (RMB)'] = "0.00000"
                            
                        if dist_rmb_input.strip():
                            form_data['Distributor RMB Price'] = f"{float(dist_rmb_input):.5f}"
                        else:
                            form_data['Distributor RMB Price'] = "0.00000"
                            
                        if dist_usd_input.strip():
                            form_data['Distributor USD Price'] = f"{float(dist_usd_input):.5f}"
                        else:
                            form_data['Distributor USD Price'] = "0.00000"
                    
                    elif category == "MOS":
                        if wafer_price_input.strip():
                            form_data['Wafer Price (RMB)'] = f"{float(wafer_price_input):.5f}"
                        else:
                            form_data['Wafer Price (RMB)'] = "0.00000"
                    
                except ValueError as e:
                    st.error("Please enter valid numeric values for prices (e.g., 1.23456)")
                    return
                
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
        st.session_state.PowerSwitch_data = load_google_sheet("PowerSwitch")
        st.session_state.Misc_data = load_google_sheet("Misc")
        st.session_state.SDOthers_data = load_google_sheet("SDOthers")
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
    elif category == "PowerSwitch":
        return st.session_state.PowerSwitch_data
    elif category == "Misc":
        return st.session_state.Misc_data
    elif category == "SDOthers":
        return st.session_state.SDOthers_data
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
            for i in range(1, 9):  # DC-1 to DC-8
                dc_col = f'DC-{i}'
                date_col = f'Quote Date {i}'
                distributor_col = f'Distributor-{i}'  # NEW: Individual distributor
                
                # Handle the inconsistent column naming for End Customer
                if i == 3:
                    customer_col = f'End Customers {i}'  # Note: "Customers" (plural) for column 3
                elif i == 4:
                    customer_col = f'End Customers {i}'  # Note: "Customers" (plural) for column 4
                else:
                    customer_col = f'End Customer {i}'   # Note: "Customer" (singular) for columns 1 & 2, 5-8
                
                # Check if the customer column exists in the dataframe, if not try the other variant
                if customer_col not in row:
                    # Try the alternative naming
                    if i in [3, 4]:
                        customer_col = f'End Customer {i}'  # Try singular
                    else:
                        customer_col = f'End Customers {i}'  # Try plural
                
                if (dc_col in row and customer_col in row and date_col in row and distributor_col in row and
                    pd.notna(row[dc_col]) and pd.notna(row[customer_col]) and pd.notna(row[date_col])):
                    
                    # Get distributor value, default to 'N/A' if empty
                    distributor_value = row.get(distributor_col, 'N/A')
                    if pd.isna(distributor_value) or str(distributor_value).strip() == '':
                        distributor_value = 'N/A'
                    
                    quotes.append({
                        'Currency': 'USD',
                        'Price': row[dc_col],
                        'Customer': row[customer_col],
                        'Distributor': distributor_value,  # NEW: Individual distributor
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
            for i in range(1, 9):  # DC-1 to DC-8
                dc_col = f'DC-{i}'
                date_col = f'Quote Date {i}'
                distributor_col = f'Distributor-{i}'  # NEW: Individual distributor
                
                # Handle the inconsistent column naming for End Customer
                if i == 3:
                    customer_col = f'End Customers {i}'  # Note: "Customers" (plural) for column 3
                elif i == 4:
                    customer_col = f'End Customers {i}'  # Note: "Customers" (plural) for column 4
                else:
                    customer_col = f'End Customer {i}'   # Note: "Customer" (singular) for columns 1 & 2, 5-8
                
                # Check if the customer column exists in the dataframe, if not try the other variant
                if customer_col not in row:
                    # Try the alternative naming
                    if i in [3, 4]:
                        customer_col = f'End Customer {i}'  # Try singular
                    else:
                        customer_col = f'End Customers {i}'  # Try plural
                
                if (dc_col in row and customer_col in row and date_col in row and distributor_col in row and
                    pd.notna(row[dc_col]) and pd.notna(row[customer_col]) and pd.notna(row[date_col])):
                    
                    # Get distributor value, default to 'N/A' if empty
                    distributor_value = row.get(distributor_col, 'N/A')
                    if pd.isna(distributor_value) or str(distributor_value).strip() == '':
                        distributor_value = 'N/A'
                    
                    quotes.append({
                        'Currency': 'RMB',
                        'Price': row[dc_col],
                        'Customer': row[customer_col],
                        'Distributor': distributor_value,  # NEW: Individual distributor
                        'Quote_Date': pd.to_datetime(row[date_col], errors='coerce'),
                        'Raw_Date': row[date_col],
                        'DC_Column': dc_col
                    })
    
    # Sort by date descending (most recent first)
    quotes.sort(key=lambda x: x['Quote_Date'] if pd.notna(x['Quote_Date']) else pd.Timestamp.min, reverse=True)
    
    return quotes

def display_dashboard():
    """Display main dashboard with key metrics"""
    st.title("Quotation Management System")
    st.markdown("---")
    
    # Get cached data
    esd_data = get_cached_data("ESD")
    cmf_data = get_cached_data("CMF")
    transistor_data = get_cached_data("Transistor")
    mos_data = get_cached_data("MOS")
    sky_data = get_cached_data("SKY")
    zener_data = get_cached_data("Zener")
    PowerSwitch_data = get_cached_data("PowerSwitch")
    Misc_data = get_cached_data("Misc")
    SDOthers_data = get_cached_data("SDOthers")
    tvs_data = get_cached_data("TVS")
    quote_usd_data = get_cached_data("QuoteUSD")
    quote_rmb_data = get_cached_data("QuoteRMB")

    # Calculate all counts first
    esd_count = len(esd_data) if esd_data is not None else 0
    cmf_count = len(cmf_data) if cmf_data is not None else 0
    transistor_count = len(transistor_data) if transistor_data is not None else 0
    mos_count = len(mos_data) if mos_data is not None else 0
    sky_count = len(sky_data) if sky_data is not None else 0
    zener_count = len(zener_data) if zener_data is not None else 0
    PowerSwitch_count = len(PowerSwitch_data) if PowerSwitch_data is not None else 0
    Misc_count = len(Misc_data) if Misc_data is not None else 0
    SDOthers_count = len(SDOthers_data) if SDOthers_data is not None else 0
    tvs_count = len(tvs_data) if tvs_data is not None else 0
    total_count = esd_count + cmf_count + transistor_count + mos_count + sky_count + zener_count + PowerSwitch_count + tvs_count + Misc_count + SDOthers_count

    # Product Metrics Section
    st.subheader("Product Inventory")
    
    # Dashboard metrics - First Row (5 columns)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("ESD Products", esd_count)
    with col2:
        st.metric("CMF Products", cmf_count)
    with col3:
        st.metric("Transistor Products", transistor_count)
    with col4:
        st.metric("MOS Products", mos_count)
    with col5:
        st.metric("SKY Products", sky_count)

    # Dashboard metrics - Second Row (5 columns)
    col6, col7, col8, col9, col10 = st.columns(5)
    
    with col6:
        st.metric("Zener Products", zener_count)
    with col7:
        st.metric("PowerSwitch Products", PowerSwitch_count)
    with col8:
        st.metric("TVS Products", tvs_count)
    with col9:
        st.metric("Misc Products", Misc_count)
    with col10:
        st.metric("SDOthers Products", SDOthers_count)
    
    # Dashboard metrics - Third Row (Total - centered)
    col11, col12, col13 = st.columns([2, 1, 2])
    with col12:
        st.metric("Total Products", total_count)
    
    # Quotes Analysis Section
    st.markdown("---")
    st.subheader("Quotes Analysis")
    
    # Process quotes data for analysis
    all_quotes = []
    
    # Process USD quotes
    if quote_usd_data is not None and not quote_usd_data.empty:
        for _, row in quote_usd_data.iterrows():
            for i in range(1, 9):  # DC-1 to DC-8
                dc_col = f'DC-{i}'
                date_col = f'Quote Date {i}'
                distributor_col = f'Distributor-{i}'  # NEW: Individual distributor
                
                # Handle the inconsistent column naming for End Customer
                if i == 3:
                    customer_col = f'End Customers {i}'  # Note: "Customers" (plural) for column 3
                elif i == 4:
                    customer_col = f'End Customers {i}'  # Note: "Customers" (plural) for column 4
                else:
                    customer_col = f'End Customer {i}'   # Note: "Customer" (singular) for columns 1 & 2, 5-8
                
                # Check if the customer column exists in the dataframe, if not try the other variant
                if customer_col not in row:
                    # Try the alternative naming
                    if i in [3, 4]:
                        customer_col = f'End Customer {i}'  # Try singular
                    else:
                        customer_col = f'End Customers {i}'  # Try plural
                
                if (dc_col in row and customer_col in row and date_col in row and distributor_col in row and
                    pd.notna(row[dc_col]) and pd.notna(row[customer_col]) and pd.notna(row[date_col])):
                    
                    # Get distributor value, default to 'N/A' if empty
                    distributor_value = row.get(distributor_col, 'N/A')
                    if pd.isna(distributor_value) or str(distributor_value).strip() == '':
                        distributor_value = 'N/A'
                    
                    all_quotes.append({
                        'Product_Category': row.get('Products', 'N/A'),
                        'Product_Name': row.get('Product Name', 'N/A'),
                        'Currency': 'USD',
                        'Price': row[dc_col],
                        'Customer': row[customer_col],
                        'Quote_Date': pd.to_datetime(row[date_col], errors='coerce'),
                        'Distributor': distributor_value  # NEW: Individual distributor per quote
                    })

    # Process RMB quotes
    if quote_rmb_data is not None and not quote_rmb_data.empty:
        for _, row in quote_rmb_data.iterrows():
            for i in range(1, 9):  # DC-1 to DC-8
                dc_col = f'DC-{i}'
                date_col = f'Quote Date {i}'
                distributor_col = f'Distributor-{i}'  # NEW: Individual distributor
                
                # Handle the inconsistent column naming for End Customer
                if i == 3:
                    customer_col = f'End Customers {i}'  # Note: "Customers" (plural) for column 3
                elif i == 4:
                    customer_col = f'End Customers {i}'  # Note: "Customers" (plural) for column 4
                else:
                    customer_col = f'End Customer {i}'   # Note: "Customer" (singular) for columns 1 & 2, 5-8
                
                # Check if the customer column exists in the dataframe, if not try the other variant
                if customer_col not in row:
                    # Try the alternative naming
                    if i in [3, 4]:
                        customer_col = f'End Customer {i}'  # Try singular
                    else:
                        customer_col = f'End Customers {i}'  # Try plural
                
                if (dc_col in row and customer_col in row and date_col in row and distributor_col in row and
                    pd.notna(row[dc_col]) and pd.notna(row[customer_col]) and pd.notna(row[date_col])):
                    
                    # Get distributor value, default to 'N/A' if empty
                    distributor_value = row.get(distributor_col, 'N/A')
                    if pd.isna(distributor_value) or str(distributor_value).strip() == '':
                        distributor_value = 'N/A'
                    
                    all_quotes.append({
                        'Product_Category': row.get('Products', 'N/A'),
                        'Product_Name': row.get('Product Name', 'N/A'),
                        'Currency': 'RMB',
                        'Price': row[dc_col],
                        'Customer': row[customer_col],
                        'Quote_Date': pd.to_datetime(row[date_col], errors='coerce'),
                        'Distributor': distributor_value  # NEW: Individual distributor per quote
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
                st.plotly_chart(fig_category, width='stretch')
        
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
                st.plotly_chart(fig_currency, width='stretch')
        
        # Recent Quotes Activity
        st.subheader("Recent Quotes Activity")
        
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
            st.plotly_chart(fig_timeline, width='stretch')
        
        # Top Customers
        st.subheader("Top Customers by Quote Volume")
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
            st.plotly_chart(fig_customers, width='stretch')
        
        with col2:
            # Recent Quotes Table
            st.write("**Recent Quotes (Last 10)**")
            recent_quotes_display = quotes_df.sort_values('Quote_Date', ascending=False).head(10)
            display_quotes = recent_quotes_display[['Product_Category', 'Product_Name', 'Currency', 'Price', 'Customer', 'Quote_Date']].copy()
            display_quotes['Quote_Date'] = display_quotes['Quote_Date'].dt.strftime('%Y-%m-%d')
            st.dataframe(display_quotes, width='stretch', hide_index=True)
    
    else:
        st.info("No quotes data available for analysis")

def add_quote_to_sheet(currency, product_category, product_name, price, customer, distributor, quote_date):
    """Add a new quote to the appropriate Google Sheets tab (QuoteUSD or QuoteRMB)"""
    try:
        # Force price to 4 decimal places
        price = round(float(price), 4)
        
        worksheet_name = f"Quote{currency}"
        
        creds_info = st.secrets["connections"]["gsheets"]
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        credentials = Credentials.from_service_account_info(creds_info, scopes=scope)
        gc = gspread.authorize(credentials)
        sheet = gc.open_by_url(creds_info["spreadsheet"])
        worksheet = sheet.worksheet(worksheet_name)
        
        # Format price with currency symbol and exactly 4 decimal places
        if currency == "USD":
            formatted_price = f"${price:.4f}"
        else:  # RMB
            formatted_price = f"¥{price:.4f}"
        
        # Get all existing data to find the right row or create new one
        existing_data = worksheet.get_all_records()
        existing_df = pd.DataFrame(existing_data) if existing_data else pd.DataFrame()
        
        # Look for existing row with same product category and product name
        matching_row = None
        row_index = None
        
        if not existing_df.empty:
            mask = (
                (existing_df['Products'].str.contains(product_category, case=False, na=False)) &
                (existing_df['Product Name'].str.contains(product_name, case=False, na=False))
            )
            matching_rows = existing_df[mask]
            
            if not matching_rows.empty:
                matching_row = matching_rows.iloc[0]
                row_index = matching_rows.index[0]
        
        if matching_row is not None:
            # Update existing row - find next available DC column
            for i in range(1, 9):  # DC-1 to DC-8
                dc_col = f'DC-{i}'
                if pd.isna(matching_row.get(dc_col)) or matching_row.get(dc_col) == '':
                    # Found empty slot, update this column and corresponding date/customer/distributor
                    col_index_dc = list(existing_df.columns).index(dc_col) + 1  # +1 for gspread indexing
                    
                    # Find corresponding date, customer, and distributor columns
                    date_col = f'Quote Date {i}'
                    distributor_col = f'Distributor-{i}'
                    if i == 3:
                        customer_col = f'End Customers {i}'  # Note: plural for column 3
                    elif i == 4:
                        customer_col = f'End Customers {i}'  # Note: plural for column 4  
                    else:
                        customer_col = f'End Customer {i}'   # Note: singular for columns 1 & 2, 5-8
                    
                    try:
                        col_index_date = list(existing_df.columns).index(date_col) + 1
                        col_index_distributor = list(existing_df.columns).index(distributor_col) + 1
                        col_index_customer = list(existing_df.columns).index(customer_col) + 1
                    except ValueError:
                        # If column doesn't exist, try alternative naming
                        if i in [3, 4]:
                            customer_col = f'End Customer {i}'  # Try singular
                        else:
                            customer_col = f'End Customers {i}'  # Try plural
                        col_index_customer = list(existing_df.columns).index(customer_col) + 1
                    
                    # Update the cells (row_index + 2 because gspread is 1-indexed and row 1 is headers)
                    worksheet.update_cell(row_index + 2, col_index_dc, formatted_price)  # Use formatted price
                    worksheet.update_cell(row_index + 2, col_index_date, quote_date)
                    worksheet.update_cell(row_index + 2, col_index_customer, customer)
                    worksheet.update_cell(row_index + 2, col_index_distributor, distributor)  # NEW: Update distributor
                    
                    return True, f"Quote added to existing product record in {dc_col}"
            
            return False, "All DC columns are filled for this product. Cannot add more quotes."
        
        else:
            # Create new row
            # Updated headers structure for new quote sheets with individual distributors
            headers = [
                'Products', 'Product Name', 'Distributor-1',
                'DC-1', 'End Customer 1', 'Quote Date 1',
                'Distributor-2', 'DC-2', 'End Customer 2', 'Quote Date 2',
                'Distributor-3', 'DC-3', 'End Customers 3', 'Quote Date 3',
                'Distributor-4', 'DC-4', 'End Customers 4', 'Quote Date 4',
                'Distributor-5', 'DC-5', 'End Customers 5', 'Quote Date 5',
                'Distributor-6', 'DC-6', 'End Customers 6', 'Quote Date 6',
                'Distributor-7', 'DC-7', 'End Customers 7', 'Quote Date 7',
                'Distributor-8', 'DC-8', 'End Customers 8', 'Quote Date 8',
            ]
            
            # Create new row data
            new_row_data = [''] * len(headers)
            
            # Fill in the basic info
            if 'Products' in headers:
                new_row_data[headers.index('Products')] = product_category
            if 'Product Name' in headers:
                new_row_data[headers.index('Product Name')] = product_name
            
            # Add the quote in DC-1 with formatted price and distributor
            if 'DC-1' in headers:
                new_row_data[headers.index('DC-1')] = formatted_price  # Use formatted price
            if 'Quote Date 1' in headers:
                new_row_data[headers.index('Quote Date 1')] = quote_date
            if 'End Customer 1' in headers:
                new_row_data[headers.index('End Customer 1')] = customer
            if 'Distributor-1' in headers:
                new_row_data[headers.index('Distributor-1')] = distributor  # NEW: Add distributor
            
            worksheet.append_row(new_row_data)
            return True, "New product quote record created"
            
    except Exception as e:
        return False, f"Error adding quote: {str(e)}"

def get_latest_quotes_with_distributor(category, product_name):
    """Get latest quotes for a product including distributor information"""
    quotes = []
    
    try:
        # Load both USD and RMB quote sheets
        usd_data = st.session_state.get('quote_usd_data')
        if usd_data is None:
            usd_data = load_google_sheet("QuoteUSD")
            
        rmb_data = st.session_state.get('quote_rmb_data')
        if rmb_data is None:
            rmb_data = load_google_sheet("QuoteRMB")
        
        # Process USD quotes
        if usd_data is not None and not usd_data.empty:
            usd_quotes = extract_quotes_from_sheet(usd_data, category, product_name, "USD")
            quotes.extend(usd_quotes)
        
        # Process RMB quotes  
        if rmb_data is not None and not rmb_data.empty:
            rmb_quotes = extract_quotes_from_sheet(rmb_data, category, product_name, "RMB")
            quotes.extend(rmb_quotes)
        
        # Sort by date (most recent first) - handle date parsing safely
        def safe_date_sort(quote):
            try:
                # Try to parse the date for sorting
                date_str = quote.get('Raw_Date', '')
                if isinstance(date_str, str) and date_str:
                    # Handle various date formats
                    from datetime import datetime
                    try:
                        return datetime.strptime(date_str, '%m/%d/%Y')
                    except:
                        try:
                            return datetime.strptime(date_str, '%Y-%m-%d')
                        except:
                            return datetime.min
                return datetime.min
            except:
                return datetime.min
        
        quotes.sort(key=safe_date_sort, reverse=True)
        
        return quotes[:10]  # Return top 10 most recent quotes
        
    except Exception as e:
        st.error(f"Error loading quotes: {str(e)}")
        return []

def extract_quotes_from_sheet(df, category, product_name, currency):
    """Extract quotes from a specific sheet with individual distributor information per quote"""
    quotes = []
    
    try:
        # Check if required columns exist
        if 'Products' not in df.columns or 'Product Name' not in df.columns:
            return quotes
        
        # Create boolean masks for filtering
        products_mask = df['Products'].str.contains(category, case=False, na=False)
        product_name_mask = df['Product Name'].str.contains(product_name, case=False, na=False)
        
        # Combine masks and filter
        combined_mask = products_mask & product_name_mask
        matching_rows = df[combined_mask]
        
        if matching_rows.empty:
            return quotes
        
        for _, row in matching_rows.iterrows():
            # Extract quotes from DC-1 through DC-8 columns
            for i in range(1, 9):
                dc_col = f'DC-{i}'
                date_col = f'Quote Date {i}'
                distributor_col = f'Distributor-{i}'  # NEW: Individual distributor per quote
                
                # Handle customer column naming variations
                if i in [3, 4]:
                    customer_col = f'End Customers {i}'  # Plural for 3 & 4
                    if customer_col not in df.columns:
                        customer_col = f'End Customer {i}'  # Try singular
                else:
                    customer_col = f'End Customer {i}'    # Singular for 1 & 2, 5-8
                    if customer_col not in df.columns:
                        customer_col = f'End Customers {i}'  # Try plural
                
                # Skip if columns don't exist
                if (dc_col not in df.columns or date_col not in df.columns or 
                    customer_col not in df.columns or distributor_col not in df.columns):
                    continue
                
                # Get values
                price_value = row.get(dc_col, '')
                date_value = row.get(date_col, '')
                customer_value = row.get(customer_col, '')
                distributor_value = row.get(distributor_col, '')  # NEW: Get individual distributor
                
                # Check if all required values exist and are not empty
                price_valid = not pd.isna(price_value) and str(price_value).strip() != ''
                date_valid = not pd.isna(date_value) and str(date_value).strip() != ''
                customer_valid = not pd.isna(customer_value) and str(customer_value).strip() != ''
                
                # Distributor can be empty/N/A
                if pd.isna(distributor_value) or str(distributor_value).strip() == '':
                    distributor_display = 'N/A'
                else:
                    distributor_display = str(distributor_value).strip()
                
                if price_valid and date_valid and customer_valid:
                    quotes.append({
                        'Price': str(price_value).strip(),
                        'Currency': currency,
                        'Customer': str(customer_value).strip(),
                        'Distributor': distributor_display,  # NEW: Individual distributor
                        'Raw_Date': str(date_value).strip(),
                        'Quote_Column': dc_col
                    })
        
        return quotes
        
    except Exception as e:
        print(f"Error in extract_quotes_from_sheet: {str(e)}")
        return quotes

def format_price_display(price_value, currency="USD"):
    """Format price for display with currency symbol and exactly 5 decimal places"""
    if pd.isna(price_value) or price_value == '' or price_value is None:
        return ''
    
    try:
        # Extract numeric value if it's already formatted with currency symbol
        if isinstance(price_value, str):
            # Remove currency symbols and convert to float
            numeric_value = float(price_value.replace('$', '').replace('¥', '').replace(',', ''))
        else:
            numeric_value = float(price_value)
        
        # Force to exactly 5 decimal places
        numeric_value = round(numeric_value, 5)
        
        # Format with appropriate currency symbol and exactly 5 decimal places
        if currency == "USD":
            return f"${numeric_value:.5f}"
        else:  # RMB
            return f"¥{numeric_value:.5f}"
            
    except (ValueError, TypeError):
        return str(price_value)  # Return original if conversion fails

def display_add_quote_form(category, product_name):
    """Display form to add a new quote - IMPROVED VERSION with 4 decimal place enforcement"""
    st.subheader("➕ Add New Quote")
    
    with st.form("add_quote_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            currency = st.selectbox("Currency", ["USD", "RMB"], key="quote_currency")
            
            # Enhanced price input with 4 decimal place enforcement
            price_str = st.text_input(
                "Price", 
                value="0.0000",
                placeholder="Enter price (will be rounded to 4 decimal places)",
                key="quote_price_text",
                help="Enter price - will automatically be formatted to exactly 4 decimal places"
            )
            
            customer = st.text_input("End Customer", key="quote_customer")
        
        with col2:
            distributor = st.text_input("Distributor (optional)", key="quote_distributor")
            quote_date = st.date_input("Quote Date", value=datetime.now().date(), key="quote_date")
        
        submitted = st.form_submit_button("💰 Add Quote", type="primary")
        
        if submitted:
            # Convert price_str to float and force 4 decimal places
            try:
                price = float(price_str) if price_str else 0.0
                price = round(price, 4)  # Force to 4 decimal places
                
                # Display the rounded price to user for confirmation
                st.info(f"Price will be saved as: {format_price_display(price, currency)}")
                
            except ValueError:
                st.error("Please enter a valid numeric price!")
                return
            
            if price > 0 and customer.strip():
                # Convert date to M/D/YYYY format (e.g., 8/25/2025)
                quote_date_str = quote_date.strftime('%m/%d/%Y').lstrip('0').replace('/0', '/')
                
                success, message = add_quote_to_sheet(
                    currency, category, product_name, price, 
                    customer, distributor, quote_date_str
                )
                
                if success:
                    st.success(message)
                    # Force refresh of quote data
                    if currency == "USD":
                        st.session_state.quote_usd_data = None
                    else:
                        st.session_state.quote_rmb_data = None
                    
                    # Reload the specific quote data
                    if currency == "USD":
                        st.session_state.quote_usd_data = load_google_sheet("QuoteUSD")
                    else:
                        st.session_state.quote_rmb_data = load_google_sheet("QuoteRMB")
                    
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Please enter a valid price and customer name!")

def display_price_lookup():
    """Display price lookup interface with enhanced quote management"""
    st.title("🔍 Price Lookup & Recommendations")
    st.markdown("---")
    
    # Product category selection - Add "All Products" as first option
    category = st.selectbox("Select Product Category:", ["All Products", "ESD", "CMF", "Transistor", "MOS", "SKY", "Zener", "PowerSwitch", "TVS", "Misc", "SDOthers"])

    # Get cached data - handle "All Products" selection
    if category == "All Products":
        # Combine all product data
        all_dfs = []
        for cat in ["ESD", "CMF", "Transistor", "MOS", "SKY", "Zener", "PowerSwitch", "TVS", "Misc", "SDOthers"]:
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
        search_label = "🔍 Search Magnias P/N:" if category in ["MOS", "CMF", "Transistor", "SKY", "Zener", "PowerSwitch", "TVS", "Misc", "SDOthers"] else "🔍 Search Product Name:"  
        search_placeholder = "Enter Magnias P/N" if category in ["MOS", "CMF", "Transistor", "SKY", "Zener", "PowerSwitch", "TVS", "Misc", "SDOthers"] else "Enter product name or part number"
    
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
            if category in ["MOS", "CMF", "Transistor", "SKY", "Zener", "PowerSwitch", "TVS", "Misc", "SDOthers"]:  
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
    elif category in ["MOS", "CMF", "Transistor", "SKY", "Zener", "PowerSwitch", "Misc", "SDOthers", "TVS"]:
        display_columns = ['Quote Date', 'Magnias P/N', 'Parts RMB Price', 'Parts USD Price']
    else:
        display_columns = ['Product Name' if 'Product Name' in df.columns else 'Product',  
                          'Parts RMB Price', 'Parts USD Price', 'Quote Date']
    
    display_columns = [col for col in display_columns if col in df.columns]
    
    # Format prices in the dataframe for display
    display_df = filtered_df[display_columns].copy()
    
    # Format price columns to exactly 4 decimal places
    if 'Parts RMB Price' in display_df.columns:
        display_df['Parts RMB Price'] = display_df['Parts RMB Price'].apply(lambda x: format_price_display(x, "RMB"))
    
    if 'Parts USD Price' in display_df.columns:
        display_df['Parts USD Price'] = display_df['Parts USD Price'].apply(lambda x: format_price_display(x, "USD"))
    
    st.dataframe(display_df, width='stretch')
    
    # Enhanced Latest Quotes and Quote Management section - only show if there's a search term and not "All Products"
    if search_term and category != "All Products":
        st.markdown("---")
        
        # Two columns for Latest Quotes and Add Quote
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("💰 Latest Quotes")
            
            # Get the product name to search for quotes
            if category in ["MOS", "CMF", "Transistor", "SKY", "Zener", "PowerSwitch", "TVS", "Misc", "SDOthers"]:
                # For these categories, use the search term as product name
                product_name_for_quotes = search_term
            else:
                # For ESD, use the Product Name from the filtered results
                if not filtered_df.empty and 'Product Name' in filtered_df.columns:
                    product_name_for_quotes = filtered_df['Product Name'].iloc[0]
                else:
                    product_name_for_quotes = search_term
            
            # Get latest quotes with enhanced distributor extraction
            quotes = get_latest_quotes_with_distributor(category, product_name_for_quotes)
            
            if quotes:
                # Display quotes in a table format with formatted prices and distributor column
                quote_data = []
                for i, quote in enumerate(quotes, 1):
                    # Format the price based on currency with exactly 5 decimal places
                    formatted_quote_price = format_price_display(quote['Price'], quote['Currency'])
                    
                    quote_data.append({
                        'Quote #': i,
                        'Currency': quote['Currency'],
                        'Price': formatted_quote_price,  # Use formatted price with 4 decimals
                        'Distributor': quote.get('Distributor', 'N/A'),  # Add distributor column
                        'Customer': quote['Customer'],
                        'Date': quote['Raw_Date'],
                    })
                
                quote_df = pd.DataFrame(quote_data)
                st.dataframe(quote_df, width='stretch')
            else:
                st.info(f"No quotes found for {category} - {product_name_for_quotes}")
        
        with col2:
            # Show Add Quote form only for authenticated users
            if st.session_state.get('authenticated', False):
                display_add_quote_form(category, product_name_for_quotes)
            else:
                st.info("Please log in to add quotes")
                
    elif search_term and category == "All Products":
        st.info("💡 Latest Quotes and Quote Management are only available when searching within a specific product category.")


def display_product_details():
    """Display detailed product information"""
    st.title("📋 Product Details & Specifications")
    st.markdown("---")
    
    # Category and product selection
    category = st.selectbox("Select Product Category:", ["ESD", "CMF", "Transistor", "MOS", "SKY", "Zener", "PowerSwitch", "TVS", "Misc", "SDOthers"], key="details_category")

    # Get cached data
    df = get_cached_data(category)
    
    if df is None or df.empty:
        st.warning(f"No data available for {category} category")
        return
    
    # Product selection
    if category in ["MOS", "CMF", "Transistor", "SKY", "Zener", "PowerSwitch", "Misc", "SDOthers"]:
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
                    'Magnias Wafer P/N': product_data['Magnias Wafer P/N'].iloc[0] if 'Magnias Wafer P/N' in product_data.columns else 'N/A',
                }
                
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
        if st.button("🚪 Logout", type="secondary", width='stretch'):
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
            st.session_state.PowerSwitch_data = None
            st.session_state.Misc_data = None
            st.session_state.SDOthers_data = None
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
            PowerSwitch_count = len(st.session_state.PowerSwitch_data) if st.session_state.PowerSwitch_data is not None else 0
            Misc_count = len(st.session_state.Misc_data) if st.session_state.Misc_data is not None else 0
            SDOthers_count = len(st.session_state.SDOthers_data) if st.session_state.SDOthers_data is not None else 0
            tvs_count = len(st.session_state.tvs_data) if st.session_state.tvs_data is not None else 0

            st.write(f"ESD: {esd_count}")
            st.write(f"CMF: {cmf_count}")
            st.write(f"Transistor: {transistor_count}")
            st.write(f"MOS: {mos_count}")
            st.write(f"SKY: {sky_count}")
            st.write(f"Zener: {zener_count}")
            st.write(f"PowerSwitch: {PowerSwitch_count}")
            st.write(f"TVS: {tvs_count}")
            st.write(f"TVS: {Misc_count}")
            st.write(f"TVS: {SDOthers_count}")
            st.write(f"**Total: {esd_count + cmf_count + transistor_count + mos_count + sky_count + zener_count + PowerSwitch_count + tvs_count + Misc_count + SDOthers_count}**")
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
