# stages/stage_manager.py
# Gerenciador de etapas do jogo

from components.display import Display
from components.matriz_led import MatrizLED
from components.buzzer import Buzzer
from utils import Botoes, navegar_menu

class StageManager:
    def __init__(self):
        """Inicializa o gerenciador de etapas com os componentes básicos"""
        # Inicializa componentes de hardware
        self.display = Display()
        self.matriz = MatrizLED()
        self.buzzer = Buzzer()
        self.botoes = Botoes()
        
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
    
    def iniciar_menu(self):
        """Exibe o menu principal do jogo"""
        while True:
            # Opções do menu
            opcoes = self.stage_names + ["Modo Desafio", "Sair"]
            
            # Exibe o menu e aguarda seleção
            self.display.mostrar_mensagem(["BitdogLab Game", "Selecione:", 
                                         "Botao A: navegar", "Botao B: selecionar"])
            self.buzzer.tocar_start()
            self.botoes.aguardar_qualquer_botao()
            
            selecao = navegar_menu(self.display, self.botoes, "Menu Principal", opcoes)
            
            # Verifica a seleção
            if selecao < len(self.stages):
                # Inicia a etapa selecionada
                stage = self.stages[selecao](self.display, self.matriz, self.buzzer, self.botoes)
                score = stage.iniciar()
                
                # Armazena pontuação
                if score is not None:
                    self.scores[self.stage_names[selecao]] = score
                
                # Mostra resultado
                self.display.mostrar_mensagem([f"Etapa: {self.stage_names[selecao]}",
                                           f"Pontuação: {score}" if score is not None else "Sem pontuação",
                                           "Pressione qualquer", "botão para continuar"])
                self.botoes.aguardar_qualquer_botao()
                
            elif selecao == len(self.stages):
                # Modo Desafio - todas as etapas em sequência
                self._iniciar_modo_desafio()
                
            else:
                # Sair
                self.display.mostrar_mensagem(["Obrigado por jogar!"])
                self.buzzer.tocar_fim_jogo()
                break
    
    def _iniciar_modo_desafio(self):
        """Inicia todas as etapas em sequência (modo desafio)"""
        total_score = 0
        
        self.display.mostrar_mensagem(["Modo Desafio!", 
                                     "Todas etapas", 
                                     "em sequência",
                                     "Pressione para iniciar"])
        self.botoes.aguardar_qualquer_botao()
        
        # Executa todas as etapas
        for i, stage_class in enumerate(self.stages):
            self.display.mostrar_mensagem([f"Etapa {i+1}/{len(self.stages)}:",
                                         self.stage_names[i],
                                         "Pressione para iniciar"])
            self.botoes.aguardar_qualquer_botao()
            
            # Inicia a etapa
            stage = stage_class(self.display, self.matriz, self.buzzer, self.botoes)
            score = stage.iniciar()
            
            if score is not None:
                total_score += score
            
            # Mostra resultado parcial
            self.display.mostrar_mensagem([f"Etapa: {self.stage_names[i]}",
                                         f"Pontuação: {score}" if score is not None else "Sem pontuação",
                                         f"Total: {total_score}",
                                         "Pressione para continuar"])
            self.botoes.aguardar_qualquer_botao()
        
        # Resultado final
        self.display.mostrar_mensagem(["Modo Desafio Concluído!",
                                     f"Pontuação Total: {total_score}",
                                     "Pressione para voltar"])
        self.buzzer.tocar_fim_jogo()
        self.botoes.aguardar_qualquer_botao()