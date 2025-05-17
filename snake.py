from machine import Pin, PWM, ADC, SoftI2C
import neopixel, ssd1306
from utime import sleep
import urandom

# === LED Matrix ===
NUM_LEDS = 25
np = neopixel.NeoPixel(Pin(7), NUM_LEDS)
LED_MATRIX = [
    [24, 23, 22, 21, 20],
    [15, 16, 17, 18, 19],
    [14, 13, 12, 11, 10],
    [5, 6, 7, 8, 9],
    [4, 3, 2, 1, 0]
]

# === Display OLED ===
i2c_oled = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = ssd1306.SSD1306_I2C(128, 64, i2c_oled)

# === Joystick ===
vrx = ADC(Pin(27))  # X
vry = ADC(Pin(26))  # Y
sw = Pin(22, Pin.IN, Pin.PULL_UP)

# === Buzzer ===
buzzer = PWM(Pin(21))
buzzer.duty_u16(0)

# === Botão A ===
button_a = Pin(5, Pin.IN, Pin.PULL_UP)

# === Utilitários ===
def leds(x, y, r=0, g=0, b=0):
    if 0 <= x <= 4 and 0 <= y <= 4:
        idx = LED_MATRIX[4 - y][x]
        np[idx] = (r, g, b)

def apagar():
    np.fill((0, 0, 0))
    np.write()

def tocar(freq, dur=100):
    buzzer.freq(freq)
    buzzer.duty_u16(32768)
    sleep(dur / 1000)
    buzzer.duty_u16(0)

def ler_direcao():
    x = vrx.read_u16()
    y = vry.read_u16()
    if x > 55000: return 'dir'
    if x < 10000: return 'esq'
    if y > 55000: return 'baixo'
    if y < 10000: return 'cima'
    return None

def contagem_regressiva():
    for i in range(3, 0, -1):
        oled.fill(0)
        oled.text("Comecando em:", 0, 10)
        oled.text(str(i), 60, 30)
        oled.show()
        tocar(440 + i * 100, 100)
        sleep(1)

def game_over(pontos):
    oled.fill(0)
    oled.text("Game Over!", 20, 20)
    oled.text(f"Pontos: {pontos}", 20, 40)
    oled.show()
    tocar(150, 500)
    sleep(3)

# === Jogo Snake ===
def snake():
    oled.fill(0)
    oled.text("Pressione A", 0, 0)
    oled.text("para comecar", 0, 10)
    oled.show()
    while button_a.value() == 1:
        pass
    sleep(0.3)
    contagem_regressiva()

    cobra = [(0, 4), (1, 4)]  # Começa no canto superior esquerdo
    direcao = 'dir'
    pontuacao = 0

    # Gera a primeira comida
    while True:
        comida = (urandom.getrandbits(3) % 5, urandom.getrandbits(3) % 5)
        if comida not in cobra:
            break

    apagar()
    for x, y in cobra:
        leds(x, y, 0, 0, 60)
    leds(comida[0], comida[1], 60, 0, 0)
    np.write()

    sleep(1.5)  # tempo pra você se preparar com o joystick

    while True:
        # Lê o movimento do joystick
        nova_dir = ler_direcao()
        if nova_dir and (nova_dir != direcao and not (direcao, nova_dir) in [('dir', 'esq'), ('esq', 'dir'), ('cima', 'baixo'), ('baixo', 'cima')]):
            direcao = nova_dir

        # Movimento da cabeça
        cabeca = cobra[-1]
        if direcao == 'dir':
            nova_pos = (cabeca[0] + 1, cabeca[1])
        elif direcao == 'esq':
            nova_pos = (cabeca[0] - 1, cabeca[1])
        elif direcao == 'cima':
            nova_pos = (cabeca[0], cabeca[1] - 1)
        elif direcao == 'baixo':
            nova_pos = (cabeca[0], cabeca[1] + 1)

        # Verifica colisão
        if nova_pos in cobra or not (0 <= nova_pos[0] <= 4 and 0 <= nova_pos[1] <= 4):
            game_over(pontuacao)
            break

        cobra.append(nova_pos)

        # Comeu comida
        if nova_pos == comida:
            pontuacao += 1
            tocar(880, 80)
            while True:
                nova_comida = (urandom.getrandbits(3) % 5, urandom.getrandbits(3) % 5)
                if nova_comida not in cobra:
                    comida = nova_comida
                    break
        else:
            cobra.pop(0)  # remove rabo

        apagar()
        for x, y in cobra:
            leds(x, y, 0, 0, 60)
        leds(comida[0], comida[1], 60, 0, 0)
        np.write()
        sleep(0.4)

# Loop principal
while True:
    snake()
