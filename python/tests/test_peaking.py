import time
import torch

def use_uint8(x1, y1, x2, y2):
    # Convert to uint8 (scale 0-255)
    p1 = torch.tensor([x1 * 255, y1 * 255], dtype=torch.uint8, device='cuda')
    p2 = torch.tensor([x2 * 255, y2 * 255], dtype=torch.uint8, device='cuda')
    
    # Convert back to float for distance computation
    p1 = p1.float() / 255.0
    p2 = p2.float() / 255.0
    
    # Compute Euclidean distance
    return torch.sqrt(torch.sum((p2 - p1) ** 2))

def use_float16(x1, y1, x2, y2):
    # Convert to float16
    p1 = torch.tensor([x1, y1], dtype=torch.float16, device='cuda')
    p2 = torch.tensor([x2, y2], dtype=torch.float16, device='cuda')
    
    # Compute Euclidean distance
    return torch.sqrt(torch.sum((p2 - p1) ** 2))

def use_float16_floats(x1, y1, x2, y2):
    # Convert to float16
    p1 = torch.tensor([x1, y1], dtype=torch.float16, device='cuda')
    p2 = torch.tensor([x2, y2], dtype=torch.float16, device='cuda')
    
    # Compute Euclidean distance
    return torch.sqrt(torch.sum((p2 - p1) ** 2))

def use_float16_list(p1:list=None, p2:list=None):
    # Convert to float16
    p1 = torch.tensor(p1, dtype=torch.float16, device='cuda')
    p2 = torch.tensor(p2, dtype=torch.float16, device='cuda')
    
    # Compute Euclidean distance
    return torch.sqrt(torch.sum((p2 - p1) ** 2))

# Test parameters
x1, y1 = 0.5, 0.5
x2, y2 = 0.8, 0.9
p1_list = [x1, y1]
p2_list = [x2, y2]

# Benchmarking float16 (floats)
start = time.time()
for _ in range(200):
    use_float16_floats(x1, y1, x2, y2)
time_float16_floats = time.time() - start

# Benchmarking float16 (list)
start = time.time()
for _ in range(200):
    use_float16_list(p1_list, p2_list)
time_float16_list = time.time() - start

# Print results
print(f"Time for float16 (floats): {time_float16_floats:.6f} seconds")
print(f"Time for float16 (list): {time_float16_list:.6f} seconds")
