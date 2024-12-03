import streamlit as st
import re
import requests
from bs4 import BeautifulSoup
import time

def validate_address(address):
    """Validate address format and return cleaned version"""
    address = address.lower().strip()
    pattern = r'^\d+\s+[a-zA-Z]+\s+(?:ave|st|rd|dr|ln|ct|pl|blvd|cir)$'
    if not re.match(pattern, address):
        return None
    return address

def search_property(address):
    """Search property using custom request sequence"""
    try:
        with st.spinner("Searching property records..."):
            # Create a session to maintain cookies
            session = requests.Session()
            
            # Headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://tax1.co.monmouth.nj.us',
                'DNT': '1',
            }
            
            # Use the NJ MOD-IV system instead
            base_url = "https://tax1.co.monmouth.nj.us/cgi-bin/prc6.cgi"
            
            # Initial parameters
            params = {
                'district': '0906',  # Jersey City
                'ms_user': 'monm' 
            }
            
            # Get initial page
            response = session.get(base_url, params=params, headers=headers)
            
            # Prepare search data
            search_data = {
                'district': '0906',
                'ms_user': 'monm',
                'address': address.upper(),
                'submit_search': 'Submit Search'
            }
            
            # Submit search
            response = session.post(base_url, data=search_data, headers=headers)
            
            # Parse response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for property details link
            detail_links = soup.find_all('a', href=True)
            property_url = None
            
            for link in detail_links:
                if 'DELAWARE' in link.text.upper():
                    property_url = 'https://tax1.co.monmouth.nj.us/cgi-bin/' + link['href']
                    break
            
            if property_url:
                return property_url
            
            # Add debugging information
            st.write("Debug: Response Status:", response.status_code)
            st.write("Debug: Response Content Preview:")
            st.code(response.text[:500])
            
            return None
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# UI Code remains the same
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
