import torch
import torch.nn as nn
from torchvision import models


class InteriorStyleClassifier(nn.Module):
    """ResNet50-based classifier for interior design style recognition."""

    def __init__(self, num_classes: int = 19, pretrained: bool = True):
        super().__init__()
        weights = models.ResNet50_Weights.DEFAULT if pretrained else None
        self.backbone = models.resnet50(weights=weights)
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(in_features, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)

    @classmethod
    def load_trained(cls, model_path: str, num_classes: int = 19, device: str = "cpu"):
        model = cls(num_classes=num_classes, pretrained=False)
        state_dict = torch.load(model_path, map_location=device, weights_only=True)
        model.load_state_dict(state_dict)
        model.eval()
        return model.to(device)
