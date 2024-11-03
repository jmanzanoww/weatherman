import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Replace with your OpenWeatherMap API key and email credentials
api_key = '62a3e70737f126f675dfa3da70dadcf2'
sender_email = 'jobmanzano104@gmail.com'
receiver_email = 'jobmanzano104@gmail.com'
password = 'aoby jhnk loag mvqq'

# Coordinates for Anulid, Alcala, Pangasinan
latitude = 15.828220
longitude = 120.490021

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
        
        # Format the email content for weather information
        weather_info = (f"Location: {location}\n"
                        f"Temperature: {temperature}°C\n"
                        f"Weather: {weather_description.capitalize()}\n"
                        f"Humidity: {humidity}%\n"
                        f"Wind Speed: {wind_speed} m/s\n")
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
        
        # Locate the typhoon alerts section
        alerts = soup.find_all('div', class_='alert')  # Adjust class if needed
        for alert in alerts:
            title = alert.find('h3').get_text(strip=True) if alert.find('h3') else "Typhoon Alert"
            details = alert.find('p').get_text(strip=True) if alert.find('p') else "Details unavailable"
            typhoon_alerts += f"{title}\n{details}\n\n"
        
        # Attempt to find specific signal information
        signals_section = soup.find_all('div', class_='signal')  # Adjust as per PAGASA structure
        for signal in signals_section:
            signal_level = signal.find('h4').get_text(strip=True) if signal.find('h4') else "Unknown Signal"
            areas = signal.find('ul').get_text(separator=', ', strip=True) if signal.find('ul') else "No areas listed"
            areas_under_signals += f"{signal_level}:\nAreas: {areas}\n\n"

        if not typhoon_alerts:
            typhoon_alerts = "No typhoon alerts from PAGASA at this time."
        
        if not areas_under_signals:
            areas_under_signals = "No areas currently under typhoon signals."

    else:
        typhoon_alerts = "Error: Unable to fetch PAGASA typhoon alerts."
        areas_under_signals = "Error: Unable to fetch areas under typhoon signals."

    return typhoon_alerts, areas_under_signals

def send_email(weather_info, typhoon_alerts, areas_under_signals):
    # Set up the MIME message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = 'Weather and Typhoon Update for Anulid, Alcala, Pangasinan'

    # Combine weather and typhoon alert information
    email_content = (f"{weather_info}\n\nTyphoon Alerts:\n{typhoon_alerts}\n\n"
                     f"Areas Under Typhoon Signals:\n{areas_under_signals}")
    message.attach(MIMEText(email_content, 'plain'))

    # Set up the server connection and send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Upgrade the connection to secure
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()

# Get the weather information from OpenWeatherMap
weather_info = get_weather()

# Get the latest typhoon alerts and areas under signals from PAGASA
typhoon_alerts, areas_under_signals = get_pagasa_typhoon_alerts()

# Send the combined email if the weather data was retrieved successfully
if "Error" not in weather_info:
    send_email(weather_info, typhoon_alerts, areas_under_signals)
else:
    print(weather_info)
