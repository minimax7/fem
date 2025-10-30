"""CLI 스크립트: 슬라이더 파이프라인 실행 및 보고서 생성."""

from __future__ import annotations

import argparse
import pathlib
from typing import List

import pandas as pd

from slider_pipeline import (
    CONFIG,
    build_plotly_report,
    demo_multiturn_pipeline,
    pipeline_multiturn,
    read_multiturn_from_single_csv,
    read_runs_manifest,
    save_plotly_report,
)


def _build_lut(args: argparse.Namespace) -> pd.DataFrame:
    if args.demo:
        lut, csv_path = demo_multiturn_pipeline(turns=args.demo_turns)
        print(f"[demo] Generated synthetic dataset at {csv_path}")
        return lut

    if args.input:
        runs = read_multiturn_from_single_csv(args.input)
    elif args.manifest:
        runs = read_runs_manifest(args.manifest)
    else:
        raise SystemExit("Either --input or --manifest or --demo must be provided.")
    return pipeline_multiturn(runs, CONFIG)


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Slider yaw/roll 보정 LUT 생성")
    parser.add_argument("--input", help="turn 열이 포함된 CSV 경로")
    parser.add_argument("--manifest", help="turn,path 매니페스트 CSV 경로")
    parser.add_argument("--output-lut", help="결과 LUT 를 저장할 CSV 경로")
    parser.add_argument("--plot-dir", help="Plotly HTML 을 저장할 디렉터리")
    parser.add_argument("--demo", action="store_true", help="합성 데이터를 생성하여 실행")
    parser.add_argument("--demo-turns", type=int, default=3, help="합성 멀티턴 반복 수")
    parser.add_argument("--preview", action="store_true", help="결과 앞부분을 표 형태로 출력")
    args = parser.parse_args(argv)

    lut_df = _build_lut(args)

    if args.preview:
        print(lut_df.head())

    if args.output_lut:
        output_path = pathlib.Path(args.output_lut)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        lut_df.to_csv(output_path, index=False)
        print(f"Saved LUT to {output_path}")

    if args.plot_dir:
        figures = build_plotly_report(lut_df)
        paths = save_plotly_report(figures, args.plot_dir)
        for path in paths:
            print(f"Saved plot: {path}")


if __name__ == "__main__":
    main()
