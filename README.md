# 🎮🤖 Projetos BitDogLab - EA801W

Repositório com projetos desenvolvidos em MicroPython para a placa BitDogLab, criados para a disciplina de Laboratório de Projetos em Sistemas Embarcados da Unicamp.

## 📁 Projetos Incluídos

### 🤖 [Braço Robótico Simples](./braco-robotico/)

Controle um braço robótico de 3 eixos com joystick e botões.

**Características principais:**

- 3 servos (garra, up/down, frente/trás)
- Controle por joystick analógico
- Sistema de economia de energia
- Interface intuitiva com feedback no console

**[📖 Documentação Completa →](./braco-robotico/README.md)**

---

### 🎮 [Multi-Game Collection](./multi-game/)

Coleção de 5 mini-jogos interativos com sensores de movimento.

**Características principais:**

- 5 jogos únicos (reação, memória, inclinação, giroscópio, equilíbrio)
- Suporte opcional ao sensor MPU-6050
- Arquitetura modular para fácil expansão
- Interface visual com display OLED e matriz LED

**[📖 Documentação Completa →](./multi-game/README.md)**

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: MicroPython
- **Plataforma**: ESP32 (BitDogLab)
- **Sensores**: MPU-6050 (giroscópio/acelerômetro)
- **Display**: OLED 128x64 SSD1306
- **LEDs**: Matriz NeoPixel 5x5
- **Servos**: SG90 ou compatíveis

## 🚀 Como usar

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/seu-usuario/bitdoglab-projects.git
   cd bitdoglab-projects
   ```

2. **Escolha um projeto:**

   - Para o braço robótico: `cd braco-robotico`
   - Para os mini-jogos: `cd multi-game`

3. **Siga as instruções específicas** no README de cada projeto

## 📋 Requisitos Básicos

### Hardware Comum:

- Placa BitDogLab (ESP32)
- Display OLED 128x64
- Matriz LED NeoPixel 5x5
- Buzzer PWM
- 2 Botões digitais

### Hardware Específico:

- **Braço Robótico**: 3x Servo motores + Joystick analógico
- **Multi-Game**: Sensor MPU-6050 (opcional, mas recomendado)

## 👥 Autores

- **Felipe Nogueira** - RA 167263
- **Giovanna Presta** - RA 173275

**Projeto Acadêmico - Unicamp 2025**  
_Disciplina: G_EA801W - Laboratório de Projetos em Sistemas Embarcados_

## 📄 Licença

Este projeto está sob a Licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

**🎯 Escolha um projeto e comece a explorar!**
