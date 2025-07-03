# stages/rhythm_game.py
# Jogo de ritmo: pressione os botões no tempo certo

import config
from utime import sleep, ticks_ms, ticks_diff
import urandom
from utils import contagem_regressiva

class RhythmGame:
    def __init__(self, display, matriz, buzzer, botoes):
        """Inicializa o jogo de ritmo"""
        self.display = display
        self.matriz = matriz
        self.buzzer = buzzer
        self.botoes = botoes
        self.pontuacao = 0
        self.total_notas = 20  # Total de notas em uma música
        
        # Definição de faixas (tracks) para as notas caírem
        self.tracks = [
            {"x": 1, "botao": 1, "cor": config.COR_VERDE},    # Faixa esquerda (Botão A)
            {"x": 3, "botao": 2, "cor": config.COR_VERMELHO}  # Faixa direita (Botão B)
        ]
        
        # Mapeamento de faixa para nota musical
        self.track_notas = {
            0: "C4",  # Faixa esquerda
            1: "G4"   # Faixa direita
        }
        
        # Zona de batida (hit zone) - altura onde a nota deve ser pressionada
        self.hit_zone_y = 0
    
    def iniciar(self):
        """Inicia o jogo de ritmo"""
        # Mensagem inicial no display
        self.display.mostrar_mensagem([
            "Jogo de Ritmo",
            "Pressione o botao",
            "quando a nota atingir",
            "a linha inferior",
            "Pressione para iniciar"
        ])
        
        # Aguarda qualquer botão ser pressionado para iniciar
        self.botoes.aguardar_qualquer_botao()
        
        # Contador regressivo
        contagem_regressiva(self.display, self.buzzer)
        
        # Reinicia pontuação
        self.pontuacao = 0
        
        # Mostra a interface do jogo
        self._mostrar_interface()
        
        # Gera sequência de notas (0 = esquerda/A, 1 = direita/B)
        notas = []
        for _ in range(self.total_notas):
            track = urandom.randint(0, 1)
            notas.append(track)
        
        # Tempo entre notas (em segundos)
        tempo_entre_notas = 1.5
        
        # Executa a música (as notas)
        nota_atual = 0
        while nota_atual < len(notas):
            # Pega a próxima nota
            track = notas[nota_atual]
            
            # Exibe informações no display
            self.display.mostrar_mensagem([
                "Jogo de Ritmo",
                f"Pontuacao: {self.pontuacao}",
                f"Nota: {nota_atual+1}/{len(notas)}"
            ])
            
            # Animação da nota caindo
            resultado = self._animar_nota_caindo(track, tempo_entre_notas)
            
            # Atualiza pontuação com base no resultado
            if resultado == "perfeito":
                self.pontuacao += 10
            elif resultado == "bom":
                self.pontuacao += 5
            elif resultado == "ok":
                self.pontuacao += 2
            # Sem pontos para "errado"
            
            # Avança para a próxima nota
            nota_atual += 1
        
        # Fim do jogo
        self.buzzer.tocar_fim_jogo()
        self.display.mostrar_mensagem([
            "Ritmo Completo!",
            f"Pontuacao: {self.pontuacao}",
            f"Max Possivel: {self.total_notas * 10}",
            "Pressione para continuar"
        ])
        
        # Aguarda botão para continuar
        self.botoes.aguardar_qualquer_botao()
        
        return self.pontuacao
    
    def _mostrar_interface(self):
        """Mostra a interface básica do jogo de ritmo"""
        # Limpa tudo
        self.matriz.apagar()
        
        # Mostra as duas faixas
        for track in self.tracks:
            # Acende LED na hit zone para indicar onde pressionar
            self.matriz.acender_led_cor(track["x"], self.hit_zone_y, track["cor"])
            sleep(0.2)
        
        # Apaga os LEDs da hit zone após mostrar
        for track in self.tracks:
            self.matriz.apagar_led(track["x"], self.hit_zone_y)
    
    def _animar_nota_caindo(self, track_idx, tempo_total):
        """
        Anima uma nota caindo na faixa especificada
        track_idx: índice da faixa (0 ou 1)
        tempo_total: tempo total da animação
        Retorna: resultado da batida ("perfeito", "bom", "ok", "errado")
        """
        track = self.tracks[track_idx]
        x = track["x"]
        botao = track["botao"]
        cor = track["cor"]
        
        # Níveis de altura para a animação (de cima para baixo)
        alturas = [4, 3, 2, 1, 0]  # 0 é a linha inferior (hit zone)
        
        # Tempo por frame da animação
        tempo_por_frame = tempo_total / len(alturas)
        
        # Inicializa variáveis para acompanhar o timing
        acertou = False
        timing_error = 0
        botao_pressionado = None
        
        # Para cada nível de altura
        for i, y in enumerate(alturas):
            # Mostra a nota na posição atual
            self.matriz.acender_led_cor(x, y, cor)
            
            # Toca som se for a primeira vez que a nota aparece
            if i == 0:
                nota = self.track_notas[track_idx]
                self.buzzer.tocar_nota(nota, 100)
            
            # Tempo de início deste frame
            t_inicio = ticks_ms()
            
            # Tempo limite para este frame
            tempo_limite = tempo_por_frame * 1000  # em ms
            
            # Verifica se o botão é pressionado durante este frame
            while ticks_diff(ticks_ms(), t_inicio) < tempo_limite:
                # Verifica botão A
                if self.botoes.esta_pressionado_a() and not acertou:
                    botao_pressionado = 1
                    timing_error = abs(y - self.hit_zone_y)  # Distância da hit zone
                    acertou = True
                    break
                
                # Verifica botão B
                if self.botoes.esta_pressionado_b() and not acertou:
                    botao_pressionado = 2
                    timing_error = abs(y - self.hit_zone_y)  # Distância da hit zone
                    acertou = True
                    break
            
            # Apaga o LED da posição atual
            self.matriz.apagar_led(x, y)
            
            # Se acertou neste frame, interrompe a animação
            if acertou:
                break
        
        # Avalia o resultado
        resultado = "errado"
        
        if acertou:
            # Verifica se pressionou o botão correto
            if botao_pressionado == botao:
                # Avalia o timing
                if timing_error == 0:
                    resultado = "perfeito"
                    self.display.texto("PERFEITO!", 30, 30)
                    self.buzzer.tocar_nota(self.track_notas[track_idx], 150)
                elif timing_error == 1:
                    resultado = "bom"
                    self.display.texto("BOM!", 45, 30)
                    self.buzzer.tocar_nota(self.track_notas[track_idx], 100)
                else:
                    resultado = "ok"
                    self.display.texto("OK", 55, 30)
                    self.buzzer.tocar_nota(self.track_notas[track_idx], 80)
            else:
                # Botão errado
                self.display.texto("ERRADO!", 35, 30)
                self.buzzer.tocar_som(200, 200)  # Som de erro
        else:
            # Não pressionou nenhum botão
            self.display.texto("FALTA!", 40, 30)
            self.buzzer.tocar_som(200, 200)  # Som de erro
        
        # Exibe o resultado brevemente
        sleep(0.3)
        
        return resultado