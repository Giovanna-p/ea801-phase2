# utils.py
# Funções utilitárias compartilhadas entre os jogos

from machine import Pin
import config
from utime import sleep, ticks_ms, ticks_diff
import urandom

class Botoes:
    """Classe para gerenciar os botões"""
    def __init__(self, pin_a=config.BUTTON_A_PIN, pin_b=config.BUTTON_B_PIN):
        self.button_a = Pin(pin_a, Pin.IN, Pin.PULL_UP)
        self.button_b = Pin(pin_b, Pin.IN, Pin.PULL_UP)
    
    def aguardar_botao_a(self, debounce=True):
        """Aguarda o botão A ser pressionado"""
        while self.button_a.value() == 1:
            pass
        if debounce:
            sleep(0.2)  # Debounce
    
    def aguardar_botao_b(self, debounce=True):
        """Aguarda o botão B ser pressionado"""
        while self.button_b.value() == 1:
            pass
        if debounce:
            sleep(0.2)  # Debounce
    
    def aguardar_qualquer_botao(self, debounce=True):
        """Aguarda qualquer botão ser pressionado e retorna qual (A=1, B=2)"""
        while True:
            if self.button_a.value() == 0:
                if debounce:
                    sleep(0.2)  # Debounce
                return 1
            if self.button_b.value() == 0:
                if debounce:
                    sleep(0.2)  # Debounce
                return 2
    
    def esta_pressionado_a(self):
        """Verifica se o botão A está pressionado"""
        return self.button_a.value() == 0
    
    def esta_pressionado_b(self):
        """Verifica se o botão B está pressionado"""
        return self.button_b.value() == 0

def contagem_regressiva(display, buzzer, segundos=3):
    """Exibe uma contagem regressiva no display"""
    for i in range(segundos, 0, -1):
        display.exibir_numero_grande(i)
        buzzer.tocar_som(440+i*100, 200)  # Tom diferente para cada número
        sleep(1)

def tempo_aleatorio(min_seg=0.8, max_seg=2.0):
    """Gera um tempo aleatório entre min_seg e max_seg em segundos"""
    return urandom.uniform(min_seg, max_seg)

def medir_tempo_ms():
    """Retorna o tempo atual em milissegundos"""
    return ticks_ms()

def diferenca_tempo_ms(tempo_final, tempo_inicial):
    """Calcula a diferença entre dois tempos em milissegundos"""
    return ticks_diff(tempo_final, tempo_inicial)

def navegar_menu(display, botoes, titulo, opcoes):
    """
    Exibe um menu e permite navegação com os botões
    Retorna o índice da opção selecionada
    
    Botão A: mover para cima/baixo na seleção
    Botão B: confirmar seleção
    """
    selecao = 0
    num_opcoes = len(opcoes)
    
    display.mostrar_menu(titulo, opcoes, selecao)
    
    while True:
        # Aguarda qualquer botão ser pressionado
        botao = botoes.aguardar_qualquer_botao()
        
        if botao == 1:  # Botão A - muda seleção
            selecao = (selecao + 1) % num_opcoes
            display.mostrar_menu(titulo, opcoes, selecao)
        
        elif botao == 2:  # Botão B - confirma seleção
            return selecao