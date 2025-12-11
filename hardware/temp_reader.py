import adafruit_DHT
import time

DHT_SENSOR = adafruit_DHT.DHT11(board.D4)

def read_temp():
    _, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    return temperature

if __name__ == "__main__":
    while True:
        t = read_temp()
        print(f"Temp: {t}°C")
        time.sleep(1)