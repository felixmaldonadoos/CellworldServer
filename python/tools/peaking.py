import time
import torch

class Peak:
    def __init__(self, occluded_cells, max_peak_time=2.0, max_peak_distance=0.01, max_peak_cooldown=3.0):
        self.occluded_cells = occluded_cells.copy()
        self.max_peak_time = max_peak_time
        self.max_peak_distance = max_peak_distance
        self.max_peak_cooldown = max_peak_cooldown
        self._initialize_cells()

    def _initialize_cells(self):
        for cell in self.occluded_cells:
            cell.peaking = False
            cell.distance = 1
            cell.peak_time_start = 0
            cell.peak_time_elapsed = 0
            cell.in_peak_cooldown = False
            cell.peak_cooldown_time_start = 0
            cell.peak_cooldown_time_elapsed = 0
            cell.max_peak_cooldown_time = self.max_peak_cooldown
    
    def update(self, prey_location):
        for cell in self.occluded_cells:
            cell.distance = self._compute_distance(prey_location, [cell.location.x, cell.location.y])
            
            if cell.distance <= abs(self.max_peak_distance):
                if not cell.in_peak_cooldown:
                    if not cell.peaking:
                        cell.peak_time_start = time.time()
                        cell.peaking = True
                        print(f'STARTED peaking! cell {cell.id} | distance: {cell.distance}')
                    elif cell.peaking:
                        cell.peak_time_elapsed = time.time() - cell.peak_time_start
                        if cell.peak_time_elapsed >= self.max_peak_time:
                            print(f'peak time elapsed! Starting cooldown. | {cell.id}')
                            cell.peaking = False
                            cell.in_peak_cooldown = True
                            cell.peak_cooldown_time_start = time.time()
                        else:
                            print(f'In an active peak! {cell.id} | {cell.peak_time_elapsed:0.2f}')
                            continue
                else:
                    cell.peak_cooldown_time_elapsed = time.time() - cell.peak_cooldown_time_start
                    if cell.peak_cooldown_time_elapsed >= cell.max_peak_cooldown_time:
                        cell.in_peak_cooldown = False
                        cell.peak_cooldown_time_elapsed = 0
                        cell.peak_cooldown_time_start = 0
                        print(f'ending peak cooldown: {cell.in_peak_cooldown} | {cell.id}')
            else:
                cell.peak_time_elapsed = 0
                cell.peaking = False
                if cell.in_peak_cooldown:
                    print(f'left active peak during cooldown period! cooldown time elapsed: {cell.peak_cooldown_time_elapsed:0.2f} | {cell.id} ')
                    cell.in_peak_cooldown = False
                    cell.peak_cooldown_time_elapsed = 0
                    cell.peak_cooldown_time_start = 0
    
    def _compute_distance(self, p1, p2):
        p1 = torch.tensor(p1, dtype=torch.float16, device='cuda')
        p2 = torch.tensor(p2, dtype=torch.float16, device='cuda')
        return torch.sqrt(torch.sum((p2 - p1) ** 2)).item()
