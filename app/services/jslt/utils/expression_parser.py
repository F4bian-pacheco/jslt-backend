"""Utility functions for parsing JSLT expressions."""
import re
from typing import List, Tuple


class ExpressionParser:
    """Utility class for parsing JSLT expressions."""

    @staticmethod
    def split_by_delimiter(
        content: str,
        delimiter: str,
        opening_chars: str = "{[(",
        closing_chars: str = "}])",
    ) -> List[str]:
        """
        Split content by delimiter, respecting nested structures and strings.

        Args:
            content: The content to split
            delimiter: The delimiter character(s) to split by
            opening_chars: Characters that increase nesting depth
            closing_chars: Characters that decrease nesting depth

        Returns:
            List of split parts
        """
        parts = []
        current_part = ""
        depth = 0
        in_string = False
        string_char = None

        i = 0
        while i < len(content):
            char = content[i]

            if not in_string and char in '"\'':
                in_string = True
                string_char = char
                current_part += char
            elif in_string and char == string_char:
                in_string = False
                string_char = None
                current_part += char
            elif not in_string:
                if char in opening_chars:
                    depth += 1
                    current_part += char
                elif char in closing_chars:
                    depth -= 1
                    current_part += char
                elif depth == 0 and content[i:i + len(delimiter)] == delimiter:
                    parts.append(current_part.strip())
                    current_part = ""
                    i += len(delimiter) - 1
                else:
                    current_part += char
            else:
                current_part += char

            i += 1

        if current_part.strip():
            parts.append(current_part.strip())

        return parts if parts else [content]

    @staticmethod
    def split_object_pairs(content: str) -> List[str]:
        """Split object content into key-value pairs."""
        return ExpressionParser.split_by_delimiter(content, ",")

    @staticmethod
    def split_array_elements(content: str) -> List[str]:
        """Split array content into elements."""
        return ExpressionParser.split_by_delimiter(content, ",")

    @staticmethod
    def split_function_args(args_str: str) -> List[str]:
        """Split function arguments."""
        return ExpressionParser.split_by_delimiter(args_str, ",")

    @staticmethod
    def split_addition_parts(expression: str) -> List[str]:
        """Split addition expression into parts, respecting string literals and nested expressions."""
        parts = []
        current_part = ""
        in_string = False
        string_char = None
        depth = 0
        i = 0

        while i < len(expression):
            char = expression[i]

            if not in_string and char in '"\'':
                in_string = True
                string_char = char
                current_part += char
            elif in_string and char == string_char:
                in_string = False
                string_char = None
                current_part += char
            elif not in_string:
                if char in "{[(":
                    depth += 1
                    current_part += char
                elif char in "}])":
                    depth -= 1
                    current_part += char
                elif char == "+" and depth == 0:
                    # Check if this is part of " + "
                    if (
                        i > 0
                        and expression[i - 1] == " "
                        and i < len(expression) - 1
                        and expression[i + 1] == " "
                    ):
                        # This is an addition operator
                        parts.append(current_part.strip())
                        current_part = ""
                        i += 1  # Skip the space after +
                    else:
                        current_part += char
                else:
                    current_part += char
            else:
                current_part += char

            i += 1

        if current_part.strip():
            parts.append(current_part.strip())

        return parts if parts else [expression]

    @staticmethod
    def split_let_expression(expression: str) -> Tuple[str, str]:
        """
        Split let expression into value part and rest part.

        Args:
            expression: The expression after 'let var = '

        Returns:
            Tuple of (value_expression, rest_expression)
        """
        # Look for patterns that likely end the value expression
        keywords = ["let", "for", "if"]

        # Try to find the next keyword that starts a new expression
        min_pos = len(expression)
        found_keyword = False

        for keyword in keywords:
            # Look for keyword preceded by whitespace (or at start)
            pattern = r"\s+(" + keyword + r")\s*[\(\w]"
            match = re.search(pattern, expression)
            if match and match.start() < min_pos:
                min_pos = match.start()
                found_keyword = True

        if found_keyword:
            value_expr = expression[:min_pos].strip()
            rest_expr = expression[min_pos:].strip()
        else:
            # If no keyword found, the entire expression is the value
            value_expr = expression.strip()
            rest_expr = ""

        return value_expr, rest_expr

    @staticmethod
    def is_string_literal(expression: str) -> bool:
        """Check if expression is a string literal."""
        return (expression.startswith('"') and expression.endswith('"')) or (
            expression.startswith("'") and expression.endswith("'")
        )

    @staticmethod
    def is_number_literal(expression: str) -> bool:
        """Check if expression is a number literal."""
        return bool(re.match(r"^-?\d+(\.\d+)?$", expression))

    @staticmethod
    def is_boolean_literal(expression: str) -> bool:
        """Check if expression is a boolean literal."""
        return expression in ("true", "false")

    @staticmethod
    def is_null_literal(expression: str) -> bool:
        """Check if expression is a null literal."""
        return expression == "null"
