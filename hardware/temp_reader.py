import Adafruit_DHT
import time

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4   # GPIO번호

def read_temp():
    _, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    return temperature

if __name__ == "__main__":
    while True:
        t = read_temp()
        print(f"Temp: {t}°C")
        time.sleep(1)