# BitdogLab Multi-Game

Este projeto implementa uma estrutura modular para jogos na placa BitdogLab, permitindo fácil adição ou remoção de etapas de jogo com sensores de movimento avançados.

## Estrutura do Projeto

```
/
├── main.py                  # Arquivo principal que gerencia o fluxo do jogo
├── boot.py                  # Configuração de inicialização do sistema
├── config.py                # Configurações compartilhadas (pinos, hardware, cores)
├── utils.py                 # Funções utilitárias compartilhadas
├── components/              # Pasta para componentes de hardware
│   ├── display.py           # Gestão do display OLED
│   ├── matriz_led.py        # Gestão da matriz de LEDs
│   └── buzzer.py            # Controle de sons e melodias
└── stages/                  # Pasta para as etapas do jogo
    ├── stage_manager.py     # Gerenciador de etapas
    ├── reaction_game.py     # Jogo de reação
    ├── memory_game.py       # Jogo de memória
    ├── rhythm_game.py       # Jogo rítmico
    ├── tilt_game.py         # Jogo de inclinação (MPU-6050)
    ├── maze_game.py         # Jogo de labirinto
    ├── balance_game.py      # Jogo de equilíbrio (MPU-6050)
    ├── gyro_game.py         # Jogo de giroscópio (MPU-6050)
    └── sensor_test.py       # Utilitário de teste do sensor
```

## Jogos Implementados

### 1. Jogo de Reação ✅

- Pressione o botão A quando o LED verde acender
- Ignore outras cores (vermelho, azul, branco)
- Mede o tempo de reação do jogador
- Pontuação baseada no melhor tempo

### 2. Jogo de Memória ✅

- Memorize e repita a sequência de cores mostrada
- Use o botão A para verde e o botão B para vermelho
- A dificuldade aumenta com sequências mais longas
- Máximo de 10 níveis

### 3. Jogo de Inclinação ✅

- **Requer sensor MPU-6050**
- Incline o dispositivo para mover a "bolinha" na matriz
- Alcance os alvos amarelos para ganhar pontos
- Controle baseado no acelerômetro

### 4. Jogo de Giroscópio ✅

- **Requer sensor MPU-6050**
- Gire o dispositivo para apontar para os alvos
- Pressione o botão A para "atirar"
- Controle baseado na rotação do giroscópio

### 5. Jogo de Equilíbrio ✅

- **Requer sensor MPU-6050**
- Mantenha o dispositivo o mais estável possível
- 5 níveis de estabilidade com pontuação crescente
- Sistema de calibração automática

### 6. Jogo de Ritmo 🚧

- Pressione os botões no tempo certo quando as notas atingirem a zona de batida
- Botão A para a faixa esquerda, Botão B para a faixa direita
- Pontuação baseada na precisão do timing

### 7. Jogo de Labirinto 🚧

- Navegue através de um labirinto usando sensores de movimento
- Encontre a saída no menor tempo possível

### 8. Teste do Sensor 🔧

- Utilitário para verificar o funcionamento do sensor MPU-6050
- Exibe valores em tempo real do acelerômetro e giroscópio

**Legenda:**

- ✅ Totalmente implementado e ativo
- 🚧 Em desenvolvimento (comentado no main.py)
- 🔧 Utilitário de desenvolvimento

## Sensor MPU-6050

Vários jogos utilizam o sensor de movimento MPU-6050 para controles avançados:

### Conexões Necessárias:

- **SCL**: Pino 1 (I2C Clock)
- **SDA**: Pino 0 (I2C Data)
- **VCC**: 3.3V
- **GND**: Ground

### Jogos que Usam o Sensor:

- **Jogo de Inclinação**: Usa o acelerômetro para detectar inclinação
- **Jogo de Giroscópio**: Usa o giroscópio para detectar rotação
- **Jogo de Equilíbrio**: Usa o acelerômetro para medir estabilidade

### Sistema de Detecção Automática:

O sistema verifica automaticamente se o sensor MPU-6050 está conectado. Se não estiver disponível, os jogos que dependem dele exibirão uma mensagem de erro e retornarão ao menu principal.

## Como Usar

1. **Conecte o hardware necessário** (especialmente o sensor MPU-6050 se quiser usar todos os jogos)
2. **Execute o main.py** na BitdogLab
3. **Navegue pelo menu** usando:
   - Botão A: Navegar pelas opções
   - Botão B: Selecionar opção
4. **Siga as instruções** de cada jogo no display OLED

## Como Adicionar uma Nova Etapa

1. **Crie um novo arquivo** Python na pasta `stages/` (ex: `my_new_game.py`)
2. **Defina uma classe** para o jogo com método `iniciar()` que retorna uma pontuação
3. **Importe a classe** no `main.py`
4. **Adicione ao gerenciador** com `manager.adicionar_etapa(MinhaClasse, "Nome do Jogo")`
5. **Descomente a linha** no main.py para ativar o jogo

### Exemplo de Implementação:

```python
# No arquivo stages/my_new_game.py
class MyNewGame:
    def __init__(self, display, matriz, buzzer, botoes):
        self.display = display
        self.matriz = matriz
        self.buzzer = buzzer
        self.botoes = botoes

    def iniciar(self):
        # Sua implementação do jogo aqui
        self.display.mostrar_mensagem([
            "Meu Novo Jogo",
            "Pressione A para jogar"
        ])
        self.botoes.aguardar_botao_a()

        # Lógica do jogo...
        pontuacao = 100  # Exemplo

        return pontuacao
```

```python
# No main.py
from stages.my_new_game import MyNewGame
# ...
manager.adicionar_etapa(MyNewGame, "Meu Novo Jogo")
```

## Sistema de Reset de Hardware

O projeto inclui uma função `reset_hardware()` que:

- Limpa o display OLED
- Apaga todos os LEDs da matriz
- Desliga o buzzer
- Garante que o sistema inicie em estado limpo

## Componentes Reutilizáveis

### Classes de Hardware Disponíveis:

- **`Display`**: Controle do display OLED para interface do usuário
- **`MatrizLED`**: Funções para manipular a matriz de LEDs 5x5 com efeitos visuais
- **`Buzzer`**: Efeitos sonoros, notas musicais e melodias
- **`Botoes`**: Gerenciamento de entrada pelos botões com debounce

### Utilitários Disponíveis:

- **`contagem_regressiva()`**: Contagem visual e sonora para iniciar jogos
- **`navegar_menu()`**: Sistema de navegação em menus com suporte a joystick
- **`abreviar_texto()`**: Abreviação inteligente de texto para o display

## Configuração

O arquivo `config.py` centraliza:

- **Pinos de hardware** (LEDs, botões, display, sensor)
- **Cores predefinidas** para os LEDs
- **Configurações de áudio** (notas musicais)
- **Parâmetros de jogo** (tempos, limites)

## Características Técnicas

- **Plataforma**: MicroPython na BitdogLab
- **Display**: OLED 128x64 pixels (I2C)
- **LEDs**: Matriz 5x5 NeoPixel RGB
- **Controles**: 2 botões digitais + sensor de movimento opcional
- **Audio**: Buzzer com PWM para efeitos sonoros
- **Sensores**: MPU-6050 (acelerômetro + giroscópio) via I2C

## Troubleshooting

### Problemas Comuns:

1. **"Sensor MPU-6050 não encontrado"**

   - Verifique as conexões I2C (pinos 0 e 1)
   - Confirme a alimentação do sensor (3.3V)

2. **Display não funciona**

   - Verifique as conexões I2C do display (pinos 14 e 15)
   - Confirme o endereço I2C (padrão: 0x3C)

3. **LEDs não acendem**

   - Verifique a conexão do pino 7 (dados dos NeoPixels)
   - Confirme a alimentação adequada

4. **Botões não respondem**
   - Verifique as conexões dos pinos 5 (A) e 6 (B)
   - Confirme se os pull-ups estão funcionando

### Debug:

Use `print()` statements para debugar - as mensagens aparecerão no console serial da BitdogLab.

## Contribuindo

Para adicionar novos jogos ou melhorar os existentes:

1. Mantenha a estrutura modular
2. Use as classes de componentes fornecidas
3. Implemente tratamento de erros adequado
4. Teste com e sem o sensor MPU-6050
5. Documente novas funcionalidades

## Licença

Este projeto é open source e pode ser usado livremente para fins educacionais e pessoais.
