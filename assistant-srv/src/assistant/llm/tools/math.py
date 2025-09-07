"""
Math tools for calculating expressions, converting units, and comparing numbers.
"""

import ast
import math
import operator
from typing import Any, Callable, Dict, List, Optional, Union

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from .base import ToolResult

# =============================================================================
# Input Parameter Models
# =============================================================================


class CalculateExpressionInput(BaseModel):
    """Mathematical expression calculation parameters."""

    expression: str = Field(description="The mathematical expression to evaluate")


class ConvertUnitsInput(BaseModel):
    """Unit conversion parameters."""

    value: float = Field(description="The numeric value to convert")
    from_unit: str = Field(description="The source unit")
    to_unit: str = Field(description="The target unit")


class CompareNumbersInput(BaseModel):
    """Number comparison parameters."""

    number_a: float = Field(description="The first number to compare")
    number_b: float = Field(description="The second number to compare")


# =============================================================================
# Safe Mathematical Expression Evaluator
# =============================================================================


class SafeMathEvaluator:
    """Safe evaluator for mathematical expressions."""

    # Supported operators
    operators: Dict[type, Callable[..., Any]] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.BitXor: operator.xor,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv,
    }

    # Supported functions
    functions: Dict[str, Callable[..., Any]] = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "pow": pow,
        # Trigonometric functions
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "atan2": math.atan2,
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        "asinh": math.asinh,
        "acosh": math.acosh,
        "atanh": math.atanh,
        # Additional math functions
        "sqrt": math.sqrt,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "degrees": math.degrees,
        "radians": math.radians,
        "ceil": math.ceil,
        "floor": math.floor,
    }

    # Math constants
    constants: Dict[str, float] = {
        "pi": 3.141592653589793,
        "e": 2.718281828459045,
    }

    def evaluate(self, node: ast.AST) -> Any:
        """Safely evaluate an AST node with comprehensive security checks."""
        # Security: Only allow specific AST node types for mathematical expressions
        allowed_node_types = {ast.Constant, ast.Name, ast.BinOp, ast.UnaryOp, ast.Call}

        if type(node) not in allowed_node_types:
            raise ValueError(
                f"Unsupported AST node type: {type(node).__name__}. " f"Only mathematical expressions are allowed."
            )

        if isinstance(node, ast.Constant):  # numbers
            return node.value
        elif isinstance(node, ast.Name):  # variables/constants
            if node.id in self.constants:
                return self.constants[node.id]
            else:
                raise ValueError(f"Unsupported variable: {node.id}. " f"Only predefined constants (pi, e) are allowed.")
        elif isinstance(node, ast.BinOp):  # binary operations
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            op = self.operators.get(type(node.op))
            if op is None:
                raise ValueError(
                    f"Unsupported operator: {type(node.op).__name__}. " f"Only basic arithmetic operators are allowed."
                )
            return op(left, right)
        elif isinstance(node, ast.UnaryOp):  # unary operations
            operand = self.evaluate(node.operand)
            op = self.operators.get(type(node.op))
            if op is None:
                raise ValueError(
                    f"Unsupported unary operator: {type(node.op).__name__}. " f"Only +/- unary operators are allowed."
                )
            return op(operand)
        elif isinstance(node, ast.Call):  # function calls
            if isinstance(node.func, ast.Name) and node.func.id in self.functions:
                func = self.functions[node.func.id]
                args = [self.evaluate(arg) for arg in node.args]
                return func(*args)
            else:
                func_name = getattr(node.func, "id", str(node.func))
                raise ValueError(
                    f"Unsupported function: {func_name}. " f"Only whitelisted mathematical functions are allowed."
                )
        else:
            # This should never be reached due to the check above, but kept for safety
            raise ValueError(f"Unsupported AST node: {type(node)}")

    def analyze_operations(self, node: ast.AST, operations_used: Optional[List[str]] = None) -> List[str]:
        """Analyze the AST to extract all operations and functions used in the expression."""
        if operations_used is None:
            operations_used = []

        if isinstance(node, ast.BinOp):
            # Binary operations
            bin_op_type: type[ast.AST] = type(node.op)
            if bin_op_type == ast.Add:
                operations_used.append("addition")
            elif bin_op_type == ast.Sub:
                operations_used.append("subtraction")
            elif bin_op_type == ast.Mult:
                operations_used.append("multiplication")
            elif bin_op_type == ast.Div:
                operations_used.append("division")
            elif bin_op_type == ast.Pow:
                operations_used.append("exponentiation")
            elif bin_op_type == ast.Mod:
                operations_used.append("modulo")
            elif bin_op_type == ast.FloorDiv:
                operations_used.append("floor_division")
            elif bin_op_type == ast.BitXor:
                operations_used.append("bitwise_xor")

            # Recursively analyze left and right operands
            self.analyze_operations(node.left, operations_used)
            self.analyze_operations(node.right, operations_used)

        elif isinstance(node, ast.UnaryOp):
            # Unary operations
            unary_op_type: type[ast.AST] = type(node.op)
            if unary_op_type == ast.USub:
                operations_used.append("unary_minus")
            elif unary_op_type == ast.UAdd:
                operations_used.append("unary_plus")
            self.analyze_operations(node.operand, operations_used)

        elif isinstance(node, ast.Call):
            # Function calls
            if isinstance(node.func, ast.Name) and node.func.id in self.functions:
                operations_used.append(f"function_{node.func.id}")
            # Analyze function arguments
            for arg in node.args:
                self.analyze_operations(arg, operations_used)

        elif isinstance(node, ast.Constant):
            # Constants (numbers) - no special operation needed
            pass

        elif isinstance(node, ast.Name):
            # Named constants (like pi, e)
            if node.id in self.constants:
                operations_used.append(f"constant_{node.id}")

        return list(set(operations_used))  # Remove duplicates and return


# =============================================================================
# Tool Implementations
# =============================================================================


@tool("math_calc", args_schema=CalculateExpressionInput)
def math_calc(expression: str) -> Dict[str, Any]:
    """
    Use it to calculate a mathematical expression safely using supported operations and functions.

    Supported operations: +, -, *, /, **, %, //
    Supported functions: abs, round, min, max, sum, pow, sin, cos, tan, asin, acos, atan, atan2,
                        sinh, cosh, tanh, asinh, acosh, atanh, sqrt, log, log10, exp,
                        degrees, radians, ceil, floor
    Supported constants: pi, e

    Examples:
        - "(2 + 3) * (4 - 1) / 2" -> 7.5
        - "round(3.14159, 2)" -> 3.14
        - "sin(pi/2)" -> 1.0

    Returns:
        Dictionary containing calculation results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'result': (float/int) The calculation result
          - 'expression': (string) The original expression
          - 'result_type': (string) Type of the result (int/float/bool)
          - 'operations_used': (list) List of operations detected in expression
        - 'error': (string, optional) Error message if calculation failed
    """
    try:
        # Parse the expression
        node = ast.parse(expression, mode="eval")

        # Evaluate safely
        evaluator = SafeMathEvaluator()
        result = evaluator.evaluate(node.body)

        # Determine result type
        result_type = type(result).__name__

        # Extract operations used (AST-based accurate detection)
        operations_used = evaluator.analyze_operations(node.body)

        return ToolResult.success(
            {"result": result, "expression": expression, "result_type": result_type, "operations_used": operations_used}
        ).model_dump()

    except Exception as e:
        return ToolResult.failure(f"Error calculating expression: {str(e)}").model_dump()


# Unit conversion mappings
UNIT_CONVERSIONS: Dict[str, Dict[str, float | str]] = {
    # Length conversions (base unit: meter)
    "length": {
        "mm": 0.001,
        "cm": 0.01,
        "m": 1.0,
        "km": 1000.0,
        "in": 0.0254,
        "ft": 0.3048,
        "yd": 0.9144,
        "mi": 1609.344,
    },
    # Weight conversions (base unit: kilogram)
    "weight": {
        "mg": 0.000001,
        "g": 0.001,
        "kg": 1.0,
        "oz": 0.0283495,
        "lb": 0.453592,
        "ton": 1000.0,
    },
    # Temperature conversions (special handling required)
    "temperature": {
        "celsius": "C",
        "fahrenheit": "F",
        "kelvin": "K",
        "c": "C",  # Celsius - restored for context-aware parsing
        "f": "F",
        "k": "K",
    },
    # Volume conversions (base unit: liter)
    "volume": {
        "ml": 0.001,
        "l": 1.0,
        "gal": 3.78541,
        "qt": 0.946353,
        "pt": 0.473176,
        "cup": 0.236588,
        "fl_oz": 0.0295735,
    },
    # Time conversions (base unit: second)
    "time": {
        "ms": 0.001,
        "s": 1.0,
        "min": 60.0,
        "h": 3600.0,
        "day": 86400.0,
        "week": 604800.0,
        "month": 2629746.0,  # average month
        "year": 31556952.0,  # average year
    },
    # Digital data conversions (base unit: byte)
    "data": {
        # Decimal (SI) prefixes
        "b": 1.0,  # byte
        "byte": 1.0,  # byte
        "bytes": 1.0,  # bytes
        "kb": 1000.0,  # kilobyte (decimal)
        "kilobyte": 1000.0,  # kilobyte (decimal)
        "mb": 1000000.0,  # megabyte (decimal)
        "megabyte": 1000000.0,  # megabyte (decimal)
        "gb": 1000000000.0,  # gigabyte (decimal)
        "gigabyte": 1000000000.0,  # gigabyte (decimal)
        "tb": 1000000000000.0,  # terabyte (decimal)
        "terabyte": 1000000000000.0,  # terabyte (decimal)
        "pb": 1000000000000000.0,  # petabyte (decimal)
        "petabyte": 1000000000000000.0,  # petabyte (decimal)
        # Binary (IEC) prefixes
        "kib": 1024.0,  # kibibyte
        "kibibyte": 1024.0,  # kibibyte
        "mib": 1048576.0,  # mebibyte
        "mebibyte": 1048576.0,  # mebibyte
        "gib": 1073741824.0,  # gibibyte
        "gibibyte": 1073741824.0,  # gibibyte
        "tib": 1099511627776.0,  # tebibyte
        "tebibyte": 1099511627776.0,  # tebibyte
        "pib": 1125899906842624.0,  # pebibyte
        "pebibyte": 1125899906842624.0,  # pebibyte
        # Bit conversions
        "bit": 0.125,  # 1/8 byte
        "bits": 0.125,  # 1/8 byte
        "kbit": 125.0,  # kilobit
        "mbit": 125000.0,  # megabit
        "gbit": 125000000.0,  # gigabit
    },
    # Area conversions (base unit: square meter)
    "area": {
        "mm2": 0.000001,  # square millimeter
        "cm2": 0.0001,  # square centimeter
        "m2": 1.0,  # square meter
        "km2": 1000000.0,  # square kilometer
        "in2": 0.00064516,  # square inch
        "ft2": 0.092903,  # square foot
        "yd2": 0.836127,  # square yard
        "acre": 4046.86,  # acre
        "hectare": 10000.0,  # hectare
        "mile2": 2589988.11,  # square mile
    },
    # Speed/Velocity conversions (base unit: meter per second)
    "speed": {
        "m/s": 1.0,  # meter per second
        "mps": 1.0,  # meter per second
        "km/h": 0.277778,  # kilometer per hour
        "kmh": 0.277778,  # kilometer per hour
        "mph": 0.44704,  # mile per hour
        "fps": 0.3048,  # foot per second
        "knot": 0.514444,  # knot (nautical mile per hour)
        "knots": 0.514444,  # knots
        "c": 299792458.0,  # speed of light (context-aware)
    },
    # Pressure conversions (base unit: pascal)
    "pressure": {
        "pa": 1.0,  # pascal
        "kpa": 1000.0,  # kilopascal
        "mpa": 1000000.0,  # megapascal
        "bar": 100000.0,  # bar
        "mbar": 100.0,  # millibar
        "psi": 6894.76,  # pound per square inch
        "psf": 47.8803,  # pound per square foot
        "atm": 101325.0,  # atmosphere
        "torr": 133.322,  # torr
        "mmhg": 133.322,  # millimeter of mercury
        "inhg": 3386.39,  # inch of mercury
    },
    # Energy conversions (base unit: joule)
    "energy": {
        "j": 1.0,  # joule
        "kj": 1000.0,  # kilojoule
        "mj": 1000000.0,  # megajoule
        "gj": 1000000000.0,  # gigajoule
        "cal": 4.184,  # calorie
        "kcal": 4184.0,  # kilocalorie
        "wh": 3600.0,  # watt-hour
        "kwh": 3600000.0,  # kilowatt-hour
        "mwh": 3600000000.0,  # megawatt-hour
        "btu": 1055.06,  # British thermal unit
        "ftlb": 1.35582,  # foot-pound
        "erg": 0.0000001,  # erg
    },
    # Power conversions (base unit: watt)
    "power": {
        "w": 1.0,  # watt
        "kw": 1000.0,  # kilowatt
        "mw": 1000000.0,  # megawatt
        "gw": 1000000000.0,  # gigawatt
        "hp": 745.7,  # horsepower (mechanical)
        "ps": 735.5,  # Pferdestärke (metric horsepower)
        "btu/h": 0.293071,  # BTU per hour
        "ftlb/s": 1.35582,  # foot-pound per second
        "cal/s": 4.184,  # calorie per second
    },
    # Frequency conversions (base unit: hertz)
    "frequency": {
        "hz": 1.0,  # hertz
        "khz": 1000.0,  # kilohertz
        "mhz": 1000000.0,  # megahertz
        "ghz": 1000000000.0,  # gigahertz
        "thz": 1000000000000.0,  # terahertz
        "rpm": 1 / 60.0,  # revolutions per minute
    },
}


def find_unit_category(unit: str) -> Union[str, None]:
    """Find which category a unit belongs to."""
    unit_lower = unit.lower()

    # Check all categories for the unit
    found_categories = []
    for category, units in UNIT_CONVERSIONS.items():
        if unit_lower in units:
            found_categories.append(category)

    # If only one category found, return it
    if len(found_categories) == 1:
        return found_categories[0]

    # If multiple categories found, return a special indicator for ambiguous units
    if len(found_categories) > 1:
        return "ambiguous"

    return None


def resolve_ambiguous_unit(unit: str, context_category: str) -> Union[str, None]:
    """Resolve ambiguous units based on context category."""
    unit_lower = unit.lower()

    if unit_lower == "c":
        if context_category == "temperature":
            return "temperature"
        elif context_category == "speed":
            return "speed"

    # For now, only handle "c" ambiguity. Could be extended for other ambiguous units
    return None


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """Convert temperature between different scales."""
    from_unit_mapped = UNIT_CONVERSIONS["temperature"].get(from_unit.lower(), from_unit.upper())
    to_unit_mapped = UNIT_CONVERSIONS["temperature"].get(to_unit.lower(), to_unit.upper())

    # Ensure both units are strings (not floats)
    if not isinstance(from_unit_mapped, str):
        from_unit_mapped = str(from_unit_mapped)
    if not isinstance(to_unit_mapped, str):
        to_unit_mapped = str(to_unit_mapped)

    # Convert to Celsius first
    if from_unit_mapped == "F":
        celsius = (value - 32) * 5 / 9
    elif from_unit_mapped == "K":
        celsius = value - 273.15
    else:  # Celsius
        celsius = value

    # Convert from Celsius to target
    if to_unit_mapped == "F":
        return celsius * 9 / 5 + 32
    elif to_unit_mapped == "K":
        return celsius + 273.15
    else:  # Celsius
        return celsius


@tool("local.math.convert_units", args_schema=ConvertUnitsInput)
def convert_units(value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
    """
    Convert a value from one unit to another across different measurement categories.

    Supported unit categories and their units:

    LENGTH (base unit: meter):
    - Millimeters: mm, cm, m, km
    - Imperial: in (inches), ft (feet), yd (yards), mi (miles)

    WEIGHT (base unit: kilogram):
    - Metric: mg (milligrams), g (grams), kg (kilograms), ton (metric tons)
    - Imperial: oz (ounces), lb (pounds)

    TEMPERATURE:
    - celsius, fahrenheit, kelvin (and their abbreviations: c, f, k)
    - Note: "c" is context-aware - when used with temperature units it means Celsius

    VOLUME (base unit: liter):
    - Metric: ml (milliliters), l (liters)
    - Imperial: gal (gallons), qt (quarts), pt (pints), cup, fl_oz (fluid ounces)

    TIME (base unit: second):
    - ms (milliseconds), s (seconds), min (minutes), h (hours)
    - day, week, month (average), year (average)

    DATA (base unit: byte):
    - Decimal (SI): b/byte/bytes, kb/kilobyte, mb/megabyte, gb/gigabyte, tb/terabyte, pb/petabyte
    - Binary (IEC): kib/kibibyte, mib/mebibyte, gib/gibibyte, tib/tebibyte, pib/pebibyte
    - Bits: bit/bits, kbit, mbit, gbit

    AREA (base unit: square meter):
    - Metric: mm2, cm2, m2, km2
    - Imperial: in2, ft2, yd2, acre, hectare, mile2

    SPEED (base unit: meter per second):
    - m/s, mps, km/h, kmh, mph, fps, knot/knots
    - Special: c (speed of light, context-aware)

    PRESSURE (base unit: pascal):
    - pa, kpa, mpa, bar, mbar, psi, psf, atm, torr, mmhg, inhg

    ENERGY (base unit: joule):
    - j, kj, mj, gj, cal, kcal, wh, kwh, mwh, btu, ftlb, erg

    POWER (base unit: watt):
    - w, kw, mw, gw, hp, ps, btu/h, ftlb/s, cal/s

    FREQUENCY (base unit: hertz):
    - hz, khz, mhz, ghz, thz, rpm

    Examples:
        - Convert 1000 meters to kilometers: (1000, "m", "km") -> 1.0
        - Convert 32°F to Celsius: (32, "fahrenheit", "celsius") -> 0.0
        - Convert 1GB to bytes: (1, "gb", "bytes") -> 1000000000.0
        - Convert 1GiB to bytes: (1, "gib", "bytes") -> 1073741824.0
        - Convert speed of light to mph: (1, "c", "mph") -> 670616629.0 (c means speed of light)

    Important notes:
    - Units are case-insensitive (e.g., "M", "m", "meter" all work)
    - Cannot convert between different categories (e.g., meters to kilograms)
    - Time conversions for month/year use average values
    - Data units support both decimal (SI) and binary (IEC) prefixes
    - Bit conversions are supported (1 byte = 8 bits)

    Returns:
        Dictionary containing unit conversion results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'converted_value': (float) The converted numeric value
          - 'original_value': (float) The original input value
          - 'from_unit': (string) Source unit
          - 'to_unit': (string) Target unit
          - 'category': (string) Unit category (length, weight, temperature, volume, time,
            data, area, speed, pressure, energy, power, frequency)
          - 'conversion_factor': (float) Factor used for conversion (None for temperature)
        - 'error': (string, optional) Error message if conversion failed
    """
    try:
        from_category = find_unit_category(from_unit)
        to_category = find_unit_category(to_unit)

        # Handle ambiguous units by using context from the other unit
        if from_category == "ambiguous":
            if to_category and to_category != "ambiguous":
                resolved_category = resolve_ambiguous_unit(from_unit, to_category)
                if resolved_category:
                    from_category = resolved_category
                else:
                    return ToolResult.failure(
                        f"Cannot resolve ambiguous unit '{from_unit}' in this context"
                    ).model_dump()
            else:
                return ToolResult.failure(
                    f"Ambiguous unit '{from_unit}' - please use more specific unit " "(celsius for temperature)"
                ).model_dump()

        if to_category == "ambiguous":
            if from_category and from_category != "ambiguous":
                resolved_category = resolve_ambiguous_unit(to_unit, from_category)
                if resolved_category:
                    to_category = resolved_category
                else:
                    return ToolResult.failure(f"Cannot resolve ambiguous unit '{to_unit}' in this context").model_dump()
            else:
                return ToolResult.failure(
                    f"Ambiguous unit '{to_unit}' - please use more specific unit " "(celsius for temperature)"
                ).model_dump()

        if from_category is None:
            return ToolResult.failure(f"Unknown unit '{from_unit}'").model_dump()
        if to_category is None:
            return ToolResult.failure(f"Unknown unit '{to_unit}'").model_dump()
        if from_category != to_category:
            return ToolResult.failure(f"Cannot convert between {from_category} and {to_category}").model_dump()

        # Special handling for temperature
        if from_category == "temperature":
            result = convert_temperature(value, from_unit, to_unit)
            conversion_factor = None  # Not applicable for temperature
        else:
            # Standard conversion through base unit
            from_factor = UNIT_CONVERSIONS[from_category][from_unit.lower()]
            to_factor = UNIT_CONVERSIONS[to_category][to_unit.lower()]
            # Ensure both factors are floats for arithmetic
            if not isinstance(from_factor, float) or not isinstance(to_factor, float):
                raise ValueError(
                    f"Cannot convert units: '{from_unit}' or '{to_unit}' is not a numeric conversion factor."
                )
            conversion_factor = from_factor / to_factor
            result = value * conversion_factor

        return ToolResult.success(
            {
                "converted_value": result,
                "original_value": value,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "category": from_category,
                "conversion_factor": conversion_factor,
            }
        ).model_dump()

    except Exception as e:
        return ToolResult.failure(f"Error converting units: {str(e)}").model_dump()


@tool("local.math.compare_numbers", args_schema=CompareNumbersInput)
def compare_numbers(number_a: float, number_b: float) -> Dict[str, Any]:
    """
    Compare two numbers and analyze their mathematical relationship.

    Returns:
        Dictionary containing number comparison results:
        - 'status': (string) Operation status ('success' or 'error')
        - 'data': (dict) Result data containing:
          - 'relationship': (string) Relationship description (greater, less, equal)
          - 'difference': (float) Absolute difference between numbers
          - 'percentage_difference': (float) Percentage difference
          - 'ratio': (float) Ratio of number_a to number_b
          - 'number_a': (float) First number
          - 'number_b': (float) Second number
          - 'larger_number': (float) The larger of the two numbers
          - 'smaller_number': (float) The smaller of the two numbers
        - 'error': (string, optional) Error message if comparison failed
    """
    try:
        # Calculate basic relationship
        if number_a > number_b:
            relationship = "greater"
            larger_number = number_a
            smaller_number = number_b
        elif number_a < number_b:
            relationship = "less"
            larger_number = number_b
            smaller_number = number_a
        else:
            relationship = "equal"
            larger_number = number_a
            smaller_number = number_b

        # Calculate metrics
        difference = abs(number_a - number_b)

        # Avoid division by zero for percentage and ratio
        if number_b != 0:
            percentage_difference = (difference / abs(number_b)) * 100
            ratio = number_a / number_b
        else:
            percentage_difference = float("inf") if difference > 0 else 0
            ratio = float("inf") if number_a > 0 else (float("-inf") if number_a < 0 else float("nan"))

        return ToolResult.success(
            {
                "relationship": relationship,
                "difference": difference,
                "percentage_difference": percentage_difference,
                "ratio": ratio,
                "number_a": number_a,
                "number_b": number_b,
                "larger_number": larger_number,
                "smaller_number": smaller_number,
            }
        ).model_dump()

    except Exception as e:
        return ToolResult.failure(f"Error comparing numbers: {str(e)}").model_dump()
