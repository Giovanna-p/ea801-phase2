# utils.py
# Funções utilitárias compartilhadas entre os jogos

from machine import Pin, ADC
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

class Joystick:
    """Classe para gerenciar o joystick analógico"""
    def __init__(self, vrx_pin=27, vry_pin=26, sw_pin=22):
        self.vrx = ADC(Pin(vrx_pin))  # Eixo X
        self.vry = ADC(Pin(vry_pin))  # Eixo Y
        self.sw = Pin(sw_pin, Pin.IN, Pin.PULL_UP)  # Botão central
        self.ultima_direcao = None
        self.ultimo_tempo = ticks_ms()
        
    def ler_direcao(self):
        """Lê a direção do joystick (cima, baixo, esq, dir, None)"""
        x = self.vrx.read_u16()
        y = self.vry.read_u16()
        
        if x > 55000: return 'dir'
        if x < 10000: return 'esq'
        # Invertendo a lógica do eixo Y
        if y > 55000: return 'cima'  # Era 'baixo'
        if y < 10000: return 'baixo'  # Era 'cima'
        return None
    
    def ler_direcao_debounce(self, debounce_ms=300):
        """
        Lê a direção com debounce - evita múltiplas leituras rápidas
        Útil para navegação em menus
        """
        tempo_atual = ticks_ms()
        direcao = self.ler_direcao()
        
        # Se não há direção ou é a mesma direção muito cedo
        if not direcao or (direcao == self.ultima_direcao and 
                          ticks_diff(tempo_atual, self.ultimo_tempo) < debounce_ms):
            return None
        
        # Atualiza controle de debounce
        self.ultima_direcao = direcao
        self.ultimo_tempo = tempo_atual
        
        return direcao
    
    def botao_central_pressionado(self):
        """Verifica se o botão central do joystick está pressionado"""
        return self.sw.value() == 0
    
    def aguardar_botao_central(self, debounce=True):
        """Aguarda o botão central ser pressionado"""
        while self.sw.value() == 1:
            pass
        if debounce:
            sleep(0.2)

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

def navegar_menu(display, botoes, titulo, opcoes, joystick=None):
    """
    Exibe um menu e permite navegação com os botões OU joystick
    Implementa scroll automático quando há muitas opções
    
    Controles:
    - Joystick: CIMA/BAIXO para navegar, CENTRO para selecionar
    - Botões: A para navegar, B para selecionar (fallback)
    
    Retorna o índice da opção selecionada
    """
    selecao = 0
    num_opcoes = len(opcoes)
    
    # Configurações de exibição
    max_opcoes_visiveis = 3  # Máximo de opções mostradas por vez (reduzido de 4 para 3)
    pagina_atual = 0
    
    def atualizar_display():
        """Atualiza o display com as opções da página atual"""
        # Calcula as opções visíveis
        inicio = pagina_atual * max_opcoes_visiveis
        fim = min(inicio + max_opcoes_visiveis, num_opcoes)
        opcoes_visiveis = opcoes[inicio:fim]
        
        # Ajusta a seleção relativa à página
        selecao_relativa = selecao - inicio
        
        # Monta as linhas do display
        linhas = [titulo, "-" * len(titulo)]
        
        for i, opcao in enumerate(opcoes_visiveis):
            marcador = ">" if i == selecao_relativa else " "
            linhas.append(f"{marcador} {opcao}")
        
        # Adiciona indicadores de scroll se necessário
        if num_opcoes > max_opcoes_visiveis:
            info_pagina = f"[{selecao+1}/{num_opcoes}]"
            if pagina_atual > 0:
                info_pagina =  info_pagina
            if fim < num_opcoes:
                info_pagina = info_pagina 
            linhas.append(info_pagina)
        
        display.mostrar_mensagem(linhas)
    
    def calcular_pagina():
        """Calcula qual página deve ser exibida baseada na seleção atual"""
        return selecao // max_opcoes_visiveis
    
    # Exibe o menu inicial
    atualizar_display()
    
    while True:
        if joystick:
            # Prioriza o joystick se estiver disponível
            direcao = joystick.ler_direcao_debounce()
            
            if direcao == 'cima':
                selecao = (selecao - 1) % num_opcoes
                pagina_atual = calcular_pagina()
                atualizar_display()
            
            elif direcao == 'baixo':
                selecao = (selecao + 1) % num_opcoes
                pagina_atual = calcular_pagina()
                atualizar_display()
            
            elif joystick.botao_central_pressionado():
                sleep(0.2)  # Debounce
                return selecao
        
        # Fallback para botões (funciona mesmo sem joystick)
        if botoes.esta_pressionado_a():
            selecao = (selecao + 1) % num_opcoes
            pagina_atual = calcular_pagina()
            atualizar_display()
            sleep(0.3)  # Debounce para botões
        
        elif botoes.esta_pressionado_b():
            sleep(0.2)  # Debounce
            return selecao
        
        sleep(0.05)  # Evita uso excessivo de CPU

def navegar_menu_simples(display, botoes, titulo, opcoes):
    """
    Versão simplificada sem joystick (compatibilidade com código existente)
    """
    return navegar_menu(display, botoes, titulo, opcoes, joystick=None)