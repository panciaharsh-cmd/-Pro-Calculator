
import ast
import operator
import re

from kivy.app import App
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex


# Dark theme
Window.clearcolor = get_color_from_hex("#101116")


# Safe mathematical evaluator
def calculate(expression):

    allowed = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def solve(node):

        if isinstance(node, ast.Expression):
            return solve(node.body)

        if isinstance(node, ast.Constant):
            if type(node.value) in (int, float):
                return node.value
            raise ValueError("Invalid number")

        if isinstance(node, ast.BinOp):
            op = type(node.op)

            if op not in allowed:
                raise ValueError("Invalid operator")

            a = solve(node.left)
            b = solve(node.right)

            if op == ast.Div and b == 0:
                raise ZeroDivisionError

            return allowed[op](a, b)

        if isinstance(node, ast.UnaryOp):
            op = type(node.op)

            if op not in allowed:
                raise ValueError("Invalid operator")

            return allowed[op](solve(node.operand))

        raise ValueError("Invalid expression")

    if len(expression) > 100:
        raise ValueError("Expression too long")

    tree = ast.parse(expression, mode="eval")
    result = solve(tree)

    if isinstance(result, float):
        if result != result or abs(result) == float("inf"):
            raise ValueError("Invalid result")

    return result


class Calculator(App):

    def build(self):

        self.title = "Pro Calculator"
        self.expression = ""
        self.just_calculated = False

        main = BoxLayout(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(12)
        )

        # Header
        header = Label(
            text="[b]PRO CALCULATOR[/b]",
            markup=True,
            font_size=sp(21),
            color=get_color_from_hex("#FFFFFF"),
            size_hint_y=0.12
        )

        main.add_widget(header)

        # Display
        display_box = BoxLayout(
            orientation="vertical",
            size_hint_y=0.27,
            padding=dp(10)
        )

        self.history = Label(
            text="Ready",
            font_size=sp(15),
            color=get_color_from_hex("#888888"),
            halign="right",
            valign="middle",
            size_hint_y=0.35
        )

        self.display = Label(
            text="0",
            font_size=sp(38),
            color=get_color_from_hex("#FFFFFF"),
            halign="right",
            valign="middle",
            size_hint_y=0.65
        )

        self.display.bind(size=self.update_text_size)
        self.history.bind(size=self.update_history_size)

        display_box.add_widget(self.history)
        display_box.add_widget(self.display)

        main.add_widget(display_box)

        # Buttons
        grid = GridLayout(
            cols=4,
            spacing=dp(9),
            size_hint_y=0.61
        )

        buttons = [
            ["AC", "DEL", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "−"],
            ["1", "2", "3", "+"],
            ["(", "0", ".", ")"]
        ]

        for row in buttons:
            for value in row:

                btn = Button(
                    text=value,
                    font_size=sp(23),
                    bold=True,
                    background_normal="",
                    background_down="",
                    background_color=self.button_color(value),
                    color=get_color_from_hex("#FFFFFF")
                )

                btn.bind(on_press=self.press)
                grid.add_widget(btn)

        main.add_widget(grid)

        # Equal button
        equal = Button(
            text="=",
            font_size=sp(30),
            bold=True,
            size_hint_y=0.12,
            background_normal="",
            background_down="",
            background_color=get_color_from_hex("#FF9F0A"),
            color=get_color_from_hex("#FFFFFF")
        )

        equal.bind(on_press=self.press)
        main.add_widget(equal)

        return main

    def update_text_size(self, instance, size):
        instance.text_size = size

    def update_history_size(self, instance, size):
        instance.text_size = size

    def button_color(self, value):

        if value in ["AC", "DEL"]:
            return get_color_from_hex("#41434D")

        if value in ["%", "÷", "×", "−", "+", "(", ")"]:
            return get_color_from_hex("#FF9F0A")

        return get_color_from_hex("#252832")

    def press(self, instance):

        value = instance.text

        if value == "AC":
            self.expression = ""
            self.display.text = "0"
            self.history.text = "Ready"
            self.just_calculated = False
            return

        if value == "DEL":
            self.expression = self.expression[:-1]
            self.show_expression()
            self.just_calculated = False
            return

        if value == "=":
            self.solve()
            return

        if value == "%":
            if self.expression and self.expression[-1].isdigit():
                self.expression += "/100"
            self.show_expression()
            self.just_calculated = False
            return

        if self.just_calculated:

            if value.isdigit() or value == "." or value == "(":
                self.expression = ""
            self.just_calculated = False

        operators = ["+", "-", "*", "/"]

        if value in ["+", "−", "×", "÷"]:

            if not self.expression:
                if value != "−":
                    return

            if self.expression and self.expression[-1] in operators:
                self.expression = self.expression[:-1]

        symbols = {
            "×": "*",
            "÷": "/",
            "−": "-"
        }

        self.expression += symbols.get(value, value)

        self.show_expression()

    def show_expression(self):

        if self.expression:
            text = self.expression.replace(
                "*", "×"
            ).replace("/", "÷").replace("-", "−")

            self.display.text = text
        else:
            self.display.text = "0"

    def solve(self):

        if not self.expression:
            return

        try:
            old = self.expression

            result = calculate(old)

            if isinstance(result, float):
                result = round(result, 10)

            self.history.text = (
                old.replace("*", "×")
                .replace("/", "÷")
                + " ="
            )

            self.expression = str(result)
            self.display.text = str(result)

            self.just_calculated = True

        except ZeroDivisionError:
            self.display.text = "Cannot divide by 0"
            self.expression = ""
            self.just_calculated = True

        except Exception:
            self.display.text = "Error"
            self.expression = ""
            self.just_calculated = True


if __name__ == "__main__":
    Calculator().run()
