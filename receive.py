from flask import Flask, request, jsonify
import pika

app = Flask(__name__)

@app.route('/send_motor_id', methods=['POST'])
def send_motor_id():
    motor_id = request.json.get('motor_id')
    if motor_id:
        send_to_queue(motor_id)
        return jsonify({"status": "Motor ID received", "motor_id": motor_id}), 200
    else:
        return jsonify({"status": "Motor ID not provided"}), 400

def send_to_queue(motor_id):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='motor_ids')

    channel.basic_publish(exchange='',
                          routing_key='motor_ids',
                          body=motor_id)
    connection.close()

if __name__ == '__main__':
    app.run(port=5000)