import math
import numpy as np
import time
def inverse_scale_legacy_y(scaled_y):
    return (scaled_y - 0.5 + math.sqrt(3) / 4) / (0.5 * math.sqrt(3))

def scale_legacy_y(y):
    return y * 0.5 * math.sqrt(3) + 0.5 - math.sqrt(3) / 4

if __name__ == '__main__':
    points = np.linspace(0,1,50)
    tolerance = 1e-3
    print(f'== Canonical Conversion tests ==')
    print(f'Tolerance: {tolerance}')
    errors = 0
    t0 = time.perf_counter()
    for y in points: 
        ys   = scale_legacy_y(y)
        yis  = inverse_scale_legacy_y(ys)
        if abs(y - yis) >= tolerance:
            print(f'y: {y:0.4f} | ys: {ys:0.4f} | yis: {yis:0.4f} | error: {(y-yis)}')
            errors+=1

    print(f'[Done] Errors: {errors}/{points.shape[0]} | Time elapsed: {(time.perf_counter() - t0)*1e3:0.4f} ms')