# stages/stage_manager.py
# Gerenciador de etapas do jogo

from components.display import Display
from components.matriz_led import MatrizLED
from components.buzzer import Buzzer
from utime import sleep
from utils import Botoes, Joystick, navegar_menu

class StageManager:
    def __init__(self):
        """Inicializa o gerenciador de etapas com os componentes básicos"""
        # Inicializa componentes de hardware
        self.display = Display()
        self.matriz = MatrizLED()
        self.buzzer = Buzzer()
        self.botoes = Botoes()
        
        # Inicializa o joystick
        try:
            self.joystick = Joystick()
            print("Joystick inicializado com sucesso")
        except Exception as e:
            print(f"Erro ao inicializar joystick: {e}")
            self.joystick = None
        
        # Lista de etapas disponíveis
        self.stages = []
        self.stage_names = []
        
        # Pontuação do jogador em cada etapa
        self.scores = {}
    
    def adicionar_etapa(self, stage_class, stage_name):
        """
        Adiciona uma etapa ao jogo
        stage_class: Classe da etapa
        stage_name: Nome para exibição
        """
        self.stages.append(stage_class)
        self.stage_names.append(stage_name)
    
    def limpar_hardware(self):
        """
        Limpa todos os componentes de hardware para estado neutro
        Chamado entre jogos para garantir que não há resíduos visuais/sonoros
        """
        try:
            # Limpa display
            self.display.limpar()
            
            # Apaga todos os LEDs
            self.matriz.apagar()
            
            # Garante que o buzzer esteja silencioso
            self.buzzer.buzzer.duty_u16(0)
            
            print("Hardware limpo entre jogos")
        except Exception as e:
            print(f"Erro ao limpar hardware: {e}")
    
    def iniciar_menu(self):
        """Exibe o menu principal do jogo"""
        while True:
            # Limpa hardware antes de mostrar o menu
            self.limpar_hardware()
            
            # Opções do menu
            opcoes = self.stage_names + ["Sair"]
            
            # Mensagem de instruções
            if self.joystick:
                instrucoes = [
                    "*BITDOGLAB GAME*",
                    " ",
                    "Joystick: + - navegar",
                    "Centro: selecionar",
                    "Bot. A: navegar",
                    "Bot. B: selecionar" 
                ]
            else:
                instrucoes = [
                    "BitdogLab Game", 
                    "Selecione:",
                    "Botao A: navegar", 
                    "Botao B: selecionar"
                ]
            
            self.display.mostrar_mensagem(instrucoes)
            self.buzzer.tocar_start()
            
            # Aguarda input para entrar no menu
            if self.joystick:
                while True:
                    if (self.joystick.botao_central_pressionado() or 
                        self.botoes.esta_pressionado_a() or 
                        self.botoes.esta_pressionado_b()):
                        sleep(0.2)
                        break
                    sleep(0.05)
            else:
                self.botoes.aguardar_qualquer_botao()
            
            # Navega no menu com joystick
            selecao = navegar_menu(self.display, self.botoes, "Menu Principal", opcoes, self.joystick)
            
            # Verifica a seleção
            if selecao < len(self.stages):
                # Inicia a etapa selecionada
                stage = self.stages[selecao](self.display, self.matriz, self.buzzer, self.botoes)
                score = stage.iniciar()
                
                # Armazena pontuação
                if score is not None:
                    self.scores[self.stage_names[selecao]] = score
                
                # Mostra resultado
                self.display.mostrar_mensagem([
                    f"Etapa: {self.stage_names[selecao]}",
                    f"Pontuacao: {score}" if score is not None else "Sem pontuacao",
                    "Pressione qualquer", 
                    "botao para continuar"
                ])
                
                # Aguarda input para continuar
                if self.joystick:
                    while True:
                        if (self.joystick.botao_central_pressionado() or 
                            self.botoes.esta_pressionado_a() or 
                            self.botoes.esta_pressionado_b()):
                            sleep(0.2)
                            break
                        sleep(0.05)
                else:
                    self.botoes.aguardar_qualquer_botao()
                
                # LIMPEZA GLOBAL: Remove todos os resíduos visuais/sonoros
                # antes de voltar ao menu principal
                self.limpar_hardware()
                
            else:
                # Sair
                self.display.mostrar_mensagem(["Obrigado " ,"por jogar!"])
                self.buzzer.tocar_fim_jogo()
                # Limpa hardware antes de sair
                self.limpar_hardware()
                break
    
    def _iniciar_modo_desafio(self):
        """Inicia todas as etapas em sequência (modo desafio)"""
        total_score = 0
        
        self.display.mostrar_mensagem([
            "Modo Desafio!", 
            "Todas etapas", 
            "em sequencia",
            "Pressione para iniciar"
        ])
        
        # Aguarda input para iniciar
        if self.joystick:
            while True:
                if (self.joystick.botao_central_pressionado() or 
                    self.botoes.esta_pressionado_a() or 
                    self.botoes.esta_pressionado_b()):
                    sleep(0.2)
                    break
                sleep(0.05)
        else:
            self.botoes.aguardar_qualquer_botao()
        
        # Executa todas as etapas
        for i, stage_class in enumerate(self.stages):
            self.display.mostrar_mensagem([
                f"Etapa {i+1}/{len(self.stages)}:",
                self.stage_names[i],
                "Pressione para iniciar"
            ])
            
            # Aguarda input para iniciar etapa
            if self.joystick:
                while True:
                    if (self.joystick.botao_central_pressionado() or 
                        self.botoes.esta_pressionado_a() or 
                        self.botoes.esta_pressionado_b()):
                        sleep(0.2)
                        break
                    sleep(0.05)
            else:
                self.botoes.aguardar_qualquer_botao()
            
            # Inicia a etapa
            stage = stage_class(self.display, self.matriz, self.buzzer, self.botoes)
            score = stage.iniciar()
            
            if score is not None:
                total_score += score
            
            # Mostra resultado parcial
            self.display.mostrar_mensagem([
                f"Etapa: {self.stage_names[i]}",
                f"Pontuacao: {score}" if score is not None else "Sem pontuacao",
                f"Total: {total_score}",
                "Pressione para continuar"
            ])
            
            # Aguarda input para continuar
            if self.joystick:
                while True:
                    if (self.joystick.botao_central_pressionado() or 
                        self.botoes.esta_pressionado_a() or 
                        self.botoes.esta_pressionado_b()):
                        sleep(0.2)
                        break
                    sleep(0.05)
            else:
                self.botoes.aguardar_qualquer_botao()
            
            # Limpa hardware entre etapas do modo desafio
            self.limpar_hardware()
        
        # Resultado final
        self.display.mostrar_mensagem([
            "Modo Desafio Concluido!",
            f"Pontuacao Total: {total_score}",
            "Pressione para voltar"
        ])
        self.buzzer.tocar_fim_jogo()
        
        # Aguarda input para voltar
        if self.joystick:
            while True:
                if (self.joystick.botao_central_pressionado() or 
                    self.botoes.esta_pressionado_a() or 
                    self.botoes.esta_pressionado_b()):
                    sleep(0.2)
                    break
                sleep(0.05)
        else:
            self.botoes.aguardar_qualquer_botao()
        
        # Limpa hardware ao final do modo desafio
        self.limpar_hardware()