"""Optimized slider correction pipeline utilities.

This module refactors the original script to remove duplicated logic and make
the individual steps easier to maintain.  The functional behaviour remains the
same, but the implementation now follows a stricter single-responsibility
design and reuses helpers for common operations such as unit conversion,
resampling, detrending and smoothing.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Optional, Tuple, Union

import os
import numpy as np
import pandas as pd


# =========================
# CONFIG: 파이프라인 설정
# =========================
CONFIG: Dict[str, object] = {
    # "mechanics" 그룹은 기구학 파라미터를 묶어 관리한다.
    #   - Abbé 오류 보상식 x_res = straight + yaw*arm_y + roll*arm_z 의 암 길이 계산에 사용.
    "mechanics": {
        "arm": {"y_mm": 20.0, "z_mm": 50.0},
        "sensor": {
            "y_offsets_um": {"L": 0.0, "C": 0.0, "R": 0.0},
            "x_positions_mm": {"L": -100.0, "C": 0.0, "R": 100.0},
            "z_offsets_um": {"L": 0.0, "C": 0.0, "R": 0.0},
        },
    },

    # "units" 그룹은 모든 단위 설정을 모아 변환 로직의 일관성을 높인다.
    "units": {
        "angle": "arcsec",  # 'arcsec'|'urad'|'rad'
        "flat": "um",  # Flatness 입력 단위
        "straight": "um",  # Straightness 입력 단위
        "posacc": "um",  # Position accuracy 단위
    },

    # "strategy"는 제어 및 신호처리 전략에 대한 선택지를 담는다.
    "strategy": {
        "yaw_compensation_channel": "C",  # 단일 런 보상기준 yaw 채널
        "pitch_reference_channel": "avg",  # roll 추정 시 참조 pitch
        "include_posacc_in_arm": True,  # posacc를 Y-Abbé 암에 포함
        "zero_mean_yaw_before_comp": False,  # yaw DC 제거 여부
    },

    # "preprocessing"은 필터링과 같은 신호 전처리 파라미터를 관리한다.
    "preprocessing": {
        "savgol_window": 9,  # 스무딩, scipy 없으면 이동평균 대체
        "savgol_poly": 2,
    },
}


# =========================
# 상수 & 유틸리티
# =========================
PIPELINE_CONSTANTS: Dict[str, object] = {
    "conversions": {
        # 1" = π/648000 rad, 1 µrad = 10^-6 rad; 길이는 mm→µm 를 기본으로 한다.
        "rad": {"arcsec": np.deg2rad(1.0 / 3600.0), "urad": 1e-6, "rad": 1.0},
        "um": {"um": 1.0, "µm": 1.0, "mm": 1000.0},
    },
    "channels": ("L", "C", "R"),
    "fields": {
        "angle": ("yaw", "pitch"),
        "length": ("straight", "flat"),
    },
}

PIPELINE_CONSTANTS["data_keys"] = tuple(
    f"{field}_{channel}"
    for field in (*PIPELINE_CONSTANTS["fields"]["angle"], *PIPELINE_CONSTANTS["fields"]["length"])
    for channel in PIPELINE_CONSTANTS["channels"]
) + ("posacc",)

PIPELINE_CONSTANTS["field_unit_config"] = {
    # 각 필드에 대해 (CONFIG 내 단위 키, 목표 단위)를 지정한다.
    # 예: yaw/pitch → angle 단위를 rad 로 변환.
    "yaw": ("angle", "rad"),
    "pitch": ("angle", "rad"),
    "straight": ("straight", "um"),
    "flat": ("flat", "um"),
}

try:  # pragma: no cover - optional dependency
    from scipy.interpolate import interp1d
except Exception:  # pragma: no cover - optional dependency
    interp1d = None

try:  # pragma: no cover - optional dependency
    from sklearn.linear_model import LinearRegression
except Exception:  # pragma: no cover - optional dependency
    LinearRegression = None

try:  # pragma: no cover - optional dependency
    import plotly.graph_objects as go
except Exception:  # pragma: no cover - optional dependency
    go = None

CHANNELS: Tuple[str, ...] = PIPELINE_CONSTANTS["channels"]
DATA_KEYS: Tuple[str, ...] = PIPELINE_CONSTANTS["data_keys"]
FIELD_UNIT_CONFIG: Dict[str, Tuple[str, str]] = PIPELINE_CONSTANTS["field_unit_config"]


def convert_measurement(values: Iterable[float], unit: str, target: str) -> Union[float, np.ndarray]:
    """단위 변환 유틸리티.

    각도는 ``θ[rad] = θ[arcsec] * π / (180 * 3600)`` 또는 ``θ[rad] = θ[µrad] * 10^-6`` 공식을,
    길이는 ``ℓ[µm] = ℓ[mm] * 10^3`` 변환식을 따른다. 스칼라는 ``float`` 로, 시퀀스는
    ``ndarray`` 로 반환하여 후속 수치 연산의 가독성을 높였다.
    """

    values_arr = np.asarray(values, float)
    conversions_by_target = PIPELINE_CONSTANTS["conversions"]
    if target not in conversions_by_target:
        raise ValueError("target must be 'rad' or 'um'")
    conversions = conversions_by_target[target]

    if unit not in conversions:
        if target == "rad":
            raise ValueError("angle_unit must be arcsec|urad|rad")
        raise ValueError("길이 단위는 'um' 또는 'mm'만 지원합니다.")

    result = values_arr * conversions[unit]

    if values_arr.ndim == 0:
        return float(result)
    return result


def classify_direction(coords: Iterable[float]) -> str:
    """궤적의 시작·종점 차분 ΔY 를 이용해 전진(fwd)/후진(bwd)을 판별한다."""

    values = np.asarray(coords, float)
    delta = values[-1] - values[0]
    if delta > 0:
        return "fwd"
    if delta < 0:
        return "bwd"
    raise ValueError("이동 방향을 전진/후진으로 판별할 수 없습니다.")


def resample_to_grid(x_src: Iterable[float], y_src: Iterable[float], x_grid: Iterable[float]) -> np.ndarray:
    """선형 보간으로 데이터를 공통 격자에 투영한다."""
    x_src_arr = np.asarray(x_src, float)
    y_src_arr = np.asarray(y_src, float)
    x_grid_arr = np.asarray(x_grid, float)
    if interp1d is not None:
        interpolator = interp1d(
            x_src_arr,
            y_src_arr,
            kind="linear",
            bounds_error=False,
            fill_value="extrapolate",
        )
        return interpolator(x_grid_arr)
    return np.interp(x_grid_arr, x_src_arr, y_src_arr)


def detrend_linear(values: Iterable[float]) -> np.ndarray:
    """최소제곱 직선 추정을 제거해 드리프트를 없앤다."""
    y = np.asarray(values, float)
    x = np.arange(y.size, dtype=float)
    if LinearRegression is not None and y.size > 1:
        model = LinearRegression()
        model.fit(x.reshape(-1, 1), y)
        trend = model.predict(x.reshape(-1, 1))
    else:
        matrix = np.vstack([x, np.ones_like(x)]).T
        coef, *_ = np.linalg.lstsq(matrix, y, rcond=None)
        trend = matrix @ coef
    return y - trend


def resample_run_series(run: Mapping[str, np.ndarray], y_grid: np.ndarray) -> Dict[str, np.ndarray]:
    """각 센서 시퀀스를 참조 격자에 정렬한다."""
    return {
        key: resample_to_grid(run["Y_mm"], run[key], y_grid)
        for key in DATA_KEYS
    }


def detrend_run_series(series: Mapping[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """시퀀스 전체에 선형 드리프트 제거를 적용한다."""
    return {key: detrend_linear(series[key]) for key in DATA_KEYS}


def smooth_series(values: Iterable[float], window: Optional[int], poly: int) -> np.ndarray:
    """Savitzky-Golay 필터(또는 이동평균)를 적용하여 고주파 노이즈를 줄인다."""

    window = None if window is None else int(window)
    if not window or window < 3:
        return np.asarray(values, float)
    if window % 2 == 0:
        window += 1
    try:
        from scipy.signal import savgol_filter

        return savgol_filter(np.asarray(values, float), window_length=window, polyorder=poly, mode="interp")
    except Exception:
        arr = np.asarray(values, float)
        win = max(3, window if window else 3)
        if win % 2 == 0:
            win += 1
        half = (win - 1) // 2
        padded = np.r_[arr[half:0:-1], arr, arr[-2 : -half - 2 : -1]]
        kernel = np.ones(win) / win
        smoothed = np.convolve(padded, kernel, mode="same")[half:-half]
        return smoothed


def smooth_many(
    series: Mapping[str, np.ndarray],
    keys: Iterable[str],
    window: Optional[int],
    poly: int,
) -> Dict[str, np.ndarray]:
    """여러 시퀀스에 동일한 스무딩 연산을 배치 적용한다."""

    return {key: smooth_series(series[key], window, poly) for key in keys}


def build_sensor_maps(config: Mapping[str, object]) -> Tuple[Dict[str, float], Dict[str, float], Dict[str, float]]:
    """센서 좌표계를 µm 기준으로 정규화한다."""

    sensor_cfg = config["mechanics"]["sensor"]
    sens_y = {channel: float(offset) for channel, offset in sensor_cfg["y_offsets_um"].items()}
    sens_x = {
        channel: float(convert_measurement(position, "mm", "um"))
        for channel, position in sensor_cfg["x_positions_mm"].items()
    }
    sens_z = {channel: float(offset) for channel, offset in sensor_cfg["z_offsets_um"].items()}
    return sens_x, sens_y, sens_z


def convert_units_run(run: Mapping[str, np.ndarray], config: Mapping[str, object]) -> Dict[str, np.ndarray]:
    """표준 단위(rad/µm)로 변환하여 기하학 계산의 전제조건을 맞춘다."""

    converted = {"Y_mm": np.asarray(run["Y"], float)}
    units_cfg = config["units"]
    for field, (unit_key, target_unit) in FIELD_UNIT_CONFIG.items():
        unit = str(units_cfg[unit_key])
        for channel in CHANNELS:
            key = f"{field}_{channel}"
            converted[key] = convert_measurement(run[key], unit, target_unit)
    converted["posacc"] = convert_measurement(run["posacc"], str(units_cfg["posacc"]), "um")
    return converted


def remove_yaw_dc(yaw_dict: Mapping[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """Yaw 신호의 평균값을 제거해 순수한 변동 성분만 남긴다."""

    return {key: values - np.mean(values) for key, values in yaw_dict.items()}


def choose_channel(series: Mapping[str, np.ndarray], field: str, channel: str) -> np.ndarray:
    """L/C/R/평균 채널 중 하나를 선택한다."""

    key = f"{field}_{channel}"
    if channel in CHANNELS:
        return series[key]
    if channel == "avg":
        return np.mean([series[f"{field}_{ch}"] for ch in CHANNELS], axis=0)
    raise ValueError(f"{field} channel must be L|C|R|avg")


def select_pitch_ref(series: Mapping[str, np.ndarray], mode: str) -> np.ndarray:
    """Roll 추정을 위한 기준 pitch 시퀀스를 반환한다."""

    return choose_channel(series, "pitch", mode)


def correct_z_for_pitch(flat: Mapping[str, np.ndarray], pitch_ref: np.ndarray, sens_y_um: Mapping[str, float]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Pitch*Y 보정을 적용해 실제 Z 편차(Flatness)를 계산한다."""

    return tuple(flat[f"flat_{ch}"] - pitch_ref * sens_y_um[ch] for ch in CHANNELS)


def estimate_roll_from_lcr(flat_z: Tuple[np.ndarray, np.ndarray, np.ndarray], sens_x_um: Mapping[str, float]) -> np.ndarray:
    """LCR 센서의 Z 분포로부터 roll ≈ ∂Z/∂X 를 최소제곱으로 추정한다."""

    x_coords = np.array([[sens_x_um[ch]] for ch in CHANNELS], dtype=float)
    fallback_matrix = None if LinearRegression is not None else np.hstack([x_coords, np.ones_like(x_coords)])
    roll = np.zeros_like(flat_z[0])
    for idx in range(roll.size):
        z_vec = np.array([flat_z[0][idx], flat_z[1][idx], flat_z[2][idx]], dtype=float)
        if LinearRegression is not None:
            model = LinearRegression()
            model.fit(x_coords, z_vec)
            roll[idx] = float(model.coef_[0])
        else:
            coef, *_ = np.linalg.lstsq(fallback_matrix, z_vec, rcond=None)
            roll[idx] = coef[0]
    return roll


def compute_abbe_arms(
    config: Mapping[str, object],
    sens_y_um: Mapping[str, float],
    sens_z_um: Mapping[str, float],
    posacc: np.ndarray,
) -> Dict[str, Tuple[np.ndarray, float]]:
    """Abbé 원리에 따라 회전각*암 길이 항을 구성한다."""

    arm_cfg = config["mechanics"]["arm"]
    strategy_cfg = config["strategy"]
    arm_y_base = float(convert_measurement(arm_cfg["y_mm"], "mm", "um"))
    arm_z_base = float(convert_measurement(arm_cfg["z_mm"], "mm", "um"))
    include_posacc = bool(strategy_cfg["include_posacc_in_arm"])

    arms: Dict[str, Tuple[np.ndarray, float]] = {}
    for channel in CHANNELS:
        arm_y = arm_y_base + sens_y_um[channel]
        if include_posacc:
            arm_y = arm_y + posacc
        arm_z = arm_z_base + sens_z_um[channel]
        arms[channel] = (arm_y, arm_z)
    return arms


def compute_x_residual_channel(
    straight_um: np.ndarray,
    yaw_rad: np.ndarray,
    roll_rad: np.ndarray,
    arm_y_um: np.ndarray,
    arm_z_um: float,
) -> np.ndarray:
    """Abbé 오차 모델 X_res = straight + yaw*arm_y + roll*arm_z."""

    return straight_um + yaw_rad * arm_y_um + roll_rad * arm_z_um


def decompose_even_odd(values_fwd: np.ndarray, values_bwd: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """짝(g)/홀(h) 성분을 동시에 계산한다."""

    even = 0.5 * (values_fwd + values_bwd)
    odd = 0.5 * (values_fwd - values_bwd)
    return even, odd


def build_directional_ff(even_arr: np.ndarray, odd_arr: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """정/역방향 피드포워드 = g ± h."""

    return even_arr + odd_arr, even_arr - odd_arr


def build_x_lut(
    g_xs: np.ndarray,
    yaw_ff_fwd: np.ndarray,
    yaw_ff_bwd: np.ndarray,
    roll_ff_fwd: np.ndarray,
    roll_ff_bwd: np.ndarray,
    arm_y_total: np.ndarray,
    arm_z_total: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """Yaw/Roll 보상항을 포함한 X 좌표 LUT 를 생성한다."""

    x_corr_fwd = g_xs + yaw_ff_fwd * arm_y_total + roll_ff_fwd * arm_z_total
    x_corr_bwd = g_xs + yaw_ff_bwd * arm_y_total + roll_ff_bwd * arm_z_total
    return x_corr_fwd, x_corr_bwd


def resample_and_detrend_runs(
    runs: Iterable[Mapping[str, np.ndarray]],
    y_grid: np.ndarray,
) -> List[Dict[str, np.ndarray]]:
    """보간 후 선형 드리프트를 제거하여 각 러닝을 정규화한다."""

    processed_runs: List[Dict[str, np.ndarray]] = []
    for run in runs:
        resampled = resample_run_series(run, y_grid)
        detrended = detrend_run_series(resampled)
        processed_runs.append({
            **detrended,
            "Y_mm": np.asarray(y_grid, float),
            "dir": classify_direction(run["Y_mm"]),
        })
    return processed_runs



def average_by_direction(runs: Iterable[Mapping[str, np.ndarray]]) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray], np.ndarray]:
    """전·후진 데이터를 분리 평균해 방향 의존성 분석 기반을 만든다."""

    runs = list(runs)
    forwards = [run for run in runs if run["dir"] == "fwd"]
    backwards = [run for run in runs if run["dir"] == "bwd"]

    def _mean_for_direction(samples: List[Mapping[str, np.ndarray]]) -> Dict[str, np.ndarray]:
        if not samples:
            raise ValueError("Forward/backward 데이터가 부족합니다.")
        stacked = {key: np.vstack([np.asarray(sample[key], float) for sample in samples]) for key in DATA_KEYS}
        return {key: np.nanmean(values, axis=0) for key, values in stacked.items()}

    mean_fwd = _mean_for_direction(forwards)
    mean_bwd = _mean_for_direction(backwards)
    y_grid = np.asarray(forwards[0]["Y_mm"] if forwards else backwards[0]["Y_mm"], float)
    return mean_fwd, mean_bwd, y_grid


def select_reference_grid(converted_runs: Iterable[Mapping[str, np.ndarray]]) -> np.ndarray:
    """정방향 궤적 중 가장 촘촘한 그리드를 공통 기준으로 선택한다."""

    forwards = [run["Y_mm"] for run in converted_runs if classify_direction(run["Y_mm"]) == "fwd"]
    reference = max(forwards, key=lambda arr: arr.size) if forwards else next(iter(converted_runs))["Y_mm"]
    return np.asarray(reference, float)


def compute_directional_orientations(
    mean_fwd: Mapping[str, np.ndarray],
    mean_bwd: Mapping[str, np.ndarray],
    sens_x_um: Mapping[str, float],
    sens_y_um: Mapping[str, float],
    strategy_cfg: Mapping[str, object],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Yaw/Roll의 짝·홀 성분을 계산하기 위한 방향별 회전량을 구한다."""

    yaw_channel = str(strategy_cfg["yaw_compensation_channel"])
    pitch_channel = str(strategy_cfg["pitch_reference_channel"])

    yaw_fwd = choose_channel(mean_fwd, "yaw", yaw_channel)
    yaw_bwd = choose_channel(mean_bwd, "yaw", yaw_channel)

    pitch_ref_fwd = select_pitch_ref(mean_fwd, pitch_channel)
    pitch_ref_bwd = select_pitch_ref(mean_bwd, pitch_channel)
    corrected_flat_fwd = correct_z_for_pitch(mean_fwd, pitch_ref_fwd, sens_y_um)
    corrected_flat_bwd = correct_z_for_pitch(mean_bwd, pitch_ref_bwd, sens_y_um)
    roll_fwd = estimate_roll_from_lcr(corrected_flat_fwd, sens_x_um)
    roll_bwd = estimate_roll_from_lcr(corrected_flat_bwd, sens_x_um)

    return yaw_fwd, yaw_bwd, roll_fwd, roll_bwd


def pipeline_multiturn(runs: Iterable[Mapping[str, np.ndarray]], config: Mapping[str, object]) -> pd.DataFrame:
    """왕복 데이터로부터 방향별 Yaw/Roll FF와 X 보정 LUT 를 계산한다."""

    converted_runs = [convert_units_run(run, config) for run in runs]
    y_grid = select_reference_grid(converted_runs)

    processed_runs = resample_and_detrend_runs(converted_runs, y_grid)
    mean_fwd, mean_bwd, y_grid = average_by_direction(processed_runs)

    sens_x_um, sens_y_um, _ = build_sensor_maps(config)
    strategy_cfg = config["strategy"]
    yaw_fwd, yaw_bwd, roll_fwd, roll_bwd = compute_directional_orientations(
        mean_fwd, mean_bwd, sens_x_um, sens_y_um, strategy_cfg
    )

    g_yaw, h_yaw = decompose_even_odd(yaw_fwd, yaw_bwd)
    g_roll, h_roll = decompose_even_odd(roll_fwd, roll_bwd)

    g_xs, _ = decompose_even_odd(mean_fwd["straight_C"], mean_bwd["straight_C"])

    posacc = mean_fwd["posacc"]
    arm_cfg = config["mechanics"]["arm"]
    strategy_cfg = config["strategy"]
    arm_y_total = float(convert_measurement(arm_cfg["y_mm"], "mm", "um")) + (
        posacc if strategy_cfg["include_posacc_in_arm"] else 0.0
    )
    arm_z_total = float(convert_measurement(arm_cfg["z_mm"], "mm", "um"))

    yaw_ff_fwd, yaw_ff_bwd = build_directional_ff(g_yaw, h_yaw)
    roll_ff_fwd, roll_ff_bwd = build_directional_ff(g_roll, h_roll)

    x_corr_fwd, x_corr_bwd = build_x_lut(g_xs, yaw_ff_fwd, yaw_ff_bwd, roll_ff_fwd, roll_ff_bwd, arm_y_total, arm_z_total)

    preprocessing_cfg = config["preprocessing"]
    window = preprocessing_cfg.get("savgol_window")
    poly = int(preprocessing_cfg.get("savgol_poly", 2))

    smoothed = smooth_many(
        {
            "yaw_ff_fwd": yaw_ff_fwd,
            "yaw_ff_bwd": yaw_ff_bwd,
            "roll_ff_fwd": roll_ff_fwd,
            "roll_ff_bwd": roll_ff_bwd,
            "x_corr_fwd": x_corr_fwd,
            "x_corr_bwd": x_corr_bwd,
        },
        keys=("yaw_ff_fwd", "yaw_ff_bwd", "roll_ff_fwd", "roll_ff_bwd", "x_corr_fwd", "x_corr_bwd"),
        window=window,
        poly=poly,
    )

    return pd.DataFrame(
        {
            "Y_mm": y_grid,
            "yaw_ff_fwd_urad": yaw_ff_fwd * 1e6,
            "yaw_ff_bwd_urad": yaw_ff_bwd * 1e6,
            "roll_ff_fwd_urad": roll_ff_fwd * 1e6,
            "roll_ff_bwd_urad": roll_ff_bwd * 1e6,
            "X_corr_fwd_um_raw": x_corr_fwd,
            "X_corr_bwd_um_raw": x_corr_bwd,
            "yaw_ff_fwd_urad_s": smoothed["yaw_ff_fwd"] * 1e6,
            "yaw_ff_bwd_urad_s": smoothed["yaw_ff_bwd"] * 1e6,
            "roll_ff_fwd_urad_s": smoothed["roll_ff_fwd"] * 1e6,
            "roll_ff_bwd_urad_s": smoothed["roll_ff_bwd"] * 1e6,
            "X_corr_fwd_um": smoothed["x_corr_fwd"],
            "X_corr_bwd_um": smoothed["x_corr_bwd"],
        }
    )


def compute_single_run_residual(run: Mapping[str, np.ndarray], config: Mapping[str, object]) -> pd.DataFrame:
    """단일 패스에서 Abbé 보정 후 잔차를 평가한다."""

    converted = convert_units_run(run, config)
    strategy_cfg = config["strategy"]
    if strategy_cfg.get("zero_mean_yaw_before_comp", False):
        yaw_dict = remove_yaw_dc({f"yaw_{channel}": converted[f"yaw_{channel}"] for channel in CHANNELS})
        converted.update(yaw_dict)

    sens_x_um, sens_y_um, sens_z_um = build_sensor_maps(config)
    yaw_rad = choose_channel(converted, "yaw", str(strategy_cfg["yaw_compensation_channel"]))
    pitch_ref = select_pitch_ref(converted, str(strategy_cfg["pitch_reference_channel"]))
    corrected_flat = correct_z_for_pitch(converted, pitch_ref, sens_y_um)
    roll_rad = estimate_roll_from_lcr(corrected_flat, sens_x_um)

    posacc = converted["posacc"]
    arms = compute_abbe_arms(config, sens_y_um, sens_z_um, posacc)

    residuals = {}
    for channel in CHANNELS:
        straight = converted[f"straight_{channel}"]
        arm_y, arm_z = arms[channel]
        residuals[f"X_res_{channel}_um"] = compute_x_residual_channel(straight, yaw_rad, roll_rad, arm_y, arm_z)

    return pd.DataFrame(
        {
            "Y_mm": converted["Y_mm"],
            **residuals,
            "yaw_comp_urad": yaw_rad * 1e6,
            "roll_est_urad": roll_rad * 1e6,
        }
    )


# =========================
# 데이터 입력/파서
# =========================
REQUIRED_COLS: Tuple[str, ...] = ("Y", *PIPELINE_CONSTANTS["data_keys"])


def _validate_columns(columns: Iterable[str], required: Iterable[str]) -> None:
    """필수 컬럼 집합을 확인한다."""

    missing = [column for column in required if column not in columns]
    if missing:
        raise ValueError(f"필수 컬럼 누락: {', '.join(missing)}")


def read_multiturn_from_single_csv(csv_path: str) -> List[Dict[str, np.ndarray]]:
    """turn 열이 포함된 CSV 를 읽어 멀티턴 런 목록을 반환한다."""

    dataframe = pd.read_csv(csv_path)
    if "turn" not in dataframe.columns:
        raise ValueError("CSV에 'turn' 열이 필요합니다.")
    _validate_columns(dataframe.columns, REQUIRED_COLS)

    runs: List[Dict[str, np.ndarray]] = []
    for turn, group in dataframe.groupby("turn"):
        run = {column: group[column].to_numpy() for column in REQUIRED_COLS}
        run["turn"] = int(turn)
        runs.append(run)
    return runs


def read_runs_manifest(manifest_csv: str) -> List[Dict[str, np.ndarray]]:
    """turn,path 매니페스트를 읽어 개별 CSV 를 조합한다."""

    dataframe = pd.read_csv(manifest_csv)
    if not {"turn", "path"}.issubset(dataframe.columns):
        raise ValueError("매니페스트 CSV는 'turn,path' 열이 필요합니다.")

    runs: List[Dict[str, np.ndarray]] = []
    for _, row in dataframe.sort_values("turn").iterrows():
        csv_path = str(row["path"])
        single = pd.read_csv(csv_path)
        _validate_columns(single.columns, REQUIRED_COLS)
        run = {column: single[column].to_numpy() for column in REQUIRED_COLS}
        run["turn"] = int(row["turn"])
        runs.append(run)
    return runs


# =========================
# 시뮬레이션/데모 유틸리티 (기능 유지)
# =========================
def synth_one_pass(
    y_mm: Iterable[float],
    yaw_amp_arcsec: float = 20.0,
    yaw_phase: float = 0.0,
    straight_amp_um: float = 4.0,
    drift: float = 0.5,
    noise: float = 0.2,
) -> Dict[str, np.ndarray]:
    """테스트용 합성 데이터 생성 (사인파 + 드리프트 + 노이즈)."""

    y = np.asarray(y_mm, float)
    yaw_c = yaw_amp_arcsec * np.sin(2 * np.pi * y / 500.0 + yaw_phase)
    yaw_l = yaw_c + 1.0
    yaw_r = yaw_c - 1.0
    rng = np.random.RandomState(0)
    straight_c = (
        straight_amp_um * np.sin(2 * np.pi * y / 300.0)
        + np.linspace(0, drift, y.size)
        + rng.normal(0, noise, y.size)
    )
    flat_c = 0.5 * np.sin(2 * np.pi * y / 400.0) * 3
    flat_l = flat_c + 0.2
    flat_r = flat_c - 0.1
    pitch_c = 5.0 * np.sin(2 * np.pi * y / 600.0)
    pitch_l = pitch_c + 0.2
    pitch_r = pitch_c - 0.2
    posacc = 0.5 * np.sin(2 * np.pi * y / 250.0) * 10
    return {
        "Y": y,
        "L_yaw": yaw_l,
        "C_yaw": yaw_c,
        "R_yaw": yaw_r,
        "L_straight": straight_c + 0.5,
        "C_straight": straight_c,
        "R_straight": straight_c - 0.3,
        "L_flat": flat_l,
        "C_flat": flat_c,
        "R_flat": flat_r,
        "L_pitch": pitch_l,
        "C_pitch": pitch_c,
        "R_pitch": pitch_r,
        "posacc": posacc,
    }


def demo_multiturn_pipeline(turns: int = 3) -> Tuple[pd.DataFrame, str]:
    """합성 데이터를 생성하고 LUT 를 산출한 뒤 CSV 경로와 결과를 반환한다."""

    y_fwd = np.linspace(0, 500, 101)
    y_bwd = np.linspace(500, 0, 101)

    rows: List[Dict[str, float]] = []
    turn_index = 0
    for repeat in np.linspace(0.0, 0.2, turns):
        for direction, y_values in (("fwd", y_fwd), ("bwd", y_bwd)):
            turn_index += 1
            data = synth_one_pass(y_values, yaw_phase=repeat, drift=0.6 + repeat)
            for idx in range(len(data["Y"])):
                rows.append({"turn": turn_index, **{key: data[key][idx] for key in REQUIRED_COLS}})

    dataframe = pd.DataFrame(rows)
    csv_path = "/mnt/data/sample_multiturn.csv"
    dataframe.to_csv(csv_path, index=False, encoding="utf-8")
    runs_loaded = read_multiturn_from_single_csv(csv_path)
    lut = pipeline_multiturn(runs_loaded, CONFIG)
    return lut, csv_path


def build_plotly_report(lut: pd.DataFrame) -> Dict[str, "go.Figure"]:
    """Yaw/Roll/X LUT 를 Plotly 도형으로 시각화한다."""

    if go is None:
        raise RuntimeError("Plotly가 설치되어 있어야 그래프를 생성할 수 있습니다.")

    figures: Dict[str, "go.Figure"] = {}
    figures["table"] = go.Figure(
        data=[go.Table(header=dict(values=list(lut.columns)), cells=dict(values=[lut[c] for c in lut.columns]))]
    )

    figures["yaw"] = go.Figure()
    figures["yaw"].add_trace(go.Scatter(x=lut["Y_mm"], y=lut["yaw_ff_fwd_urad_s"], mode="lines", name="Yaw FF fwd [µrad]"))
    figures["yaw"].add_trace(go.Scatter(x=lut["Y_mm"], y=lut["yaw_ff_bwd_urad_s"], mode="lines", name="Yaw FF bwd [µrad]"))
    figures["yaw"].update_layout(title="Yaw Feed-forward", xaxis_title="Y [mm]", yaxis_title="Yaw [µrad]")

    figures["roll"] = go.Figure()
    figures["roll"].add_trace(
        go.Scatter(x=lut["Y_mm"], y=lut["roll_ff_fwd_urad_s"], mode="lines", name="Roll FF fwd [µrad]")
    )
    figures["roll"].add_trace(
        go.Scatter(x=lut["Y_mm"], y=lut["roll_ff_bwd_urad_s"], mode="lines", name="Roll FF bwd [µrad]")
    )
    figures["roll"].update_layout(title="Roll Feed-forward", xaxis_title="Y [mm]", yaxis_title="Roll [µrad]")

    figures["x_corr"] = go.Figure()
    figures["x_corr"].add_trace(
        go.Scatter(x=lut["Y_mm"], y=lut["X_corr_fwd_um"], mode="lines", name="X LUT fwd [µm]")
    )
    figures["x_corr"].add_trace(
        go.Scatter(x=lut["Y_mm"], y=lut["X_corr_bwd_um"], mode="lines", name="X LUT bwd [µm]")
    )
    figures["x_corr"].update_layout(title="X Pre-distortion", xaxis_title="Y [mm]", yaxis_title="X [µm]")

    return figures


def save_plotly_report(figures: Mapping[str, "go.Figure"], output_dir: str) -> List[str]:
    """그래프를 HTML 로 저장하고 경로 목록을 반환한다."""

    if go is None:
        raise RuntimeError("Plotly가 설치되어 있어야 그래프를 저장할 수 있습니다.")

    os.makedirs(output_dir, exist_ok=True)
    paths: List[str] = []
    for name, figure in figures.items():
        path = os.path.join(output_dir, f"{name}.html")
        figure.write_html(path)
        paths.append(path)
    return paths


__all__ = [
    "CONFIG",
    "compute_single_run_residual",
    "pipeline_multiturn",
    "read_multiturn_from_single_csv",
    "read_runs_manifest",
    "synth_one_pass",
    "demo_multiturn_pipeline",
    "build_plotly_report",
    "save_plotly_report",
]

