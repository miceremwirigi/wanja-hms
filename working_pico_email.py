import network
import socket
import ubinascii
import time
import ssl

# Wi-Fi credentials
SSID = "Galaxy A52"
PASSWORD = "Cassie18"

# Gmail credentials
sender_email = "wanjah1112@gmail.com"
sender_password = "xrjn mfxx ltfw dpxn"  # Use an App Password (without Base64 encoding)
recipient_email = "medcalsupplies@gmail.com"
subject = "ABNORMAL HEARTRATE"
body = "Patient heartrate is too high/low:."

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

def read_response(sock, timeout=10):
    """Read a response from the server with a timeout."""
    #sock.settimeout(timeout)  # Set a timeout for the response reading
    try:
        response = sock.read(1024)  # Read the response from the server
        if response:
            print(f"Server response: {response.decode()}")
            return response.decode()
        else:
            print("Empty response received.")
            return ""
    except Exception as e:
        print(f"Error reading response: {e}")
        return ""

def send_email_gmail(sender_email, sender_password, recipient_email, subject, body):
    smtp_server = "smtp.gmail.com"
    port = 465  # SSL port

    try:
        print("Connecting to SMTP server...")
        # Connect to the SMTP server
        addr = socket.getaddrinfo(smtp_server, port)[0][-1]
        sock = socket.socket()
        sock.connect(addr)        
        sock = ssl.wrap_socket(sock)
        sock.setblocking(False)

        # Wrap socket with SSL manually
        # SSL encryption can be manually handled here if needed, but MicroPython doesn't support `ssl.wrap_socket()`
        # directly in some versions. Hence, alternative methods are needed or use higher level protocols.
        
        print("Connected to SMTP server.")

        # Read server greeting
        response = read_response(sock)
        print(f"Server response: {response}")  

        # Send HELO command
        print("Sending HELO command...")
        sock.write(b"HELO example.com\r\n")
        time.sleep(1)
        response = read_response(sock)
        print(f"Server response: {response}")

        # Authenticate
        print("Starting authentication...")
        sock.write(b"AUTH LOGIN\r\n")
        time.sleep(1)
        response = read_response(sock)
        print(f"Server response: {response}")

        print("Sending email (username)...")
        # Base64 encode the sender's email
        encoded_email = ubinascii.b2a_base64(sender_email.encode()).decode().strip()
        sock.write(encoded_email.encode() + b"\r\n")        
        time.sleep(1)
        response = read_response(sock)
        print(f"Server response: {response}")

        print("Sending password...")
        encoded_password = ubinascii.b2a_base64(sender_password.encode()).decode().strip()
        sock.write(encoded_password.encode() + b"\r\n")        
        time.sleep(1)
        response = read_response(sock)
        print(f"Server response: {response}")

        # Specify sender
        print("Specifying sender email...")
        sock.write(f"MAIL FROM:<{sender_email}>\r\n".encode())
        time.sleep(1)
        response = read_response(sock)
        print(f"Server response: {response}")

        # Specify recipient
        print("Specifying recipient email...")
        sock.write(f"RCPT TO:<{recipient_email}>\r\n".encode())
        time.sleep(1)
        response = read_response(sock)
        print(f"Server response: {response}")

        # Send email body
        print("Sending email body...")
        sock.write(b"DATA\r\n")
        time.sleep(1)
        response = read_response(sock)
        print(f"Server response: {response}")

        message = f"Subject: {subject}\r\n\r\n{body}\r\n.\r\n"
        sock.write(message.encode())
        time.sleep(1)
        response = read_response(sock)
        print(f"Server response: {response}")

        # Quit the session
        print("Closing connection...")
        sock.write(b"QUIT\r\n")
        time.sleep(1)
        response = read_response(sock)
        print(f"Server response: {response}")
        sock.close()

        print("Email sent successfully!")
    except Exception as e:
        print(f"Error occurred: {e}")

# Main Script
try:
    # Step 1: Connect to Wi-Fi
    connect_wifi(SSID, PASSWORD)

    # Step 2: Send an Email
    send_email_gmail(
        sender_email=sender_email,
        sender_password=sender_password,
        recipient_email=recipient_email,
        subject=subject,
        body=body
    )
except Exception as e:
    print(f"Error in main script: {e}")
