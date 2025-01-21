from typing import Generic, TypeVar, Optional

# Define a generic type variable
T = TypeVar("T")

class Result(Generic[T]):
    def __init__(self, success: bool, data: Optional[T] = None, error: Optional[str] = None):
        self.success = success
        self.data = data  # The type of data is now generic
        self.error = error  # Error message (string)

    @staticmethod
    def success(data: T = None) -> "Result[T]":
        return Result(True, data=data)

    @staticmethod
    def failure(error: str) -> "Result[T]":
        return Result(False, error=error)

    def __repr__(self):
        if self.success:
            return f"Result(success=True, data={self.data})"
        else:
            return f"Result(success=False, error='{self.error}')"