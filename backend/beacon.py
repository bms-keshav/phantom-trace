from __future__ import annotations

import numpy as np
from scipy.fft import fft, fftfreq


def compute_beacon_score(timestamps: list[float]) -> dict:
    """
    Detect periodic beacon-like behavior from event timestamps in epoch-seconds.
    """
    if len(timestamps) < 10:
        return {
            "score": 0.0,
            "dominant_freq_hz": None,
            "dominant_period_sec": None,
            "iat_std": None,
            "spectral_ratio": None,
        }

    sorted_ts = np.array(sorted(timestamps), dtype=float)
    iats = np.diff(sorted_ts)
    iats = iats[iats > 0]

    if len(iats) < 8:
        return {
            "score": 0.0,
            "dominant_freq_hz": None,
            "dominant_period_sec": None,
            "iat_std": float(np.std(iats)) if len(iats) else None,
            "spectral_ratio": None,
        }

    iat_std = float(np.std(iats))

    # Remove DC component before FFT so periodicity peaks are clearer.
    centered = iats - np.mean(iats)
    n = len(centered)
    yf = np.abs(fft(centered))
    xf = fftfreq(n, d=max(float(np.mean(iats)), 1e-9))

    pos_slice = slice(1, max(2, n // 2))
    band = yf[pos_slice]

    if len(band) == 0:
        spectral_ratio = 0.0
        dominant_freq = 0.0
    else:
        peak_power = float(np.max(band))
        mean_power = float(np.mean(band))
        spectral_ratio = peak_power / (mean_power + 1e-9)
        dominant_idx = int(np.argmax(band)) + 1
        dominant_freq = float(abs(xf[dominant_idx]))

    iat_score = 1.0 / (1.0 + iat_std)
    fft_score = min(spectral_ratio / 10.0, 1.0)
    beacon_score = 0.4 * iat_score + 0.6 * fft_score

    return {
        "score": round(float(beacon_score), 4),
        "dominant_freq_hz": round(dominant_freq, 4) if dominant_freq > 0 else None,
        "dominant_period_sec": round(1.0 / dominant_freq, 2) if dominant_freq > 0 else None,
        "iat_std": round(iat_std, 4),
        "spectral_ratio": round(float(spectral_ratio), 2),
    }
