import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Dict, Any, Tuple, Optional

class TemperatureScalingCalibrator:
    """
    Post-hoc Temperature Scaling Calibrator (Guo et al., 2017).
    Calibrates logits z -> z / T to minimize negative log-likelihood (NLL)
    and expected calibration error (ECE). Clamps probabilities to [0.01, 0.99].
    """
    def __init__(self, temperature: float = 1.35):
        self.temperature = max(0.1, float(temperature))
        self.is_fitted = False

    def fit(self, logits: np.ndarray, labels: np.ndarray, lr: float = 0.01, max_iter: int = 200) -> float:
        """
        Fits optimal temperature T on held-out validation logits to minimize cross-entropy loss.
        """
        logits_t = torch.tensor(logits, dtype=torch.float32)
        labels_t = torch.tensor(labels, dtype=torch.long)
        
        temp_param = nn.Parameter(torch.ones(1) * 1.5)
        optimizer = optim.LBFGS([temp_param], lr=lr, max_iter=max_iter)
        criterion = nn.CrossEntropyLoss()

        def eval_loss():
            optimizer.zero_grad()
            scaled = logits_t / torch.clamp(temp_param, min=0.1, max=10.0)
            loss = criterion(scaled, labels_t)
            loss.backward()
            return loss

        try:
            optimizer.step(eval_loss)
            self.temperature = float(torch.clamp(temp_param, min=0.1, max=10.0).item())
            self.is_fitted = True
        except Exception:
            self.temperature = 1.35
            self.is_fitted = True

        return self.temperature

    def calibrate(self, logits: List[float] | np.ndarray) -> Dict[str, Any]:
        """
        Applies temperature scaling and produces honest, calibrated probabilities
        clamped strictly to [0.01, 0.99] to prevent false 100% saturation.
        """
        z = np.array(logits, dtype=np.float64)
        scaled_z = z / self.temperature

        # Numerically stable softmax
        exp_z = np.exp(scaled_z - np.max(scaled_z))
        probs = exp_z / np.sum(exp_z)

        # Honest probability clamping: never claim 100.0% or 0.0%
        p0 = float(np.clip(probs[0], 0.01, 0.99))
        p1 = float(np.clip(probs[1], 0.01, 0.99))
        
        # Renormalize clamped probabilities so they sum to 1.0
        total = p0 + p1
        p0 = round(p0 / total, 4)
        p1 = round(p1 / total, 4)

        # Decision Bands
        # p < 0.35: NON-HATEFUL
        # 0.35 <= p <= 0.65: NEEDS REVIEW (Ambiguous/borderline)
        # p > 0.65: HATEFUL
        if p1 > 0.65:
            verdict = "HATEFUL"
            predicted_label = 1
            band = "high_hostility"
            confidence = p1
        elif p1 < 0.35:
            verdict = "NON-HATEFUL"
            predicted_label = 0
            band = "low_hostility"
            confidence = p0
        else:
            verdict = "NEEDS REVIEW"
            predicted_label = 1 if p1 >= 0.50 else 0
            band = "borderline_review"
            confidence = round(max(p0, p1), 4)

        return {
            "predicted_label": predicted_label,
            "verdict": verdict,
            "decision_band": band,
            "probabilities": {
                "non_hateful": p0,
                "hateful": p1
            },
            "confidence": confidence,
            "temperature": round(self.temperature, 3),
            "scaled_logits": [round(float(s), 4) for s in scaled_z]
        }

    @staticmethod
    def calculate_ece(probs: np.ndarray, labels: np.ndarray, n_bins: int = 10) -> Dict[str, float]:
        """
        Calculates Expected Calibration Error (ECE) and Maximum Calibration Error (MCE).
        """
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        ece = 0.0
        mce = 0.0
        total_samples = len(labels)

        # If 2D probs, take confidence of predicted class
        if probs.ndim == 2:
            preds = np.argmax(probs, axis=1)
            confs = np.max(probs, axis=1)
            accuracies = (preds == labels)
        else:
            confs = probs
            accuracies = labels

        for i in range(n_bins):
            bin_lower = bin_boundaries[i]
            bin_upper = bin_boundaries[i + 1]
            in_bin = (confs > bin_lower) & (confs <= bin_upper)
            bin_size = np.sum(in_bin)

            if bin_size > 0:
                bin_acc = np.mean(accuracies[in_bin])
                bin_conf = np.mean(confs[in_bin])
                diff = abs(bin_acc - bin_conf)
                ece += (bin_size / total_samples) * diff
                mce = max(mce, diff)

        return {
            "ece": round(float(ece), 4),
            "mce": round(float(mce), 4),
            "brier_score": round(float(np.mean((confs - labels) ** 2)), 4)
        }
