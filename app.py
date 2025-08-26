def add_quote_to_sheet(currency, product_category, product_name, price, customer, distributor, quote_date):
    """Add a new quote to the appropriate Google Sheets tab (QuoteUSD or QuoteRMB)"""
    try:
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
            for i in range(1, 5):  # DC-1 to DC-4
                dc_col = f'DC-{i}'
                if pd.isna(matching_row.get(dc_col)) or matching_row.get(dc_col) == '':
                    # Found empty slot, update this column and corresponding date/customer
                    col_index_dc = list(existing_df.columns).index(dc_col) + 1  # +1 for gspread indexing
                    
                    # Find corresponding date and customer columns
                    date_col = f'Quote Date {i}'
                    if i == 3:
                        customer_col = f'End Customers {i}'  # Note: plural for column 3
                    elif i == 4:
                        customer_col = f'End Customers {i}'  # Note: plural for column 4  
                    else:
                        customer_col = f'End Customer {i}'   # Note: singular for columns 1 & 2
                    
                    try:
                        col_index_date = list(existing_df.columns).index(date_col) + 1
                        col_index_customer = list(existing_df.columns).index(customer_col) + 1
                    except ValueError:
                        # If column doesn't exist, try alternative naming
                        if i in [3, 4]:
                            customer_col = f'End Customer {i}'  # Try singular
                        else:
                            customer_col = f'End Customers {i}'  # Try plural
                        col_index_customer = list(existing_df.columns).index(customer_col) + 1
                    
                    # Update the cells (row_index + 2 because gspread is 1-indexed and row 1 is headers)
                    worksheet.update_cell(row_index + 2, col_index_dc, price)
                    worksheet.update_cell(row_index + 2, col_index_date, quote_date)
                    worksheet.update_cell(row_index + 2, col_index_customer, customer)
                    
                    return True, f"Quote added to existing product record in {dc_col}"
            
            return False, "All DC columns are filled for this product. Cannot add more quotes."
        
        else:
            # Create new row
            # Get headers from existing sheet to maintain structure
            if not existing_df.empty:
                headers = list(existing_df.columns)
            else:
                # Default headers structure for quote sheets
                headers = [
                    'Products', 'Product Name', 'Distributor',
                    'DC-1', 'Quote Date 1', 'End Customer 1',
                    'DC-2', 'Quote Date 2', 'End Customer 2', 
                    'DC-3', 'Quote Date 3', 'End Customers 3',
                    'DC-4', 'Quote Date 4', 'End Customers 4'
                ]
            
            # Create new row data
            new_row_data = [''] * len(headers)
            
            # Fill in the basic info
            if 'Products' in headers:
                new_row_data[headers.index('Products')] = product_category
            if 'Product Name' in headers:
                new_row_data[headers.index('Product Name')] = product_name
            if 'Distributor' in headers:
                new_row_data[headers.index('Distributor')] = distributor
            
            # Add the quote in DC-1
            if 'DC-1' in headers:
                new_row_data[headers.index('DC-1')] = price
            if 'Quote Date 1' in headers:
                new_row_data[headers.index('Quote Date 1')] = quote_date
            if 'End Customer 1' in headers:
                new_row_data[headers.index('End Customer 1')] = customer
            
            worksheet.append_row(new_row_data)
            return True, "New product quote record created"
            
    except Exception as e:
        return False, f"Error adding quote: {str(e)}"

def display_add_quote_form(category, product_name):
    """Display form to add a new quote"""
    st.subheader("➕ Add New Quote")
    
    with st.form("add_quote_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            currency = st.selectbox("Currency", ["USD", "RMB"], key="quote_currency")
            price = st.number_input("Price", min_value=0.0, step=0.01, key="quote_price")
            customer = st.text_input("End Customer", key="quote_customer")
        
        with col2:
            distributor = st.text_input("Distributor (optional)", key="quote_distributor")
            quote_date = st.date_input("Quote Date", value=datetime.now().date(), key="quote_date")
        
        submitted = st.form_submit_button("💰 Add Quote", type="primary")
        
        if submitted:
            if price > 0 and customer.strip():
                # Convert date to string format
                quote_date_str = quote_date.strftime('%Y-%m-%d')
                
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
    
    # Enhanced Latest Quotes and Quote Management section - only show if there's a search term and not "All Products"
    if search_term and category != "All Products":
        st.markdown("---")
        
        # Two columns for Latest Quotes and Add Quote
        col1, col2 = st.columns([2, 1])
        
        with col1:
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
                
                # Display quotes in a table format
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
        
        with col2:
            # Show Add Quote form only for authenticated users
            if st.session_state.get('authenticated', False):
                display_add_quote_form(category, product_name_for_quotes)
            else:
                st.info("Please log in to add quotes")
                
    elif search_term and category == "All Products":
        st.info("💡 Latest Quotes and Quote Management are only available when searching within a specific product category.")
