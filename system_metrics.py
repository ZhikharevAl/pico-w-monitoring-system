"""Сбор системных метрик Pico W."""

import machine
import gc
import time
import network
import ubinascii
import uos  # Импортируем для получения системной информации


class SystemMetrics:
    def __init__(self):
        self.temp_sensor = machine.ADC(4)
        # ADC(29) соответствует GPIO 29, который подключен к делителю Vsys/3.
        self.vsys_pin = machine.ADC(29)
        self.start_time = time.time()
        self.wlan = network.WLAN(network.STA_IF)

    def get_temperature(self) -> float:
        """Температура процессора в °C."""
        reading = self.temp_sensor.read_u16() * 3.3 / 65535
        temperature = 27 - (reading - 0.706) / 0.001721
        return round(temperature, 2)

    def get_memory_stats(self) -> dict:
        """Статистика памяти."""
        gc.collect()
        free_mem = gc.mem_free()
        allocated_mem = gc.mem_alloc()
        total_mem = free_mem + allocated_mem

        return {
            "memory_free_bytes": free_mem,
            "memory_allocated_bytes": allocated_mem,
            "memory_total_bytes": total_mem,
            "memory_usage_percent": round((allocated_mem / total_mem) * 100, 2),
        }

    def get_vsys_voltage(self) -> float:
        """Напряжение системы Vsys (напряжение питания)."""
        reading = self.vsys_pin.read_u16()
        # Формула для Vsys: чтение * (3.3 / 65535) * 3
        # (Пин измеряет Vsys/3)
        voltage = reading * (3.3 / 65535) * 3
        return round(voltage, 2)

    def get_cpu_frequency(self) -> int:
        """Частота CPU в Hz."""
        return machine.freq()

    def get_uptime(self) -> int:
        """Время работы в секундах."""
        return int(time.time() - self.start_time)

    def get_wifi_metrics(self, reconnect_count: int) -> dict:
        """Метрики WiFi соединения."""
        metrics = {
            "wifi_connected": 1 if self.wlan.isconnected() else 0,
            "wifi_status": self.wlan.status(),
            # Новый счетчик переподключений
            "wifi_reconnect_count": reconnect_count,
        }

        if self.wlan.isconnected():
            # RSSI (уровень сигнала)
            rssi = self.wlan.status("rssi")
            metrics["wifi_rssi_dbm"] = rssi

            # MAC адрес и IP
            mac = ubinascii.hexlify(self.wlan.config("mac"), ":").decode()
            ifconfig = self.wlan.ifconfig()
            metrics["wifi_mac"] = mac
            metrics["wifi_ip"] = ifconfig[0]
        else:
            metrics["wifi_rssi_dbm"] = -100
            metrics["wifi_mac"] = "disconnected"
            metrics["wifi_ip"] = "0.0.0.0"

        return metrics

    def get_system_info(self) -> dict:
        """Информация о прошивке и ID устройства."""
        unique_id = ubinascii.hexlify(machine.unique_id()).decode()
        return {
            "sys_unique_id": unique_id,
            "sys_version": uos.uname().version,
        }

    def get_all_metrics(self, reconnect_count: int) -> dict:
        """Собрать все метрики."""
        metrics = {
            "temperature_celsius": self.get_temperature(),
            "cpu_frequency_hz": self.get_cpu_frequency(),
            "uptime_seconds": self.get_uptime(),
            "vsys_voltage": self.get_vsys_voltage(),
        }

        metrics.update(self.get_memory_stats())
        metrics.update(self.get_wifi_metrics(reconnect_count))
        metrics.update(self.get_system_info())

        return metrics
