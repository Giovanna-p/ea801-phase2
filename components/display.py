# display.py
# Controle do display OLED

from machine import Pin, SoftI2C
import ssd1306
import config
from utime import sleep

class Display:
    def __init__(self, scl_pin=config.OLED_SCL_PIN, sda_pin=config.OLED_SDA_PIN, 
                 width=config.OLED_WIDTH, height=config.OLED_HEIGHT, addr=config.OLED_ADDR):
        """Inicializa o display OLED"""
        self.i2c = SoftI2C(scl=Pin(scl_pin), sda=Pin(sda_pin))
        self.oled = ssd1306.SSD1306_I2C(width, height, self.i2c, addr=addr)
    
    def limpar(self):
        """Limpa o display"""
        self.oled.fill(0)
        self.oled.show()
    
    def texto(self, texto, x=0, y=0, mostrar=True):
        """Exibe texto em coordenadas específicas"""
        self.oled.text(texto, x, y)
        if mostrar:
            self.oled.show()
    
    def mostrar_mensagem(self, mensagens, y_inicial=0, espacamento=10):
        """
        Exibe múltiplas linhas de texto
        mensagens: lista de strings para exibir
        """
        self.limpar()
        y = y_inicial
        for msg in mensagens:
            self.texto(msg, 0, y, False)
            y += espacamento
        self.oled.show()
    
    def exibir_numero_grande(self, numero):
        """Exibe um número grande no centro do display (1, 2 ou 3)"""
        self.limpar()
        
        if numero == 3:
            # Número 3 grande
            self.texto("  #  ", 30, 10, False)
            self.texto("      ## ", 30, 20, False)
            self.texto("   ####  ", 30, 30, False)
            self.texto("      ## ", 30, 40, False)
            self.texto("  #####  ", 30, 50, False)
        elif numero == 2:
            # Número 2 grande
            self.texto("  #####  ", 30, 10, False)
            self.texto("      ## ", 30, 20, False)
            self.texto("  #####  ", 30, 30, False)
            self.texto(" ##      ", 30, 40, False)
            self.texto("  #####  ", 30, 50, False)
        elif numero == 1:
            # Número 1 grande
            self.texto("    ##   ", 30, 10, False)
            self.texto("  ####   ", 30, 20, False)
            self.texto("    ##   ", 30, 30, False)
            self.texto("    ##   ", 30, 40, False)
            self.texto("  ######  ", 30, 50, False)
        
        self.oled.show()
    
    def exibir_tempos(self, resultados):
        """Exibe os tempos de reação no OLED em forma de ranking"""
        self.limpar()
        self.texto("Ranking:", 0, 0, False)
        sorted_times = sorted(resultados)  # Ordena os tempos do menor para o maior
        for i in range(min(10, len(sorted_times))):
            self.texto(f"{i + 1}. {sorted_times[i]/1000:.2f} s", 0, (i + 1) * 10, False)
        self.oled.show()
    
    def exibir_game_over(self):
        """Exibe tela de Game Over"""
        self.limpar()
        self.texto("GAME OVER!", 30, 20, False)
        self.texto("Voce apertou na", 10, 35, False)
        self.texto("cor errada!", 25, 45, False)
        self.oled.show()
    
    def mostrar_menu(self, titulo, opcoes, selecao=0):
        """
        Exibe um menu com opções selecionáveis
        titulo: texto do título
        opcoes: lista de strings com as opções
        selecao: índice da opção selecionada (0-based)
        """
        self.limpar()
        self.texto(titulo, 0, 0, False)
        self.texto("-" * 20, 0, 10, False)
        
        for i, opcao in enumerate(opcoes):
            # Marca a opção selecionada com ">"
            marcador = ">" if i == selecao else " "
            self.texto(f"{marcador} {opcao}", 0, 20 + (i * 10), False)
        
        self.oled.show()