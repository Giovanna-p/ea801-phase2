# stages/memory_game.py
# Jogo de memória: memorize e repita a sequência de cores

import config
from utime import sleep, ticks_ms, ticks_diff
import urandom
from utils import contagem_regressiva

class MemoryGame:
    def __init__(self, display, matriz, buzzer, botoes):
        """Inicializa o jogo de memória"""
        self.display = display
        self.matriz = matriz
        self.buzzer = buzzer
        self.botoes = botoes
        self.sequencia = []          # Sequência de cores a ser memorizada
        self.nivel = 1               # Nível atual (tamanho da sequência)
        self.max_nivel = 10          # Nível máximo
        self.posicoes_botoes = {     # Mapeamento de posições/cores para botões
            1: {"pos": (1, 1), "cor": config.COR_VERDE},    # Botão A: Verde
            2: {"pos": (3, 1), "cor": config.COR_VERMELHO}  # Botão B: Vermelho
        }
        
        # Mapeamento de cores para notas musicais
        self.cores_notas = {
            config.COR_VERDE: "C4",
            config.COR_VERMELHO: "G4"
        }
    
    def iniciar(self):
        """Inicia o jogo de memória"""
        # Mensagem inicial no display
        self.display.mostrar_mensagem([
            "Jogo de Memoria",
            "Memorize a sequencia",
            "Bot. A = Verde",
            "Bot. B = Vermelho",
            "Pressione para iniciar"
        ])
        
        # Aguarda qualquer botão ser pressionado para iniciar
        self.botoes.aguardar_qualquer_botao()
        
        # Contador regressivo
        contagem_regressiva(self.display, self.buzzer)
        
        # Reinicia o jogo
        self.nivel = 1
        pontuacao = 0
        
        # Loop principal do jogo
        while self.nivel <= self.max_nivel:
            self.display.mostrar_mensagem([
                f"Nivel {self.nivel}",
                "Observe a sequencia"
            ])
            sleep(1)
            
            # Gera sequência para o nível atual
            self._gerar_sequencia()
            
            # Mostra a sequência
            self._mostrar_sequencia()
            
            # Aguarda a resposta do jogador
            self.display.mostrar_mensagem([
                f"Nivel {self.nivel}",
                "Repita a sequencia",
                "Bot. A = Verde",
                "Bot. B = Vermelho"
            ])
            
            # Verifica a resposta
            if self._verificar_resposta():
                # Resposta correta
                self.buzzer.tocar_fim_jogo()
                self.display.mostrar_mensagem([
                    "Correto!",
                    f"Nivel {self.nivel} completado"
                ])
                pontuacao += self.nivel
                sleep(1)
                
                # Avança para o próximo nível
                self.nivel += 1
            else:
                # Resposta incorreta - fim de jogo
                self.buzzer.tocar_game_over()
                self.display.mostrar_mensagem([
                    "Game Over!",
                    f"Voce chegou ao nivel {self.nivel}",
                    f"Pontuacao: {pontuacao}"
                ])
                sleep(2)
                break
                
        # Se completou todos os níveis
        if self.nivel > self.max_nivel:
            self.display.mostrar_mensagem([
                "Parabens!",
                "Voce completou",
                "todos os niveis!",
                f"Pontuacao: {pontuacao}"
            ])
            self.buzzer.tocar_fim_jogo()
            sleep(2)
        
        # Aguarda botão para continuar
        self.display.mostrar_mensagem([
            "Jogo finalizado",
            f"Pontuacao: {pontuacao}",
            "Pressione para continuar"
        ])
        self.botoes.aguardar_qualquer_botao()
        
        return pontuacao
    
    def _gerar_sequencia(self):
        """Gera uma sequência aleatória para o nível atual"""
        self.sequencia = []
        for _ in range(self.nivel):
            # Gera 1 (botão A) ou 2 (botão B)
            botao = urandom.randint(1, 2)
            self.sequencia.append(botao)
    
    def _mostrar_sequencia(self):
        """Mostra a sequência de cores para o jogador memorizar"""
        # Tempo base para exibição (diminui com o nível para aumentar dificuldade)
        tempo_base = max(0.3, 1.0 - (self.nivel * 0.05))
        
        for botao in self.sequencia:
            # Obtém posição e cor do botão
            pos = self.posicoes_botoes[botao]["pos"]
            cor = self.posicoes_botoes[botao]["cor"]
            nota = self.cores_notas.get(cor, "C4")
            
            # Acende o LED e toca a nota
            self.matriz.acender_led_cor(pos[0], pos[1], cor)
            self.buzzer.tocar_nota(nota, 200)
            
            # Aguarda um tempo
            sleep(tempo_base)
            
            # Apaga o LED
            self.matriz.apagar_led(pos[0], pos[1])
            sleep(0.2)  # Pequena pausa entre cada cor
    
    def _verificar_resposta(self):
        """
        Verifica se a resposta do jogador está correta
        Retorna True se estiver correta, False caso contrário
        """
        for i, botao_correto in enumerate(self.sequencia):
            # Mostrar qual botão se espera (opcional, para debug)
            print(f"Esperando botão {botao_correto} (posição {i+1})")
            
            # Aguarda qualquer botão ser pressionado
            botao_pressionado = self.botoes.aguardar_qualquer_botao()
            
            # Acende o LED correspondente ao botão pressionado
            pos = self.posicoes_botoes[botao_pressionado]["pos"]
            cor = self.posicoes_botoes[botao_pressionado]["cor"]
            nota = self.cores_notas.get(cor, "C4")
            
            # Feedback visual e sonoro
            self.matriz.acender_led_cor(pos[0], pos[1], cor)
            self.buzzer.tocar_nota(nota, 200)
            sleep(0.1)
            self.matriz.apagar_led(pos[0], pos[1])
            
            # Verifica se o botão pressionado é o correto
            if botao_pressionado != botao_correto:
                return False
        
        # Se chegou aqui, toda a sequência está correta
        return True