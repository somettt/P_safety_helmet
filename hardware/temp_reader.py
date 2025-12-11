import time
import board
import adafruit_dht

dht = adafruit_dht.DHT22(board.D4) 

def read_temp():
    while True:
        temp = dht.temperature 
        time.sleep(1) 
        return temp

if __name__ == "__main__":
    print(read_temp())
