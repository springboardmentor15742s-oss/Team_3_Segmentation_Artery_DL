
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from PIL import Image


class DoubleConv(nn.Module):
    def __init__(self, cin, cout):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(cin, cout, 3, padding=1, bias=False),
            nn.BatchNorm2d(cout),
            nn.ReLU(inplace=True),
            nn.Conv2d(cout, cout, 3, padding=1, bias=False),
            nn.BatchNorm2d(cout),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.net(x)


class UNet(nn.Module):
    def __init__(self, in_ch=1, out_ch=1, ch=(16, 32, 64, 128)):
        super().__init__()
        self.downs = nn.ModuleList()
        c = in_ch
        for f in ch:
            self.downs.append(DoubleConv(c, f))
            c = f

        self.pool = nn.MaxPool2d(2)
        self.bottleneck = DoubleConv(ch[-1], ch[-1] * 2)
        self.ups = nn.ModuleList()
        self.up_convs = nn.ModuleList()
        c = ch[-1] * 2

        for f in reversed(ch):
            self.ups.append(nn.ConvTranspose2d(c, f, 2, stride=2))
            self.up_convs.append(DoubleConv(f * 2, f))
            c = f

        self.head = nn.Conv2d(ch[0], out_ch, 1)

    def forward(self, x):
        skips = []
        for d in self.downs:
            x = d(x)
            skips.append(x)
            x = self.pool(x)

        x = self.bottleneck(x)

        for up, conv, skip in zip(
            self.ups, self.up_convs, reversed(skips)
        ):
            x = up(x)
            x = conv(torch.cat([skip, x], dim=1))

        return self.head(x)


MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "models"
    / "stenosis_unet_best.pth"
)

device = torch.device("cpu")
checkpoint = torch.load(
    MODEL_PATH, map_location=device, weights_only=True
)

model = UNet()
model.load_state_dict(checkpoint["model"])
model.to(device)
model.eval()


def predict_stenosis(image_path: Path) -> Image.Image:
    original = Image.open(image_path).convert("L")
    original_size = original.size

    resized = original.resize(
        (256, 256), Image.Resampling.BILINEAR
    )
    array = np.asarray(resized, dtype=np.float32) / 255.0
    tensor = torch.from_numpy(array).unsqueeze(0).unsqueeze(0)

    with torch.inference_mode():
        probabilities = torch.sigmoid(model(tensor))
        mask = (
            probabilities.squeeze().numpy() >= 0.40
        ).astype(np.uint8) * 255

    result = Image.fromarray(mask)
    return result.resize(original_size, Image.Resampling.NEAREST)
