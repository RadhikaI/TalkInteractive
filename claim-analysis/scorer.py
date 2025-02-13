from typing import List, Dict, Tuple

import numpy as np
import math

def weightedMeanAndVariance(values: List[int], weights: List[int]) -> Tuple[int, int]:
    avg = np.average(values, weights=weights)
    var = np.average((values-avg)**2, weights=weights)
    return (avg, var)

def uniteVerdict(score: int, uncertainty: int) -> int:
    print(f"mean: {score}, uncertainty: {uncertainty}")
    return score / (9*uncertainty + 1)

# def determineScore(values: List[int], weights: List[int]) -> int:
#     return np.average(values, weights=weights)
# def determineUncertainty(values: List[int], weights: List[int]) -> int:

def shift(x: int) -> int:
    return -x**4 + x**3 + x**2 # (1-x**2) * x**2 + (x**2) * x
def shiftZ(x: int) -> int:
    return math.copysign(shift(abs(x)), x)

def plotShiftZ():
    import matplotlib.pyplot as plt
    x = np.linspace(-1, 1, 1000)
    shiftZ2 = np.vectorize(shiftZ)
    y = shiftZ2(x)

    plt.figure(figsize=(10, 100))
    plt.plot(x, y, 'b-', linewidth=2)
    plt.title("Shift")
    plt.xlabel("Perplexity's support score")
    plt.ylabel("Adjusted support score")
    plt.grid(True)
    plt.axhline(y=0, color='k', linestyle='--')
    plt.axvline(x=0, color='k', linestyle='--')

    plt.show()

accuracy = 0.01
def roundDown(x):
    return math.copysign(abs(x) // accuracy * accuracy, x)

def score(evidence: List[Dict[str, int]]) -> Tuple[int, int]:
    values = []
    weights = []
    for d in evidence:
        w = d.get("reliability") # weight
        x = d.get("support") # value

        x = shiftZ(x)

        values.append(x)
        weights.append(w)
    return int(100 * roundDown(uniteVerdict(*weightedMeanAndVariance(values, weights))))

data1 = [
    {"reliability": 1, "support": 0},
    {"reliability": 0, "support": 1},
    {"reliability": 1, "support": 1},
    {"reliability": 1, "support": 1},
    {"reliability": 1, "support": 0},
]
data2 = [
    {"reliability": 1, "support": +1},
    {"reliability": 1, "support": -1},
    {"reliability": 1, "support": -1},
    {"reliability": 1, "support": -1},
    {"reliability": 1, "support": +1},
]
data3 = [
    {"reliability": 1, "support": +1},
    {"reliability": 1, "support": -1}
]
data4 = [
    {"reliability": 1, "support": 0},
    {"reliability": 0, "support": 1},
    {"reliability": 1, "support": 1},
    {"reliability": 1, "support": 1},
    {"reliability": 1, "support": 1},
    {"reliability": 1, "support": 0},
]
data5 = [
    {"reliability": 1, "support": +1},
    {"reliability": 1, "support": +1}
]

print(score(data1))
print(score(data2))
print(score(data3))
print(score(data4))
print(score(data5))
plotShiftZ()

# print(weightedMeanAndVariance([1, 1, 1], [1, 1, 1]))
