import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time


# Replace with your OpenWeatherMap API key and email credentials
api_key = '62a3e70737f126f675dfa3da70dadcf2'
sender_email = 'jobmanzano104@gmail.com'
receiver_email = 'jobmanzano104@gmail.com'
password = 'aoby jhnk loag mvqq'

# Coordinates for Anulid, Alcala, Pangasinan
latitude = 15.8256
longitude = 120.4865

def get_weather():
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        location = data['name']
        temperature = data['main']['temp']
        weather_description = data['weather'][0]['description']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        
        # Format weather information as an HTML table
        weather_info = f"""
        <table border="1">
            <tr><th colspan="2">Weather Information</th></tr>
            <tr><td>Location</td><td>{location}</td></tr>
            <tr><td>Temperature</td><td>{temperature}°C</td></tr>
            <tr><td>Weather</td><td>{weather_description.capitalize()}</td></tr>
            <tr><td>Humidity</td><td>{humidity}%</td></tr>
            <tr><td>Wind Speed</td><td>{wind_speed} m/s</td></tr>
        </table>
        """
        return weather_info
    else:
        return f"Error: Unable to fetch data (Status code: {response.status_code})"

def get_pagasa_typhoon_alerts():
    url = "https://www.pagasa.dost.gov.ph/tropical-cyclone/severe-weather-bulletin"
    response = requests.get(url)
    typhoon_alerts = ""
    areas_under_signals = ""

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        alerts = soup.find_all('div', class_='alert')
        for alert in alerts:
            title = alert.find('h3').get_text(strip=True) if alert.find('h3') else "Typhoon Alert"
            details = alert.find('p').get_text(strip=True) if alert.find('p') else "Details unavailable"
            typhoon_alerts += f"<tr><td>{title}</td><td>{details}</td></tr>"

        signals_section = soup.find_all('div', class_='signal')
        for signal in signals_section:
            signal_level = signal.find('h4').get_text(strip=True) if signal.find('h4') else "Unknown Signal"
            areas = signal.find('ul').get_text(separator=', ', strip=True) if signal.find('ul') else "No areas listed"
            areas_under_signals += f"<tr><td>{signal_level}</td><td>{areas}</td></tr>"

        if not typhoon_alerts:
            typhoon_alerts = "<tr><td colspan='2'>No typhoon alerts from PAGASA at this time.</td></tr>"
        
        if not areas_under_signals:
            areas_under_signals = "<tr><td colspan='2'>No areas currently under typhoon signals.</td></tr>"

    else:
        typhoon_alerts = "<tr><td colspan='2'>Error: Unable to fetch PAGASA typhoon alerts.</td></tr>"
        areas_under_signals = "<tr><td colspan='2'>Error: Unable to fetch areas under typhoon signals.</td></tr>"

    return f"<table border='1'><tr><th>Typhoon Alerts</th><th>Details</th></tr>{typhoon_alerts}</table>", \
           f"<table border='1'><tr><th>Signal Level</th><th>Areas</th></tr>{areas_under_signals}</table>"

def get_ndrrmc_alert():
    url = "https://www.pagasa.dost.gov.ph/tropical-cyclone/severe-weather-bulletin"
    ndrrmc_info = ""

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(5)  # Adjust based on loading times

        element = driver.find_element(By.XPATH, "//*[@id='tcwb-1']/div[5]/div/div/table")
        rows = element.text.splitlines()

        # Count occurrences of "Affected Areas" and prepare for appending Signal Numbers
        affected_areas_count = sum(1 for row in rows if "AFFECTED" in row)
        signal_number = affected_areas_count

        ndrrmc_info = "<table border='1'><tr><th>Date</th><th>Report</th></tr>"
        for row in rows[1:]:  # Skip header
            if "AFFECTED" in row:
                # Apply red color directly in the HTML table cell for affected areas
                row = f"<tr><td colspan='2' style='color: red;'>Affected Areas Signal Number {signal_number}</td></tr>"
                signal_number -= 1  # Decrease the signal number for the next occurrence
                ndrrmc_info += row  # Add the styled row directly to the HTML table
                continue  # Skip the rest of the loop for this row

            # Check if "Alcala" is in the row and style it as large, bold, and blue
            if "Alcala" in row:
                row = row.replace("Alcala", "<span style='color: blue; font-size: 1.2em; font-weight: bold;'>Alcala</span>")

            # Process other rows normally
            cells = row.split(" ", 1)
            if len(cells) == 2:  # Only process rows with two parts
                ndrrmc_info += f"<tr><td>{cells[0]}</td><td>{cells[1]}</td></tr>"
            elif len(cells) == 1:
                ndrrmc_info += f"<tr><td colspan='2'>{cells[0]}</td></tr>"

        ndrrmc_info += "</table>"

    except Exception as e:
        ndrrmc_info = f"Error fetching PAGASA data: {e}"
    finally:
        driver.quit()

    return ndrrmc_info



def get_additional_info():
    url = "https://www.pagasa.dost.gov.ph/tropical-cyclone/severe-weather-bulletin"
    additional_info = ""

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(5)  # Wait for the page to load

        # Extract information from the specified XPath
        element = driver.find_element(By.XPATH, "//*[@id='tcwb-1']/div[4]")
        raw_text = element.text

        # Split the text into lines
        lines = raw_text.splitlines()
        additional_info = "<table border='1'><tr><th>Date</th><th>Data</th></tr>"

        # Process each line to structure it into "Date" and "Data" columns
        for line in lines:
            # Check if the line starts with a date-like format, e.g., "YYYY-MM-DD"
            if len(line) >= 10 and line[:10].count("-") == 2:  # Simplified date check
                date, data = line[:10], line[11:]  # Assume date is the first 10 characters
                additional_info += f"<tr><td>{date}</td><td>{data}</td></tr>"
            else:
                # If line does not start with a date, it’s considered part of the previous data
                additional_info += f"<tr><td colspan='2'>{line}</td></tr>"

        additional_info += "</table>"

    except Exception as e:
        additional_info = f"Error fetching additional data: {e}"
    finally:
        driver.quit()

    return additional_info


def send_email(weather_info, typhoon_alerts, areas_under_signals, ndrrmc_info, additional_info):
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = 'Weather and Typhoon Update for Anulid, Alcala, Pangasinan'

    email_content = f"""
    <html>
    <body>
        {weather_info}<br><br>
        {typhoon_alerts}<br><br>
        {areas_under_signals}<br><br>
        <h2>PAGASA Alert Information</h2>
        {ndrrmc_info}<br><br>
        <h2>Additional Information</h2>
        <p>{additional_info}</p>
    </body>
    </html>
    """
    message.attach(MIMEText(email_content, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()

# Fetch data and send email
weather_info = get_weather()
typhoon_alerts, areas_under_signals = get_pagasa_typhoon_alerts()
ndrrmc_info = get_ndrrmc_alert()
additional_info = get_additional_info()

if "Error" not in weather_info:
    send_email(weather_info, typhoon_alerts, areas_under_signals, ndrrmc_info, additional_info)
else:
    print(weather_info)
