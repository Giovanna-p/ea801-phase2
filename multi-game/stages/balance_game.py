# stages/balance_game.py
# Jogo de equilíbrio: mantenha o dispositivo estável para acumular pontos

import config
from utime import sleep, ticks_ms, ticks_diff
import urandom
from utils import contagem_regressiva
from machine import I2C, Pin, SoftI2C
import math

class BalanceGame:
    def __init__(self, display, matriz, buzzer, botoes):
        """Inicializa o jogo de equilíbrio"""
        self.display = display
        self.matriz = matriz
        self.buzzer = buzzer
        self.botoes = botoes
        self.pontuacao = 0
        self.tempo_total = 30  # segundos de jogo
        self.nivel_atual = 1   # Nível atual (1 a 5)
        self.nivel_mais_alto = 1  # Nível mais alto atingido durante o jogo
        
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
    
    def iniciar(self):
        """Inicia o jogo de equilíbrio"""
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
            "Jogo de Equilibrio",
            "Mantenha o dispositivo",
            "o mais estavel possivel",
            "Pressione para iniciar"
        ])
        
        # Aguarda qualquer botão ser pressionado para iniciar
        self.botoes.aguardar_qualquer_botao()
        
        # Contador regressivo
        contagem_regressiva(self.display, self.buzzer)
        
        # Reinicia pontuação e níveis
        self.pontuacao = 0
        self.nivel_atual = 1
        self.nivel_mais_alto = 1
        
        # Tempo inicial
        tempo_inicio = ticks_ms()
        ultimo_movimento = ticks_ms()
        ultima_atualizacao_display = ticks_ms()
        
        # Calibração inicial
        self.display.mostrar_mensagem([
            "Calibrando...",
            "Mantenha o dispositivo",
            "imóvel na posição",
            "de jogo..."
        ])
        
        # Lê algumas amostras para calibração
        amostras = 10
        soma_x, soma_y, soma_z = 0, 0, 0
        for _ in range(amostras):
            dados = self._ler_mpu6050()
            if dados:
                soma_x += dados['accel']['x']
                soma_y += dados['accel']['y']
                soma_z += dados['accel']['z']
            sleep(0.1)
        
        # Calcula as médias como valores de referência
        self.ref_x = soma_x / amostras
        self.ref_y = soma_y / amostras
        self.ref_z = soma_z / amostras
        
        self.display.mostrar_mensagem([
            "Calibrado!",
            "Mantenha esta",
            "posicao para",
            "ganhar pontos!"
        ])
        sleep(1)
        
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
                    f"Nivel: {self.nivel_atual}",
                    f"Tempo: {int(self.tempo_total - tempo_passado)}s",
                    f"Pontuacao: {self.pontuacao}",
                    "Mantenha estavel!"
                ])
                ultima_atualizacao_display = tempo_atual
            
            # Verifica o equilíbrio e atualiza a pontuação a cada 200ms
            if ticks_diff(tempo_atual, ultimo_movimento) > 200:
                # Lê os dados do acelerômetro
                dados = self._ler_mpu6050()
                if dados:
                    # Calcula o desvio em relação à referência
                    desvio = self._calcular_desvio(
                        dados['accel']['x'], 
                        dados['accel']['y'], 
                        dados['accel']['z']
                    )
                    
                    # Atualiza o nível e a pontuação
                    self._atualizar_nivel_e_pontuacao(desvio)
                    
                    # Atualiza a matriz de LEDs
                    self._atualizar_matriz(desvio)
                
                ultimo_movimento = tempo_atual
            
            # Pausa para economizar CPU
            sleep(0.01)
        
        # Fim do jogo
        self.buzzer.tocar_fim_jogo()
        self.matriz.apagar()
        self.display.mostrar_mensagem([
            "Tempo Esgotado!",
            f"Nivel mais alto: {self.nivel_mais_alto}",
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
    
    def _calcular_desvio(self, x, y, z):
        """Calcula o desvio em relação à posição de referência"""
        # Distância euclidiana em relação à referência
        dx = x - self.ref_x
        dy = y - self.ref_y
        dz = z - self.ref_z
        
        # Retorna a magnitude do desvio
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def _atualizar_nivel_e_pontuacao(self, desvio):
        """Atualiza o nível atual e a pontuação com base no desvio"""
        # Limiares para cada nível (menor desvio = nível mais alto)
        limiar_nivel = [0.5, 0.3, 0.2, 0.1, 0.05]
        
        # Determina o novo nível com base no desvio
        novo_nivel = 1
        for i, limiar in enumerate(limiar_nivel):
            if desvio < limiar:
                novo_nivel = 5 - i
                break
        
        # Atualiza o nível atual
        if novo_nivel != self.nivel_atual:
            self.nivel_atual = novo_nivel
            # Toca um som quando o nível muda
            self.buzzer.tocar_som(500 + 100*self.nivel_atual, 50)
        
        # Atualiza o nível mais alto atingido
        if self.nivel_atual > self.nivel_mais_alto:
            self.nivel_mais_alto = self.nivel_atual
            # Som especial ao atingir um novo nível mais alto
            self.buzzer.tocar_nota("C4", 100)
            self.buzzer.tocar_nota("E4", 100)
            self.buzzer.tocar_nota("G4", 100)
        
        # Adiciona pontos com base no nível atual
        self.pontuacao += self.nivel_atual
    
    def _atualizar_matriz(self, desvio):
        """Atualiza a visualização na matriz de LEDs com base no nível atual"""
        self.matriz.apagar()
        
        # Define a cor com base no nível
        cores = [
            config.COR_VERMELHO,   # Nível 1 (vermelho)
            config.COR_AMARELO,    # Nível 2 (amarelo)
            config.COR_AZUL,       # Nível 3 (azul)
            config.COR_ROXO,       # Nível 4 (roxo)
            config.COR_VERDE       # Nível 5 (verde)
        ]
        
        cor_atual = cores[self.nivel_atual - 1]
        
        # Desenha um padrão de acordo com o nível atual
        if self.nivel_atual == 1:
            # Nível 1: Um ponto central
            self.matriz.acender_led_cor(2, 2, cor_atual)
            
        elif self.nivel_atual == 2:
            # Nível 2: Cruz simples
            for i in range(5):
                self.matriz.acender_led_cor(2, i, cor_atual)
                self.matriz.acender_led_cor(i, 2, cor_atual)
            
        elif self.nivel_atual == 3:
            # Nível 3: Círculo
            self.matriz.acender_led_cor(1, 1, cor_atual)
            self.matriz.acender_led_cor(1, 2, cor_atual)
            self.matriz.acender_led_cor(1, 3, cor_atual)
            self.matriz.acender_led_cor(2, 1, cor_atual)
            self.matriz.acender_led_cor(2, 3, cor_atual)
            self.matriz.acender_led_cor(3, 1, cor_atual)
            self.matriz.acender_led_cor(3, 2, cor_atual)
            self.matriz.acender_led_cor(3, 3, cor_atual)
            
        elif self.nivel_atual == 4:
            # Nível 4: Bordas
            for i in range(5):
                self.matriz.acender_led_cor(0, i, cor_atual)
                self.matriz.acender_led_cor(4, i, cor_atual)
                self.matriz.acender_led_cor(i, 0, cor_atual)
                self.matriz.acender_led_cor(i, 4, cor_atual)
            
        elif self.nivel_atual == 5:
            # Nível 5: Matriz completa
            for x in range(5):
                for y in range(5):
                    self.matriz.acender_led_cor(x, y, cor_atual)
                    
        # Indica o desvio com um LED piscante se estiver fora do limiar
        if desvio > 0.5:  # Desvio grande
            if (ticks_ms() // 100) % 2 == 0:  # Pisca rápido
                self.matriz.acender_led_cor(2, 2, config.COR_VERMELHO)