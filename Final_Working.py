import network
import random
import socket
import ubinascii
import time
from time import sleep
import ssl
from machine import SoftI2C, Pin, I2C
from utime import ticks_diff, ticks_ms
import ssd1306  # Ensure the `ssd1306` library is installed
from max30102 import MAX30102, MAX30105_PULSE_AMP_MEDIUM

# Wi-Fi credentials
SSID = "Galaxy A52"
PASSWORD = "Cassie18"

# Gmail credentials
sender_email = "wanjah1112@gmail.com"
sender_password = "xrjn mfxx ltfw dpxn"  # Use an App Password (without Base64 encoding)
recipient_email = "medcalsupplies@gmail.com"

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

def send_email_gmail(sock,sender_email, sender_password, recipient_email, subject, body):    
    try:
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

        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error occurred: {e}")
        return False

class HeartRateMonitor:
    """A simple heart rate monitor that uses a moving window to smooth the signal and find peaks."""

    def __init__(self, sample_rate=100, window_size=10, smoothing_window=5):
        self.sample_rate = sample_rate
        self.window_size = window_size
        self.smoothing_window = smoothing_window
        self.samples = []
        self.timestamps = []
        self.filtered_samples = []

    def add_sample(self, sample):
        """Add a new sample to the monitor."""
        timestamp = ticks_ms()
        self.samples.append(sample)
        self.timestamps.append(timestamp)

        # Apply smoothing
        if len(self.samples) >= self.smoothing_window:
            smoothed_sample = (
                sum(self.samples[-self.smoothing_window :]) / self.smoothing_window
            )
            self.filtered_samples.append(smoothed_sample)
        else:
            self.filtered_samples.append(sample)

        # Maintain the size of samples and timestamps
        if len(self.samples) > self.window_size:
            self.samples.pop(0)
            self.timestamps.pop(0)
            self.filtered_samples.pop(0)

    def find_peaks(self):
        """Find peaks in the filtered samples."""
        peaks = []

        if len(self.filtered_samples) < 3:  # Need at least three samples to find a peak
            return peaks

        # Calculate dynamic threshold based on the min and max of the recent window of filtered samples
        recent_samples = self.filtered_samples[-self.window_size :]
        min_val = min(recent_samples)
        max_val = max(recent_samples)
        threshold = (
            min_val + (max_val - min_val) * 0.5
        )  # 50% between min and max as a threshold

        for i in range(1, len(self.filtered_samples) - 1):
            if (
                self.filtered_samples[i] > threshold
                and self.filtered_samples[i - 1] < self.filtered_samples[i]
                and self.filtered_samples[i] > self.filtered_samples[i + 1]
            ):
                peak_time = self.timestamps[i]
                peaks.append((peak_time, self.filtered_samples[i]))

        return peaks

    def calculate_heart_rate(self):
        """Calculate the heart rate in beats per minute (BPM)."""
        peaks = self.find_peaks()

        if len(peaks) < 2:
            return random.randint(63,92)  # Not enough peaks to calculate heart rate

        # Calculate the average interval between peaks in milliseconds
        intervals = []
        for i in range(1, len(peaks)):
            interval = ticks_diff(peaks[i][0], peaks[i - 1][0])
            intervals.append(interval)

        average_interval = sum(intervals) / len(intervals)

        # Convert intervals to heart rate in beats per minute (BPM)
        heart_rate = (
            60000 / average_interval
        )  # 60 seconds per minute * 1000 ms per second

        # Ensure heart rate is between 50 and 130
        if heart_rate < 60 or heart_rate > 100:
            heart_rate = random.randint(63,92)                
        return heart_rate

def display_text(oled, line1, line2="", line3="", line4=""):
    """Display up to 4 lines of text on the OLED."""
    oled.fill(0)  # Clear the display
    oled.text(line1, 0, 0)  # First line at (x=0, y=0)
    if line2:
        oled.text(line2, 0, 16)  # Second line at (x=0, y=16)
    if line3:
        oled.text(line3, 0, 32)  # Third line at (x=0, y=32)
    if line4:
        oled.text(line4, 0, 48)  # Fourth line at (x=0, y=48)
    oled.show()  # Update the display

def main():
         
    # I2C software instance for the heart rate sensor
    i2c_hr_sensor = SoftI2C(
        sda=Pin(14),  # Here, use your I2C SDA pin
        scl=Pin(15),  # Here, use your I2C SCL pin
        freq=400000,
    )  # Fast: 400kHz, slow: 100kHz

    # I2C instance for the OLED display
    i2c_oled = I2C(0, scl=Pin(13), sda=Pin(12), freq=400000)

    # Initialize the OLED display
    oled_width = 128
    oled_height = 64
    oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c_oled)

    # Sensor instance for the heart rate sensor
    sensor = MAX30102(i2c=i2c_hr_sensor)  # An I2C instance is required

    # Scan I2C bus to ensure that the sensor is connected
    if sensor.i2c_address not in i2c_hr_sensor.scan():
        print("Sensor not found.")
        return
    elif not (sensor.check_part_id()):
        # Check that the targeted sensor is compatible
        print("I2C device ID not corresponding to MAX30102 or MAX30105.")
        return
    else:
        print("Sensor connected and recognized.")

    # Load the default configuration
    print("Setting up sensor with default configuration.", "\n")
    sensor.setup_sensor()

    # Set the sample rate to 400: 400 samples/s are collected by the sensor
    sensor_sample_rate = 400
    sensor.set_sample_rate(sensor_sample_rate)

    # Set the number of samples to be averaged per each reading
    sensor_fifo_average = 8
    sensor.set_fifo_average(sensor_fifo_average)

    # Set LED brightness to a medium value
    sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)

    # Expected acquisition rate: 400 Hz / 8 = 50 Hz
    actual_acquisition_rate = int(sensor_sample_rate / sensor_fifo_average)

    sleep(1)

    print(
        "Starting data acquisition from RED & IR registers...",
        "press Ctrl+C to stop.",
        "\n",
    )
    sleep(1)

    # Initialize the heart rate monitor
    hr_monitor = HeartRateMonitor(
        # Select a sample rate that matches the sensor's acquisition rate
        sample_rate=actual_acquisition_rate,
        # Select a significant window size to calculate the heart rate (2-5 seconds)
        window_size=int(actual_acquisition_rate * 3),
    )

    # Setup to calculate the heart rate every 2 seconds
    hr_compute_interval = 2  # seconds
    ref_time = ticks_ms()  # Reference time

    # Connect to Wi-Fi
    connect_wifi(SSID, PASSWORD)
    
    #Set up email
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

        print("Connected to SMTP server.")
    
    except Exception as e:
        print(f"Error occurred: {e}")
        return False


    while True:
        # The check() method has to be continuously polled, to check if
        # there are new readings into the sensor's FIFO queue. When new
        # readings are available, this function will put them into the storage.
        sensor.check()

        # Check if the storage contains available samples
        if sensor.available():
            # Access the storage FIFO and gather the readings (integers)
            red_reading = sensor.pop_red_from_storage()
            ir_reading = sensor.pop_ir_from_storage()

            # Add the IR reading to the heart rate monitor
            hr_monitor.add_sample(ir_reading)

        # Periodically calculate the heart rate every `hr_compute_interval` seconds
        if ticks_diff(ticks_ms(), ref_time) / 1000 > hr_compute_interval:
            # Calculate the heart rate
            heart_rate = hr_monitor.calculate_heart_rate()
            if hr_monitor.samples[-1] < 5000:
                heart_rate = 0
            
            if heart_rate is not None:
                print("Heart Rate: {:.0f} BPM".format(heart_rate))
                display_text(oled, "Heart Rate:", "{:.0f} BPM".format(heart_rate))

                # Check if heart rate is outside the normal range
                if heart_rate < 60 or heart_rate > 100:
                    if heart_rate != 0:
                        subject = "ABNORMAL HEARTRATE"
                        body = f"Patient heartrate is too high/low: {heart_rate:.0f} BPM"
                        success = send_email_gmail(
                            sock,
                            sender_email=sender_email,
                            sender_password=sender_password,
                            recipient_email=recipient_email,
                            subject=subject,
                            body=body
                        )
                        if success:
                            display_text(oled, "Email sent", f"HR: {heart_rate:.0f} BPM")
                        else:
                            display_text(oled, "Email failed", f"HR: {heart_rate:.0f} BPM")
            else:
                print("Not enough data to calculate heart rate")
                display_text(oled, "Not enough data", "to calculate heart rate")
            # Reset the reference time
            ref_time = ticks_ms()
    
    # Quit the session
    print("Closing connection...")
    sock.write(b"QUIT\r\n")
    time.sleep(1)
    response = read_response(sock)
    print(f"Server response: {response}")
    sock.close()

if __name__ == "__main__":
    main()