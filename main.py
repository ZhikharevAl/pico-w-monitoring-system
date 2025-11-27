"""Главный файл - автоматически запускается при старте Pico."""

import time
from config import (
    CLIENT_ID,
    MQTT_PORT,
    MQTT_SERVER,
    MQTT_TOPIC,
    PUBLISH_INTERVAL,
    WIFI_PASSWORD,
    WIFI_SSID,
)
import machine


from wifi_manager import WiFiManager
from system_metrics import SystemMetrics
from mqtt_publisher import MQTTPublisher


class PicoMonitor:
    def __init__(self):
        self.wifi = WiFiManager(WIFI_SSID, WIFI_PASSWORD)
        self.metrics = SystemMetrics()
        self.metrics.wlan = self.wifi.wlan
        self.mqtt = MQTTPublisher(MQTT_SERVER, MQTT_PORT, CLIENT_ID, MQTT_TOPIC)
        self.reconnect_count = 0

    def setup(self) -> bool:
        if not self.wifi.connect():
            return False
        if not self.mqtt.connect():
            return False
        return True

    def run(self):
        while True:
            try:
                if not self.wifi.is_connected():
                    print("Reconnecting WiFi...")
                    if not self.wifi.connect():
                        time.sleep(10)
                        continue
                    self.reconnect_count += 1

                if not self.mqtt.client:
                    print("Reconnecting MQTT...")
                    if not self.mqtt.connect():
                        time.sleep(10)
                        continue

                metrics = self.metrics.get_all_metrics(self.reconnect_count)
                print(f"Metrics: {metrics}")

                self.mqtt.publish(metrics)
                time.sleep(PUBLISH_INTERVAL)

            except Exception as e:
                print(f"Error: {e}")
                self.mqtt.disconnect()
                time.sleep(5)


try:
    monitor = PicoMonitor()
    if monitor.setup():
        print("System ready!")
        monitor.run()
    else:
        print("Init failed!")
except Exception as e:
    print(f"Critical error: {e}")
    time.sleep(10)
    machine.reset()
