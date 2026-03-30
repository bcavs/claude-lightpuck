import json

latest_usage = {
    "five_hour_utilization": 0,
    "seven_day_utilization": 0
}

def handle_request(request):
    global latest_usage

    try:
        body = request.read().decode()
        data = json.loads(body)
        latest_usage.update(data)
        print("Updated usage:", latest_usage)
        return "OK"
    except Exception as e:
        print("Error:", e)
        return "ERROR"
