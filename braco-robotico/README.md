# 🤖 Braço Robótico Simples - BitDogLab

Um braço robótico controlado por joystick e botões, desenvolvido em MicroPython para a placa BitDogLab.

## 📋 O que faz?

Este projeto controla um braço robótico simples com 3 servos:

- **Garra**: Abre e fecha para pegar objetos
- **Up/Down**: Move o braço para cima e para baixo
- **Frente/Trás**: Move o braço para frente e para trás

## 🎮 Como usar?

### Controles:

- **Botão A**: Abre/fecha a garra
- **Joystick**: Move o braço para cima/baixo
- **Joystick + Botão B**: Move o braço para frente/trás
- **Botão A + B juntos**: Centraliza o movimento frente/trás

### Para começar:

1. Conecte os servos nos pinos corretos
2. Execute o código `main.py`
3. Use os controles para movimentar o braço

## 🔌 Conexões

| Componente        | Pino BitDogLab |
| ----------------- | -------------- |
| Servo da Garra    | Pino 8 (PWM)   |
| Servo Up/Down     | Pino 9 (PWM)   |
| Servo Frente/Trás | Pino 4 (PWM)   |
| Botão A           | Pino 5         |
| Botão B           | Pino 6         |
| Joystick          | Pino 26 (ADC)  |

## ⚡ Recursos especiais

### Economia de energia:

- Desliga servos automaticamente quando não estão sendo usados
- Usa apenas um servo por vez para evitar sobrecarga
- PWM é desligado após 1 segundo de inatividade

### Segurança:

- Limites de movimento para proteger os servos
- Zona morta no joystick para evitar movimentos acidentais
- Inicialização segura com posições conhecidas

## 🛠️ Características técnicas

- **Linguagem**: MicroPython
- **Placa**: BitDogLab
- **Servos**: 3x Servo SG90 (ou similar)
- **Frequência PWM**: 50Hz
- **Range PWM**: 1600-8200 (0°-180°)

## 🚀 Como instalar

1. Conecte a placa BitDogLab ao computador
2. Copie o arquivo `main.py` para a placa
3. Conecte os servos e componentes conforme a tabela
4. Execute o programa

## 📊 Indicadores no console

O programa mostra informações úteis:

- Status atual de cada servo
- Posições em graus (0°-180°)
- Estado da garra (aberta/fechada)
- Confirmação de movimentos

## 🔧 Personalização

Você pode ajustar no código:

- **Velocidade**: Altere `self.incremento = 300`
- **Timeout**: Modifique `self.TIMEOUT_SERVO = 1.0`
- **Zona morta**: Ajuste `self.zona_morta = 8000`

## 📝 Exemplo de uso

```
🤖 Iniciando Braço Robótico...
📍 Posicionando servos no LIMITE MÁXIMO...
🎮 === CONTROLES DO BRAÇO ROBÓTICO ===
🔘 Botão A: Abrir/Fechar garra
🕹️ Joystick: Mover UP/DOWN
🕹️ Joystick + Botão B: Mover FRENTE/TRÁS
```

## 🎯 Dicas importantes

- O braço inicia com todos os servos na posição máxima
- Use movimentos suaves para não forçar os servos
- Pressione Ctrl+C para sair do programa com segurança
- Observe os limites de movimento para não danificar o equipamento

## 🤝 Contribuição

Este é um projeto educacional. Sinta-se livre para:

- Melhorar o código
- Adicionar novos recursos
- Criar novos modos de controle
- Compartilhar suas modificações

---

## 👥 Autores e Créditos

### Desenvolvedores Principais

- **Felipe Nogueira** - RA 167263 - _Arquitetura e jogos principais_
- **Giovanna Presta** - RA 173275 - _Integração de sensores e interface_

### Projeto Acadêmico

\*Desenvolvido para a disciplina **G_EA801W - Laboratório de Projetos em Sistemas Embarcados\***  
**Universidade Estadual de Campinas (Unicamp) - 2025**

**Desenvolvido para BitDogLab com MicroPython** 🐍
