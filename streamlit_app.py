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
    """Search property using NJ MOD-IV system"""
    try:
        session = requests.Session()
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Using the NJ MOD-IV system
        base_url = "https://njactb.org"
        search_url = f"{base_url}/mod4/search"
        
        # Prepare search data
        search_data = {
            'county': 'HUDSON',
            'town': 'JERSEY CITY',
            'street': address.upper(),
            'submit': 'Search'
        }
        
        st.write("Debug: Search parameters:", search_data)
        
        # Make the search request
        response = session.post(search_url, data=search_data, headers=headers)
        st.write("Debug: Response status:", response.status_code)
        
        if response.status_code == 200:
            # Parse the response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for property results table
            table = soup.find('table', class_='results')
            
            if table:
                st.write("Debug: Found results table")
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Skip header row
                    cells = row.find_all('td')
                    if cells and address.upper() in cells[2].text.upper():  # Address column
                        link = row.find('a')
                        if link and 'href' in link.attrs:
                            detail_url = urllib.parse.urljoin(base_url, link['href'])
                            return detail_url
            
            st.write("Debug: Response preview:")
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
    .info-box {
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Jersey City Property Lookup 🏠")

st.markdown("""
    ### Enter Property Address
    Format: number + street name + abbreviated type  
    Example: "192 olean ave" or "413 summit ave"
""")

# Add info box about data source
st.markdown("""
    <div class="info-box">
    This tool searches the New Jersey Property Tax Assessment Records system.
    Results include property details and assessment information.
    </div>
    """, unsafe_allow_html=True)

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
                st.info("Note: You can also search directly on the [NJ Property Tax Assessment Records](https://njactb.org) website.")

st.markdown("---")
st.markdown("Made with Streamlit ❤️")
