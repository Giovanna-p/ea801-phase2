# config.py
# Arquivo de configurações compartilhadas para o jogo BitdogLab

from machine import Pin, SoftI2C, PWM

# === CONFIGURAÇÃO DE PINOS ===
# Matriz de LEDs
LED_PIN = 7

# Botões
BUTTON_A_PIN = 5
BUTTON_B_PIN = 6

# Buzzer
BUZZER_PIN = 21

# Display OLED
OLED_SCL_PIN = 15
OLED_SDA_PIN = 14
OLED_ADDR = 0x3C
OLED_WIDTH = 128
OLED_HEIGHT = 64

# === CONFIGURAÇÃO DA MATRIZ DE LEDs ===
NUM_LEDS = 25  # Matriz 5x5

# Mapeamento lógico da matriz (posição [x][y] corresponde ao índice real do LED)
LED_MATRIX = [
    [24, 23, 22, 21, 20],
    [15, 16, 17, 18, 19],
    [14, 13, 12, 11, 10],
    [5, 6, 7, 8, 9],
    [4, 3, 2, 1, 0]
]

# === DEFINIÇÃO DAS CORES ===
# Cores básicas para os LEDs (valores RGB)
COR_VERDE = (0, 100, 0)
COR_AZUL = (0, 0, 100)
COR_VERMELHO = (100, 0, 0)
COR_AMARELO = (100, 100, 0)
COR_ROXO = (100, 0, 100)
COR_CIANO = (0, 100, 100)
COR_BRANCO = (30, 30, 30)
COR_APAGADO = (0, 0, 0)

# === CONFIGURAÇÕES DO JOGO ===
# Tempo máximo de exibição de um LED (em milissegundos)
LED_MAX_TIME = 1000

# === CONFIGURAÇÕES DE ÁUDIO ===
# Frequências para notas musicais básicas
NOTAS = {
    'C4': 262,  # Dó
    'D4': 294,  # Ré
    'E4': 330,  # Mi
    'F4': 349,  # Fá
    'G4': 392,  # Sol
    'A4': 440,  # Lá
    'B4': 494,  # Si
    'C5': 523,  # Dó (oitava superior)
}