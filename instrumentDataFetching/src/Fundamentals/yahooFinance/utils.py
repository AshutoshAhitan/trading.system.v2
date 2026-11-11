from datetime import datetime
import logging

def convert_to_datetime(date_time_str):
    # Correct the format by adding a space between PM and IST
    if "PMIST" in date_time_str:
        date_time_str = date_time_str.replace("PMIST", "PM IST")
    elif "AMIST" in date_time_str:
        date_time_str = date_time_str.replace("AMIST", "AM IST")
    
    # Define the format string
    format_str = "%b %d, %Y, %I %p %Z"
    
    # Convert to datetime object
    dt = datetime.strptime(date_time_str, format_str)
    
    return dt

def get_indices(items, intrested_item):
    indices = []
    for index, item in enumerate(items):
        if item == intrested_item:
            indices.append(index)

    indices = sorted(indices)
    logging.debug(f'indices : {indices}')

    return indices


def get_financial_quarter(date_str: str) -> str:
    # Parse the input string into a datetime object
    date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    
    # Extract the month from the datetime object
    month = date.month
    
    # Determine the financial quarter and last month of the quarter
    if 1 <= month <= 3:
        quarter_end_month = "Mar"
    elif 4 <= month <= 6:
        quarter_end_month = "Jun"
    elif 7 <= month <= 9:
        quarter_end_month = "Sep"
    else:
        quarter_end_month = "Dec"
    
    # Return the year and the last month of the quarter
    return f"{date.year} {quarter_end_month}"

