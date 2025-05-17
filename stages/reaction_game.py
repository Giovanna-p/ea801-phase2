# stages/reaction_game.py
# Jogo de reação: pressione o botão quando ver o LED verde

import config
from utime import sleep, ticks_ms, ticks_diff
import urandom
from utils import contagem_regressiva

class ReactionGame:
    def __init__(self, display, matriz, buzzer, botoes):
        """Inicializa o jogo de reação"""
        self.display = display
        self.matriz = matriz
        self.buzzer = buzzer
        self.botoes = botoes
        self.resultados = []  # Lista para armazenar os tempos de reação
        self.rodadas = 3      # Número de rodadas
        
        # Cores disponíveis para o jogo
        self.cores = [
            config.COR_VERDE,    # Verde - cor alvo
            config.COR_AZUL,     # Azul - distrator
            config.COR_VERMELHO, # Vermelho - distrator
            config.COR_BRANCO    # Branco - distrator
        ]
    
    def iniciar(self):
        """Inicia o jogo de reação"""
        # Mensagem inicial no display
        self.display.mostrar_mensagem([
            "Jogo de Reacao",
            "Aperte bot. A",
            "APENAS quando",
            "aparecer LED VERDE",
            "Ignore outras cores"
        ])
        
        # Aguarda o botão ser pressionado para iniciar
        self.botoes.aguardar_botao_a()
        
        # Contador regressivo
        contagem_regressiva(self.display, self.buzzer)
        
        self.buzzer.tocar_start()
        self.resultados = []  # Limpa resultados anteriores
        
        # Laço principal: rodadas de teste de reação
        for i in range(self.rodadas):
            self.display.mostrar_mensagem([
                f"Rodada {i+1}/{self.rodadas}",
                "Aguarde..."
            ])
            
            # Executa uma rodada
            if not self._executar_rodada():
                # Se retornou False, houve game over
                return None
        
        # Toca melodia de fim de jogo se concluiu todas as rodadas
        if len(self.resultados) > 0:
            self.buzzer.tocar_fim_jogo()
            
            # Exibe os tempos no OLED
            self.display.exibir_tempos(self.resultados)
            
            # Calcular estatísticas
            tempo_medio = sum(self.resultados) / len(self.resultados)
            melhor_tempo = min(self.resultados)
            
            # Rolar para baixo e mostrar estatísticas adicionais
            sleep(3)  # Tempo para visualizar o ranking
            self.display.mostrar_mensagem([
                "Estatisticas:",
                f"Media: {tempo_medio/1000:.3f}s",
                f"Melhor: {melhor_tempo/1000:.3f}s",
                "Botao B para continuar"
            ])
            
            # Também exibe os resultados no terminal (útil para debug)
            print("Tempos de reação (em milissegundos):")
            for i, tempo in enumerate(self.resultados, 1):
                print(f"Tentativa {i}: {tempo} ms")
            print(f"Tempo médio: {tempo_medio:.2f} ms")
            print(f"Melhor tempo: {melhor_tempo:.2f} ms")
            
            # Aguarda o botão B ser pressionado para continuar
            self.botoes.aguardar_botao_b()
            
            # O score para este jogo é o tempo médio (quanto menor, melhor)
            return melhor_tempo
        else:
            # Se não tiver resultados, mostra mensagem
            self.display.mostrar_mensagem([
                "Sem resultados!",
                "Tente novamente"
            ])
            sleep(2)
            return None
    
    def _executar_rodada(self):
        """
        Executa uma rodada do jogo de reação
        Retorna True se a rodada foi concluída com sucesso, False se houve game over
        """
        # Número de distratores (de 1 a 3 luzes antes da verde)
        num_distratores = urandom.randint(1, 3)
        
        # Loop para mostrar os distratores e a cor alvo (verde)
        for j in range(num_distratores + 1):
            self.matriz.apagar()  # Garante que os LEDs estejam apagados antes de iniciar
            
            espera = urandom.uniform(0.8, 2.0)  # Tempo de espera aleatório entre as luzes
            sleep(espera)  # Aguarda o tempo gerado
            
            # Gera posição aleatória para o LED
            x, y = self.matriz.posicao_aleatoria()
            
            # Seleciona uma cor aleatória, ou verde se for a última luz
            if j == num_distratores:
                cor_atual = self.cores[0]  # Verde (alvo)
            else:
                # Seleciona uma cor distratora aleatória (não verde)
                cor_atual = self.cores[urandom.randint(1, 3)]
            
            # Acende o LED na posição aleatória com a cor selecionada
            self.matriz.acender_led_cor(x, y, cor_atual)
            
            t_inicio = ticks_ms()  # Marca o tempo atual
            
            # Verifica se o botão é pressionado enquanto a luz está acesa
            botao_pressionado = False
            t_reacao = 0
            
            # Tempo máximo que a luz ficará acesa (1 segundo)
            tempo_maximo = config.LED_MAX_TIME  # em milissegundos
            
            while ticks_diff(ticks_ms(), t_inicio) < tempo_maximo:
                if self.botoes.esta_pressionado_a():  # Botão pressionado
                    botao_pressionado = True
                    t_atual = ticks_ms()
                    t_reacao = ticks_diff(t_atual, t_inicio)
                    break
            
            # Verifica se o botão foi pressionado e se a cor era verde
            if botao_pressionado:
                if cor_atual == self.cores[0]:  # Verde
                    # Acertou! Era verde e clicou
                    self.buzzer.bipe_reacao()
                    self.resultados.append(t_reacao)
                    
                    # Exibe o resultado da rodada
                    self.display.mostrar_mensagem([
                        f"Tempo: {t_reacao/1000:.3f}s",
                        "Muito bem!"
                    ])
                    
                    sleep(1.5)  # Tempo para visualizar o resultado
                    return True  # Rodada concluída com sucesso
                else:
                    # Errou! Clicou em uma cor diferente de verde
                    self.matriz.apagar()
                    
                    # Pisca o LED em vermelho para indicar erro
                    self.matriz.piscar_led(x, y, config.COR_VERMELHO)
                    
                    self.buzzer.tocar_game_over()
                    self.display.exibir_game_over()
                    sleep(2)
                    return False  # Game over
            
            # Se chegou ao final do loop com a luz verde e não clicou
            elif cor_atual == self.cores[0]:
                # Não clicou no verde - tempo de reação ruim
                self.matriz.apagar()
                self.display.mostrar_mensagem([
                    "Muito lento!",
                    "Tente novamente"
                ])
                sleep(1.5)
                return True  # Continua para próxima rodada
            
            self.matriz.apagar()  # Apaga o LED após o período de exibição
        
        return True  # Se chegou até aqui, a rodada foi concluída com sucesso