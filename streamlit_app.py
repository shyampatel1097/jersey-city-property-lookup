import streamlit as st
import re
import requests
from bs4 import BeautifulSoup
import urllib.parse

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
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://tax1.co.monmouth.nj.us/cgi-bin/prc6.cgi'
        }
        
        # Construct search URL based on the JavaScript in the page
        search_params = {
            'ms_user': 'monm',
            'passwd': '',
            'srch_type': '1',
            'out_type': '0',
            'district': '0906',
            'adv': '1',
            'location': address.upper(),
            'Submit': 'Submit+Search'
        }
        
        # Format the search URL
        base_url = "https://tax1.co.monmouth.nj.us/cgi-bin/prc6.cgi"
        search_url = f"{base_url}?{urllib.parse.urlencode(search_params)}"
        
        st.write("Debug: Search URL:", search_url)
        
        # Make the request
        response = session.get(search_url, headers=headers)
        st.write("Debug: Response status:", response.status_code)
        
        # Parse the response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for tables
        tables = soup.find_all('table')
        st.write(f"Debug: Found {len(tables)} tables")
        
        # Print the text content of each table for debugging
        for i, table in enumerate(tables):
            st.write(f"Debug: Table {i+1} content preview:")
            table_text = table.get_text().strip()
            st.code(table_text[:200])
            
            # Check if this table has our address
            if address.upper() in table_text.upper():
                st.write(f"Debug: Found address in table {i+1}")
                # Look for More Info link in this table
                links = table.find_all('a')
                for link in links:
                    if 'More Info' in link.text:
                        detail_url = urllib.parse.urljoin(base_url, link['href'])
                        return detail_url
        
        # If we get here, we didn't find the property
        st.write("Debug: Full page content preview:")
        st.code(response.text[:1000])
        
        return None
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Debug: Full error details:", str(e))
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
