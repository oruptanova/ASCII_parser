import argparse
import socket

import serial


class SerialHandler:
    def __init__(self, port, baudrate=9600):
        try:
            self.ser = serial.Serial(port, baudrate)
        except Exception as e:
            raise Exception(f"Ошибка при подключении к серийному порту: {e}")

    def send_command(self, command):
        self.ser.write(command.encode())
        response = self.ser.readline().decode().strip()
        return response

    def close(self):
        self.ser.close()


class TcpHandler:
    def __init__(self, host, port):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, int(port)))
        except Exception as e:
            raise Exception(f"Ошибка при подключении к TCP серверу: {e}")

    def send_command(self, command):
        self.socket.sendall(command.encode())
        response = self.socket.recv(1024).decode().strip()
        return response

    def close(self):
        self.socket.close()


class DataHandler:
    # Определение точек для получения напряжения и тока
    voltage_points = ['A', 'B']
    current_points = ['C']
    points = voltage_points + current_points

    @staticmethod
    def parse_response(response):
        try:
            voltage = None
            current = None
            if 'Voltage:' in response:
                voltage = float(response.split('Voltage:')[1].split('V')[0].strip())
            if 'Current:' in response:
                current = float(response.split('Current:')[1].split('A')[0].strip())
            return voltage, current
        except ValueError as e:
            raise ValueError(f"Ошибка в разборе данных: {e}")
        except Exception as e:
            raise Exception(f"Неизвестная ошибка: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Выберите тип интерфейса и введите необходимые параметры.")
    parser.add_argument('--type', choices=['serial', 'tcp'], required=True, help='Тип интерфейса: "serial" или "tcp"')
    parser.add_argument('--port', required=True, help='Порт для Serial или TCP')
    parser.add_argument('--baudrate', type=int, default=9600, help='Скорость передачи данных для Serial')
    parser.add_argument('--host', default='127.0.0.1', help='IP-адрес для TCP')

    args = parser.parse_args()

    if args.type == 'serial':
        session_handler = SerialHandler(args.port, args.baudrate)
    elif args.type == 'tcp':
        if not args.port.isdigit() or not (1 <= int(args.port) <= 65535):
            raise ValueError("Для TCP соединения необходимо указать корректный номер порта (от 1 до 65535).")
        session_handler = TcpHandler(args.host, args.port)

    for point in DataHandler.points:
        command = input(f"Введите команду для точки {point}: ")
        response = session_handler.send_command(command + '\n')
        voltage, current = DataHandler.parse_response(response)

        if voltage is not None and point in DataHandler.voltage_points:
            print(f"{point}: {voltage} V")
        elif current is not None and point in DataHandler.current_points:
            print(f"{point}: {current} A")
        elif voltage is None or current is None in DataHandler.points:
            print(f"{point}: incorrect value")

    # Закрытие соединения
    session_handler.close()
