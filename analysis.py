"""JSON 검증, 케이스별 판정과 결과 요약."""

import json
import re
from pathlib import Path

from core import validate_matrix, normalize_label, mac, decide
from console import print_performance


def load_filters(raw, size):
    key = f"size_{size}"
    group = raw.get(key)
    if not isinstance(group, dict):
        raise ValueError(f"{key} 필터가 없거나 객체 형식이 아닙니다.")

    result = {}
    for label, matrix in group.items():
        standard = normalize_label(label)
        if standard in result:
            raise ValueError(f"{key}: 중복 라벨 {standard}")
        validate_matrix(matrix, size)
        result[standard] = matrix

    if set(result) != {"Cross", "X"}:
        raise ValueError(f"{key}: Cross와 X 필터가 모두 필요합니다.")
    return result


def run_json(path=None):
    if path is None:
        path = Path(__file__).resolve().parent / "data.json"

    try:
        with open(path, encoding="utf-8-sig") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError("최상위 데이터는 객체여야 합니다.")
        filters = data.get("filters")
        patterns = data.get("patterns")
        if not isinstance(filters, dict):
            raise ValueError("filters는 객체여야 합니다.")
        if not isinstance(patterns, dict):
            raise ValueError("patterns는 객체여야 합니다.")
    except (OSError, ValueError, UnicodeError) as error:
        print(f"파일/스키마 오류: {error}")
        print("분석을 수행하지 못했습니다. data.json을 확인하세요.")
        return

    loaded = {}
    filter_errors = {}
    print("\n[필터 로드]")
    for size in (5, 13, 25):
        try:
            loaded[size] = load_filters(filters, size)
            print(f"size_{size}: 필터 로드 완료 (Cross, X)")
        except ValueError as error:
            filter_errors[size] = str(error)
            print(f"size_{size}: 필터 오류 - {error}")

    failures = []
    passed = 0
    print("\n[패턴 분석]")
    for identifier, case in patterns.items():
        print(f"\n--- {identifier} ---")
        try:
            match = re.fullmatch(r"size_([1-9][0-9]*)_([0-9]+)", identifier)
            if match is None:
                raise ValueError("패턴 키는 size_N_idx 형식이어야 합니다.")
            size = int(match.group(1))
            if size not in (5, 13, 25):
                raise ValueError(f"지원하지 않는 JSON 패턴 크기: {size}")
            if size not in loaded:
                raise ValueError(filter_errors[size])
            if not isinstance(case, dict):
                raise ValueError("패턴 항목은 객체여야 합니다.")
            if "input" not in case or "expected" not in case:
                raise ValueError("input 또는 expected가 없습니다.")

            pattern = case["input"]
            validate_matrix(pattern, size)
            expected = normalize_label(case["expected"])
            group = loaded[size]
            cross_score = mac(pattern, group["Cross"])
            x_score = mac(pattern, group["X"])
            prediction = decide(cross_score, x_score)

            print(f"Cross 점수: {cross_score:.17g}")
            print(f"X 점수: {x_score:.17g}")
            print(f"판정: {prediction} | expected: {expected}")

            if prediction == expected:
                passed += 1
                print("PASS")
            else:
                reason = (
                    "동점 규칙에 따른 UNDECIDED"
                    if prediction == "UNDECIDED"
                    else "판정과 expected 불일치"
                )
                failures.append((identifier, reason))
                print(f"FAIL: {reason}")
        except (ValueError, OverflowError) as error:
            reason = f"데이터/계산 오류: {error}"
            failures.append((identifier, reason))
            print(f"FAIL: {reason}")

    cross3 = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    samples = [(3, cross3, cross3)]
    for size in (5, 13, 25):
        if size in loaded:
            matrix = loaded[size]["Cross"]
            samples.append((size, matrix, matrix))
        else:
            print(f"size_{size}: 유효한 필터가 없어 성능 측정 생략")

    try:
        print_performance(samples)
    except (ValueError, OverflowError) as error:
        print(f"성능 측정 오류: {error}")

    print("\n[결과 요약]")
    print(f"총 테스트: {len(patterns)}개")
    print(f"통과: {passed}개")
    print(f"실패: {len(failures)}개")
    if failures:
        print("실패 케이스:")
        for identifier, reason in failures:
            print(f"- {identifier}: {reason}")
    else:
        print("실패 케이스 없음")
