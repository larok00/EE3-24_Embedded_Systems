from umqtt.simple import MQTTClient

topic = "esys/Embedded_girls(and_Koral)/flex"

client = MQTTClient(machine.unique_id(), "192.168.0.10")

client.publish(topic, bytes(payload, 'utf-8'))