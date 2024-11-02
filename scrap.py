import requests
import smtplib
import yagmail
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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
        
        # Format the email content
        weather_info = (f"Location: {location}\n"
                        f"Temperature: {temperature}°C\n"
                        f"Weather: {weather_description.capitalize()}\n"
                        f"Humidity: {humidity}%\n"
                        f"Wind Speed: {wind_speed} m/s\n")
        return weather_info
    else:
        return f"Error: Unable to fetch data (Status code: {response.status_code})"

def send_email(weather_info):
    # Set up the MIME message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = 'Weather Update for Anulid, Alcala, Pangasinan'

    # Attach the weather information as the email body
    message.attach(MIMEText(weather_info, 'plain'))

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

# Get the weather information
weather_info = get_weather()

# Send the email if the weather data was retrieved successfully
if "Error" not in weather_info:
    send_email(weather_info)
else:
    print(weather_info)
