import time
import board
import adafruit_dht

dht = adafruit_dht.DHT11(board.D4)

def read_temp():
    for _ in range(5): 
        try:
            temp = dht.temperature
            if temp is not None:
                return temp
        except RuntimeError:
            time.sleep(0.2)
    return None