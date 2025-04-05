from dataclasses import dataclass

from app.models import Prediction


@dataclass
class RankedPrediction:
    prediction: Prediction
    rank: int
