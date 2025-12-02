import re
import json
import time
from typing import Any, Dict, List, Optional, Union
from app.models.transform import TransformResponse, JSLTValidationResponse


class JSLTService:
    """Custom JSLT interpreter for JSON transformations."""

    def __init__(self):
        self.functions = {
            "size": self._size,
            "string": self._string,
            "number": self._number,
            "boolean": self._boolean,
            "round": self._round,
        }
        self.variables = {}  # Global variable context

    def transform(
        self, input_json: Dict[str, Any], jslt_expression: str
    ) -> TransformResponse:
        """Transform JSON using JSLT expression."""
        start_time = time.perf_counter()

        try:
            # Reset variables for each transform
            self.variables = {}
            result = self._evaluate_expression(jslt_expression.strip(), input_json, {})
            execution_time = (time.perf_counter() - start_time) * 1000

            return TransformResponse(
                success=True, output=result, execution_time_ms=round(execution_time, 3)
            )
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            return TransformResponse(
                success=False, error=str(e), execution_time_ms=round(execution_time, 3)
            )

    def validate_jslt(self, jslt_expression: str) -> JSLTValidationResponse:
        """Validate JSLT expression syntax."""
        # TODO: Implement more thorough syntax checking
        try:
            # Try to parse the expression with a more comprehensive dummy input
            test_input = {
                "test": "value",
                "array": [1, 2, 3],
                "name": "John Doe",
                "age": 25,
                "city": "New York",
                "skills": ["JavaScript", "Python", "Java"]
            }
            self.variables = {}  # Reset variables for validation
            self._evaluate_expression(jslt_expression.strip(), test_input, {})
            return JSLTValidationResponse(valid=True)
        except Exception as e:
            return JSLTValidationResponse(
                valid=False, error=str(e), suggestions=self._get_suggestions(str(e))
            )

    def _evaluate_expression(
        self, expression: str, context: Any, variables: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Evaluate a JSLT expression in the given context."""
        if variables is None:
            variables = {}

        expression = expression.strip()

        if not expression:
            return None

        # Handle multi-line expressions with let statements
        if "let " in expression and "\n" in expression:
            return self._evaluate_multiline_expression(expression, context, variables)

        # Handle let statements
        if expression.startswith("let "):
            return self._evaluate_let_statement(expression, context, variables)

        # Handle variable references
        if expression.startswith("$"):
            # Extract just the variable name (up to first non-alphanumeric character)
            var_match = re.match(r"^\$(\w+)", expression)
            if var_match:
                var_name = var_match.group(1)
                if var_name in variables:
                    return variables[var_name]
                elif var_name in self.variables:
                    return self.variables[var_name]
                else:
                    raise ValueError(f"Undefined variable: ${var_name}")
            else:
                raise ValueError(f"Invalid variable reference: {expression}")

        # Handle string/number concatenation/addition (before string literals)
        if " + " in expression:
            return self._evaluate_addition(expression, context, variables)

        # Handle object construction
        if expression.startswith("{") and expression.endswith("}"):
            return self._evaluate_object(expression, context, variables)

        # Handle array construction
        if expression.startswith("[") and expression.endswith("]"):
            return self._evaluate_array(expression, context, variables)

        # Handle string literals
        if (expression.startswith('"') and expression.endswith('"')) or (
            expression.startswith("'") and expression.endswith("'")
        ):
            return expression[1:-1]

        # Handle number literals
        if re.match(r"^-?\d+(\.\d+)?$", expression):
            return float(expression) if "." in expression else int(expression)

        # Handle boolean literals
        if expression == "true":
            return True
        if expression == "false":
            return False
        if expression == "null":
            return None

        # Handle for loops
        if expression.startswith("for"):
            return self._evaluate_for_loop(expression, context, variables)

        # Handle if expressions
        if expression.startswith("if"):
            return self._evaluate_if_expression(expression, context, variables)

        # Handle function calls
        func_match = re.match(r"^(\w+)\s*\(([^)]*)\)$", expression)
        if func_match:
            func_name, args_str = func_match.groups()
            return self._evaluate_function(func_name, args_str, context, variables)

        # Handle comparison operations
        if " >= " in expression:
            return self._evaluate_comparison(expression, context, ">=", variables)
        if " <= " in expression:
            return self._evaluate_comparison(expression, context, "<=", variables)
        if " > " in expression:
            return self._evaluate_comparison(expression, context, ">", variables)
        if " < " in expression:
            return self._evaluate_comparison(expression, context, "<", variables)
        if " == " in expression:
            return self._evaluate_comparison(expression, context, "==", variables)
        if " != " in expression:
            return self._evaluate_comparison(expression, context, "!=", variables)

        # Handle path expressions
        if expression.startswith("."):
            return self._evaluate_path(expression, context)

        raise ValueError(f"Invalid expression: {expression}")

    def _evaluate_let_statement(
        self, expression: str, context: Any, variables: Dict[str, Any]
    ) -> Any:
        """Evaluate let statement and return the rest of the expression."""
        # Check for "let var = value in expression" syntax first
        in_match = re.match(
            r"^let\s+(\w+)\s*=\s*(.+?)\s+in\s+(.+)$", expression, re.DOTALL
        )
        if in_match:
            var_name, value_expr, rest_expr = in_match.groups()

            # Evaluate the value expression
            value = self._evaluate_expression(value_expr.strip(), context, variables)

            # Store in local variables (takes precedence over global)
            new_variables = variables.copy()
            new_variables[var_name] = value

            # Evaluate the rest expression with the new variable
            return self._evaluate_expression(rest_expr.strip(), context, new_variables)

        # Fallback to the original approach for backward compatibility
        let_match = re.match(r"^let\s+(\w+)\s*=\s*", expression)
        if not let_match:
            raise ValueError(
                "Invalid let syntax. Use: let variable = expression in expression"
            )

        var_name = let_match.group(1)
        after_equals = expression[let_match.end() :]

        # Find where the value expression ends
        value_expr, rest_expr = self._split_let_expression(after_equals)

        # Evaluate the value expression
        value = self._evaluate_expression(value_expr.strip(), context, variables)

        # Store in local variables (takes precedence over global)
        new_variables = variables.copy()
        new_variables[var_name] = value

        # If there's more expression after the let, evaluate it with the new variable
        if rest_expr and rest_expr.strip():
            return self._evaluate_expression(rest_expr.strip(), context, new_variables)

        # If it's just a let statement, return the value
        return value

    def _evaluate_object(
        self, expression: str, context: Any, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Evaluate object construction."""
        if variables is None:
            variables = {}

        content = expression[1:-1].strip()
        if not content:
            return {}

        # TODO: Handle let statements in object construction in future

        result = {}
        pairs = self._split_object_pairs(content)

        for pair in pairs:
            if ":" not in pair:
                raise ValueError(f"Invalid object pair: {pair}")

            key_part, value_part = pair.split(":", 1)
            key = key_part.strip()

            # Remove quotes from key if present
            if key.startswith('"') and key.endswith('"'):
                key = key[1:-1]
            elif key.startswith("'") and key.endswith("'"):
                key = key[1:-1]

            value = self._evaluate_expression(value_part.strip(), context, variables)
            result[key] = value

        return result

    def _evaluate_multiline_expression(
        self, expression: str, context: Any, variables: Dict[str, Any]
    ) -> Any:
        """Evaluate multi-line expression with let statements."""
        lines = expression.split('\n')
        current_variables = variables.copy()

        # Process let statements first
        let_statements = []
        object_lines = []

        for line in lines:
            line = line.strip()
            if line.startswith("let "):
                let_statements.append(line)
            elif line:
                object_lines.append(line)

        # Evaluate let statements
        for let_stmt in let_statements:
            let_match = re.match(r"^let\s+(\w+)\s*=\s*(.+)$", let_stmt)
            if let_match:
                var_name, value_expr = let_match.groups()
                value = self._evaluate_expression(value_expr.strip(), context, current_variables)
                current_variables[var_name] = value

        # Evaluate the remaining expression (usually an object)
        remaining_expr = '\n'.join(object_lines)
        if remaining_expr:
            return self._evaluate_expression(remaining_expr, context, current_variables)

        return None

    def _evaluate_array(
        self, expression: str, context: Any, variables: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """Evaluate array construction."""
        if variables is None:
            variables = {}

        content = expression[1:-1].strip()
        if not content:
            return []

        elements = self._split_array_elements(content)
        return [
            self._evaluate_expression(elem.strip(), context, variables)
            for elem in elements
        ]

    def _evaluate_path(self, path: str, context: Any) -> Any:
        """Evaluate path expression like .field or .array[0]."""
        if path == ".":
            return context

        path = path[1:]  # Remove leading dot
        current = context

        # Handle path with array indexing
        while path:
            # Check for array indexing
            array_match = re.match(r"^([^.\[]+)\[(\d+)\](.*)$", path)
            if array_match:
                field_name, index_str, remaining = array_match.groups()

                # Get the field
                if isinstance(current, dict):
                    current = current.get(field_name)
                    if current is None:
                        return None
                else:
                    return None

                # Apply array index
                index = int(index_str)
                if isinstance(current, list) and 0 <= index < len(current):
                    current = current[index]
                else:
                    return None

                # Continue with remaining path
                path = remaining.lstrip(".")
                continue

            # Check for field access
            dot_pos = path.find(".")
            bracket_pos = path.find("[")

            if dot_pos == -1 and bracket_pos == -1:
                # Last field
                if isinstance(current, dict):
                    return current.get(path)
                else:
                    return None

            # Find next separator
            next_sep = float("inf")
            if dot_pos != -1:
                next_sep = min(next_sep, dot_pos)
            if bracket_pos != -1:
                next_sep = min(next_sep, bracket_pos)

            if next_sep == float("inf"):
                # Single field remaining
                if isinstance(current, dict):
                    return current.get(path)
                else:
                    return None

            # Extract field name up to next separator
            field_name = path[:next_sep]
            if isinstance(current, dict):
                current = current.get(field_name)
                if current is None:
                    return None
            else:
                return None

            # Update path
            if next_sep == dot_pos:
                path = path[dot_pos + 1 :]
            else:
                path = path[bracket_pos:]

        return current

    def _evaluate_function(
        self,
        func_name: str,
        args_str: str,
        context: Any,
        variables: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Evaluate function call."""
        if variables is None:
            variables = {}

        if func_name not in self.functions:
            raise ValueError(f"Unknown function: {func_name}")

        args = []
        if args_str.strip():
            arg_expressions = self._split_function_args(args_str)
            args = [
                self._evaluate_expression(arg.strip(), context, variables)
                for arg in arg_expressions
            ]

        return self.functions[func_name](*args)

    def _evaluate_comparison(
        self,
        expression: str,
        context: Any,
        operator: str,
        variables: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Evaluate comparison expression."""
        if variables is None:
            variables = {}

        left_expr, right_expr = expression.split(f" {operator} ", 1)
        left_val = self._evaluate_expression(left_expr.strip(), context, variables)
        right_val = self._evaluate_expression(right_expr.strip(), context, variables)

        # Handle null/None values
        if operator == "==":
            return left_val == right_val
        elif operator == "!=":
            return left_val != right_val

        # For ordering operators, treat None as falsy in comparisons
        # This follows common behavior where null < any number is false
        if left_val is None or right_val is None:
            return False

        # Both values are not None, proceed with comparison
        try:
            if operator == ">=":
                return left_val >= right_val
            elif operator == "<=":
                return left_val <= right_val
            elif operator == ">":
                return left_val > right_val
            elif operator == "<":
                return left_val < right_val
        except TypeError:
            # If types are incompatible for comparison, return False
            return False

        return False

    def _evaluate_addition(
        self, expression: str, context: Any, variables: Optional[Dict[str, Any]] = None
    ) -> Union[str, int, float]:
        """Evaluate addition/concatenation expression."""
        if variables is None:
            variables = {}

        # Split by " + " but be careful with nested expressions
        parts = self._split_addition_parts(expression)
        if len(parts) == 1:
            return self._evaluate_expression(parts[0].strip(), context, variables)

        # Evaluate all parts
        values = []
        for part in parts:
            val = self._evaluate_expression(part.strip(), context, variables)
            values.append(val)

        # If any value is a string, do string concatenation
        if any(isinstance(v, str) for v in values):
            result = ""
            for val in values:
                result += str(val if val is not None else "")
            return result

        # If all are numbers, do numeric addition
        if all(isinstance(v, (int, float)) for v in values if v is not None):
            result = 0
            for val in values:
                if val is not None:
                    result += val
            return result

        # Default: string concatenation
        result = ""
        for val in values:
            result += str(val if val is not None else "")
        return result

    def _evaluate_for_loop(
        self, expression: str, context: Any, variables: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """Evaluate for loop expression."""
        if variables is None:
            variables = {}

        # Pattern: for (array_expr) loop_expr
        match = re.match(r"for\s*\(\s*([^)]+)\s*\)\s*(.+)", expression)
        if not match:
            raise ValueError("Invalid for loop syntax")

        array_expr, loop_expr = match.groups()
        array_value = self._evaluate_expression(array_expr.strip(), context, variables)

        if not isinstance(array_value, list):
            raise ValueError("For loop requires an array")

        results = []
        for item in array_value:
            result = self._evaluate_expression(loop_expr.strip(), item, variables)
            results.append(result)

        return results

    def _evaluate_if_expression(
        self, expression: str, context: Any, variables: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Evaluate if-then-else expression."""
        if variables is None:
            variables = {}

        # Pattern: if (condition) then_expr else else_expr
        match = re.match(r"if\s*\(\s*([^)]+)\s*\)\s*(.+?)\s+else\s+(.+)", expression)
        if not match:
            raise ValueError("Invalid if expression syntax")

        condition_expr, then_expr, else_expr = match.groups()
        condition = self._evaluate_expression(
            condition_expr.strip(), context, variables
        )

        if condition:
            return self._evaluate_expression(then_expr.strip(), context, variables)
        else:
            return self._evaluate_expression(else_expr.strip(), context, variables)

    def _split_object_pairs(self, content: str) -> List[str]:
        """Split object content into key-value pairs."""
        pairs = []
        current_pair = ""
        depth = 0
        in_string = False
        string_char = None

        for char in content:
            if not in_string and char in "\"'":
                in_string = True
                string_char = char
            elif in_string and char == string_char:
                in_string = False
                string_char = None
            elif not in_string:
                if char in "{[":
                    depth += 1
                elif char in "}]":
                    depth -= 1
                elif char == "," and depth == 0:
                    pairs.append(current_pair.strip())
                    current_pair = ""
                    continue

            current_pair += char

        if current_pair.strip():
            pairs.append(current_pair.strip())

        return pairs

    def _split_array_elements(self, content: str) -> List[str]:
        """Split array content into elements."""
        elements = []
        current_element = ""
        depth = 0
        in_string = False
        string_char = None

        for char in content:
            if not in_string and char in "\"'":
                in_string = True
                string_char = char
            elif in_string and char == string_char:
                in_string = False
                string_char = None
            elif not in_string:
                if char in "{[":
                    depth += 1
                elif char in "}]":
                    depth -= 1
                elif char == "," and depth == 0:
                    elements.append(current_element.strip())
                    current_element = ""
                    continue

            current_element += char

        if current_element.strip():
            elements.append(current_element.strip())

        return elements

    def _split_function_args(self, args_str: str) -> List[str]:
        """Split function arguments."""
        args = []
        current_arg = ""
        depth = 0
        in_string = False
        string_char = None

        for char in args_str:
            if not in_string and char in "\"'":
                in_string = True
                string_char = char
            elif in_string and char == string_char:
                in_string = False
                string_char = None
            elif not in_string:
                if char in "{[(":
                    depth += 1
                elif char in "}])":
                    depth -= 1
                elif char == "," and depth == 0:
                    args.append(current_arg.strip())
                    current_arg = ""
                    continue

            current_arg += char

        if current_arg.strip():
            args.append(current_arg.strip())

        return args

    def _split_let_expression(self, expression: str) -> tuple[str, str]:
        """Split let expression into value part and rest part."""
        # For simple cases, try to find common delimiters that separate expressions
        # This is a simplified approach - a full parser would be more robust

        # Look for patterns that likely end the value expression
        # Priority: keywords like 'let', 'for', 'if' at the beginning of words
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

    def _split_addition_parts(self, expression: str) -> List[str]:
        """Split addition expression into parts, respecting string literals and nested expressions."""
        parts = []
        current_part = ""
        in_string = False
        string_char = None
        depth = 0
        i = 0

        while i < len(expression):
            char = expression[i]

            if not in_string and char in "\"'":
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

    def _get_suggestions(self, error_msg: str) -> List[str]:
        """Get suggestions based on error message."""
        suggestions = []

        if "Unknown function" in error_msg:
            suggestions.append(
                "Available functions: size(), string(), number(), boolean(), round()"
            )

        if "Invalid expression" in error_msg:
            suggestions.extend(
                [
                    "Use .field to access object properties",
                    "Use .array[0] to access array elements",
                    "Use {} for object construction",
                    "Use [] for array construction",
                ]
            )

        return suggestions

    # Built-in functions
    def _size(self, value: Any) -> int:
        """Get size of array, object, or string."""
        if isinstance(value, (list, dict, str)):
            return len(value)
        return 0

    def _string(self, value: Any) -> str:
        """Convert value to string."""
        if value is None:
            return ""
        return str(value)

    def _number(self, value: Any) -> Union[int, float]:
        """Convert value to number."""
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            try:
                return int(value) if value.isdigit() else float(value)
            except ValueError:
                return 0
        return 0

    def _boolean(self, value: Any) -> bool:
        """Convert value to boolean."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        if isinstance(value, (int, float)):
            return value != 0
        return bool(value)

    def _round(self, value: Union[int, float]) -> int:
        """Round number to nearest integer."""
        return round(float(value))
