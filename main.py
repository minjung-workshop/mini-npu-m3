"""Mini NPU Simulator 실행 파일."""

from console import run_manual
from analysis import run_json


def main():
    print("=== Mini NPU Simulator ===")
    print("1. 사용자 입력 (3×3)")
    print("2. data.json 분석")

    try:
        while True:
            choice = input("선택: ").strip()
            if choice in ("1", "2"):
                break
            print("1 또는 2를 입력하세요.")

        if choice == "1":
            run_manual()
        else:
            run_json()
    except (KeyboardInterrupt, EOFError):
        print("\n입력이 중단되어 종료합니다.")
    except (ValueError, OverflowError) as error:
        print(f"계산을 완료하지 못했습니다: {error}")


if __name__ == "__main__":
    main()
