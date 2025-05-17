# BitdogLab Multi-Game

Este projeto implementa uma estrutura modular para jogos na placa BitdogLab, permitindo fácil adição ou remoção de etapas de jogo.

## Estrutura do Projeto

```
/
├── main.py                  # Arquivo principal que gerencia o fluxo do jogo
├── config.py                # Configurações compartilhadas (pinos, hardware, cores)
├── utils.py                 # Funções utilitárias compartilhadas
├── components/              # Pasta para componentes de hardware
│   ├── display.py           # Gestão do display OLED
│   ├── matriz_led.py        # Gestão da matriz de LEDs
│   └── buzzer.py            # Controle de sons e melodias
└── stages/                  # Pasta para as etapas do jogo
    ├── stage_manager.py     # Gerenciador de etapas
    ├── reaction_game.py     # Jogo de reação (já implementado)
    ├── memory_game.py       # Segunda etapa (jogo de memória)
    └── rhythm_game.py       # Terceira etapa (jogo rítmico)
```

## Jogos Implementados

### 1. Jogo de Reação

- Pressione o botão A quando o LED verde acender
- Ignore outras cores (vermelho, azul, branco)
- Mede o tempo de reação do jogador

### 2. Jogo de Memória

- Memorize e repita a sequência de cores mostrada
- Use o botão A para verde e o botão B para vermelho
- A dificuldade aumenta com sequências mais longas

### 3. Jogo de Ritmo

- Pressione os botões no tempo certo quando as notas atingirem a zona de batida
- Botão A para a faixa esquerda, Botão B para a faixa direita
- Pontuação baseada na precisão do timing

## Como Adicionar uma Nova Etapa

1. Crie um novo arquivo Python na pasta `stages/` (ex: `my_new_game.py`)
2. Defina uma classe para o jogo com método `iniciar()` que retorna uma pontuação
3. Importe a classe no `main.py`
4. Adicione ao gerenciador com `manager.adicionar_etapa(MinhaClasse, "Nome do Jogo")`

Exemplo:

```python
# No arquivo stages/my_new_game.py
class MyNewGame:
    def __init__(self, display, matriz, buzzer, botoes):
        self.display = display
        self.matriz = matriz
        self.buzzer = buzzer
        self.botoes = botoes

    def iniciar(self):
        # Implementação do jogo
        # ...
        return pontuacao

# No main.py
from stages.my_new_game import MyNewGame
# ...
manager.adicionar_etapa(MyNewGame, "Meu Novo Jogo")
```

## Modo Desafio

O programa também inclui um "Modo Desafio" que executa todas as etapas em sequência, somando as pontuações para um resultado final.

## Componentes Reutilizáveis

O projeto possui classes para os componentes de hardware que podem ser usadas em qualquer etapa:

- `Display`: Controle do display OLED para UI
- `MatrizLED`: Funções para manipular a matriz de LEDs 5x5
- `Buzzer`: Efeitos sonoros e melodias
- `Botoes`: Gerenciamento de entrada pelos botões

## Configuração

O arquivo `config.py` centraliza todas as configurações de hardware e parâmetros de jogo, facilitando a configuração para diferentes placas BitdogLab.
