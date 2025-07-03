from machine import Pin, PWM, ADC
import time

class BracoRoboticoSimples:
    def __init__(self):
        """Braço Robótico SIMPLES - Versão Otimizada para Economia de Energia"""
        print("🤖 Iniciando Braço Robótico...")
        
        # === CONFIGURAÇÃO DOS SERVOS ===
        self.servo_garra = PWM(Pin(8))
        self.servo_garra.freq(50)
        
        self.servo_updown = PWM(Pin(9))
        self.servo_updown.freq(50)
        
        self.servo_frente_tras = PWM(Pin(4))  # Pino correto
        self.servo_frente_tras.freq(50)
        
        # === VALORES DOS SERVOS ===
        self.GARRA_ABERTA = 8200      # Valores mais seguros
        self.GARRA_FECHADA = 1600     # Valores mais seguros
        
        # Limites dos servos
        self.SERVO_MIN = 1600         
        self.SERVO_MAX = 8200         
        self.SERVO_CENTRO = 4900      
        
        # Limites removidos - usar limites completos dos servos
        self.FRENTE_TRAS_MIN = self.SERVO_MIN   # 1600
        self.FRENTE_TRAS_MAX = self.SERVO_MAX   # 8200   
        
        # === CONFIGURAÇÃO DOS CONTROLES ===
        self.botao_A = Pin(5, Pin.IN, Pin.PULL_UP)
        self.botao_B = Pin(6, Pin.IN, Pin.PULL_UP)
        self.joystick = ADC(Pin(26))
        
        # === VARIÁVEIS DE ESTADO ===
        self.garra_esta_aberta = True
        self.posicao_updown = self.SERVO_MAX         # Começa no MÁXIMO
        self.posicao_frente_tras = self.SERVO_MAX    # Começa no MÁXIMO
        
        # Controle dos botões
        self.botao_A_anterior = 1
        self.botao_B_anterior = 1
        
        # Configurações de movimento
        self.incremento = 300          # Incremento maior para ter força
        self.zona_morta = 8000
        
        # Timer para desligar servos inativos
        self.tempo_ultima_acao_updown = time.time()
        self.tempo_ultima_acao_frente_tras = time.time()
        self.TIMEOUT_SERVO = 1.0      # Desliga servo após 2 segundos
        
        # Flags para evitar spam de mensagens
        self.updown_no_limite = False
        self.frente_tras_no_limite = False
        
        # Inicializa posições
        self.inicializar_servos()
    
    def inicializar_servos(self):
        """Inicia com todos os servos no LIMITE MÁXIMO SUPERIOR"""
        print("📍 Posicionando servos no LIMITE MÁXIMO...")
        
        # Garra aberta
        self.servo_garra.duty_u16(self.GARRA_ABERTA)
        self.garra_esta_aberta = True
        print("  ✅ Garra: ABERTA")
        time.sleep(0.5)
        self.servo_garra.duty_u16(0)  # Desliga PWM
        
        # UP/DOWN no MÁXIMO
        #self.servo_updown.duty_u16(self.SERVO_MAX)
        #self.posicao_updown = self.SERVO_MAX
        print(f"  ✅ Up/Down: MÁXIMO - {self.SERVO_MAX} ({self.pwm_para_graus(self.SERVO_MAX):.1f}°)")
        time.sleep(0.8)
        
        # FRENTE/TRÁS no MÁXIMO
        #self.servo_frente_tras.duty_u16(self.SERVO_MAX)
        #self.posicao_frente_tras = self.SERVO_MAX
        print(f"  ✅ Frente/Trás: MÁXIMO - {self.SERVO_MAX} ({self.pwm_para_graus(self.SERVO_MAX):.1f}°)")
        time.sleep(0.8)
        
        print("🎯 Todos os servos estão no LIMITE MÁXIMO!")
        print("📝 Agora teste os movimentos para encontrar os limites inferiores")
    
    def pwm_para_graus(self, valor_pwm):
        """Converte valor PWM para graus aproximados (0-180°)"""
        pwm_min = 1600    # 0 graus
        pwm_max = 8200    # 180 graus
        
        # Regra de três para conversão
        graus = ((valor_pwm - pwm_min) / (pwm_max - pwm_min)) * 180
        return max(0, min(180, graus))  # Limita entre 0-180°
    
    def processar_botao_garra(self):
        """Processa o botão A para controlar a garra"""
        estado_atual_A = self.botao_A.value()
        
        # Detecta quando o botão A foi pressionado
        if estado_atual_A == 0 and self.botao_A_anterior == 1:
            if self.garra_esta_aberta:
                # Fecha a garra
                self.servo_garra.duty_u16(self.GARRA_FECHADA)
                self.garra_esta_aberta = False
                print("✊ Garra FECHADA")
                time.sleep(0.5)  # Tempo para posicionar
                self.servo_garra.duty_u16(0)  # Desliga PWM
            else:
                # Abre a garra
                self.servo_garra.duty_u16(self.GARRA_ABERTA)
                self.garra_esta_aberta = True
                print("🤏 Garra ABERTA")
                time.sleep(0.5)  # Tempo para posicionar
                self.servo_garra.duty_u16(0)  # Desliga PWM
            
            time.sleep(0.3)  # Evita múltiplos acionamentos
        
        # Salva o estado anterior
        self.botao_A_anterior = estado_atual_A
    
    def ler_direcao_joystick(self):
        """Lê o joystick e retorna a direção de movimento"""
        valor_joystick = self.joystick.read_u16()
        centro_joystick = 32768  # Meio do range 0-65535
        
        # Verifica se está na zona morta
        if abs(valor_joystick - centro_joystick) < self.zona_morta:
            return 0  # Não move
        
        # Determina a direção
        if valor_joystick > centro_joystick + self.zona_morta:
            return 1   # Positivo
        elif valor_joystick < centro_joystick - self.zona_morta:
            return -1  # Negativo
        
        return 0
    
    def mover_servo_updown(self, direcao):
        """Move o servo up/down com economia de energia"""
        if direcao == 0:
            self.updown_no_limite = False
            return
        
        # ECONOMIA: Desliga o servo frente/trás antes de mover up/down
        self.servo_frente_tras.duty_u16(0)
        time.sleep(0.05)  # Pequena pausa para estabilizar
        
        # Atualiza timer de atividade
        self.tempo_ultima_acao_updown = time.time()
        
        # Calcula nova posição
        nova_posicao = self.posicao_updown + (self.incremento * direcao)
        
        
        # Reset flag se não está no limite
        self.updown_no_limite = False
        
        # Move o servo
        self.posicao_updown = nova_posicao
        self.servo_updown.duty_u16(self.posicao_updown)
        
        if direcao > 0:
            print(f"🔼 SUBINDO: {self.posicao_updown}")
        else:
            print(f"🔽 DESCENDO: {self.posicao_updown}")
    
    def mover_servo_frente_tras(self, direcao):
        """Move o servo frente/trás com economia de energia"""
        if direcao == 0:
            self.frente_tras_no_limite = False
            return
        
        # ECONOMIA: Desliga o servo up/down antes de mover frente/trás
        self.servo_updown.duty_u16(0)
        time.sleep(0.05)  # Pequena pausa para estabilizar
        
        # Atualiza timer de atividade
        self.tempo_ultima_acao_frente_tras = time.time()
        
        # Calcula nova posição
        nova_posicao = self.posicao_frente_tras + (self.incremento * direcao)
        
        # Reset flag se não está no limite
        self.frente_tras_no_limite = False
        
        # Move o servo
        self.posicao_frente_tras = nova_posicao
        self.servo_frente_tras.duty_u16(self.posicao_frente_tras)
        
        if direcao > 0:
            print(f"➡️ FRENTE: {self.posicao_frente_tras}")
        else:
            print(f"⬅️ TRÁS: {self.posicao_frente_tras}")
    
    def gerenciar_servos_inativos(self):
        """Desliga servos inativos para economizar energia"""
        tempo_atual = time.time()
        
        # Desliga servo up/down se inativo
        if tempo_atual - self.tempo_ultima_acao_updown > self.TIMEOUT_SERVO:
            self.servo_updown.duty_u16(0)
        
        # Desliga servo frente/trás se inativo  
        if tempo_atual - self.tempo_ultima_acao_frente_tras > self.TIMEOUT_SERVO:
            self.servo_frente_tras.duty_u16(0)
    
    def centralizar_frente_tras(self):
        """Centraliza o servo frente/trás na posição do meio"""
        print("🎯 Centralizando frente/trás...")
        self.servo_frente_tras.duty_u16(self.SERVO_CENTRO)
        self.posicao_frente_tras = self.SERVO_CENTRO
        self.tempo_ultima_acao_frente_tras = time.time()
        print(f"  ✅ Frente/Trás centralizado: {self.SERVO_CENTRO} ({self.pwm_para_graus(self.SERVO_CENTRO):.1f}°)")
        time.sleep(0.8)
    
    def mostrar_status(self):
        """Mostra o status atual do braço com posições em graus"""
        graus_updown = self.pwm_para_graus(self.posicao_updown)
        graus_frente_tras = self.pwm_para_graus(self.posicao_frente_tras)
        
        print(f"📊 Status do Braço:")
        print(f"  🔼 UP/DOWN: {self.posicao_updown} ({graus_updown:.1f}°)")
        print(f"  ➡️ FRENTE/TRÁS: {self.posicao_frente_tras} ({graus_frente_tras:.1f}°)")
        print(f"  ✋ GARRA: {'ABERTA' if self.garra_esta_aberta else 'FECHADA'}")
    
    def executar_loop_principal(self):
        """Loop principal do braço robótico"""
        print("\n🎮 === CONTROLES DO BRAÇO ROBÓTICO ===")
        print("🔘 Botão A: Abrir/Fechar garra")
        print("🕹️ Joystick (normal): Mover UP/DOWN")
        print("🕹️ Joystick + Botão B: Mover FRENTE/TRÁS")
        print("🎯 Pressione ambos os botões (A+B): Centralizar frente/trás")
        print("⌨️ Ctrl+C: Sair do programa")
        print("=" * 45)
        
        contador_status = 0
        
        try:
            while True:
                # Lê estados dos botões
                estado_atual_A = self.botao_A.value()
                botao_B_pressionado = (self.botao_B.value() == 0)
                
                # Centralizar frente/trás (A+B juntos)
                if estado_atual_A == 0 and botao_B_pressionado:
                    self.centralizar_frente_tras()
                    time.sleep(0.5)  # Evita acionamentos múltiplos
                    continue  # Pula o resto do loop
                
                # Processa o controle da garra (normal)
                self.processar_botao_garra()
                
                # Lê a direção do joystick
                direcao = self.ler_direcao_joystick()
                
                # Move o servo apropriado baseado no modo
                if direcao != 0:
                    if botao_B_pressionado:
                        # Modo frente/trás ativo
                        self.mover_servo_frente_tras(direcao)
                    else:
                        # Modo normal (up/down)
                        self.mover_servo_updown(direcao)
                    
                    # Pausa após movimento (economia de energia)
                    time.sleep(0.15)
                
                # ECONOMIA: Gerencia servos inativos
                self.gerenciar_servos_inativos()
                
                # Mostra status a cada 200 ciclos
                contador_status += 1
                if contador_status >= 200:
                    self.mostrar_status()
                    contador_status = 0
                
                # Pausa do loop principal
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\n🛑 Programa interrompido pelo usuário")
        finally:
            self.desligar_todos_servos()
    
    def desligar_todos_servos(self):
        """Desliga todos os servos para economizar energia"""
        print("🔌 Desligando todos os servos...")
        self.servo_garra.duty_u16(0)
        self.servo_updown.duty_u16(0)
        self.servo_frente_tras.duty_u16(0)
        print("✅ Todos os servos foram desligados")

# === FUNÇÃO PRINCIPAL ===
def main():
    """Função principal do programa"""
    print("🚀 Iniciando sistema do braço robótico...")
    braco_robotico = BracoRoboticoSimples()
    braco_robotico.executar_loop_principal()

# === EXECUÇÃO ===
if __name__ == "__main__":
    main()
