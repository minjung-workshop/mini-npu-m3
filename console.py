"""콘솔 배열 입력과 MAC 성능 측정."""

from time import perf_counter
from core import validate_matrix, mac, decide, EPSILON

REPEATS = 10


def read_matrix(name, size=3):
    print(f"\n{name}: {size}줄을 입력하세요.")
    print(f"각 줄에 숫자 {size}개를 공백으로 구분하세요.")
    matrix = []

    while len(matrix) < size:
        row_number = len(matrix) + 1
        text = input(f"{row_number}행: ")
        try:
            row = [float(value) for value in text.split()]
            validate_matrix([row], 1) if size == 1 else None
            if len(row) != size:
                raise ValueError("열 개수가 맞지 않습니다.")
            candidate = [row[:] for _ in range(size)]
            validate_matrix(candidate, size)
        except (ValueError, OverflowError):
            print(
                f"입력 형식 오류: 각 줄에 유한한 숫자 {size}개를 "
                "공백으로 구분해 입력하세요."
            )
            continue
        matrix.append(row)

    print(f"{name} 저장 확인: {size}×{size}")
    return matrix


def measure_mac(pattern, kernel, repeats=REPEATS):
    size = len(pattern)
    validate_matrix(pattern, size)
    validate_matrix(kernel, size)
    if repeats < 10:
        raise ValueError("최소 10회 반복 측정해야 합니다.")

    mac(pattern, kernel)
    elapsed = 0.0
    for _ in range(repeats):
        start = perf_counter()
        mac(pattern, kernel)
        elapsed += perf_counter() - start
    return elapsed * 1000 / repeats


def print_performance(samples):
    print(f"\n[성능 분석: MAC 1회 평균 / {REPEATS}회 반복]")
    print("크기       평균 시간(ms)    MAC 횟수(N²)")
    for size, pattern, kernel in samples:
        average = measure_mac(pattern, kernel)
        print(f"{size}×{size:<6} {average:>12.6f} {size * size:>14}")
    print("입력·출력·파일 읽기·배열 검증 시간은 측정에서 제외합니다.")


def run_manual():
    a = read_matrix("필터 A")
    b = read_matrix("필터 B")
    pattern = read_matrix("패턴")

    score_a = mac(pattern, a)
    score_b = mac(pattern, b)
    result = decide(score_a, score_b, "A", "B")

    print("\n[MAC 결과]")
    print(f"A 점수: {score_a:.17g}")
    print(f"B 점수: {score_b:.17g}")
    if result == "UNDECIDED":
        print(f"판정: 판정 불가 (UNDECIDED, |A-B| < {EPSILON})")
    else:
        print(f"판정: {result}")

    print_performance([(3, pattern, a)])
