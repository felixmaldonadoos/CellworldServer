import time
import torch

class PeakingSystem:
    def __init__(self, 
                 occluded_cells, 
                 max_peak_time=2.0, 
                 max_peak_distance=0.01,
                 min_movement_threshold:float = 0.5,
                 max_peak_cooldown=3.0):
        
        self.occluded_cells = occluded_cells.copy()
        self.max_peak_time = max_peak_time
        self.max_peak_distance = max_peak_distance
        self.max_peak_cooldown = max_peak_cooldown
        self.last_prey_location = None
        self.min_movement_threshold = min_movement_threshold
        self.is_peaking = False
        self._initialize_cells_()

    def _initialize_cells_(self):
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
        self.is_peaking = False
        for cell in self.occluded_cells:
            cell.distance = self._compute_distance_(prey_location, [cell.location.x, cell.location.y])
            if cell.distance <= abs(self.max_peak_distance):
                if not cell.in_peak_cooldown:
                    self.is_peaking = True
                    self.last_prey_location = prey_location
                    if not cell.peaking:
                        cell.peak_time_start = time.time()
                        cell.peaking = True
                        # print(f'STARTED peaking! cell {cell.id} | distance: {cell.distance}')
                        return
                    elif cell.peaking:
                        cell.peak_time_elapsed = time.time() - cell.peak_time_start
                        if cell.peak_time_elapsed >= self.max_peak_time:
                            # print(f'peak time elapsed! Starting cooldown. | {cell.id}')
                            cell.peaking = False
                            cell.in_peak_cooldown = True
                            cell.peak_cooldown_time_start = time.time()
                        else:
                            # print(f'In an active peak! {cell.id} | {cell.peak_time_elapsed:0.2f}')
                            continue
                else:
                    cell.peak_cooldown_time_elapsed = time.time() - cell.peak_cooldown_time_start
                    if cell.peak_cooldown_time_elapsed >= cell.max_peak_cooldown_time: # make self.max_peak_cooldown_time? 
                        # before resetting, check if the player has actually moved!! prevent camping
                        movement_distance = self._compute_distance_(self.last_prey_location, prey_location)
                        if movement_distance >= self.min_movement_threshold:
                            cell.in_peak_cooldown = False
                            cell.peak_cooldown_time_elapsed = 0
                            cell.peak_cooldown_time_start = 0
                            # print(f'movement threshold met! ending peak cooldown | {cell.id}')
                        else:
                            return
                            # print(f'peak cooldown time elapsed but player is camping! cooldown time elapsed: {cell.peak_cooldown_time_elapsed:0.2f} / {cell.max_peak_cooldown_time:0.2f}')
            else:
                cell.peak_time_elapsed = 0
                cell.peaking = False
                if cell.in_peak_cooldown:
                    # print(f'left active peak during cooldown period! cooldown time elapsed: {cell.peak_cooldown_time_elapsed:0.2f} | {cell.id} ')
                    cell.in_peak_cooldown = False
                    cell.peak_cooldown_time_elapsed = 0
                    cell.peak_cooldown_time_start = 0
    
    def _compute_distance_(self, p1, p2):
        p1 = torch.tensor(p1, dtype=torch.float16, device='cuda')
        p2 = torch.tensor(p2, dtype=torch.float16, device='cuda')
        return torch.sqrt(torch.sum((p2 - p1) ** 2)).item()
