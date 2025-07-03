# matriz_led.py
# Controle da matriz de LEDs

from machine import Pin
import neopixel
import config
import urandom
from utime import sleep

class MatrizLED:
    def __init__(self, pin=config.LED_PIN, num_leds=config.NUM_LEDS):
        """Inicializa a matriz de LEDs"""
        self.np = neopixel.NeoPixel(Pin(pin), num_leds)
        self.matrix = config.LED_MATRIX
    
    def acender_led(self, x, y, r=20, g=20, b=20):
        """Acende um LED específico (coordenadas x,y) com cor personalizada"""
        if 0 <= x <= 4 and 0 <= y <= 4:
            led_index = self.matrix[4 - y][x]  # Conversão da coordenada (x,y) para índice do LED
            self.np[led_index] = (r, g, b)     # Define a cor RGB do LED
            self.np.write()                    # Atualiza a matriz
    
    def acender_led_cor(self, x, y, cor):
        """Acende um LED usando uma tupla de cor predefinida"""
        r, g, b = cor
        self.acender_led(x, y, r, g, b)
    
    def apagar(self):
        """Apaga todos os LEDs da matriz"""
        self.np.fill(config.COR_APAGADO)
        self.np.write()
    
    def apagar_led(self, x, y):
        """Apaga um LED específico (coordenadas x,y)"""
        if 0 <= x <= 4 and 0 <= y <= 4:
            led_index = self.matrix[4 - y][x]
            self.np[led_index] = (0, 0, 0)
            self.np.write()
    
    def posicao_aleatoria(self):
        """Gera uma posição aleatória na matriz 5x5"""
        x = urandom.randint(0, 4)
        y = urandom.randint(0, 4)
        return x, y
    
    def piscar_led(self, x, y, cor, vezes=3, duracao=0.2):
        """Pisca um LED específico várias vezes"""
        for _ in range(vezes):
            self.acender_led_cor(x, y, cor)
            sleep(duracao)
            self.apagar_led(x, y)
            sleep(duracao)
    
    def mostrar_padrao(self, padrao, duracao=0.5):
        """
        Mostra um padrão na matriz. O padrão é uma lista de tuplas (x, y, cor)
        Exemplo: [(0, 0, COR_VERDE), (1, 1, COR_AZUL)]
        """
        self.apagar()
        for x, y, cor in padrao:
            self.acender_led_cor(x, y, cor)
        sleep(duracao)
        self.apagar()
    
    def mostrar_animacao(self, frames, duracao_frame=0.2):
        """
        Mostra uma animação na matriz. 
        frames é uma lista de padrões, cada um sendo uma lista de tuplas (x, y, cor)
        """
        for frame in frames:
            self.apagar()
            for x, y, cor in frame:
                self.acender_led_cor(x, y, cor)
            sleep(duracao_frame)
        self.apagar()