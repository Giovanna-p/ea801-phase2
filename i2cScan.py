from machine import Pin, I2C
import time

# Usando hardware I2C
# id: número do controlador I2C (0 ou 1 para a maioria dos ESP32)
# scl: pino SCL
# sda: pino SDA
# freq: frequência em Hz (normalmente 100kHz ou 400kHz)

# Tente primeiro com o ID 0


try:
    i2c = I2C(1, scl=Pin(1), sda=Pin(0), freq=400000)
    print("I2C inicializado com ID 0")
except Exception as e:
    print(f"Erro ao inicializar I2C com ID 0: {e}")
    try:
        # Se falhar, tente com o ID 1
        i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
        print("I2C inicializado com ID 1")
    except Exception as e:
        print(f"Erro ao inicializar I2C com ID 1: {e}")
        # Se ambos falharem, use SoftI2C como fallback
        i2c = SoftI2C(scl=Pin(1), sda=Pin(0), freq=100000)
        print("Fallback para SoftI2C")

def scan_i2c():
    dispositivos = i2c.scan()
    print(f"Encontrados {len(dispositivos)} dispositivos I2C:")
    
    if dispositivos:
        for dispositivo in dispositivos:
            print(f"  Endereço: 0x{dispositivo:02x}")
    else:
        print("  Nenhum dispositivo encontrado.")
    
    return dispositivos

# Função para ler dados do MPU-6050
def read_mpu6050_data():
    mpu_addr = 0x68  # Endereço padrão do MPU-6050
    
    try:
        # Verifica se o MPU-6050 está no barramento
        if mpu_addr not in i2c.scan():
            print("MPU-6050 não encontrado!")
            return None
            
        # Acorda o MPU-6050 escrevendo 0 no registro de gerenciamento de energia
        i2c.writeto_mem(mpu_addr, 0x6B, b'\x00')
        time.sleep_ms(50)
        
        # Lê o registro WHO_AM_I para confirmar que é um MPU-6050
        who_am_i = i2c.readfrom_mem(mpu_addr, 0x75, 1)[0]
        print(f"WHO_AM_I: 0x{who_am_i:02x} (deve ser 0x68)")
        
        # Lê os dados do acelerômetro
        data = i2c.readfrom_mem(mpu_addr, 0x3B, 14)
        
        # Converte os dados (cada valor é de 16 bits, em complemento de 2)
        accel_x = (data[0] << 8) | data[1]
        accel_y = (data[2] << 8) | data[3]
        accel_z = (data[4] << 8) | data[5]
        
        # Converte para valor com sinal se for negativo
        if accel_x > 32767:
            accel_x -= 65536
        if accel_y > 32767:
            accel_y -= 65536
        if accel_z > 32767:
            accel_z -= 65536
            
        # Temperatura
        temp = (data[6] << 8) | data[7]
        if temp > 32767:
            temp -= 65536
        temp_c = temp / 340.0 + 36.53
        
        # Dados do giroscópio
        gyro_x = (data[8] << 8) | data[9]
        gyro_y = (data[10] << 8) | data[11]
        gyro_z = (data[12] << 8) | data[13]
        
        if gyro_x > 32767:
            gyro_x -= 65536
        if gyro_y > 32767:
            gyro_y -= 65536
        if gyro_z > 32767:
            gyro_z -= 65536
            
        # Converte para unidades físicas
        accel_x_g = accel_x / 16384.0  # para ±2g
        accel_y_g = accel_y / 16384.0
        accel_z_g = accel_z / 16384.0
        
        gyro_x_deg = gyro_x / 131.0  # para ±250°/s
        gyro_y_deg = gyro_y / 131.0
        gyro_z_deg = gyro_z / 131.0
        
        return {
            'accel': {
                'x': accel_x_g,
                'y': accel_y_g,
                'z': accel_z_g,
                'raw': (accel_x, accel_y, accel_z)
            },
            'gyro': {
                'x': gyro_x_deg,
                'y': gyro_y_deg,
                'z': gyro_z_deg,
                'raw': (gyro_x, gyro_y, gyro_z)
            },
            'temp': temp_c
        }
        
    except Exception as e:
        print(f"Erro ao ler MPU-6050: {e}")
        return None

# Programa principal
print("=== Teste do MPU-6050 com Hardware I2C ===")

# Primeiro escaneia o barramento
print("\n--- Escaneando barramento I2C ---")
dispositivos = scan_i2c()

if 0x68 in dispositivos or 0x69 in dispositivos:
    print("MPU-6050 detectado! Iniciando leitura de dados...")
    
    try:
        while True:
            dados = read_mpu6050_data()
            
            if dados:
                print("\n=== Leitura do MPU-6050 ===")
                print(f"Acelerômetro (g): X={dados['accel']['x']:.3f}, Y={dados['accel']['y']:.3f}, Z={dados['accel']['z']:.3f}")
                print(f"Giroscópio (°/s): X={dados['gyro']['x']:.3f}, Y={dados['gyro']['y']:.3f}, Z={dados['gyro']['z']:.3f}")
                print(f"Temperatura: {dados['temp']:.2f}°C")
                print(f"Raw Accel: {dados['accel']['raw']}")
                print(f"Raw Gyro: {dados['gyro']['raw']}")
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")
else:
    print("MPU-6050 não detectado no barramento I2C.")