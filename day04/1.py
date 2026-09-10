def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        raise ValueError("0으로 나눌 수 없습니다.")
    return x / y

def calculator():
    print("=== 간단한 파이썬 계산기 ===")
    while True:
        print("\n원하는 연산을 선택하세요:")
        print("1. 더하기 (+)")
        print("2. 빼기 (-)")
        print("3. 곱하기 (*)")
        print("4. 나누기 (/)")
        print("5. 종료")
        
        choice = input("선택 (1-5): ").strip()
        
        if choice == '5':
            print("계산기를 종료합니다. 감사합니다!")
            break
            
        if choice not in ('1', '2', '3', '4'):
            print("올바른 선택이 아닙니다. 1에서 5 사이의 숫자를 입력해주세요.")
            continue
            
        try:
            num1 = float(input("첫 번째 숫자를 입력하세요: "))
            num2 = float(input("두 번째 숫자를 입력하세요: "))
        except ValueError:
            print("유효한 숫자를 입력해 주세요.")
            continue
            
        if choice == '1':
            print(f"결과: {num1} + {num2} = {add(num1, num2)}")
        elif choice == '2':
            print(f"결과: {num1} - {num2} = {subtract(num1, num2)}")
        elif choice == '3':
            print(f"결과: {num1} * {num2} = {multiply(num1, num2)}")
        elif choice == '4':
            try:
                print(f"결과: {num1} / {num2} = {divide(num1, num2)}")
            except ValueError as e:
                print(f"오류: {e}")

if __name__ == "__main__":
    calculator()
