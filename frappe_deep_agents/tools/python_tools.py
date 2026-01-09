"""
Python execution tools for agents.
"""
from typing import Optional, Any
from langchain.tools import BaseTool
from pydantic import Field
import sys
import io
import traceback
import contextlib


class PythonREPLTool(BaseTool):
    """
    Execute Python code in a sandboxed environment.

    This tool allows agents to run Python code for calculations,
    data processing, and other computational tasks.
    """
    name: str = "python_repl"
    description: str = """Execute Python code and return the result.

Use this tool when you need to:
- Perform calculations
- Process data with Python
- Test code snippets
- Generate outputs programmatically

Input: Python code as a string (can be multiline)

The code runs in a restricted environment. Some modules may not be available.
The last expression's value is returned, or print() output if no expression.

Examples:
- "2 + 2 * 10"
- "import math; math.sqrt(144)"
- "[x**2 for x in range(10)]"
- '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

[fibonacci(i) for i in range(10)]
'''
"""

    session_id: Optional[str] = Field(default=None, exclude=True)
    sandbox: Any = Field(default=None, exclude=True)
    sandbox_pod: Optional[str] = Field(default=None, exclude=True)
    _globals: dict = {}
    _locals: dict = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize with safe builtins
        self._globals = {
            '__builtins__': {
                'abs': abs, 'all': all, 'any': any, 'bin': bin, 'bool': bool,
                'chr': chr, 'dict': dict, 'dir': dir, 'divmod': divmod,
                'enumerate': enumerate, 'filter': filter, 'float': float,
                'format': format, 'frozenset': frozenset, 'getattr': getattr,
                'hasattr': hasattr, 'hash': hash, 'hex': hex, 'id': id,
                'int': int, 'isinstance': isinstance, 'issubclass': issubclass,
                'iter': iter, 'len': len, 'list': list, 'map': map, 'max': max,
                'min': min, 'next': next, 'oct': oct, 'ord': ord, 'pow': pow,
                'print': print, 'range': range, 'repr': repr, 'reversed': reversed,
                'round': round, 'set': set, 'slice': slice, 'sorted': sorted,
                'str': str, 'sum': sum, 'tuple': tuple, 'type': type, 'zip': zip,
                '__import__': self._safe_import,
                'True': True, 'False': False, 'None': None,
            }
        }
        self._locals = {}

    def _safe_import(self, name, *args, **kwargs):
        """Restricted import that only allows safe modules."""
        safe_modules = {
            'math', 'random', 'datetime', 'json', 're', 'collections',
            'itertools', 'functools', 'operator', 'string', 'textwrap',
            'decimal', 'fractions', 'statistics', 'copy', 'pprint',
            'hashlib', 'base64', 'urllib.parse', 'html', 'uuid'
        }

        if name in safe_modules or name.split('.')[0] in safe_modules:
            return __import__(name, *args, **kwargs)
        else:
            raise ImportError(f"Module '{name}' is not allowed for security reasons")

    def _run(self, code: str) -> str:
        """Execute Python code."""
        # If we have a sandbox, execute there
        if self.sandbox and self.sandbox_pod:
            return self._run_in_sandbox(code)

        # Otherwise, run locally in restricted environment
        return self._run_local(code)

    def _run_local(self, code: str) -> str:
        """Execute code locally in restricted environment."""
        try:
            # Capture stdout
            stdout_capture = io.StringIO()

            with contextlib.redirect_stdout(stdout_capture):
                # Try to evaluate as expression first
                try:
                    result = eval(code, self._globals, self._locals)
                    if result is not None:
                        stdout_capture.write(repr(result))
                except SyntaxError:
                    # Not an expression, execute as statements
                    exec(code, self._globals, self._locals)

            output = stdout_capture.getvalue()

            if not output:
                return "Code executed successfully (no output)"

            # Truncate if too long
            if len(output) > 5000:
                output = output[:5000] + "\n... (output truncated)"

            return output

        except Exception as e:
            # Get traceback but limit to relevant parts
            tb = traceback.format_exc()
            # Remove internal frames
            lines = tb.split('\n')
            filtered = [l for l in lines if 'python_tools.py' not in l]
            return f"Error: {str(e)}\n\n" + '\n'.join(filtered[-10:])

    def _run_in_sandbox(self, code: str) -> str:
        """Execute code in Kubernetes sandbox."""
        try:
            # Create a temporary Python script
            script = f'''
import sys
import json

try:
    # Execute the code
    result = None
    exec_globals = {{}}
    exec_locals = {{}}

    code = {repr(code)}

    try:
        result = eval(code, exec_globals, exec_locals)
        if result is not None:
            print(repr(result))
    except SyntaxError:
        exec(code, exec_globals, exec_locals)

except Exception as e:
    import traceback
    print(f"Error: {{e}}")
    traceback.print_exc()
'''
            # Execute in sandbox
            result = self.sandbox.exec_command(
                f"python3 -c {repr(script)}",
                pod_name=self.sandbox_pod
            )

            stdout = result.get('stdout', '')
            stderr = result.get('stderr', '')

            if stderr:
                return f"Output:\n{stdout}\n\nErrors:\n{stderr}"

            if not stdout:
                return "Code executed successfully (no output)"

            return stdout

        except Exception as e:
            return f"Sandbox execution error: {str(e)}"


class PythonCalculatorTool(BaseTool):
    """
    Simple calculator for mathematical expressions.
    """
    name: str = "calculator"
    description: str = """Evaluate a mathematical expression.

Use this tool for simple calculations. Supports:
- Basic arithmetic: +, -, *, /, //, %, **
- Functions: sqrt, sin, cos, tan, log, exp, abs, round, etc.

Input: A mathematical expression as a string

Examples:
- "2 + 2 * 10"
- "sqrt(144) + pow(2, 10)"
- "(100 - 20) / 4"
"""

    session_id: Optional[str] = Field(default=None, exclude=True)

    def _run(self, expression: str) -> str:
        """Evaluate mathematical expression."""
        import math

        # Create safe namespace with math functions
        safe_dict = {
            'abs': abs, 'round': round, 'min': min, 'max': max,
            'sum': sum, 'pow': pow,
            'sqrt': math.sqrt, 'log': math.log, 'log10': math.log10,
            'exp': math.exp, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
            'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
            'ceil': math.ceil, 'floor': math.floor,
            'pi': math.pi, 'e': math.e,
            'factorial': math.factorial, 'gcd': math.gcd,
        }

        try:
            # Clean expression
            expr = expression.strip()

            # Evaluate safely
            result = eval(expr, {"__builtins__": {}}, safe_dict)

            return str(result)

        except ZeroDivisionError:
            return "Error: Division by zero"
        except ValueError as e:
            return f"Math error: {str(e)}"
        except SyntaxError as e:
            return f"Syntax error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
