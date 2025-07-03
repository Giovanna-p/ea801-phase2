import machine
import time
import gc

# Configura o garbage collector
gc.enable()
gc.collect()

# Configura comunicação serial
uart = machine.UART(0, baudrate=115200)

# Configuração do LED da placa (ajuste o pino conforme necessário para BitDogLab)
led = machine.Pin(25, machine.Pin.OUT)

# Função para piscar o LED indicando inicialização
def blink_led(times=3):
    for _ in range(times):
        led.value(1)
        time.sleep(0.1)
        led.value(0)
        time.sleep(0.1)

# Pisca o LED para indicar que o boot foi iniciado
blink_led()

print("Boot inicializado com sucesso!")