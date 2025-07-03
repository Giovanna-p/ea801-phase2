from machine import Pin, SoftI2C
import sys
import os

i2c = SoftI2C(scl=Pin(3), sda=Pin(2))


# Executa o programa quando este arquivo é executado diretamente
if __name__ == "__main__":
    try:
        print("Arquivos no diretório atualllll:", os.listdir())
        print(i2c.scan())  # Deve mostrar [104] se for 0x68
    except Exception as e:
        # Tratamento básico de erros para debug
        print(f"Erro: {e}")