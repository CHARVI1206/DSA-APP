from datetime import date, timedelta
from typing import Tuple

def calculate_next_review(quality: int, repetitions: int, ease_factor: float, interval: int) -> Tuple[int, float, int]:
    """
    Calculates the next review date using a modified SM-2 algorithm.
    quality: 0-5 (0-2 fail, 3-5 pass)
    """
    if quality < 3:
        repetitions = 0
        interval = 1
        ease_factor = max(1.3, ease_factor - 0.2)
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * ease_factor)
        
        repetitions += 1
        ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        ease_factor = max(1.3, ease_factor)

    allowed_intervals = [1, 3, 7, 14, 30, 60, 90]
    if interval not in allowed_intervals:
        closest = min(allowed_intervals, key=lambda x: abs(x - interval))
        if closest < interval and closest != allowed_intervals[-1]:
            # snap up or down logic
            interval = min([i for i in allowed_intervals if i >= interval] + [allowed_intervals[-1]])
        else:
            interval = closest
            
    return interval, ease_factor, repetitions

def get_due_date(interval: int) -> date:
    """Returns the due date based on the interval in days."""
    return date.today() + timedelta(days=interval)
