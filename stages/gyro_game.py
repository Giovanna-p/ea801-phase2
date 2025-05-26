# stages/gyro_game.py
# Jogo que utiliza o giroscópio para controle rotacional

import config
from utime import sleep, ticks_ms, ticks_diff
import urandom
from utils import contagem_regressiva
from machine import I2C, Pin, SoftI2C
import math

class GyroGame:
    def __init__(self, display, matriz, buzzer, botoes):
        """Inicializa o jogo de giroscópio"""
        self.display = display
        self.matriz = matriz
        self.buzzer = buzzer
        self.botoes = botoes
        self.pontuacao = 0
        self.tempo_total = 30  # segundos de jogo
        self.alvos_acertados = 0
        
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
        
        # Posição atual do ponteiro (centro da matriz)
        self.ponteiro_x = 2
        self.ponteiro_y = 2
        
        # Posição do alvo atual
        self.alvo_x = 0
        self.alvo_y = 0
        
        # Direção atual do ponteiro (em graus, 0 = direita, 90 = cima)
        self.direcao = 0
        
        # Lista de direções dos LEDs a partir do centro
        # Cada item é [x, y] representando uma direção
        self.direcoes = [
            [1, 0],   # 0 graus (direita)
            [1, 1],   # 45 graus (direita-cima)
            [0, 1],   # 90 graus (cima)
            [-1, 1],  # 135 graus (esquerda-cima)
            [-1, 0],  # 180 graus (esquerda)
            [-1, -1], # 225 graus (esquerda-baixo)
            [0, -1],  # 270 graus (baixo)
            [1, -1]   # 315 graus (direita-baixo)
        ]
        
    def iniciar(self):
        """Inicia o jogo de giroscópio"""
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
            "Gire a placa,",
            "aponte para o",
            "alvo amarelo",
            "e pressione o",
            "botao A"          
        ])
        
        # Aguarda qualquer botão ser pressionado para iniciar
        self.botoes.aguardar_qualquer_botao()
        
        # Contador regressivo
        contagem_regressiva(self.display, self.buzzer)
        
        # Reinicia pontuação e gera primeiro alvo
        self.pontuacao = 0
        self.alvos_acertados = 0
        self._gerar_novo_alvo()
        
        # Tempo inicial
        tempo_inicio = ticks_ms()
        ultimo_movimento = ticks_ms()
        ultima_atualizacao_display = ticks_ms()
        
        # Laço principal do jogo
        while True:
            tempo_atual = ticks_ms()
            tempo_passado = ticks_diff(tempo_atual, tempo_inicio) / 1000  # em segundos
            
            # Verifica se o tempo acabou
            if tempo_passado >= self.tempo_total:
                break
            
            # Atualiza o display a cada 500ms
            if ticks_diff(tempo_atual, ultima_atualizacao_display) > 500:
                self.display.mostrar_mensagem([
                    "Jogo de Giroscopio",
                    f"Tempo: {int(self.tempo_total - tempo_passado)}s",
                    f"Alvos: {self.alvos_acertados}",
                    f"Pontuacao: {self.pontuacao}"
                ])
                ultima_atualizacao_display = tempo_atual
            
            # Atualiza a direção do ponteiro a cada 100ms
            if ticks_diff(tempo_atual, ultimo_movimento) > 100:
                # Lê os dados do giroscópio
                dados = self._ler_mpu6050()
                if dados:
                    # Atualiza a direção com base na rotação do giroscópio
                    self._atualizar_direcao(dados['gyro']['z'])
                    
                    # Verifica se o botão A é pressionado para "atirar"
                    if self.botoes.esta_pressionado_a():
                        self._verificar_acerto()
                
                # Atualiza a matriz de LEDs
                self._atualizar_matriz()
                ultimo_movimento = tempo_atual
            
            # Pausa para economizar CPU
            sleep(0.01)
        
        # Fim do jogo
        self.buzzer.tocar_fim_jogo()
        self.matriz.apagar()
        self.display.mostrar_mensagem([
            "Tempo Esgotado!",
            f"Alvos acertados: {self.alvos_acertados}",
            f"Pontuacao: {self.pontuacao}",
            "Pressione para continuar"
        ])
        
        # Aguarda botão para continuar
        self.botoes.aguardar_qualquer_botao()
        
        return self.pontuacao
    
    def _ler_mpu6050(self):
        """Lê os dados do acelerômetro e giroscópio do MPU-6050"""
        try:
            # Lê os dados do acelerômetro e giroscópio (registros 0x3B-0x48)
            data = self.i2c.readfrom_mem(self.mpu_addr, 0x3B, 14)
            
            # Converte os dados (cada valor é de 16 bits, em complemento de 2)
            accel_x = (data[0] << 8) | data[1]
            accel_y = (data[2] << 8) | data[3]
            accel_z = (data[4] << 8) | data[5]
            
            # Pula a temperatura (bytes 6 e 7)
            
            gyro_x = (data[8] << 8) | data[9]
            gyro_y = (data[10] << 8) | data[11]
            gyro_z = (data[12] << 8) | data[13]
            
            # Converte para valor com sinal
            if accel_x > 32767:
                accel_x -= 65536
            if accel_y > 32767:
                accel_y -= 65536
            if accel_z > 32767:
                accel_z -= 65536
            
            if gyro_x > 32767:
                gyro_x -= 65536
            if gyro_y > 32767:
                gyro_y -= 65536
            if gyro_z > 32767:
                gyro_z -= 65536
            
            # Converte para unidades g (±2g) e graus/s (±250°/s)
            accel_x_g = accel_x / 16384.0
            accel_y_g = accel_y / 16384.0
            accel_z_g = accel_z / 16384.0
            
            gyro_x_deg = gyro_x / 131.0
            gyro_y_deg = gyro_y / 131.0
            gyro_z_deg = gyro_z / 131.0
            
            return {
                'accel': {
                    'x': accel_x_g,
                    'y': accel_y_g,
                    'z': accel_z_g
                },
                'gyro': {
                    'x': gyro_x_deg,
                    'y': gyro_y_deg,
                    'z': gyro_z_deg
                }
            }
        except Exception as e:
            print(f"Erro ao ler MPU-6050: {e}")
            return None
    
    def _atualizar_direcao(self, gyro_z):
        """Atualiza a direção do ponteiro com base na rotação do giroscópio"""
        # Ajusta a sensibilidade do controle
        sensibilidade = 0.5
        
        # Atualiza a direção apenas se a rotação for significativa
        if abs(gyro_z) > 10:
            # gyro_z positivo = rotação anti-horária (aumenta ângulo)
            # gyro_z negativo = rotação horária (diminui ângulo)
            self.direcao -= gyro_z * sensibilidade
            
            # Mantém a direção entre 0 e 360 graus
            self.direcao = self.direcao % 360
    
    def _gerar_novo_alvo(self):
      """
      Gera um novo alvo apenas nas 8 posições que podem ser apontadas diretamente
      do centro da matriz.
      """
      # Lista das 8 posições possíveis na borda que podem ser apontadas diretamente
      posicoes_possiveis = [
          (2, 0),  # Centro-topo
          (4, 2),  # Centro-direita
          (2, 4),  # Centro-base
          (0, 2),  # Centro-esquerda
          (0, 0),  # Canto superior-esquerdo
          (4, 0),  # Canto superior-direito
          (0, 4),  # Canto inferior-esquerdo
          (4, 4)   # Canto inferior-direito
      ]
      
      # Escolhe uma posição aleatória da lista
      indice = urandom.randint(0, 7)  # 8 posições (0-7)
      self.alvo_x, self.alvo_y = posicoes_possiveis[indice]
    
    def _verificar_acerto(self):
        """Verifica se o jogador acertou o alvo"""
        # Converte a direção para índice da lista de direções
        indice_direcao = int((self.direcao + 22.5) / 45) % 8
        dir_x, dir_y = self.direcoes[indice_direcao]
        
        # Calcula a posição onde o "tiro" atingiria a borda
        # Para simplificar, vamos verificar se a direção apontada está correta
        # Calcula o ângulo até o alvo
        dx = self.alvo_x - self.ponteiro_x
        dy = self.alvo_y - self.ponteiro_y
        angulo_alvo = (math.degrees(math.atan2(dy, dx)) + 360) % 360
        
        # Verifica se a direção está próxima o suficiente do ângulo do alvo
        diferenca_angulo = min(abs(angulo_alvo - self.direcao), 360 - abs(angulo_alvo - self.direcao))
        
        if diferenca_angulo < 30:  # Tolerância de 30 graus
            # Acertou o alvo!
            self.pontuacao += 10
            self.alvos_acertados += 1
            
            # Efeito visual
            self.matriz.piscar_led(self.alvo_x, self.alvo_y, config.COR_VERDE)
            
            # Som de acerto
            self.buzzer.tocar_som(1000, 100)
            
            # Gera novo alvo
            self._gerar_novo_alvo()
        else:
            # Errou o alvo
            self.buzzer.tocar_som(200, 100)
            
            # Efeito visual de erro
            # Encontra a posição aproximada do "tiro" errático
            # Simplificação: usa posição baseada na direção atual
            tiro_x = self.ponteiro_x + dir_x * 2
            tiro_y = self.ponteiro_y + dir_y * 2
            
            # Limita às bordas da matriz
            tiro_x = max(0, min(4, tiro_x))
            tiro_y = max(0, min(4, tiro_y))
            
            # Pisca o LED onde o tiro "atingiu"
            self.matriz.piscar_led(tiro_x, tiro_y, config.COR_VERMELHO)
    
    def _atualizar_matriz(self):
        """Atualiza a visualização na matriz de LEDs"""
        self.matriz.apagar()
        
        # Mostra o alvo (piscando para destacar)
        if (ticks_ms() // 200) % 2 == 0:  # Pisca a cada 200ms
            self.matriz.acender_led_cor(self.alvo_x, self.alvo_y, config.COR_AMARELO)
        
        # Mostra o ponteiro central
        self.matriz.acender_led_cor(self.ponteiro_x, self.ponteiro_y, config.COR_AZUL)
        
        # Mostra a direção apontada
        # Converte a direção para índice da lista de direções
        indice_direcao = int((self.direcao + 22.5) / 45) % 8
        dir_x, dir_y = self.direcoes[indice_direcao]
        
        # Acende o LED na direção atual (a partir do centro)
        x = self.ponteiro_x + dir_x
        y = self.ponteiro_y + dir_y
        
        # Verifica se a posição está dentro da matriz
        if 0 <= x <= 4 and 0 <= y <= 4:
            self.matriz.acender_led_cor(x, y, config.COR_ROXO)