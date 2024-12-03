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
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://tax1.co.monmouth.nj.us',
            'Referer': 'https://tax1.co.monmouth.nj.us/cgi-bin/prc6.cgi'
        }
        
        # First request - get initial page and set up session
        base_url = "https://tax1.co.monmouth.nj.us/cgi-bin/prc6.cgi"
        initial_params = {
            'district': '0906',
            'ms_user': 'monm'
        }
        
        initial_response = session.get(base_url, params=initial_params, headers=headers)
        st.write("Debug: Initial response status:", initial_response.status_code)
        
        # Parse the initial page to get any hidden fields
        soup = BeautifulSoup(initial_response.text, 'html.parser')
        form = soup.find('form')
        
        # Prepare the search data
        search_data = {
            'district': '0906',
            'ms_user': 'monm',
            'type': '1',
            'adv': '0',
            'out_type': '0',
            'location': address.upper()
        }
        
        # Add any hidden fields from the form
        if form:
            for hidden in form.find_all('input', type='hidden'):
                if 'name' in hidden.attrs and 'value' in hidden.attrs:
                    search_data[hidden['name']] = hidden['value']
        
        # Submit the search
        st.write("Debug: Submitting search with parameters:", search_data)
        response = session.post(base_url, data=search_data, headers=headers, allow_redirects=True)
        st.write("Debug: Search response status:", response.status_code)
        
        # Parse the results
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for property link
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                for cell in cells:
                    if address.upper() in cell.text.upper():
                        link = row.find('a')
                        if link and 'href' in link.attrs:
                            detail_url = urllib.parse.urljoin(base_url, link['href'])
                            return detail_url
        
        # If we didn't find the property, show the response content
        st.write("Debug: Response Content Preview:")
        st.code(response.text[:500])
        
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
