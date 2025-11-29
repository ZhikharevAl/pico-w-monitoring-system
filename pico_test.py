from umqtt.simple import MQTTClient
import time

print("Testing MQTT...")
try:
    client = MQTTClient("pico-test", "192.168.1.51", 1883, keepalive=60)
    client.connect(clean_session=True)
    print("✓ CONNECTED!")

    client.publish(b"test/pico", b"Hello!")
    print("✓ PUBLISHED!")

    client.disconnect()
    print("✓ SUCCESS!")

except Exception as e:
    print(f"✗ Error: {e}")
