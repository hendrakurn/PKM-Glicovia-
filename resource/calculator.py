#!/usr/bin/env python3
"""
Simple Calculator Application
"""


class Calculator:
    """A simple calculator class."""

    def add(self, a, b):
        """Add two numbers."""
        return a + b

    def subtract(self, a, b):
        """Subtract b from a."""
        return a - b

    def multiply(self, a, b):
        """Multiply two numbers."""
        return a * b

    def divide(self, a, b):
        """Divide a by b."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b


def main():
    """Main function to run the calculator in interactive mode."""
    calc = Calculator()

    print("Simple Calculator")
    print("Operations: +, -, *, /")
    print("Type 'quit' to exit")
    print()

    while True:
        try:
            user_input = input("Enter expression (e.g., 5 + 3): ").strip()

            if user_input.lower() == 'quit':
                print("Goodbye!")
                break

            parts = user_input.split()
            if len(parts) != 3:
                print("Invalid format. Use: number operator number")
                continue

            num1 = float(parts[0])
            operator = parts[1]
            num2 = float(parts[2])

            if operator == '+':
                result = calc.add(num1, num2)
            elif operator == '-':
                result = calc.subtract(num1, num2)
            elif operator == '*':
                result = calc.multiply(num1, num2)
            elif operator == '/':
                result = calc.divide(num1, num2)
            else:
                print(f"Unknown operator: {operator}")
                continue

            print(f"Result: {result}")
            print()

        except ValueError as e:
            print(f"Error: {e}")
            print()
        except Exception as e:
            print(f"Unexpected error: {e}")
            print()


if __name__ == "__main__":
    main()
