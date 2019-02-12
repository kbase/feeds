from .kafka.listener import KafkaListener
from logger import log

if __name__ == "__main__":
    name = 'kafka_listener'
    log(name, "Initializing Kafka listener.")
    listener = KafkaListener()
    log(name, "Starting Kafka listener loop.")
    listener.start_listening()
