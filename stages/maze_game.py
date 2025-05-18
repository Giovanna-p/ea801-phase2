# stages/maze_game.py
# Jogo de labirinto: navegue pelo labirinto inclinando o dispositivo

import config
from utime import sleep, ticks_ms, ticks_diff
import urandom
from utils import contagem_regressiva
from machine import I2C, Pin, SoftI2C

class MazeGame:
    def __init__(self, display, matriz, buzzer, botoes):
        """Inicializa o jogo de labirinto"""
        self.display = display
        self.matriz = matriz
        self.buzzer = buzzer
        self.botoes = botoes
        self.pontuacao = 0
        self.nivel_atual = 1
        self.max_niveis = 3
        self.tempo_inicio = 0
        self.tempo_total = 0  # Será atualizado com base no nível
        
        # Configuração do MPU-6050
        try:
            # Tenta inicializar o I2C em hardware
            self.i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
            print("I2C inicializado com ID 0")
        except Exception as e:
            print(f"Erro ao inicializar I2C: {e}")
            # Fallback para SoftI2C
            self.i2c = SoftI2C(scl=Pin(1), sda=Pin(0), freq=100000)
            print("Usando SoftI2C")
        
        self.mpu_addr = 0x68  # Endereço padrão do MPU-6050
        
        # Verifica se o sensor está presente
        self.sensor_presente = self.mpu_addr in self.i2c.scan()
        if self.sensor_presente:
            # Inicializa o sensor
            self.i2c.writeto_mem(self.mpu_addr, 0x6B, b'\x00')  # Acorda o MPU-6050
            sleep(0.1)
        
        # Definição dos labirintos
        # 0 = caminho livre, 1 = parede, 2 = início, 3 = saída
        self.labirintos = [
            # Nível 1 - Labirinto simples
            [
                [1, 1, 1, 1, 1],
                [1, 2, 0, 0, 1],
                [1, 1, 1, 0, 1],
                [1, 3, 0, 0, 1],
                [1, 1, 1, 1, 1]
            ],
            # Nível 2 - Labirinto médio
            [
                [1, 1, 1, 1, 1],
                [1, 2, 0, 0, 1],
                [1, 1, 1, 0, 1],
                [1, 0, 0, 0, 1],
                [1, 3, 1, 1, 1]
            ],
            # Nível 3 - Labirinto difícil
            [
                [1, 1, 1, 1, 1],
                [1, 2, 0, 0, 1],
                [1, 1, 1, 0, 1],
                [1, 0, 1, 0, 1],
                [1, 3, 1, 1, 1]
            ]
        ]
        
        # Posição inicial (será definida ao iniciar cada nível)
        self.jogador_x = 0
        self.jogador_y = 0
        
        # Posição da saída (será definida ao iniciar cada nível)
        self.saida_x = 0
        self.saida_y = 0
    
    def iniciar(self):
        """Inicia o jogo de labirinto"""
        # Verifica se o sensor está disponível
        if not self.sensor_presente:
            self.display.mostrar_mensagem([
                "Erro!",
                "Sensor MPU-6050",
                "nao encontrado!",
                "Verifique conexao"
            ])
            sleep(3)
            return None
        
        # Mensagem inicial no display
        self.display.mostrar_mensagem([
            "Jogo de Labirinto",
            "Encontre a saida",
            "inclinando o dispositivo",
            "Pressione para iniciar"
        ])
        
        # Aguarda qualquer botão ser pressionado para iniciar
        self.botoes.aguardar_qualquer_botao()
        
        # Reinicia pontuação e nível
        self.pontuacao = 0
        self.nivel_atual = 1
        
        # Loop principal para cada nível
        while self.nivel_atual <= self.max_niveis:
            # Inicia o nível atual
            resultado = self._jogar_nivel()
            
            # Se retornou False, o jogador saiu ou perdeu
            if not resultado:
                break
            
            # Avança para o próximo nível
            self.nivel_atual += 1
            
            # Mensagem de transição
            if self.nivel_atual <= self.max_niveis:
                self.display.mostrar_mensagem([
                    f"Nivel {self.nivel_atual-1} Concluido!",
                    f"Pontuacao: {self.pontuacao}",
                    "Preparando proximo nivel",
                    "Pressione para continuar"
                ])
                self.botoes.aguardar_qualquer_botao()
        
        # Final do jogo (todos os níveis concluídos ou saiu)
        self.buzzer.tocar_fim_jogo()
        if self.nivel_atual > self.max_niveis:
            self.display.mostrar_mensagem([
                "Parabens!",
                "Todos os niveis concluidos!",
                f"Pontuacao final: {self.pontuacao}",
                "Pressione para sair"
            ])
        else:
            self.display.mostrar_mensagem([
                "Fim de jogo!",
                f"Nivel alcancado: {self.nivel_atual}",
                f"Pontuacao final: {self.pontuacao}",
                "Pressione para sair"
            ])
        
        # Aguarda botão para continuar
        self.botoes.aguardar_qualquer_botao()
        
        return self.pontuacao
    
    def _jogar_nivel(self):
        """
        Executa um nível do jogo
        Retorna True se o nível foi concluído, False se o jogador saiu
        """
        # Obtem o labirinto atual
        labirinto = self.labirintos[self.nivel_atual - 1]
        
        # Encontra a posição inicial e a saída
        for y in range(5):
            for x in range(5):
                if labirinto[y][x] == 2:  # Início
                    self.jogador_x = x
                    self.jogador_y = y
                elif labirinto[y][x] == 3:  # Saída
                    self.saida_x = x
                    self.saida_y = y
        
        # Define o tempo para este nível (mais difícil = mais tempo)
        self.tempo_total = 30 + (self.nivel_atual * 10)  # 40, 50, 60 segundos
        
        # Conta regressiva para iniciar
        contagem_regressiva(self.display, self.buzzer)
        
        # Registra o tempo de início
        self.tempo_inicio = ticks_ms()
        ultima_atualizacao_display = ticks_ms()
        ultimo_movimento = ticks_ms()
        
        # Loop principal do nível
        while True:
            tempo_atual = ticks_ms()
            tempo_passado = ticks_diff(tempo_atual, self.tempo_inicio) / 1000  # em segundos
            
            # Verifica se o tempo acabou
            if tempo_passado >= self.tempo_total:
                self.display.mostrar_mensagem([
                    "Tempo Esgotado!",
                    "Tente novamente"
                ])
                sleep(2)
                return False
            
            # Atualiza o display a cada 500ms
            if ticks_diff(tempo_atual, ultima_atualizacao_display) > 500:
                self.display.mostrar_mensagem([
                    f"Nivel: {self.nivel_atual}/{self.max_niveis}",
                    f"Tempo: {int(self.tempo_total - tempo_passado)}s",
                    "Incline para mover",
                    "Bot. B para sair"
                ])
                ultima_atualizacao_display = tempo_atual
            
            # Verifica se o botão B foi pressionado (sair)
            if self.botoes.esta_pressionado_b():
                return False
            
            # Atualiza a posição do jogador a cada 200ms
            if ticks_diff(tempo_atual, ultimo_movimento) > 200:
                # Lê os dados do acelerômetro
                dados = self._ler_mpu6050()
                if dados:
                    # Move o jogador com base na inclinação
                    self._mover_jogador(dados['accel']['x'], dados['accel']['y'])
                    
                    # Verifica se alcançou a saída
                    if self.jogador_x == self.saida_x and self.jogador_y == self.saida_y:
                        # Calcula pontuação para este nível (tempo restante + bônus de nível)
                        tempo_restante = self.tempo_total - tempo_passado
                        bonus_nivel = self.nivel_atual * 50
                        pontos_nivel = int(tempo_restante * 10) + bonus_nivel
                        self.pontuacao += pontos_nivel
                        
                        # Efeito sonoro de vitória
                        self.buzzer.tocar_fim_jogo()
                        
                        return True  # Nível concluído
                
                # Atualiza a matriz de LEDs
                self._atualizar_matriz(labirinto)
                ultimo_movimento = tempo_atual
            
            # Pausa para economizar CPU
            sleep(0.01)
    
    def _ler_mpu6050(self):
        """Lê os dados do acelerômetro e giroscópio do MPU-6050"""
        try:
            # Lê os dados do acelerômetro (registros 0x3B-0x40)
            data = self.i2c.readfrom_mem(self.mpu_addr, 0x3B, 6)
            
            # Converte os dados (cada valor é de 16 bits, em complemento de 2)
            accel_x = (data[0] << 8) | data[1]
            accel_y = (data[2] << 8) | data[3]
            accel_z = (data[4] << 8) | data[5]
            
            # Converte para valor com sinal
            if accel_x > 32767:
                accel_x -= 65536
            if accel_y > 32767:
                accel_y -= 65536
            if accel_z > 32767:
                accel_z -= 65536
            
            # Converte para unidades g (±2g)
            accel_x_g = accel_x / 16384.0
            accel_y_g = accel_y / 16384.0
            accel_z_g = accel_z / 16384.0
            
            return {
                'accel': {
                    'x': accel_x_g,
                    'y': accel_y_g,
                    'z': accel_z_g
                }
            }
        except Exception as e:
            print(f"Erro ao ler MPU-6050: {e}")
            return None
    
    def _mover_jogador(self, accel_x, accel_y):
        """Move o jogador com base nos dados do acelerômetro"""
        # Os valores do acelerômetro indicam inclinação
        # Positivo em X inclina para a direita, negativo para a esquerda
        # Positivo em Y inclina para frente, negativo para trás
        
        # Determina a direção da movimentação com um limiar
        novo_x = self.jogador_x
        novo_y = self.jogador_y
        
        # Ajusta a sensibilidade conforme necessário
        sensibilidade = 0.3
        
        # Atualiza X (accel_y move no eixo X da matriz)
        if accel_y > sensibilidade:
            novo_x = max(0, self.jogador_x - 1)  # Move para a esquerda
        elif accel_y < -sensibilidade:
            novo_x = min(4, self.jogador_x + 1)  # Move para a direita
        
        # CORREÇÃO: Inverte a direção do eixo Y
        # Antes: accel_x positivo (inclinação para frente) movia para baixo
        # Agora: accel_x positivo (inclinação para frente) move para cima
        if accel_x > sensibilidade:
            novo_y = max(0, self.jogador_y - 1)  # Move para cima (inclinação para frente)
        elif accel_x < -sensibilidade:
            novo_y = min(4, self.jogador_y + 1)  # Move para baixo (inclinação para trás)
        
        # Verifica se a nova posição é válida (não é uma parede)
        labirinto = self.labirintos[self.nivel_atual - 1]
        
        # Verifica movimento em X
        if novo_x != self.jogador_x and labirinto[self.jogador_y][novo_x] != 1:
            self.jogador_x = novo_x
            self.buzzer.tocar_som(800, 10)  # Som de movimento
        
        # Verifica movimento em Y
        if novo_y != self.jogador_y and labirinto[novo_y][self.jogador_x] != 1:
            self.jogador_y = novo_y
            self.buzzer.tocar_som(800, 10)  # Som de movimento
    
    def _atualizar_matriz(self, labirinto):
        """Atualiza a visualização do labirinto na matriz de LEDs"""
        self.matriz.apagar()
        
        # Mostra o labirinto
        for y in range(5):
            for x in range(5):
                if labirinto[y][x] == 1:  # Parede
                    self.matriz.acender_led_cor(x, y, config.COR_BRANCO)
                elif labirinto[y][x] == 3:  # Saída
                    if (ticks_ms() // 200) % 2 == 0:  # Pisca a cada 200ms
                        self.matriz.acender_led_cor(x, y, config.COR_VERDE)
        
        # Mostra o jogador (sempre visível, por cima de tudo)
        self.matriz.acender_led_cor(self.jogador_x, self.jogador_y, config.COR_AZUL)