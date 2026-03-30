LED_PIN = 18
LED_COUNT = 24
MODE = "seven_day"  # "five_hour", "seven_day", "dual", or "split"

HEARTBEAT_TIMEOUT = 120  # seconds with no data before showing disconnected animation

HOST = "0.0.0.0"
# 8080 avoids needing root on Linux; override to 80 if you use sudo.
HTTP_PORT = 8080
CORS_ALLOW_ORIGIN = "*"
