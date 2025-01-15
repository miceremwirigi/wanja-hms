import network
import requests
import json

# Wi-Fi credentials
SSID = "Galaxy A52"
PASSWORD = "Cassie18"

def connect_wifi(ssid, password):
    print("Connecting to WiFi...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)    
    
    # Wait for the connection to establish
    timeout = 10
    while not wlan.isconnected() and timeout > 0:
        timeout -= 1
        time.sleep(1)

    if wlan.isconnected():
        print("Wi-Fi connected")
        print("IP address:", wlan.ifconfig()[0])
    else:
        print("Failed to connect to Wi-Fi")

    
connect_wifi(SSID, PASSWORD)
    # Define the URL of the API endpoint
api_url = "https://phr-backend.onrender.com/api/heartmonitorentries"

# Define the data to be sent in JSON format
data = {
    #"id":"3eaec43a-09b6-43ea-9f3e-f59368174692",
    #"created_at":"2025-01-15T12:54:07.664953+03:00",
    #"updated_at":"2025-01-15T12:54:07.664953+03:00",
    #"PersonID":"34bfba05-7788-47a3-9202-ba44d7425f63",
    "person":{
        "id":"373025c5-60b5-4c66-9c97-532d28826490",
        #"created_at":"2025-01-15T12:54:07.34121+03:00",
        #"updated_at":"2025-01-15T12:54:07.341211+03:00",
        #"first_name":"Wanja",
        #"last_name":"Ndwiga",
        #"date_of_birth":"1990-01-01T00:00:00Z",
        #"is_dependent": False
        },
    "heart_rate":660,
    "recorded_at":"2025-01-15 12:54:07.653539592 +0300 EAT m=+0.456799707"
    }

# Convert the data to JSON format
json_data = json.dumps(data)

# Set the headers for the HTTP request
headers = {
    "Content-Type": "application/json",
    #"Authorization": "Bearer YOUR_API_KEY"  # Replace with your actual API key if needed
}

# Send the HTTP GET request to the API
response = requests.get(api_url, headers=headers)
# Check the response from the API
if response.status_code == 200:
    print("Data received successfully")
    print(f"Response: {response.text}")
    
else:
    print(f"Failed to send data. Status code: {response.status_code}")
    print(f"Response: {response.text}")


# Send the HTTP POST request to the API
response = requests.post(api_url, headers=headers, data=json_data)

# Check the response from the API
if response.status_code == 201:
    print("Data sent successfully")
    print(f"Response: {response.text}")
else:
    print(f"Failed to send data. Status code: {response.status_code}")
    print(f"Response: {response.text}")