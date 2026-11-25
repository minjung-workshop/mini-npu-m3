"""MAC 계산, 배열 검증, 라벨 정규화."""

import math

EPSILON = 1e-9


def validate_matrix(matrix, size):
    if not isinstance(matrix, list) or len(matrix) != size:
        raise ValueError(f"행 개수 오류: {size}행이 필요합니다.")

    for index, row in enumerate(matrix, 1):
        if not isinstance(row, list) or len(row) != size:
            raise ValueError(f"{index}행 열 개수 오류: {size}열이 필요합니다.")
        for value in row:
            if type(value) not in (int, float):
                raise ValueError("배열에는 숫자만 사용할 수 있습니다.")
            try:
                finite = math.isfinite(value)
            except OverflowError:
                finite = False
            if not finite:
                raise ValueError("유한한 범위의 숫자만 사용할 수 있습니다.")


def normalize_label(label):
    if not isinstance(label, str):
        raise ValueError("라벨은 문자열이어야 합니다.")
    labels = {"+": "Cross", "cross": "Cross", "x": "X"}
    key = label.strip().lower()
    if key not in labels:
        raise ValueError(f"지원하지 않는 라벨: {label!r}")
    return labels[key]


def mac(pattern, kernel):
    """검증된 같은 크기의 배열을 반복문으로 곱하고 누적합니다."""
    total = 0.0
    for row in range(len(pattern)):
        for column in range(len(pattern)):
            total += pattern[row][column] * kernel[row][column]
    if not math.isfinite(total):
        raise ValueError("MAC 계산 결과가 유한한 숫자 범위를 벗어났습니다.")
    return total


def decide(score_a, score_b, label_a="Cross", label_b="X"):
    if not math.isfinite(score_a) or not math.isfinite(score_b):
        raise ValueError("점수는 유한한 숫자여야 합니다.")
    if abs(score_a - score_b) < EPSILON:
        return "UNDECIDED"
    return label_a if score_a > score_b else label_b
