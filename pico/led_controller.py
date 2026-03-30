def percent_to_leds(percent, total_leds):
    percent = max(0, min(100, float(percent)))
    return int((percent / 100.0) * total_leds)
