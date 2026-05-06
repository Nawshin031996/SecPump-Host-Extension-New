from dataclasses import dataclass, field
import random

import numpy as np
from scipy.integrate import odeint


@dataclass
class SimulationState:
    y0: np.ndarray = field(default_factory=lambda: np.array([280.0, 0.0, 0.0]))
    prev_glucose: float = 280.0
    integral_error: float = 0.0
    controller_output: float = 0.0
    disturbance_start_index: int = 0
    disturbance_factor: float = 0.0


@dataclass(frozen=True)
class ControllerConfig:
    kc: float = -0.07
    tau_i: float = 1.0
    tau_d: float = 1.2
    bias: float = 0.0
    p4: float = 0.05
    set_point: float = 85.0
    op_hi: float = 100.0
    op_lo: float = 0.0
    enable_p: bool = True
    enable_i: bool = True
    enable_d: bool = True
    disturb: bool = True


def diabetic(y, t, ui, d, p4):
    """Same Bergman-style glucose-insulin model used by Scripts/Model-Sim.py."""
    g = y[0]
    x = y[1]
    i = y[2]

    gb = 280.0
    p1 = 0.028735
    p2 = 0.028344
    p3 = 5.035e-5
    ib = 0
    vi = 12.0

    dydt = np.empty(3)
    dydt[0] = -p1 * (g - gb) - x * g + d
    dydt[1] = -p2 * x + p3 * (i - ib)
    dydt[2] = -p4 * i + ui / vi

    return dydt * 60


class BaselineSimulator:
    def __init__(self, config=None, seed=7):
        self.config = config or ControllerConfig()
        self.random = random.Random(seed)

    def time_grid(self, hours=24, samples_per_hour=6):
        return np.linspace(0, hours, hours * samples_per_hour + 1)

    def next_disturbance(self, index, state):
        cfg = self.config
        if cfg.disturb and index in (8 * 6 + 1, 13 * 6 + 1, 19 * 6 + 1):
            state.disturbance_start_index = index
            state.disturbance_factor = self.random.randint(1, 10)

        return state.disturbance_factor * np.exp(
            -0.05 * (index - state.disturbance_start_index)
        )

    def controller_command(self, state, current_glucose, delta_t):
        cfg = self.config
        error = cfg.set_point - current_glucose
        derivative_pv = (current_glucose - state.prev_glucose) / delta_t
        state.integral_error += error * delta_t

        p_term = cfg.kc * error
        i_term = cfg.kc / cfg.tau_i * state.integral_error
        d_term = -cfg.kc * cfg.tau_d * derivative_pv

        output = cfg.bias
        if cfg.enable_p:
            output += p_term
        if cfg.enable_i:
            output += i_term
        if cfg.enable_d:
            output += d_term

        if output > cfg.op_hi:
            output = cfg.op_hi
            state.integral_error -= error * delta_t
        if output < cfg.op_lo:
            output = cfg.op_lo
            state.integral_error -= error * delta_t

        state.prev_glucose = current_glucose
        return output

    def step(self, state, start_time, end_time, command, disturbance):
        y = odeint(diabetic, state.y0, [start_time, end_time], args=(command, disturbance, self.config.p4))
        state.y0 = y[-1]
        return {
            "glucose": float(state.y0[0]),
            "remote_insulin": float(state.y0[1]),
            "insulin": float(state.y0[2]),
        }
