# 🎮 BitdogLab Multi-Game (MINIJI)

Uma coleção modular de mini-jogos interativos desenvolvida em MicroPython para a placa BitdogLab (ESP32), testando reflexos, memória, coordenação e equilíbrio através de sensores de movimento avançados.

## 🚀 Características

- **Arquitetura Totalmente Modular** - Fácil adição/remoção de jogos
- **Sistema de Detecção Automática** do sensor MPU-6050
- **Reset Automático de Hardware** a cada inicialização
- **Interface Intuitiva** com feedback visual, sonoro e tátil
- **5 Jogos Únicos** com mecânicas distintas implementados
- **Sistema de Pontuação** individual por jogo

## 📁 Estrutura do Projeto

```
BitdogLab-Games/
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
    ├── reaction_game.py     # ✅ Jogo de reação
    ├── memory_game.py       # ✅ Jogo de memória
    ├── tilt_game.py         # ✅ Jogo de inclinação (MPU-6050)
    ├── gyro_game.py         # ✅ Jogo de giroscópio (MPU-6050)
    ├── balance_game.py      # ✅ Jogo de equilíbrio (MPU-6050)
    ├── rhythm_game.py       # 🚧 Jogo rítmico
    ├── maze_game.py         # 🚧 Jogo de labirinto
    └── sensor_test.py       # 🔧 Utilitário de teste do sensor
```

**Legendas:**

- ✅ Totalmente implementado e ativo
- 🚧 Em desenvolvimento (comentado no main.py)
- 🔧 Utilitário de desenvolvimento

## 🎯 Jogos Implementados

### 1. 🟢 Jogo de Reação (reaction_game.py)

**Teste seus reflexos!**

- Pressione o botão A **APENAS** quando o LED **VERDE** aparecer
- Ignore cores distratoras (azul, vermelho, branco)
- 3 rodadas com estatísticas detalhadas de tempo de reação
- Pontuação baseada no melhor tempo
- Mede tempos de reação em milissegundos com precisão

### 2. 🧠 Jogo de Memória (memory_game.py)

**Desafie sua memória!**

- Memorize e repita sequências de cores crescentes
- **Verde = Botão A** | **Vermelho = Botão B**
- Progressão de 1 a 10 níveis de dificuldade
- Feedback sonoro único para cada cor (notas musicais)
- Velocidade aumenta conforme o nível avança

### 3. 📱 Jogo de Inclinação (tilt_game.py)

**Controle por inclinação!**

- **Requer sensor MPU-6050**
- Incline o dispositivo para mover a "bolinha" azul na matriz
- Alcance os alvos amarelos piscantes para ganhar pontos
- Controle baseado no acelerômetro em tempo real
- Sistema de física realista com gravidade

### 4. 🎯 Jogo de Giroscópio (gyro_game.py)

**Controle por rotação!**

- **Requer sensor MPU-6050**
- Gire o dispositivo para apontar o ponteiro roxo nos alvos
- Pressione botão A para "atirar" no alvo amarelo
- 30 segundos de ação contínua
- Tolerância de ±30° para facilitar a jogabilidade

### 5. ⚖️ Jogo de Equilíbrio (balance_game.py)

**Mantenha-se estável!**

- **Requer sensor MPU-6050**
- Sistema de calibração automática da posição inicial
- 5 níveis de estabilidade com padrões visuais únicos:
  - **Nível 1**: Ponto central (vermelho)
  - **Nível 2**: Cruz simples (amarelo)
  - **Nível 3**: Círculo (azul)
  - **Nível 4**: Bordas da matriz (roxo)
  - **Nível 5**: Matriz completa (verde)
- Pontuação contínua baseada na estabilidade mantida
- 30 segundos de concentração total

### 6. 🎵 Jogo de Ritmo (rhythm_game.py) 🚧

**Em desenvolvimento**

- Pressione os botões no tempo certo quando as notas atingirem a zona
- Botão A para faixa esquerda, Botão B para faixa direita
- Pontuação baseada na precisão do timing

### 7. 🧩 Jogo de Labirinto (maze_game.py) 🚧

**Em desenvolvimento**

- Navegue através de um labirinto usando sensores de movimento
- Encontre a saída no menor tempo possível

### 8. 🔧 Teste do Sensor (sensor_test.py)

**Utilitário de desenvolvimento**

- Verifica o funcionamento do sensor MPU-6050
- Exibe valores em tempo real do acelerômetro e giroscópio
- Útil para debug e calibração

## 🛠️ Hardware Necessário

### Componentes Principais

- **BitdogLab** (ESP32)
- **Display OLED** 128x64 SSD1306 (I2C)
- **Matriz LED** 5x5 NeoPixel (25 LEDs RGB)
- **MPU-6050** Sensor 6-DOF (I2C) - _Opcional mas recomendado_
- **Buzzer PWM**
- **2 Botões digitais** (com pull-up interno)

### 🔌 Pinout Completo

```python
# LEDs e Controles
LED_PIN = 7           # Matriz NeoPixel (WS2812B)
BUTTON_A_PIN = 5      # Botão A (pull-up interno)
BUTTON_B_PIN = 6      # Botão B (pull-up interno)
BUZZER_PIN = 21       # Buzzer PWM

# I2C Devices
OLED_SCL_PIN = 15     # Display OLED (Clock)
OLED_SDA_PIN = 14     # Display OLED (Data)
OLED_ADDR = 0x3C      # Endereço I2C do display

# Sensor MPU-6050 (I2C secundário)
MPU_SCL_PIN = 1       # Sensor Clock
MPU_SDA_PIN = 0       # Sensor Data
MPU_ADDR = 0x68       # Endereço I2C do sensor
```

### 🔗 Conexões do Sensor MPU-6050

| MPU-6050 | BitdogLab |
| -------- | --------- |
| VCC      | 3.3V      |
| GND      | GND       |
| SCL      | Pino 1    |
| SDA      | Pino 0    |

## 🚀 Como Usar

### 1. Preparação do Hardware

1. Monte a BitdogLab com todos os componentes básicos
2. **[Opcional]** Conecte o MPU-6050 via I2C (pinos 0 e 1) para jogos avançados
3. Verifique todas as conexões e alimentação

### 2. Upload do Código

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/bitdoglab-games.git

# Copie todos os arquivos para a BitdogLab via Thonny/rshell/ampy
# IMPORTANTE: Mantenha a estrutura de pastas
```

### 3. Execução

```python
# Execute o arquivo principal
python main.py

# Ou simplesmente reinicie a placa (boot automático)
```

### 4. 🎮 Controles

- **Botão A**: Navegação nos menus / Verde no jogo de memória / Ação primária
- **Botão B**: Seleção nos menus / Vermelho no jogo de memória
- **Movimento Físico**: Inclinar/girar o dispositivo (jogos com MPU-6050)

## 🎯 Como Jogar

1. **Inicialização**: A placa executa reset automático e mostra o menu principal
2. **Navegação**: Use botão A para navegar, B para selecionar jogos
3. **Detecção Automática**: O sistema verifica se o sensor MPU-6050 está disponível
4. **Jogo**: Siga as instruções específicas mostradas no display OLED
5. **Pontuação**: Veja seu desempenho e estatísticas ao final
6. **Repetir**: Volte ao menu para experimentar outros jogos

## 🔧 Sistema de Reset de Hardware

O projeto inclui uma função `reset_hardware()` executada automaticamente que:

- ✅ Limpa completamente o display OLED
- ✅ Apaga todos os LEDs da matriz NeoPixel
- ✅ Desliga o buzzer (duty = 0)
- ✅ Garante que o sistema inicie em estado limpo e previsível

## 🤖 Sistema de Detecção Automática

### Detecção Inteligente do MPU-6050

O sistema verifica automaticamente se o sensor está conectado:

```python
# Verifica se o sensor está presente no barramento I2C
self.sensor_presente = self.mpu_addr in self.i2c.scan()
```

**Comportamento:**

- ✅ **Sensor presente**: Jogos avançados ficam disponíveis
- ❌ **Sensor ausente**: Jogos básicos funcionam normalmente, avançados mostram erro informativo

### Fallback Automático

- **I2C Hardware** não disponível → **SoftI2C** automaticamente
- **Sensor não encontrado** → Mensagem amigável e retorno ao menu
- **Erro de leitura** → Continuidade do jogo sem travamento

## 🛠️ Adicionando Novos Jogos

A arquitetura modular facilita extremamente a criação de novos jogos:

### 1. Crie o arquivo do jogo

```python
# stages/meu_jogo_incrivel.py
class MeuJogoIncrivel:
    def __init__(self, display, matriz, buzzer, botoes):
        """Inicializa o jogo com os componentes de hardware"""
        self.display = display
        self.matriz = matriz
        self.buzzer = buzzer
        self.botoes = botoes

    def iniciar(self):
        """Método principal do jogo - deve retornar pontuação ou None"""
        # Sua implementação aqui
        self.display.mostrar_mensagem([
            "Meu Jogo Incrivel!",
            "Pressione A para",
            "comecar a jogar"
        ])

        self.botoes.aguardar_botao_a()

        # Lógica do jogo...
        pontuacao = 100  # Exemplo

        return pontuacao  # ou None se não houver pontuação
```

### 2. Adicione no main.py

```python
# No topo do arquivo
from stages.meu_jogo_incrivel import MeuJogoIncrivel

# Na função main(), dentro do manager:
manager.adicionar_etapa(MeuJogoIncrivel, "Jogo Incrivel")
```

### 3. Ative o jogo

Descomente a linha correspondente no `main.py` para tornar o jogo ativo.

## 🎨 Recursos Disponíveis

### 🌈 Cores Predefinidas

```python
COR_VERDE = (0, 100, 0)      # Verde principal
COR_AZUL = (0, 0, 100)       # Azul do jogador
COR_VERMELHO = (100, 0, 0)   # Vermelho de perigo
COR_AMARELO = (100, 100, 0)  # Amarelo de alvos
COR_ROXO = (100, 0, 100)     # Roxo de ponteiros
COR_CIANO = (0, 100, 100)    # Ciano decorativo
COR_BRANCO = (30, 30, 30)    # Branco suave
COR_APAGADO = (0, 0, 0)      # Apagado/off
```

### 🎵 Notas Musicais

```python
NOTAS = {
    'C4': 262,  # Dó
    'D4': 294,  # Ré
    'E4': 330,  # Mi
    'F4': 349,  # Fá
    'G4': 392,  # Sol
    'A4': 440,  # Lá
    'B4': 494,  # Si
    'C5': 523   # Dó (oitava superior)
}
```

### 🔧 Classes de Hardware Reutilizáveis

#### Display (display.py)

```python
display.mostrar_mensagem(["Linha 1", "Linha 2", "Linha 3"])
display.exibir_numero_grande(3)  # Contagem regressiva
display.mostrar_menu("Titulo", ["Op1", "Op2"], selecao=0)
```

#### Matriz LED (matriz_led.py)

```python
matriz.acender_led_cor(x, y, config.COR_VERDE)
matriz.piscar_led(x, y, config.COR_VERMELHO, vezes=3)
matriz.mostrar_padrao([(0,0,COR_AZUL), (1,1,COR_VERDE)])
```

#### Buzzer (buzzer.py)

```python
buzzer.tocar_nota("A4", 200)  # Lá por 200ms
buzzer.tocar_fim_jogo()       # Melodia de vitória
buzzer.tocar_game_over()      # Melodia de derrota
```

#### Botões (utils.py)

```python
botoes.aguardar_botao_a()           # Aguarda botão A
botao = botoes.aguardar_qualquer_botao()  # Retorna 1 ou 2
if botoes.esta_pressionado_a():     # Verifica sem aguardar
```

### 🛠️ Utilitários Disponíveis

```python
# Contagem regressiva visual e sonora
contagem_regressiva(display, buzzer, segundos=3)

# Sistema de navegação em menus
selecao = navegar_menu(display, botoes, "Titulo", ["Op1", "Op2"])

# Abreviação inteligente para display pequeno
texto_curto = abreviar_texto("Texto muito longo para display", max_chars=15)
```

## 🐛 Troubleshooting

### ❌ Problemas Comuns e Soluções

#### 1. "Sensor MPU-6050 não encontrado"

```
Erro: Sensor MPU-6050 nao encontrado!
Verifique conexao
```

**Soluções:**

- ✅ Verifique conexões I2C (pinos 0 e 1)
- ✅ Confirme alimentação 3.3V (não 5V!)
- ✅ Teste com outro sensor MPU-6050
- ✅ Use `sensor_test.py` para diagnóstico

#### 2. Display OLED não funciona

**Verificações:**

- ✅ Conexões I2C corretas (pinos 14 e 15)
- ✅ Endereço I2C correto (0x3C padrão)
- ✅ Compatibilidade SSD1306
- ✅ Alimentação adequada

#### 3. LEDs NeoPixel não acendem

**Verificações:**

- ✅ Conexão no pino 7 (sinal de dados)
- ✅ Ordem dos fios: GND, VCC, DATA
- ✅ Alimentação suficiente (25 LEDs = ~1.5A máximo)
- ✅ Teste com `matriz.acender_led_cor(2, 2, config.COR_BRANCO)`

#### 4. Botões não respondem

**Verificações:**

- ✅ Conexões nos pinos 5 (A) e 6 (B)
- ✅ Pull-ups internos habilitados (automático no código)
- ✅ Teste com multímetro (0V pressionado, 3.3V solto)

#### 5. Som não funciona

**Verificações:**

- ✅ Conexão no pino 21
- ✅ Buzzer passivo (não ativo)
- ✅ Teste com `buzzer.tocar_som(1000, 200)`

### 🔍 Debug e Diagnóstico

#### Console Serial

```python
# Use print() para debug - aparece no console da BitdogLab
print(f"Valor do sensor: {dados['accel']['x']}")
print("Debug: Botão A pressionado")
```

#### Sensor Test Utility

Execute `sensor_test.py` diretamente para testar o MPU-6050:

```python
# Mostra valores em tempo real
# Útil para calibração e diagnóstico
```

## 📊 Especificações Técnicas

- **Plataforma**: ESP32 com MicroPython
- **Display**: OLED 128x64 pixels SSD1306 (I2C)
- **LEDs**: Matriz 5x5 NeoPixel WS2812B (RGB individual)
- **Controles**: 2 botões digitais + sensor de movimento 6-DOF
- **Áudio**: Buzzer PWM com notas musicais e melodias
- **Sensores**: MPU-6050 (acelerômetro + giroscópio 3-eixos cada)
- **Comunicação**: Duplo I2C (hardware + software)

## 🤝 Contribuindo

### Como Contribuir

1. **Fork** o projeto no GitHub
2. **Clone** sua fork localmente
3. **Crie uma branch** para sua feature (`git checkout -b feature/JogoIncrivel`)
4. **Implemente** seguindo os padrões do projeto
5. **Teste** com e sem sensor MPU-6050
6. **Commit** suas mudanças (`git commit -m 'Add: Jogo Incrível implementado'`)
7. **Push** para sua branch (`git push origin feature/JogoIncrivel`)
8. **Abra um Pull Request** detalhado

### 💡 Ideias para Contribuições

#### Novos Jogos

- 🐍 **Snake Game**: Jogo da cobrinha na matriz LED
- 🎵 **Simon Says**: Versão eletrônica do jogo clássico
- 🏃 **Runner Game**: Endless runner com obstáculos
- 🧩 **Puzzle Game**: Quebra-cabeças deslizantes
- 🎯 **Target Practice**: Tiro ao alvo avançado

#### Melhorias do Sistema

- 🏆 **Sistema de Ranking**: Persistência de high scores
- 📊 **Estatísticas Avançadas**: Gráficos de desempenho
- 🌐 **WiFi Integration**: Multiplayer ou cloud saves
- 🎚️ **Configurações**: Dificuldade, volume, calibração
- 📱 **Mobile App**: Controle remoto via Bluetooth

#### Sensores Adicionais

- 🌈 **TCS34725**: Sensor de cor RGB
- 📏 **Ultrasônico**: Sensor de distância
- 🌡️ **DHT22**: Temperatura e umidade
- 💡 **LDR**: Sensor de luminosidade

### 📋 Diretrizes de Contribuição

- **Mantenha** a estrutura modular existente
- **Use** as classes de componentes fornecidas
- **Implemente** tratamento de erros robusto
- **Teste** compatibilidade com/sem sensores opcionais
- **Documente** novas funcionalidades no código
- **Siga** os padrões de nomenclatura Python (PEP 8)

## 📜 Licença

Este projeto está sob a **Licença MIT**. Veja o arquivo `LICENSE` para detalhes completos.

### Resumo da Licença

- ✅ **Uso comercial** permitido
- ✅ **Modificação** permitida
- ✅ **Distribuição** permitida
- ✅ **Uso privado** permitido
- ❌ **Sem garantia** - uso por sua conta e risco

## 👥 Autores e Créditos

### Desenvolvedores Principais

- **Felipe Nogueira** - RA 167263 - _Arquitetura e jogos principais_
- **Giovanna Presta** - RA 173275 - _Integração de sensores e interface_

### Projeto Acadêmico

\*Desenvolvido para a disciplina **G_EA801W - Laboratório de Projetos em Sistemas Embarcados\***  
**Universidade Estadual de Campinas (Unicamp) - 2025**

## 🙏 Agradecimentos

- **Professor e equipe** da disciplina EA801W pela orientação
- **Comunidade MicroPython** pela documentação e suporte
- **Espressif Systems** pela plataforma ESP32
- **Adafruit** pelas bibliotecas de sensores e LEDs
- **Biblioteca ssd1306** para MicroPython
- **Comunidade BitdogLab** pelos testes e feedback

---

## 🎮 Comece a Jogar!

```bash
git clone https://github.com/Giovanna-p/ea801-phase2
cd ea801-phase2
# Copie para sua BitdogLab e execute main.py
```

**🎯 Divirta-se testando seus reflexos, memória e coordenação!**

---

[![Made with MicroPython](https://img.shields.io/badge/Made%20with-MicroPython-blue.svg)](https://micropython.org/)
[![Platform ESP32](https://img.shields.io/badge/Platform-ESP32-red.svg)](https://www.espressif.com/en/products/socs/esp32)
[![Sensor MPU6050](https://img.shields.io/badge/Sensor-MPU6050-green.svg)](https://invensense.tdk.com/products/motion-tracking/6-axis/mpu-6050/)
[![License MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Unicamp 2025](https://img.shields.io/badge/Unicamp-2025-purple.svg)](https://www.unicamp.br/)
