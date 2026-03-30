"""Small Y combinator demonstration helpers.

This module is intentionally simple and educational so the project can show
how anonymous recursion works in Python.
"""


def y_combinator(function_builder):
    """Return a recursive function using a Y-combinator style pattern."""

    return (lambda x: function_builder(lambda *args: x(x)(*args)))(
        lambda x: function_builder(lambda *args: x(x)(*args))
    )


def factorial_with_y(n: int) -> int:
    """Compute factorial using the Y combinator."""

    if n < 0:
        raise ValueError("factorial input must be >= 0")

    factorial = y_combinator(
        lambda recurse: lambda value: 1 if value <= 1 else value * recurse(value - 1)
    )
    return factorial(n)


def fibonacci_with_y(n: int) -> int:
    """Compute fibonacci using the Y combinator."""

    if n < 0:
        raise ValueError("fibonacci input must be >= 0")

    fibonacci = y_combinator(
        lambda recurse: lambda value: value
        if value <= 1
        else recurse(value - 1) + recurse(value - 2)
    )
    return fibonacci(n)


def y_combinator_demo_payload(number: int) -> dict:
    """Return a concise payload for API/demo usage."""

    return {
        "number": number,
        "factorial": factorial_with_y(number),
        "fibonacci": fibonacci_with_y(number),
        "note": "Values computed through anonymous recursion via Y combinator",
    }
