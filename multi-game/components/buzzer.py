# buzzer.py
# Controle do buzzer para efeitos sonoros

from machine import Pin, PWM
from utime import sleep
import config

class Buzzer:
    def __init__(self, pin=config.BUZZER_PIN):
        """Inicializa o buzzer no pino especificado"""
        self.buzzer = PWM(Pin(pin))
        self.buzzer.duty_u16(0)  # Inicialmente sem som
    
    def tocar_som(self, frequencia, duracao_ms):
        """Toca um som com frequência e duração específicas"""
        self.buzzer.freq(frequencia)
        self.buzzer.duty_u16(32768)  # 50% do ciclo de trabalho
        sleep(duracao_ms/1000)
        self.buzzer.duty_u16(0)  # Desliga o som
    
    def tocar_nota(self, nota, duracao_ms):
        """Toca uma nota musical pelo nome (ex: 'A4' para Lá)"""
        if nota in config.NOTAS:
            self.tocar_som(config.NOTAS[nota], duracao_ms)
        else:
            print(f"Nota {nota} não encontrada")
    
    # === MELODIAS PRÉ-DEFINIDAS ===
    def tocar_fim_jogo(self):
        """Melodia simples de fim de jogo (3 notas)"""
        self.tocar_som(440, 150)  # Lá
        sleep(0.05)
        self.tocar_som(554, 150)  # Dó#
        sleep(0.05)
        self.tocar_som(659, 300)  # Mi
    
    def tocar_game_over(self):
        """Melodia triste de game over"""
        self.tocar_som(392, 200)  # Sol
        sleep(0.05)
        self.tocar_som(349, 200)  # Fá
        sleep(0.05)
        self.tocar_som(330, 400)  # Mi
    
    def bipe_reacao(self):
        """Bipe rápido para reação"""
        self.tocar_som(880, 50)
    
    def tocar_start(self):
        """Som de início do jogo"""
        for f in range(200, 600, 20):  # Sobe de 200 Hz até 600 Hz
            self.buzzer.freq(f)
            self.buzzer.duty_u16(30000)
            sleep(0.01)
        self.buzzer.duty_u16(0)
    
    def tocar_sequencia(self, sequencia):
        """Toca uma sequência de notas conforme lista de tuplas (nota, duração)"""
        for nota, duracao in sequencia:
            self.tocar_nota(nota, duracao)
            sleep(0.05)  # Pequena pausa entre notas