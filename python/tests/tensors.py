import torch

def scale_legacy_y_tensor(y):
    y_tensor = torch.tensor(y, dtype=torch.float32)
    return y_tensor * 0.5 * torch.sqrt(torch.tensor(3.0)) + 0.5 - torch.sqrt(torch.tensor(3.0)) / 4

y = 0.5

print(type(scale_legacy_y_tensor(y)))
print((scale_legacy_y_tensor(y).item()))