import streamlit as st
import re
import requests
from bs4 import BeautifulSoup
import urllib.parse
import json

def validate_address(address):
    """Validate address format and return cleaned version"""
    address = address.lower().strip()
    pattern = r'^\d+\s+[a-zA-Z]+\s+(?:ave|st|rd|dr|ln|ct|pl|blvd|cir)$'
    if not re.match(pattern, address):
        return None
    return address

def search_property(address):
    """Search property using requests"""
    try:
        session = requests.Session()
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Base URL for the tax assessment system
        base_url = "https://tax1.co.monmouth.nj.us/cgi-bin/prc6.cgi"
        
        # First, get initial form page
        params = {
            'district': '0906',
            'ms_user': 'monm'
        }
        
        initial_response = session.get(base_url, params=params)
        st.write("Debug: Initial response status:", initial_response.status_code)
        
        # Now prepare form data for search
        search_data = {
            'district': '0906',
            'ms_user': 'monm',
            'srch_type': '1',
            'out_type': '0',
            'adv': '1',
            'location': address.upper()
        }
        
        # Add debug information
        st.write("Debug: Submitting search with data:", json.dumps(search_data, indent=2))
        
        # Submit the search form
        response = session.post(
            base_url,
            data=search_data,
            headers=headers,
            allow_redirects=True
        )
        
        st.write("Debug: Search response status:", response.status_code)
        st.write("Debug: Final URL:", response.url)
        
        # Parse the response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for tables that might contain our results
        tables = soup.find_all('table')
        st.write(f"Debug: Found {len(tables)} tables")
        
        for idx, table in enumerate(tables):
            st.write(f"Debug: Checking table {idx + 1}")
            table_text = table.get_text()
            if 'DELAWARE' in table_text.upper():
                st.write("Debug: Found table with property information")
                # Look for property link
                links = table.find_all('a')
                for link in links:
                    if link.text.strip() == 'More Info':
                        detail_url = urllib.parse.urljoin(base_url, link['href'])
                        return detail_url
        
        # If we get here, we didn't find the property
        st.write("Debug: Response Content Preview:")
        st.code(response.text[:1000])
        return None
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# UI Code
st.set_page_config(
    page_title="Jersey City Property Lookup",
    page_icon="🏠",
    layout="centered"
)

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 12px 0;
        font-size: 16px;
    }
    .stTextInput>div>div>input {
        font-size: 16px;
        padding: 8px 12px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Jersey City Property Lookup 🏠")

st.markdown("""
    ### Enter Property Address
    Format: number + street name + abbreviated type  
    Example: "192 olean ave" or "413 summit ave"
""")

address = st.text_input("Property Address:", key="address_input")

if st.button("Find Property Details"):
    if not address:
        st.error("Please enter an address")
    else:
        clean_address = validate_address(address)
        if not clean_address:
            st.error("Please enter address in correct format: number + street name + abbreviated type (ave, st, rd, etc.)")
        else:
            result_url = search_property(clean_address)
            if result_url:
                st.success("Property found! Click below to view details:")
                st.markdown(f"[View Property Details]({result_url})", unsafe_allow_html=True)
            else:
                st.error("Property not found or an error occurred. Please check the address and try again.")

st.markdown("---")
st.markdown("Made with Streamlit ❤️")
