import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import base64

def scrape_tables(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        tables = soup.find_all("table")
        table_data = []

        for table in tables:
            table_rows = table.find_all("tr")
            table_rows_data = []

            for row in table_rows:
                row_data = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
                table_rows_data.append(row_data)

            if table_rows_data:
                table_data.append(table_rows_data)

        return table_data

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        return []

st.title("Table Scraping and Download App")
st.write("Enter a URL to scrape tables from a webpage.")

url = st.text_input("Enter a URL:", "https://en.wikipedia.org/wiki/Table_(information)")
submit_button = st.button("Scrape Tables")

if submit_button:
    table_data = scrape_tables(url)
    if table_data:
        for table_index, table_rows_data in enumerate(table_data, start=1):
            st.write(f"Table {table_index}:")
            if table_rows_data:
                max_columns = max(len(row) for row in table_rows_data)
                padded_rows_data = [row + [""] * (max_columns - len(row)) for row in table_rows_data]
                header_row = padded_rows_data[0]
                cleaned_header_row = [header for header in header_row if header]
                num_columns = len(cleaned_header_row)
                
                # Filter rows with matching column count
                valid_rows_data = [row for row in padded_rows_data[1:] if len(row) == num_columns]
                
                df = pd.DataFrame(valid_rows_data, columns=cleaned_header_row)
                st.write(df)

                csv_filename = f"table_{table_index}.csv"
                csv_data = df.to_csv(index=False).encode()
                b64_csv = base64.b64encode(csv_data).decode()
                st.markdown(f"Download [Table {table_index} as CSV](data:file/csv;base64,{b64_csv})",
                            unsafe_allow_html=True)
