# main.py
# Arquivo principal do jogo BitdogLab

from components.display import Display
from components.matriz_led import MatrizLED
from components.buzzer import Buzzer

# Importa o gerenciador de etapas
from stages.stage_manager import StageManager

# Importa as etapas do jogo
from stages.reaction_game import ReactionGame
from stages.memory_game import MemoryGame
from stages.rhythm_game import RhythmGame
from stages.tilt_game import TiltGame         # Jogo de inclinação
from stages.maze_game import MazeGame         # Jogo de labirinto
from stages.balance_game import BalanceGame   # Jogo de equilíbrio
from stages.gyro_game import GyroGame
from stages.sensor_test import SensorTest     # Utilitário de teste do sensor

def reset_hardware():
    """Reseta todos os componentes de hardware para seu estado inicial"""
    try:
        # Inicializa componentes apenas para resetá-los
        display = Display()
        matriz = MatrizLED()
        buzzer = Buzzer()
        
        # Limpa display
        display.limpar()
        
        # Apaga todos os LEDs
        matriz.apagar()
        
        # Garante que o buzzer esteja desligado
        buzzer.buzzer.duty_u16(0)
        
        print("Hardware resetado com sucesso")
    except Exception as e:
        print("Erro ao resetar hardware:", e)
        
def main():
    # Reseta todos os componentes de hardware
    reset_hardware()
    
    """Função principal do programa"""
    print("=== BitdogLab Game Iniciando ===")
    
    # Inicializa o gerenciador de etapas
    manager = StageManager()
    
    # Adiciona as etapas disponíveis
    # Formato: manager.adicionar_etapa(ClasseDoJogo, "Nome do Jogo")
    manager.adicionar_etapa(ReactionGame, "Reacao")
    manager.adicionar_etapa(MemoryGame, "Memoria")
    # manager.adicionar_etapa(RhythmGame, "Jogo de Ritmo")
    manager.adicionar_etapa(TiltGame, "Inclinacao")
    # manager.adicionar_etapa(MazeGame, "Jogo de Labirinto")
    manager.adicionar_etapa(GyroGame, "Giroscopio")
    # manager.adicionar_etapa(BalanceGame, "Jogo de Equilibrio")
    # manager.adicionar_etapa(SensorTest, "Teste do Sensor")

    
    # IMPORTANTE: Para adicionar ou remover etapas, basta adicionar ou 
    # remover linhas acima conforme necessário. A estrutura modular
    # faz o resto automaticamente.
    
    # Inicia o menu principal
    manager.iniciar_menu()

# Executa o programa quando este arquivo é executado diretamente
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Tratamento básico de erros para debug
        print("Erro:", e)