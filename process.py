import pika
import time
import threading

class MotorTest:
    def __init__(self):
        self.tasks = {}
        self.lock = threading.Lock()

    def process_motor_id(self, ch, method, properties, body):
        motor_id = body.decode()
        motor_type = motor_id[-2:]  # OL ou AG
        base_motor_id = motor_id[:-2]

        if motor_type == "OL":
            with self.lock:
                self.tasks[base_motor_id] = threading.Thread(target=self.test_oil, args=(motor_id,))
                self.tasks[base_motor_id].start()
        elif motor_type == "AG":
            if base_motor_id in self.tasks:
                self.tasks[base_motor_id].join()
                self.test_water(motor_id)
            else:
                print(f"Tarefa para motor {motor_id} não encontrada")

    def test_oil(self, motor_id):
        print(f"Iniciando teste de óleo para motor {motor_id}")
        time.sleep(2)  # Simulação do teste
        print(f"Finalizando teste de óleo para motor {motor_id}")
        print('Teste de óleo concluído')

    def test_water(self, motor_id):
        print(f"Iniciando teste de água para motor {motor_id}")
        time.sleep(2)  # Simulação do teste
        print(f"Finalizando teste de água para motor {motor_id}")
        print('Teste de água concluído')

def main():
    motor_test = MotorTest()

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='motor_ids')

    channel.basic_consume(queue='motor_ids', on_message_callback=motor_test.process_motor_id, auto_ack=True)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    main()