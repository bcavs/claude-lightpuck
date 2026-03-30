def percent_to_leds(percent, total_leds):
    percent = max(0, min(100, float(percent)))
    return int((percent / 100.0) * total_leds)


def log_strip_state(percent, leds_on, total_leds, mode):
    """Log what would be driven on the strip (no GPIO / NeoPixel yet)."""
    if total_leds <= 0:
        print("[LED] mode=%s — no pixels configured" % mode)
        return
    bar = "#" * leds_on + "." * (total_leds - leds_on)
    if leds_on <= 0:
        idx_note = "none lit"
    elif leds_on == 1:
        idx_note = "index 0"
    else:
        idx_note = "indices 0..%d" % (leds_on - 1)
    print(
        "[LED] mode=%s util=%s%% | %d/%d on (%s) | %s"
        % (mode, percent, leds_on, total_leds, idx_note, bar)
    )
