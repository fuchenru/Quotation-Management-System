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

if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.esd_data = None
    st.session_state.cmf_data = None
    st.session_state.transistor_data = None
    st.session_state.mos_data = None
    st.session_state.last_refresh = None
    st.session_state.sky_data = None

def authenticate_user(username, password):
    """Authenticate user with credentials from secrets"""
    try:
        # Get credentials from secrets
        auth_username = st.secrets["auth"]["username"]
        auth_password = st.secrets["auth"]["password"]
        
        return username == auth_username and password == auth_password
    except KeyError:
        st.error("Authentication credentials not configured in secrets. Please check your secrets.toml file.")
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
    st.session_state.data_loaded = False
    st.session_state.esd_data = None
    st.session_state.cmf_data = None
    st.session_state.transistor_data = None
    st.session_state.mos_data = None
    st.session_state.last_refresh = None
    st.session_state.sky_data = None
    st.rerun()

def load_google_sheet(worksheet_name):
    """Load data from specific Google Sheets worksheet"""
    try:
        # Use Streamlit secrets instead of connections.toml
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
            'Wafer Supplier', 'Wafer Supplier Material Name', 'Magnias Wafer P/N', 'Wafer Price (RMB)',
            'Finished product supplier', 'Finished Product Supplier Material Name', 'Finished Product Price (RMB)', 'Finished Product Price (USD)',
            'Quote Date', 'Product Name', 'Package', 'POD Type', 'VrwmMAX(V)', 'VBR MIN(V)',
            'CJTYP(pF)', 'CJMAX(pF)', 'CH', 'Direction', 'ESDC(kV)', 'ESDA(kV)',
            'Ipp8/20,2Ω(A)', 'Ppk(W)', 'VCTYP (V)', 'MPQ',
            'Distributor RMB Price', 'Distributor USD Price', 'Notes'
        ]
    elif category == "CMF":
        return [
            'Quote Date', 'Magnias P/N', 'FG Supplier', 'FG Supplier P/N', 'Distributor RMB Price', 'Distributor USD Price', 'Notes'
        ]
    elif category == "Transistor":
        return [
            'Quote Date', 'Magnias P/N', 'Package', 'FG Supplier', 'FG Supplier P/N', 'Distributor RMB Price', 'Distributor USD Price', 'Polarity', 'Notes'
        ]
    elif category == "MOS":
        return [
            'Quote Date', 'Magnias P/N', 'Package', 'Type', 'VDS (V)', 'ID (A)', 'FG Supplier', 'FG Supplier P/N',
            'Distributor RMB Price', 'Distributor USD Price', 'Wafer Supplier', 'Wafer Supplier P/N', 'Magnias Wafer P/N', 'Wafer Price (RMB)'
        ]
    elif category == "SKY":
        return [
            'Quote Date', 'Magnias P/N', 'FG Supplier', 'FG Supplier P/N', 'Distributor RMB Price', 'Distributor USD Price', 'Notes', 'IF (mA)',
            'IFSM (A)',	'VRRM (V)',	'Vf @ If= 1mA'
        ]
    return []

def display_data_management():
    """Display data management interface for CRUD operations"""
    st.title("⚙️ Data Management")
    st.markdown("---")
    
    # Category selection
    category = st.selectbox("Select Product Category:", ["ESD", "CMF", "Transistor", "MOS", "SKY"], key="mgmt_category")
    
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
            if category in ["MOS", "CMF", "Transistor", "SKY"]:  # Added Transistor here
                form_data['Magnias P/N'] = st.text_input("Magnias P/N*", key="add_magnias_pn")
                if category == "MOS":
                    form_data['Package'] = st.text_input("Package", key="add_package")
                    form_data['Type'] = st.selectbox("Type", ["N-Channel", "P-Channel", "Enhancement", "Depletion", "N/A"], key="add_mos_type")
                elif category == "Transistor":
                    form_data['Package'] = st.text_input("Package", key="add_package")
                    form_data['Polarity'] = st.selectbox("Polarity", ["NPN", "PNP", "N/A"], key="add_polarity")
            else:
                form_data['Product Name'] = st.text_input("Product Name*", key="add_product_name")
                form_data['Package'] = st.text_input("Package", key="add_package")
                
                if category == "ESD":
                    form_data['POD Type'] = st.text_input("POD Type", key="add_pod_type")
        
        with col2:
            if category in ["MOS", "CMF", "Transistor", "SKY"]:  # Added Transistor here
                form_data['FG Supplier'] = st.text_input("FG Supplier", key="add_fg_supplier")
                form_data['FG Supplier P/N'] = st.text_input("FG Supplier P/N", key="add_fg_supplier_pn")
            else:
                form_data['Wafer Supplier'] = st.text_input("Wafer Supplier", key="add_wafer_supplier")
                form_data['Wafer Supplier Material Name'] = st.text_input("Wafer Supplier Material Name", key="add_wafer_material")
                form_data['MPQ'] = st.number_input("MPQ", min_value=0, step=1, key="add_mpq")
        
        # Remove the Technical Specifications section for Transistor since it's now simplified
        # Only show Technical Specifications for ESD and MOS
        if category in ["ESD", "MOS"]:
            st.markdown("**Technical Specifications**")
            
            # Category-specific technical fields (keep existing ESD, MOS logic, remove Transistor)
            if category == "ESD":
                col1, col2, col3 = st.columns(3)
                with col1:
                    form_data['VrwmMAX(V)'] = st.number_input("VrwmMAX(V)", step=0.1, key="add_vrwm")
                    form_data['VBR MIN(V)'] = st.number_input("VBR MIN(V)", step=0.1, key="add_vbr")
                    form_data['CJTYP(pF)'] = st.number_input("CJTYP(pF)", step=0.1, key="add_cjtyp")
                with col2:
                    form_data['CJMAX(pF)'] = st.number_input("CJMAX(pF)", step=0.1, key="add_cjmax")
                    form_data['CH'] = st.number_input("CH", step=1, key="add_ch")
                    form_data['Direction'] = st.selectbox("Direction", ["Uni", "Bi", "N/A"], key="add_direction")
                with col3:
                    form_data['ESDC(kV)'] = st.number_input("ESDC(kV)", step=0.1, key="add_esdc")
                    form_data['ESDA(kV)'] = st.number_input("ESDA(kV)", step=0.1, key="add_esda")
                    form_data['VCTYP (V)'] = st.number_input("VCTYP (V)", step=0.1, key="add_vctyp")
                
                col1, col2 = st.columns(2)
                with col1:
                    form_data['Ipp8/20,2Ω(A)'] = st.number_input("Ipp8/20,2Ω(A)", step=0.1, key="add_ipp")
                with col2:
                    form_data['Ppk(W)'] = st.number_input("Ppk(W)", step=0.1, key="add_ppk")
                    
            elif category == "MOS":
                col1, col2 = st.columns(2)
                with col1:
                    form_data['VDS (V)'] = st.number_input("VDS (V)", step=0.1, key="add_vds")
                with col2:
                    form_data['ID (A)'] = st.number_input("ID (A)", step=0.1, key="add_id")
        
        st.markdown("**Pricing Information**")
        col1, col2 = st.columns(2)
        with col1:
            if category not in ["MOS", "CMF", "Transistor", "SKY"]:  # Added Transistor here
                form_data['Finished Product Price (RMB)'] = st.number_input("Finished Product Price (RMB)", step=0.01, key="add_price_rmb")
            form_data['Distributor RMB Price'] = st.number_input("Distributor RMB Price", step=0.01, key="add_dist_rmb")
        with col2:
            if category not in ["MOS", "CMF", "Transistor", "SKY"]:  # Added Transistor here
                form_data['Finished Product Price (USD)'] = st.number_input("Finished Product Price (USD)", step=0.01, key="add_price_usd")
            form_data['Distributor USD Price'] = st.number_input("Distributor USD Price", step=0.01, key="add_dist_usd")
        
        # Additional fields - only for ESD and MOS
        if category == "ESD":
            form_data['Magnias Wafer P/N'] = st.text_input("Magnias Wafer P/N", key="add_wafer_pn")
            form_data['Wafer Price (RMB)'] = st.number_input("Wafer Price (RMB)", step=0.01, key="add_wafer_price")
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
            required_field = 'Magnias P/N' if category in ["MOS", "CMF", "Transistor", "SKY"] else 'Product Name'  # Added Transistor
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
    else:
        return None

def get_price_recommendations(df, product_name, price_column):
    """Get price recommendations based on historical data"""
    if df is None or df.empty:
        return None
    
    # For MOS category, search by Magnias P/N instead of Product Name
    search_column = 'Magnias P/N' if 'Magnias P/N' in df.columns else 'Product Name'
    
    # Filter by product name (case insensitive)
    product_data = df[df[search_column].str.contains(product_name, case=False, na=False)]
    
    if product_data.empty:
        return None
    
    # Calculate price statistics
    prices = pd.to_numeric(product_data[price_column], errors='coerce').dropna()
    
    if prices.empty:
        return None
    
    return {
        'count': len(prices),
        'min_price': prices.min(),
        'max_price': prices.max(),
        'avg_price': prices.mean(),
        'median_price': prices.median(),
        'latest_price': prices.iloc[-1] if len(prices) > 0 else None,
        'latest_date': product_data['Quote Date'].max() if 'Quote Date' in product_data.columns else None
    }

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
    
    # Dashboard metrics
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
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
    
    with col5:
        sky_count = len(sky_data) if mos_data is not None else 0
        st.metric("SKY Products", sky_count)

    with col6:
        total_count = esd_count + cmf_count + transistor_count + mos_count
        st.metric("Total Products", total_count)
    
    # Recent activity chart
    if any([esd_data is not None and not esd_data.empty, 
            cmf_data is not None and not cmf_data.empty, 
            transistor_data is not None and not transistor_data.empty,
            mos_data is not None and not mos_data.empty,
            sky_data is not None and not sky_data.empty,]):
        
        st.subheader("📈 Recent Quotation Activity")
        
        # Combine recent data
        recent_data = []
        for name, data in [("ESD", esd_data), ("CMF", cmf_data), ("Transistor", transistor_data), ("MOS", mos_data), ("SKY", sky_data)]:
            if data is not None and not data.empty and 'Quote Date' in data.columns:
                data_with_type = data.copy()
                data_with_type['Product Type'] = name
                recent_data.append(data_with_type[['Quote Date', 'Product Type']])
        
        if recent_data:
            combined_data = pd.concat(recent_data, ignore_index=True)
            combined_data['Quote Date'] = pd.to_datetime(combined_data['Quote Date'], errors='coerce')
            combined_data = combined_data.dropna(subset=['Quote Date'])
            
            if not combined_data.empty:
                # Group by date and product type
                daily_counts = combined_data.groupby([combined_data['Quote Date'].dt.date, 'Product Type']).size().reset_index(name='Count')
                daily_counts['Quote Date'] = pd.to_datetime(daily_counts['Quote Date'])
                
                fig = px.line(daily_counts, x='Quote Date', y='Count', color='Product Type',
                             title="Daily Quotation Activity by Product Type")
                st.plotly_chart(fig, use_container_width=True)

def display_price_lookup():
    """Display price lookup interface"""
    st.title("🔍 Price Lookup & Recommendations")
    st.markdown("---")
    
    # Product category selection
    category = st.selectbox("Select Product Category:", ["ESD", "CMF", "Transistor", "MOS", "SKY"])
    
    # Get cached data
    df = get_cached_data(category)
    
    if df is None or df.empty:
        st.warning(f"No data available for {category} category")
        return
    
    # Search functionality
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_label = "🔍 Search Magnias P/N:" if category in ["MOS", "CMF", "Transistor", "SKY"] else "🔍 Search Product Name:"  # Added Transistor
        search_placeholder = "Enter Magnias P/N" if category in ["MOS", "CMF", "Transistor", "SKY"] else "Enter product name or part number"  # Added Transistor
        search_term = st.text_input(search_label, placeholder=search_placeholder)
    
    with col2:
        st.write("")  # Spacing
        show_all = st.checkbox("Show All Products", value=False)
    
    # Filter data based on search
    if search_term and not show_all:
        # Try to find in Product Name or Magnias P/N columns
        if category in ["MOS", "CMF", "Transistor", "SKY"]:  # Added Transistor
            search_column = 'Magnias P/N'
        else:
            search_column = 'Product Name' if 'Product Name' in df.columns else 'Product'
        
        filtered_df = df[df[search_column].str.contains(search_term, case=False, na=False)]
        
        if filtered_df.empty:
            st.warning(f"No products found matching '{search_term}'")
            return
    elif show_all:
        filtered_df = df
    else:
        st.info("Enter a search term or check 'Show All Products' to view data")
        return
    
    # Display results
    st.subheader(f"📋 {category} Products")
    
    # Key columns to display
    if category in ["MOS", "CMF", "Transistor", "SKY"]:  # Added Transistor
        if category == "MOS":
            display_columns = ['Magnias P/N', 'Package', 'FG Supplier', 'FG Supplier P/N', 'Wafer Supplier', 'Wafer Supplier P/N',
                              'Magnias Wafer P/N', 'Distributor RMB Price', 'Distributor USD Price', 'Quote Date']
        elif category == "Transistor":
            display_columns = ['Magnias P/N', 'Package', 'FG Supplier', 'FG Supplier P/N', 'Polarity', 'Distributor RMB Price', 'Distributor USD Price', 'Quote Date']
        elif category == "CMF":  # CMF
            display_columns = ['Magnias P/N', 'FG Supplier', 'FG Supplier P/N', 'Distributor RMB Price', 'Distributor USD Price', 'Quote Date']
        else:
            display_columns = ['Magnias P/N', 'FG Supplier', 'FG Supplier P/N', 'Distributor RMB Price', 'Distributor USD Price', 'Quote Date']
    else:
        display_columns = ['Product Name' if 'Product Name' in df.columns else 'Product',  
                          'Finished Product Price (RMB)', 'Finished Product Price (USD)', 
                          'Distributor RMB Price', 'Distributor USD Price', 'Quote Date']
    
    display_columns = [col for col in display_columns if col in df.columns]
    
    st.dataframe(filtered_df[display_columns], use_container_width=True)
    
    # Price recommendations for searched product
    if search_term and not filtered_df.empty:
        st.subheader("💰 Latest Quote")
        
        recommendations_rmb = get_price_recommendations(df, search_term, 'Distributor RMB Price')
        recommendations_usd = get_price_recommendations(df, search_term, 'Distributor USD Price')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**RMB:**")
            if recommendations_rmb:
                st.write(f"- Historical quotes: {recommendations_rmb['count']}")
                if recommendations_rmb['latest_date']:
                    st.write(f"- Latest quote: ¥{recommendations_rmb['latest_price']:.4f} ({recommendations_rmb['latest_date'].strftime('%Y-%m-%d')})")
            else:
                st.write("No RMB price data available")
        
        with col2:
            st.write("**USD:**")
            if recommendations_usd:
                st.write(f"- Historical quotes: {recommendations_usd['count']}")
                if recommendations_usd['latest_date']:
                    st.write(f"- Latest quote: ${recommendations_usd['latest_price']:.4f} ({recommendations_usd['latest_date'].strftime('%Y-%m-%d')})")
            else:
                st.write("No USD price data available")

def display_product_details():
    """Display detailed product information"""
    st.title("📋 Product Details & Specifications")
    st.markdown("---")
    
    # Category and product selection
    category = st.selectbox("Select Product Category:", ["ESD", "CMF", "Transistor", "MOS", "SKY"], key="details_category")
    
    # Get cached data
    df = get_cached_data(category)
    
    if df is None or df.empty:
        st.warning(f"No data available for {category} category")
        return
    
    # Product selection
    if category in ["MOS", "CMF", "Transistor", "SKY"]:  # Added Transistor
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
            # Display product specifications
            st.subheader(f"🔧 {selected_product} Specifications")
            
            # Technical specifications (category-specific)
            tech_specs = {}
            
            if category == "ESD":
                tech_specs = {
                    'Package': product_data['Package'].iloc[0] if 'Package' in product_data.columns else 'N/A',
                    'POD Type': product_data['POD Type'].iloc[0] if 'POD Type' in product_data.columns else 'N/A',
                    'VrwmMAX(V)': product_data['VrwmMAX(V)'].iloc[0] if 'VrwmMAX(V)' in product_data.columns else 'N/A',
                    'VBR MIN(V)': product_data['VBR MIN(V)'].iloc[0] if 'VBR MIN(V)' in product_data.columns else 'N/A',
                    'CJTYP(pF)': product_data['CJTYP(pF)'].iloc[0] if 'CJTYP(pF)' in product_data.columns else 'N/A',
                    'CJMAX(pF)': product_data['CJMAX(pF)'].iloc[0] if 'CJMAX(pF)' in product_data.columns else 'N/A',
                    'CH': product_data['CH'].iloc[0] if 'CH' in product_data.columns else 'N/A',
                    'Direction': product_data['Direction'].iloc[0] if 'Direction' in product_data.columns else 'N/A',
                    'ESDC(kV)': product_data['ESDC(kV)'].iloc[0] if 'ESDC(kV)' in product_data.columns else 'N/A',
                    'ESDA(kV)': product_data['ESDA(kV)'].iloc[0] if 'ESDA(kV)' in product_data.columns else 'N/A',
                    'Ipp8/20,2Ω(A)': product_data['Ipp8/20,2Ω(A)'].iloc[0] if 'Ipp8/20,2Ω(A)' in product_data.columns else 'N/A',
                    'Ppk(W)': product_data['Ppk(W)'].iloc[0] if 'Ppk(W)' in product_data.columns else 'N/A',
                    'VCTYP (V)': product_data['VCTYP (V)'].iloc[0] if 'VCTYP (V)' in product_data.columns else 'N/A',
                    'MPQ': product_data['MPQ'].iloc[0] if 'MPQ' in product_data.columns else 'N/A',
                }
            elif category in ["CMF", "Transistor"]:  # Combined CMF and Transistor logic
                # Both now have minimal specs - show basic info
                latest_date = product_data['Quote Date'].max() if 'Quote Date' in product_data.columns else 'N/A'
                # Convert timestamp to string if it's not 'N/A'
                if latest_date != 'N/A' and latest_date is not None:
                    latest_date = latest_date.strftime('%Y-%m-%d')
                
                tech_specs = {
                    'Magnias P/N': selected_product,
                    'Latest Quote Date': latest_date,
                }
                
                # Add package and polarity for Transistor
                if category == "Transistor":
                    tech_specs['Package'] = product_data['Package'].iloc[0] if 'Package' in product_data.columns else 'N/A'
                    tech_specs['Polarity'] = product_data['Polarity'].iloc[0] if 'Polarity' in product_data.columns else 'N/A'
                    
            elif category == "MOS":
                tech_specs = {
                    'Package': product_data['Package'].iloc[0] if 'Package' in product_data.columns else 'N/A',
                    'Type': product_data['Type'].iloc[0] if 'Type' in product_data.columns else 'N/A',
                    'VDS (V)': product_data['VDS (V)'].iloc[0] if 'VDS (V)' in product_data.columns else 'N/A',
                    'ID (A)': product_data['ID (A)'].iloc[0] if 'ID (A)' in product_data.columns else 'N/A',
                }
            elif category == "SKY":
                tech_specs = {
                    'IF (mA)': product_data['IF (mA)'].iloc[0] if 'IF (mA)' in product_data.columns else 'N/A',
                    'IFSM (A)': product_data['IFSM (A)'].iloc[0] if 'IFSM (A)' in product_data.columns else 'N/A',
                    'VRRM (V)': product_data['VRRM (V)'].iloc[0] if 'VRRM (V)' in product_data.columns else 'N/A',
                    'Vf @ If= 1mA': product_data['Vf @ If= 1mA'].iloc[0] if 'Vf @ If= 1mA' in product_data.columns else 'N/A',
                }
            
            # Display specifications in columns
            cols = st.columns(3)
            for i, (key, value) in enumerate(tech_specs.items()):
                with cols[i % 3]:
                    st.metric(key, value)
            
            # For CMF and Transistor, show FG Supplier info instead of wafer supplier
            if category in ["CMF", "Transistor", "SKY"]:  # Added Transistor
                st.subheader("🏪 FG Supplier Information")
                fg_specs = {
                    'FG Supplier': product_data['FG Supplier'].iloc[0] if 'FG Supplier' in product_data.columns else 'N/A',
                    'FG Supplier P/N': product_data['FG Supplier P/N'].iloc[0] if 'FG Supplier P/N' in product_data.columns else 'N/A',
                }
                
                # Display FG supplier specifications in columns
                cols = st.columns(3)
                for i, (key, value) in enumerate(fg_specs.items()):
                    with cols[i % 3]:
                        st.metric(key, value)
            else:
                # Wafer supplier information for ESD and MOS
                st.subheader("📟 Wafer Supplier")
                wafer_specs = {}
                
                if category == "ESD":
                    wafer_specs = {
                        'Wafer Supplier': product_data['Wafer Supplier'].iloc[0] if 'Wafer Supplier' in product_data.columns else 'N/A',
                        'Wafer Supplier Material Name': product_data['Wafer Supplier Material Name'].iloc[0] if 'Wafer Supplier Material Name' in product_data.columns else 'N/A',
                        'Magnias Wafer P/N': product_data['Magnias Wafer P/N'].iloc[0] if 'Magnias Wafer P/N' in product_data.columns else 'N/A',
                        'Wafer Price (RMB)': product_data['Wafer Price (RMB)'].iloc[0] if 'Wafer Price (RMB)' in product_data.columns else 'N/A',
                    }
                elif category == "MOS":
                    wafer_specs = {
                        'Wafer Supplier': product_data['Wafer Supplier'].iloc[0] if 'Wafer Supplier' in product_data.columns else 'N/A',
                        'Wafer Supplier P/N': product_data['Wafer Supplier P/N'].iloc[0] if 'Wafer Supplier P/N' in product_data.columns else 'N/A',
                        'Magnias Wafer P/N': product_data['Magnias Wafer P/N'].iloc[0] if 'Magnias Wafer P/N' in product_data.columns else 'N/A',
                        'Wafer Price (RMB)': product_data['Wafer Price (RMB)'].iloc[0] if 'Wafer Price (RMB)' in product_data.columns else 'N/A',
                    }
                
                # Display wafer specifications in columns
                if wafer_specs:
                    cols = st.columns(3)
                    for i, (key, value) in enumerate(wafer_specs.items()):
                        with cols[i % 3]:
                            st.metric(key, value)

                # Show MOS distributor info separately since it still has FG Supplier
                if category == "MOS":
                    st.subheader("🏪 Distributor Information")
                    dis_specs = {
                        'FG Supplier': product_data['FG Supplier'].iloc[0] if 'FG Supplier' in product_data.columns else 'N/A',
                        'FG Supplier P/N': product_data['FG Supplier P/N'].iloc[0] if 'FG Supplier P/N' in product_data.columns else 'N/A',
                    }
                    
                    # Display distributor specifications in columns
                    cols = st.columns(3)
                    for i, (key, value) in enumerate(dis_specs.items()):
                        with cols[i % 3]:
                            st.metric(key, value)

            # Quotation history
            st.subheader("📈 Quotation History")
            
            # Display historical data
            if category in ["MOS", "CMF", "Transistor", "SKY"]:  # Added Transistor
                history_columns = ['Quote Date', 'Distributor RMB Price', 'Distributor USD Price', 'Notes']
            else:
                history_columns = ['Quote Date', 'Finished Product Price (RMB)', 'Finished Product Price (USD)', 
                                 'Distributor RMB Price', 'Distributor USD Price', 'MPQ', 'Notes']
            
            history_columns = [col for col in history_columns if col in product_data.columns]
            
            st.dataframe(product_data[history_columns], use_container_width=True)
            
            # Price trend chart
            if len(product_data) > 1 and 'Quote Date' in product_data.columns:
                product_data_sorted = product_data.sort_values('Quote Date')
                
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                
                # RMB prices
                if 'Distributor RMB Price' in product_data.columns:
                    rmb_prices = pd.to_numeric(product_data_sorted['Distributor RMB Price'], errors='coerce')
                    fig.add_trace(
                        go.Scatter(x=product_data_sorted['Quote Date'], y=rmb_prices, 
                                  name="RMB Price", line=dict(color="blue")),
                        secondary_y=False,
                    )
                
                # USD prices
                if 'Distributor USD Price' in product_data.columns:
                    usd_prices = pd.to_numeric(product_data_sorted['Distributor USD Price'], errors='coerce')
                    fig.add_trace(
                        go.Scatter(x=product_data_sorted['Quote Date'], y=usd_prices, 
                                  name="USD Price", line=dict(color="red")),
                        secondary_y=True,
                    )
                
                fig.update_xaxes(title_text="Date")
                fig.update_yaxes(title_text="Price (RMB)", secondary_y=False)
                fig.update_yaxes(title_text="Price (USD)", secondary_y=True)
                fig.update_layout(title_text=f"{selected_product} - Distributor Price Trend")
                
                st.plotly_chart(fig, use_container_width=True)

def authenticated_main():
    """Main application function for authenticated users"""
    
    # Sidebar navigation
    with st.sidebar:
        st.sidebar.image("https://i.postimg.cc/j5G8ytbC/cropped-logo.png")
        st.header("Navigation")
        
        # Add logout button at the top
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            logout()
        
        st.markdown("---")
        
        page = st.radio("Select Page:", 
                       ["Dashboard", "Price Lookup", "Product Details", "Data Management"])
        
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
            
            st.write(f"ESD: {esd_count}")
            st.write(f"CMF: {cmf_count}")
            st.write(f"Transistor: {transistor_count}")
            st.write(f"MOS: {mos_count}")
            st.write(f"SKY: {sky_count}")
            st.write(f"**Total: {esd_count + cmf_count + transistor_count + mos_count + sky_count}**")
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
        display_data_management()

def main():
    """Main application function with authentication check"""
    
    # Check if user is authenticated
    if not st.session_state.authenticated:
        login_page()
    else:
        authenticated_main()

if __name__ == "__main__":
    main()
