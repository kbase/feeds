from .kafka.listener import KafkaListener


if __name__ == "__main__":
    print("Initializing Listener")
    listener = KafkaListener()
    print("Starting to listen")
    listener.start_listening()
