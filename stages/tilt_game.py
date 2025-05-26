# stages/tilt_game.py
# Jogo de inclinação: controle um LED na matriz inclinando o dispositivo

import config
from utime import sleep, ticks_ms, ticks_diff
import urandom
from utils import contagem_regressiva
from machine import I2C, Pin, SoftI2C

class TiltGame:
    def __init__(self, display, matriz, buzzer, botoes):
        """Inicializa o jogo de inclinação"""
        self.display = display
        self.matriz = matriz
        self.buzzer = buzzer
        self.botoes = botoes
        self.pontuacao = 0
        self.tempo_total = 30  # segundos de jogo
        self.objetivos_coletados = 0
        
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
        
        # Posição da "bola" (LED controlado)
        self.bola_x = 2
        self.bola_y = 2
        
        # Posição do objetivo
        self.objetivo_x = 0
        self.objetivo_y = 0
        
    def iniciar(self):
        """Inicia o jogo de inclinação"""
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
            "Capture a ",
            "bolinha VERDE",
            "inclinando o",
            "dispositivo. ",
            "Pressione para",
            "iniciar"
        ])
        
        # Aguarda qualquer botão ser pressionado para iniciar
        self.botoes.aguardar_qualquer_botao()
        
        # Contador regressivo
        contagem_regressiva(self.display, self.buzzer)
        
        # Reinicia pontuação e posições
        self.pontuacao = 0
        self.objetivos_coletados = 0
        self.bola_x = 2
        self.bola_y = 2
        self._gerar_novo_objetivo()
        
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
                    "Jogo de Inclinacao",
                    f"Tempo: {int(self.tempo_total - tempo_passado)}s",
                    f"Objetivos: {self.objetivos_coletados}",
                    f"Pontuacao: {self.pontuacao}"
                ])
                ultima_atualizacao_display = tempo_atual
            
            # Atualiza a posição da bola a cada 200ms
            if ticks_diff(tempo_atual, ultimo_movimento) > 200:
                # Lê os dados do acelerômetro
                dados = self._ler_mpu6050()
                if dados:
                    # Move a bola com base na inclinação
                    self._mover_bola(dados['accel']['x'], dados['accel']['y'])
                    # Verifica colisão com objetivo
                    self._verificar_colisao()
                
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
            f"Objetivos: {self.objetivos_coletados}",
            f"Pontuacao: {self.pontuacao}",
            "Pressione para continuar"
        ])
        
        # Aguarda botão para continuar
        self.botoes.aguardar_qualquer_botao()
        
        return self.pontuacao
    
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
    
    def _mover_bola(self, accel_x, accel_y):
        """Move a bola com base nos dados do acelerômetro"""
        # Calcula a nova posição com base na inclinação
        novo_x = self.bola_x
        novo_y = self.bola_y
        
        # Ajusta a sensibilidade
        sensibilidade = 0.3
        
        # Atualiza X (accel_y move no eixo X da matriz)
        if accel_y > sensibilidade:
            novo_x = max(0, self.bola_x - 1)  # Move para a esquerda
        elif accel_y < -sensibilidade:
            novo_x = min(4, self.bola_x + 1)  # Move para a direita
        
        # CORREÇÃO: Inverte a direção do eixo Y
        # Inclinação para frente (accel_x positivo) move para cima
        # Inclinação para trás (accel_x negativo) move para baixo
        if accel_x > sensibilidade:
            novo_y = max(0, self.bola_y - 1)  # Move para cima (quando inclina para frente)
        elif accel_x < -sensibilidade:
            novo_y = min(4, self.bola_y + 1)  # Move para baixo (quando inclina para trás)
        
        # Atualiza a posição se mudou
        if novo_x != self.bola_x or novo_y != self.bola_y:
            self.bola_x = novo_x
            self.bola_y = novo_y
            self.buzzer.tocar_som(800, 10)  # Som de movimento
    
    def _gerar_novo_objetivo(self):
        """Gera um novo objetivo em posição aleatória (diferente da bola)"""
        while True:
            self.objetivo_x = urandom.randint(0, 4)
            self.objetivo_y = urandom.randint(0, 4)
            
            # Garante que o objetivo não seja gerado na mesma posição da bola
            if self.objetivo_x != self.bola_x or self.objetivo_y != self.bola_y:
                break
    
    def _verificar_colisao(self):
        """Verifica se a bola colidiu com o objetivo"""
        if self.bola_x == self.objetivo_x and self.bola_y == self.objetivo_y:
            # Coletou o objetivo!
            self.pontuacao += 10
            self.objetivos_coletados += 1
            
            # Som de coleta
            self.buzzer.tocar_som(1000, 100)
            
            # Gera novo objetivo
            self._gerar_novo_objetivo()
    
    def _atualizar_matriz(self):
        """Atualiza a visualização na matriz de LEDs"""
        self.matriz.apagar()
        
        # Mostra o objetivo (piscando para destacar)
        if (ticks_ms() // 200) % 2 == 0:  # Pisca a cada 200ms
            self.matriz.acender_led_cor(self.objetivo_x, self.objetivo_y, config.COR_AMARELO)
        
        # Mostra a bola
        self.matriz.acender_led_cor(self.bola_x, self.bola_y, config.COR_AZUL)