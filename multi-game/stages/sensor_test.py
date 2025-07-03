# stages/sensor_test.py
# Utilitário para testar e calibrar o sensor MPU-6050

import config
from utime import sleep, ticks_ms, ticks_diff
from machine import I2C, Pin, SoftI2C
import math

class SensorTest:
    def __init__(self, display, matriz, buzzer, botoes):
        """Inicializa o teste de sensor"""
        self.display = display
        self.matriz = matriz
        self.buzzer = buzzer
        self.botoes = botoes
        
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
        """Inicia o utilitário de teste de sensor"""
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
        
        # Menu de opções de teste
        opcoes = [
            "Visualizacao ao vivo",
            "Calibracao",
            "Teste na matriz LED",
            "Voltar"
        ]
        
        while True:
            # Exibe o menu e aguarda seleção
            selecao = self._exibir_menu("Teste do Sensor", opcoes)
            
            if selecao == 0:  # Visualização ao vivo
                self._visualizacao_ao_vivo()
            elif selecao == 1:  # Calibração
                self._calibracao()
            elif selecao == 2:  # Teste na matriz LED
                self._teste_matriz()
            else:  # Voltar
                break
        
        return 0  # Não há pontuação para este utilitário
    
    def _exibir_menu(self, titulo, opcoes):
        """Exibe um menu e retorna a opção selecionada"""
        from utils import navegar_menu
        return navegar_menu(self.display, self.botoes, titulo, opcoes)
    
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
    
    def _visualizacao_ao_vivo(self):
        """Mostra os valores do sensor em tempo real"""
        self.display.mostrar_mensagem([
            "Visualizacao ao vivo",
            "Mova o dispositivo",
            "Bot. B para sair"
        ])
        sleep(1)
        
        while True:
            # Verifica se o botão B foi pressionado (sair)
            if self.botoes.esta_pressionado_b():
                break
            
            # Lê os dados do sensor
            dados = self._ler_mpu6050()
            if dados:
                # Exibe os valores no display
                self.display.limpar()
                self.display.texto("Acelerometro:", 0, 0, False)
                self.display.texto(f"X:{dados['accel']['x']:.2f}", 0, 10, False)
                self.display.texto(f"Y:{dados['accel']['y']:.2f}", 0, 20, False)
                self.display.texto(f"Z:{dados['accel']['z']:.2f}", 0, 30, False)
                self.display.texto("Bot. B: Sair", 0, 50, True)
            
            sleep(0.2)
    
    def _calibracao(self):
        """Calibra o sensor para uma posição neutra"""
        self.display.mostrar_mensagem([
            "Calibracao",
            "Coloque o dispositivo",
            "em uma superficie plana",
            "Pressione A para iniciar"
        ])
        
        # Aguarda o botão A ser pressionado
        self.botoes.aguardar_botao_a()
        
        self.display.mostrar_mensagem([
            "Calibrando...",
            "Nao mova o dispositivo!"
        ])
        
        # Lê várias amostras para uma média mais precisa
        amostras = 50
        soma_accel_x = soma_accel_y = soma_accel_z = 0
        soma_gyro_x = soma_gyro_y = soma_gyro_z = 0
        
        for i in range(amostras):
            # Mostra progresso
            self.display.mostrar_mensagem([
                "Calibrando...",
                f"Progresso: {i+1}/{amostras}",
                "Nao mova o dispositivo!"
            ])
            
            dados = self._ler_mpu6050()
            if dados:
                soma_accel_x += dados['accel']['x']
                soma_accel_y += dados['accel']['y']
                soma_accel_z += dados['accel']['z']
                soma_gyro_x += dados['gyro']['x']
                soma_gyro_y += dados['gyro']['y']
                soma_gyro_z += dados['gyro']['z']
            
            sleep(0.1)
        
        # Calcula as médias
        offset_accel_x = soma_accel_x / amostras
        offset_accel_y = soma_accel_y / amostras
        offset_accel_z = soma_accel_z / amostras
        offset_gyro_x = soma_gyro_x / amostras
        offset_gyro_y = soma_gyro_y / amostras
        offset_gyro_z = soma_gyro_z / amostras
        
        # Exibe os resultados
        self.display.mostrar_mensagem([
            "Calibracao concluida!",
            "Offset accel:",
            f"X:{offset_accel_x:.2f} Y:{offset_accel_y:.2f}",
            f"Z:{offset_accel_z:.2f}"
        ])
        sleep(3)
        
        self.display.mostrar_mensagem([
            "Offset gyro:",
            f"X:{offset_gyro_x:.2f}",
            f"Y:{offset_gyro_y:.2f}",
            f"Z:{offset_gyro_z:.2f}",
            "Pressione para continuar"
        ])
        self.botoes.aguardar_qualquer_botao()
    
    def _teste_matriz(self):
        """Testa a visualização da inclinação na matriz de LEDs"""
        self.display.mostrar_mensagem([
            "Teste na Matriz LED",
            "Incline o dispositivo",
            "para mover o pixel",
            "Bot. B para sair"
        ])
        sleep(1)
        
        # Posição inicial do pixel
        x, y = 2, 2
        ultima_atualizacao = ticks_ms()
        
        while True:
            # Verifica se o botão B foi pressionado (sair)
            if self.botoes.esta_pressionado_b():
                break
            
            tempo_atual = ticks_ms()
            
            # Atualiza a posição a cada 200ms
            if ticks_diff(tempo_atual, ultima_atualizacao) > 200:
                # Lê os dados do sensor
                dados = self._ler_mpu6050()
                if dados:
                    # Calcula a nova posição com base na inclinação
                    novo_x = x
                    novo_y = y
                    
                    # Ajusta a sensibilidade
                    sensibilidade = 0.3
                    
                    # Atualiza X (accel_y move no eixo X da matriz)
                    if dados['accel']['y'] > sensibilidade:
                        novo_x = max(0, x - 1)  # Move para a esquerda
                    elif dados['accel']['y'] < -sensibilidade:
                        novo_x = min(4, x + 1)  # Move para a direita
                    
                    # CORREÇÃO: Inverte a direção do eixo Y
                    # Antes: inclinação para frente (accel_x positivo) movia para baixo
                    # Agora: inclinação para frente (accel_x positivo) move para cima
                    if dados['accel']['x'] > sensibilidade:
                        novo_y = max(0, y - 1)  # Move para cima (quando inclina para frente)
                    elif dados['accel']['x'] < -sensibilidade:
                        novo_y = min(4, y + 1)  # Move para baixo (quando inclina para trás)
                    
                    # Atualiza a posição se mudou
                    if novo_x != x or novo_y != y:
                        x, y = novo_x, novo_y
                        self.buzzer.tocar_som(800, 10)  # Som de movimento
                    
                    # Atualiza a matriz de LEDs
                    self.matriz.apagar()
                    self.matriz.acender_led_cor(x, y, config.COR_AZUL)
                
                ultima_atualizacao = tempo_atual
            
            sleep(0.01)
        
        self.matriz.apagar()