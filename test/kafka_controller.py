import os
from pathlib import Path
from jinja2 import Template
import tempfile
import subprocess
import time
import shutil
import test.util as test_util

KAFKA_SCRIPT = "bin/kafka-server-start.sh"
ZOOKEEPER_SCRIPT = "bin/zookeeper-server-start.sh"
KAFKA_TOPIC_SCRIPT = "bin/kafka-topics.sh"
KAFKA_CONFIG_OUT = "kafka.properties"
ZOOKEEPER_CONFIG_OUT = "zookeeper.properties"
ZOOKEEPER_DATA_DIR = "zookeeper"
KAFKA_LOG_DIR = "kafka-logs"
KAFKA_STDOUT = "kafka_stdout"
ZOOKEEPER_STDOUT = "zookeeper_stdout"


class KafkaController(object):
    def __init__(self, kafka_root: Path, kafka_config_template: Path,
                 zookeeper_config_template: Path, root_temp_dir: Path) -> None:
        self.kafka_root = kafka_root
        kafka_cmd = os.path.join(kafka_root, KAFKA_SCRIPT)
        zookeeper_cmd = os.path.join(kafka_root, ZOOKEEPER_SCRIPT)

        if not kafka_cmd or not os.access(kafka_cmd, os.X_OK):
            raise test_util.TestException("Kafka startup script {} doesn't exist or isn't executable".format(kafka_cmd))

        if not zookeeper_cmd or not os.access(zookeeper_cmd, os.X_OK):
            raise test_util.TestException("Zookeeper startup script {} doesn't exist or isn't executable".format(zookeeper_cmd))

        if not root_temp_dir:
            raise test_util.TestException("Kafka temp_dir is None")

        # make temp dirs
        self._init_temp_dir(root_temp_dir)
        self._init_kafka_configs(kafka_config_template, zookeeper_config_template)
        self._start_process(kafka_cmd, zookeeper_cmd)

    def _init_temp_dir(self, root_temp_dir: Path) -> None:
        """
        Sets up internal property temp_dir
        """
        root_temp_dir = root_temp_dir.absolute()
        os.makedirs(root_temp_dir, exist_ok=True)
        self.temp_dir = Path(tempfile.mkdtemp(prefix='KafkaController-', dir=str(root_temp_dir)))
        data_dir = self.temp_dir.joinpath('data')
        os.makedirs(data_dir)

    def _init_kafka_configs(self, kafka_config: Path, zookeeper_config: Path) -> None:
        """
        Sets up internal properties kafka_port and zookeeper_port,
        kafka_config_path, zookeeper_config_path
        """
        self.kafka_port = test_util.find_free_port()
        self.zookeeper_port = test_util.find_free_port()
        self.zookeeper_data_dir = os.path.join(self.temp_dir, ZOOKEEPER_DATA_DIR)
        self.kafka_log_dir = os.path.join(self.temp_dir, KAFKA_LOG_DIR)

        template_data = {
            "zookeeper_port": self.zookeeper_port,
            "kafka_port": self.kafka_port,
            "zookeeper_data_dir": str(self.zookeeper_data_dir),
            "kafka_log_dir": str(self.kafka_log_dir)
        }

        kafka_config = kafka_config.absolute()
        with open(kafka_config, "r") as f:
            k_file = f.read()
        tmpl = Template(k_file)
        self.kafka_config_path = os.path.join(self.temp_dir, KAFKA_CONFIG_OUT)
        with open(self.kafka_config_path, "w") as f:
            f.write(tmpl.render(template_data))

        zookeeper_config = zookeeper_config.absolute()
        with open(zookeeper_config, "r") as f:
            z_file = f.read()
        tmpl = Template(z_file)
        self.zookeeper_config_path = os.path.join(self.temp_dir, ZOOKEEPER_CONFIG_OUT)
        with open(self.zookeeper_config_path, "w") as f:
            f.write(tmpl.render(template_data))

    def _start_process(self, kafka_cmd: Path, zookeeper_cmd: Path) -> None:
        self._zookeeper_out = open(os.path.join(self.temp_dir, ZOOKEEPER_STDOUT), "w")
        zookeeper_run_cmd = [zookeeper_cmd, self.zookeeper_config_path]
        self._zookeeper_proc = subprocess.Popen(zookeeper_run_cmd, stdout=self._zookeeper_out, stderr=subprocess.STDOUT)

        time.sleep(5)

        self._kafka_out = open(os.path.join(self.temp_dir, KAFKA_STDOUT), "w")
        kafka_run_cmd = [kafka_cmd, self.kafka_config_path]
        self._kafka_proc = subprocess.Popen(kafka_run_cmd, stdout=self._kafka_out, stderr=subprocess.STDOUT)

        time.sleep(5)

        cfg = test_util.test_config()
        topics = cfg.get("kafka", "topics").split(",")
        for topic in topics:
            create_topic_cmd = [os.path.join(self.kafka_root, KAFKA_TOPIC_SCRIPT), "--create", "--zookeeper",
                                "localhost:{}".format(self.zookeeper_port), "--replication-factor", "1",
                                "--partitions", "1", "--topic", topic]
            print("Running create topic script for {}".format(topic))
            print(" ".join(create_topic_cmd))
            subprocess.run(create_topic_cmd)


    def destroy(self, delete_temp_files: bool) -> None:
        if self._kafka_out:
            self._kafka_out.close()
        if self._kafka_proc:
            self._kafka_proc.terminate()
        if self._zookeeper_out:
            self._zookeeper_out.close()
        if self._zookeeper_proc:
            self._zookeeper_proc.terminate()
        if delete_temp_files and self.temp_dir:
            shutil.rmtree(self.temp_dir)

def main():
    from . import conftest
    from kafka import (
        KafkaProducer,
        KafkaConsumer
    )
    conftest.pytest_sessionstart(None)

    tempdir = test_util.get_kafka_temp_dir()
    kc = KafkaController(
        test_util.get_kafka_root(),
        test_util.get_kafka_config(),
        test_util.get_zookeeper_config(),
        tempdir
    )
    print("Running Kafka and Zookeeper")
    print("Zookeeper port: {}".format(kc.zookeeper_port))
    print("Kafka port: {}".format(kc.kafka_port))
    print("Temp dir: {}".format(kc.temp_dir))
    host = "localhost:{}".format(kc.kafka_port)
    print("connecting to Kafka host: {}".format(host))
    time.sleep(3)
    print("posting test message")
    msg = b"Simple Test Message"
    topic = "test"
    p = KafkaProducer(bootstrap_servers=host)

    p.send(topic, msg)
    print("done. waiting before consuming it.")
    time.sleep(3)
    print("consuming test message")
    c = KafkaConsumer(bootstrap_servers=host,
                      group_id=None,
                      consumer_timeout_ms=1000,
                      enable_auto_commit=True,
                      auto_offset_reset="earliest")
    c.subscribe([topic])
    for msg in c:
        print("got message: {}".format(msg.value))
    input("Done. Press enter to shutdown and destroy.")
    kc.destroy(True)

if __name__ == '__main__':
    main()
