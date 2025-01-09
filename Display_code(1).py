from machine import Pin, I2C
import ssd1306  # Ensure the `ssd1306` library is installed

# Define I2C pins and initialize the I2C bus
scl_pin = 13  # GPIO pin for SCL
sda_pin =  12 # GPIO pin for SDA
i2c = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=400000)

# Check if device is connected to specified pins
print("Checking if device is connected to specified pins")
print(i2c.scan())

# OLED display dimensions
oled_width = 128
oled_height = 64

# Initialize the OLED display
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

def display_text(line1, line2="", line3="", line4=""):
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

# Example usage
display_text("Hello, World!", "Line 2", "Line 3", "Line 4")

# Additional functions to demonstrate other features of the OLED
def draw_shapes():
    """Draw basic shapes on the OLED."""
    oled.fill(0)  # Clear the display
    oled.rect(10, 10, 50, 30, 1)  # Draw a rectangle
    oled.fill_rect(70, 10, 40, 30, 1)  # Draw a filled rectangle
    oled.line(0, 0, oled_width, oled_height, 1)  # Draw a diagonal line
    oled.show()

def scroll_text():
    """Scroll text horizontally across the OLED."""
    oled.fill(0)  # Clear the display
    message = "Scrolling Text Example"
    for offset in range(len(message) * 8):
        oled.fill(0)
        oled.text(message, -offset, 0)
        oled.show()

# Uncomment the following lines to test other functions
# draw_shapes()
# scroll_text()

