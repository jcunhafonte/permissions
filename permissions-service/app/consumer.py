import time

from os import getenv
from confluent_kafka import Consumer, KafkaException
from confluent_avro import AvroKeyValueSerde, SchemaRegistry
from confluent_avro.schema_registry import HTTPBasicAuth

from policies.service import PoliciesService


def print_assignment(consumer, partitions):
    print('Assignment:', partitions)


policies_service = PoliciesService()
topic = "service.permissions.roles"

registry_client = SchemaRegistry(
    "https://psrc-4r3xk.us-east-2.aws.confluent.cloud",
    HTTPBasicAuth(
        getenv("SCHEMA_REGISTRY_ID"),
        getenv("SCHEMA_REGISTRY_SECRET")
    ),
    headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
)
avroSerde = AvroKeyValueSerde(registry_client, topic)

conf = {
    "bootstrap.servers": "pkc-pgq85.us-west-2.aws.confluent.cloud:9092",
    "security.protocol": "SASL_SSL",
    "sasl.mechanisms": "PLAIN",
    "sasl.username": getenv("KAFKA_USERNAME"),
    "sasl.password": getenv("KAFKA_PASSWORD"),
    "group.id": "JOSE.PERMISSIONS-SERVICE.FINAL",
    "auto.offset.reset": "earliest",
}
consumer = Consumer(conf)
consumer.subscribe([topic], on_assign=print_assignment)

start_time = time.time()
message_count = 0
total_count = 0

try:
    while True:
        message = consumer.poll(1.0)

        if message is None:
            print("Waiting...")
        elif message.error():
            if message.error().code() == KafkaException._PARTITION_EOF:
                continue
            else:
                print("ERROR: %s".format(message.error()))
        else:
            total_count += 1
            print(f"Key: {message.key()}")

            if message.value() is not None:
                role = avroSerde.value.deserialize(message.value())
                print(f"Message: {role}")

                policies_service.create_policy(
                    role["id"], role["resource"], role["action"])
                message_count += 1

except KeyboardInterrupt:
    pass
finally:
    consumer.close()

print("Total number of messages: {}".format(total_count))
print("Total number of messages without tombstones: {}".format(message_count))
print("--- %s seconds ---" % (time.time() - start_time))
