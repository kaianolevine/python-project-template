#!/usr/bin/env python3


def main() -> None:
    """
    Print the nth Fibonacci number where:
    F(1) = 1, F(2) = 1
    """
    n = 42
    a, b = 1, 1

    for _ in range(n - 1):
        a, b = b, a + b

    print(f"F({n}) = {a}")


if __name__ == "__main__":
    main()
