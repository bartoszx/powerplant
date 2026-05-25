# Pico 2 – MTR1_DATA (34 LEDy) + podświetlenie 5 pasków WS2812 z RPi przez UART.
#
# Pico GPIO6 → MTR1_DATA (34 LEDy). Pico GPIO11..15 → dane WS2812: MTR1,MTR2 po 2 LED (kWh, Hz – pary 1-2 i 3-4 jako jedno), MTR3..5 po 40 LED.
#
# Protokół: 0xFF = ping | 0x01 + 102B = 34 LEDy | 0x02 + 1B maska + 3B R,G,B | 0x03 = backlight OFF | 0x04 OTA = 2B len + body → main.py, reboot.

from machine import UART, Pin, soft_reset
import neopixel
import time

UART_RX = 1
UART_TX = 0
MTR1_DATA_PIN = 6
BACKLIGHT_PINS = [11, 12, 13, 14, 15]   # MTR1..MTR5 (J5 spare)
# MTR1 (kWh), MTR2 (Hz) = po 2 LED, traktowane jako jedno przy podświetlaniu; MTR3..5 = po 40 LED
BACKLIGHT_LED_COUNTS = [2, 2, 40, 40, 40]
NUM_LEDS = 34
BAUD = 115200
# Strip MTR1_DATA (łuk): wiele taśm WS2812 ma kolejność GRB – wtedy (255,0,0) z hosta daje czerwony
# Ustaw False jeśli kolory się nie zgadzają (np. czerwony świeci na zielono).
MTR1_STRIP_GRB = True

CMD_PING = 0xFF
CMD_SET_STRIP = 0x01
CMD_BACKLIGHT_MASK = 0x02   # +1 B maska (bit0..4 = MTR1..5) + 3 B R,G,B – kolor z danych
CMD_BACKLIGHT_OFF = 0x03
CMD_OTA = 0x04   # + 2 B długość (big-endian) + body → zapis do main.py, soft_reset()
OTA_MAX_SIZE = 16384   # max 16 KB

def main():
    uart = UART(0, BAUD, tx=Pin(UART_TX), rx=Pin(UART_RX), timeout=0)
    np = neopixel.NeoPixel(Pin(MTR1_DATA_PIN), NUM_LEDS)
    bl_strips = [neopixel.NeoPixel(Pin(p), n) for p, n in zip(BACKLIGHT_PINS, BACKLIGHT_LED_COUNTS)]
    for bl, n in zip(bl_strips, BACKLIGHT_LED_COUNTS):
        for i in range(n):
            bl[i] = (0, 0, 0)
        bl.write()

    while True:
        buf = uart.read(1)
        if not buf:
            time.sleep_ms(10)
            continue

        cmd = buf[0]

        if cmd == CMD_PING:
            uart.write(bytes([CMD_PING]))
            continue

        if cmd == CMD_SET_STRIP:
            # Zbierz 102 B (34×RGB) – przy timeout=0 read() może zwrócić mniej
            need = NUM_LEDS * 3
            data = b""
            deadline = time.ticks_add(time.ticks_ms(), 200)
            while len(data) < need and time.ticks_diff(deadline, time.ticks_ms()) > 0:
                chunk = uart.read(need - len(data))
                if chunk:
                    data += chunk
                if len(data) < need:
                    time.sleep_ms(2)
            if len(data) >= need:
                for i in range(NUM_LEDS):
                    r = data[i * 3] & 0xFF
                    g = data[i * 3 + 1] & 0xFF
                    b = data[i * 3 + 2] & 0xFF
                    if MTR1_STRIP_GRB:
                        np[i] = (g, r, b)
                    else:
                        np[i] = (r, g, b)
                np.write()
            continue

        if cmd == CMD_BACKLIGHT_MASK:
            # Zbierz 4 B (maska + R,G,B) – przy timeout=0 read() może zwrócić mniej
            data = b""
            deadline = time.ticks_add(time.ticks_ms(), 100)
            while len(data) < 4 and time.ticks_diff(deadline, time.ticks_ms()) > 0:
                chunk = uart.read(4 - len(data))
                if chunk:
                    data += chunk
                if len(data) < 4:
                    time.sleep_ms(2)
            if len(data) >= 4:
                mask = data[0] & 0x1F
                r, g, b = data[1] & 0xFF, data[2] & 0xFF, data[3] & 0xFF
                # Taśma WS2812 w praktyce często GRB – podaj (G,R,B) żeby wyświetlić kolor (R,G,B)
                c = (g, r, b)
                for i in range(5):
                    color = c if (mask >> i) & 1 else (0, 0, 0)
                    n = BACKLIGHT_LED_COUNTS[i]
                    for j in range(n):
                        bl_strips[i][j] = color
                    bl_strips[i].write()
            continue

        if cmd == CMD_BACKLIGHT_OFF:
            for bl, n in zip(bl_strips, BACKLIGHT_LED_COUNTS):
                for j in range(n):
                    bl[j] = (0, 0, 0)
                bl.write()
            continue

        if cmd == CMD_OTA:
            # 2 B długość (big-endian), potem body – zapis do main.py i reboot
            len_buf = b""
            deadline = time.ticks_add(time.ticks_ms(), 100)
            while len(len_buf) < 2 and time.ticks_diff(deadline, time.ticks_ms()) > 0:
                chunk = uart.read(2 - len(len_buf))
                if chunk:
                    len_buf += chunk
                if len(len_buf) < 2:
                    time.sleep_ms(2)
            if len(len_buf) >= 2:
                L = (len_buf[0] << 8) | len_buf[1]
                if 0 < L <= OTA_MAX_SIZE:
                    body = b""
                    deadline = time.ticks_add(time.ticks_ms(), 30000)
                    while len(body) < L and time.ticks_diff(deadline, time.ticks_ms()) > 0:
                        chunk = uart.read(min(256, L - len(body)))
                        if chunk:
                            body += chunk
                        if len(body) < L:
                            time.sleep_ms(2)
                    if len(body) >= L:
                        try:
                            f = open("main.py", "wb")
                            f.write(body[:L])
                            f.close()
                            soft_reset()
                        except Exception:
                            pass
            continue

main()
