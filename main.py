# main.py
# Arquivo principal do jogo BitdogLab

# Importa o gerenciador de etapas
from stages.stage_manager import StageManager

# Importa as etapas do jogo
from stages.reaction_game import ReactionGame
from stages.memory_game import MemoryGame
from stages.rhythm_game import RhythmGame

def main():
    """Função principal do programa"""
    print("=== BitdogLab Game Iniciando ===")
    
    # Inicializa o gerenciador de etapas
    manager = StageManager()
    
    # Adiciona as etapas disponíveis
    # Formato: manager.adicionar_etapa(ClasseDoJogo, "Nome do Jogo")
    manager.adicionar_etapa(ReactionGame, "Jogo de Reacao")
    manager.adicionar_etapa(MemoryGame, "Jogo de Memoria")
    manager.adicionar_etapa(RhythmGame, "Jogo de Ritmo")
    
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