#!/usr/bin/env python3
"""
Скрипт для проверки SSE endpoint /operations/{operation_id}/status

Использование:
    python test_sse.py <operation_id> [base_url]

Примеры:
    python test_sse.py fa7647d4-2c0d-4d6f-829c-097931134e36
    python test_sse.py fa7647d4-2c0d-4d6f-829c-097931134e36 http://localhost:8008
"""

import httpx


def listen_sse(operation_id: str, base_url: str = "https://payments.createrra.ru"):
    url = f"{base_url}/api/v1/operations/{operation_id}/status"
    print(f"Подключаюсь к SSE: {url}")
    print("-" * 50)

    with httpx.Client(timeout=None) as client:
        with client.stream("GET", url) as response:
            print(f"HTTP {response.status_code}")
            if response.status_code != 200:
                print(f"Ошибка: {response.text}")
                return

            for line in response.iter_lines():
                if line.startswith(":"):
                    print(f"  [keepalive] {line}")
                elif line:
                    print(f"  {line}")
                else:
                    print(f"  [пустая строка]")


if __name__ == "__main__":
    operation_id = "48ca8954-34f3-4fdb-a9c4-009b2dfd8a60"
    base_url = "https://payments.createrra.ru"
    try:
        listen_sse(operation_id, base_url)
    except KeyboardInterrupt:
        print("\nОстановлено.")
    except Exception as e:
        print(f"Ошибка: {e}")
