import time

import board
import adafruit_dht


# DHT22 + Raspberry Pi 5 안정화 옵션
dht = adafruit_dht.DHT22(
    board.D4,
    use_pulseio=False 
)
# 물리 7번핀 + 3.3ㅍ


def read_temp():

    for _ in range(5):

        try:

            temp = dht.temperature

            if temp is not None:

                return round(
                    float(temp),
                    1
                )

        except RuntimeError as e:

            print(
                "[DHT22 RuntimeError]",
                e
            )

            time.sleep(0.2)

        except Exception as e:

            print(
                "[DHT22 ERROR]",
                e
            )

            time.sleep(0.5)

    return None