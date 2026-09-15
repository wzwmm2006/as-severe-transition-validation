"""Frozen standard-library estimators used for reported aggregate results."""
import math

Z = 1.959963985


def wilson(successes: int, total: int) -> tuple[float, float]:
    if total == 0:
        return (math.nan, math.nan)
    p = successes / total
    z = 1.96
    d = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / d
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / d
    return centre - half, centre + half


def km_survival(times, events, horizon=365):
    survival, greenwood = 1.0, 0.0
    for event_time in sorted({t for t, e in zip(times, events) if e == 1 and t <= horizon}):
        at_risk = sum(t >= event_time for t in times)
        deaths = sum(t == event_time and e == 1 for t, e in zip(times, events))
        survival *= 1 - deaths / at_risk
        if at_risk > deaths:
            greenwood += deaths / (at_risk * (at_risk - deaths))
    return survival, survival * math.sqrt(greenwood)


def aalen_johansen(times, causes, horizon=365):
    """Cause 1 CIF; cause 2 is competing death and cause 0 is censoring."""
    survival, cif = 1.0, 0.0
    for event_time in sorted({t for t, c in zip(times, causes) if c in (1, 2) and t <= horizon}):
        at_risk = sum(t >= event_time for t in times)
        cause1 = sum(t == event_time and c == 1 for t, c in zip(times, causes))
        all_events = sum(t == event_time and c in (1, 2) for t, c in zip(times, causes))
        cif += survival * cause1 / at_risk
        survival *= 1 - all_events / at_risk
    return cif


def _solve(matrix, vector):
    n = len(matrix)
    work = [row[:] + [vector[i]] for i, row in enumerate(matrix)]
    for column in range(n):
        pivot = max(range(column, n), key=lambda row: abs(work[row][column]))
        if abs(work[pivot][column]) < 1e-14:
            raise ValueError("singular matrix")
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(n):
            if row != column and work[row][column] != 0:
                factor = work[row][column]
                work[row] = [work[row][k] - factor * work[column][k] for k in range(n + 1)]
    return [work[i][n] for i in range(n)]


def cox_efron(times, events, covariates, max_iter=200, tolerance=1e-11):
    """Cox proportional hazards model with explicit Efron tie handling."""
    n, p = len(times), len(covariates[0])
    order = sorted(range(n), key=lambda i: times[i])
    t = [times[i] for i in order]; e = [events[i] for i in order]
    x = [covariates[i] for i in order]
    event_times = sorted({t[i] for i in range(n) if e[i] == 1})

    def evaluate(beta):
        eta = [sum(beta[k] * x[i][k] for k in range(p)) for i in range(n)]
        score = [0.0] * p; hessian = [[0.0] * p for _ in range(p)]
        for event_time in event_times:
            risk = [i for i in range(n) if t[i] >= event_time]
            deaths = [i for i in range(n) if t[i] == event_time and e[i] == 1]
            d = len(deaths)
            s0 = sum(math.exp(eta[i]) for i in risk)
            s1 = [sum(math.exp(eta[i]) * x[i][k] for i in risk) for k in range(p)]
            s2 = [[sum(math.exp(eta[i]) * x[i][k] * x[i][l] for i in risk) for l in range(p)] for k in range(p)]
            d0 = sum(math.exp(eta[i]) for i in deaths)
            d1 = [sum(math.exp(eta[i]) * x[i][k] for i in deaths) for k in range(p)]
            d2 = [[sum(math.exp(eta[i]) * x[i][k] * x[i][l] for i in deaths) for l in range(p)] for k in range(p)]
            for j in range(d):
                fraction = j / d
                a0 = s0 - fraction * d0
                a1 = [s1[k] - fraction * d1[k] for k in range(p)]
                a2 = [[s2[k][l] - fraction * d2[k][l] for l in range(p)] for k in range(p)]
                for k in range(p):
                    score[k] += x[deaths[j]][k] - a1[k] / a0
                    for l in range(p):
                        hessian[k][l] -= a2[k][l] / a0 - (a1[k] / a0) * (a1[l] / a0)
        return score, hessian

    beta = [0.0] * p
    for _ in range(max_iter):
        score, hessian = evaluate(beta)
        step = _solve([[-hessian[k][l] for l in range(p)] for k in range(p)], score)
        beta = [beta[k] + step[k] for k in range(p)]
        if max(abs(value) for value in score) < tolerance:
            break
    score, hessian = evaluate(beta)
    return beta
