
import torch
import torch.nn as nn
import torch.nn.functional as F


class DoubleConv(nn.Module):

    def __init__(self, in_ch, out_ch):
        super().__init__()

        self.block = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),

            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.block(x)


class AttentionGate(nn.Module):

    def __init__(self, channels):
        super().__init__()

        hidden = max(channels // 2, 1)

        self.Wx = nn.Conv2d(channels, hidden, 1)
        self.Wg = nn.Conv2d(channels, hidden, 1)

        self.psi = nn.Sequential(
            nn.ReLU(),
            nn.Conv2d(hidden, 1, 1),
            nn.Sigmoid()
        )

        self.attention_map = None

    def forward(self, x, g):

        alpha = self.psi(
            self.Wx(x) + self.Wg(g)
        )

        self.attention_map = alpha.detach()

        return x * alpha


class UNet(nn.Module):

    def __init__(self, out_channels=1,
                 attention=False, base=16):

        super().__init__()

        self.attention = attention

        self.enc1 = DoubleConv(1, base)
        self.enc2 = DoubleConv(base, base * 2)
        self.enc3 = DoubleConv(base * 2, base * 4)

        self.pool = nn.MaxPool2d(2)

        self.bottleneck = DoubleConv(
            base * 4, base * 8
        )

        self.up3 = nn.ConvTranspose2d(
            base * 8, base * 4, 2, stride=2
        )

        self.up2 = nn.ConvTranspose2d(
            base * 4, base * 2, 2, stride=2
        )

        self.up1 = nn.ConvTranspose2d(
            base * 2, base, 2, stride=2
        )

        self.dec3 = DoubleConv(base * 8, base * 4)
        self.dec2 = DoubleConv(base * 4, base * 2)
        self.dec1 = DoubleConv(base * 2, base)

        if attention:
            self.att3 = AttentionGate(base * 4)
            self.att2 = AttentionGate(base * 2)
            self.att1 = AttentionGate(base)

        self.output = nn.Conv2d(
            base, out_channels, 1
        )

    def forward(self, x):

        e1 = self.enc1(x)
        e2 = self.enc2(self.pool(e1))
        e3 = self.enc3(self.pool(e2))

        b = self.bottleneck(self.pool(e3))

        d3 = self.up3(b)
        s3 = self.att3(e3, d3) if self.attention else e3
        d3 = self.dec3(torch.cat([d3, s3], dim=1))

        d2 = self.up2(d3)
        s2 = self.att2(e2, d2) if self.attention else e2
        d2 = self.dec2(torch.cat([d2, s2], dim=1))

        d1 = self.up1(d2)
        s1 = self.att1(e1, d1) if self.attention else e1
        d1 = self.dec1(torch.cat([d1, s1], dim=1))

        return self.output(d1)


class AttentionUNet(UNet):

    def __init__(self, out_channels=1, base=16):

        super().__init__(
            out_channels=out_channels,
            attention=True,
            base=base
        )
