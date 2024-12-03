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
    """Search property using Hudson County tax records"""
    try:
        session = requests.Session()
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://hudsoncp.envelope.com'
        }
        
        # Get the initial search page to establish session
        search_url = "https://hudsoncp.envelope.com/search"
        
        # Format the address for search
        search_address = address.upper()
        st.write("Debug: Searching for address:", search_address)
        
        # Prepare search data
        search_data = {
            'property_address': search_address,
            'city': 'JERSEY CITY',
            'state': 'NJ'
        }
        
        # Make the search request
        response = session.post(search_url, data=search_data, headers=headers)
        st.write("Debug: Response status:", response.status_code)
        
        # Parse the response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for property results
        results = soup.find_all('div', class_='property-result')
        st.write(f"Debug: Found {len(results)} property results")
        
        for result in results:
            result_text = result.get_text().strip()
            st.write("Debug: Result content preview:")
            st.code(result_text[:200])
            
            if address.upper() in result_text.upper():
                st.write("Debug: Found matching property")
                link = result.find('a')
                if link and 'href' in link.attrs:
                    return urllib.parse.urljoin(search_url, link['href'])
        
        # If we didn't find any matches, show response content
        st.write("Debug: Response content preview:")
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
                st.info("Note: You can also try searching directly on the [Hudson County Property Records](https://hudsoncp.envelope.com/search) website.")

st.markdown("---")
st.markdown("Made with Streamlit ❤️")
