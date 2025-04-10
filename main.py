import sys

def create_context(variables, functions):
    context = {}
    for var, (typ, val) in variables.items():
        context[var] = val
    for func, (args, expr) in functions.items():
        context[func] = lambda *vals: eval(expr, dict(zip(args, vals)))
    return context

def process_instructions(filename):
    variables = {}  # {имя: (тип, значение)}
    functions = {}  # {имя: (список_аргументов, выражение)}

    try:
        with open(filename, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Ошибка: файл {filename} не найден")
        return

    instructions = [instr.strip() for instr in content.split(';') if instr.strip()]

    for instr in instructions:
        instr = instr.strip()

        if ':' in instr:
            name_args, expr = instr.split(':', 1)
            expr = expr.strip()
            name_args = name_args.strip()
            if '(' not in name_args or ')' not in name_args:
                print(f"Ошибка: неверное определение функции: {instr}")
                continue
            name = name_args.split('(')[0].strip()
            args_str = name_args.split('(')[1].split(')')[0].strip()
            args = [arg.strip() for arg in args_str.split(',')] if args_str else []
            functions[name] = (args, expr)

        elif '=' in instr:
            left, right = instr.split('=', 1)
            left = left.strip()
            right = right.strip()

            if '(' in left and ')' in left:
                var_type_str = left.split('(')[1].split(')')[0].strip()
                var_name = left.split('(')[0].strip()
                if var_type_str not in ['i', 'f']:
                    print(f"Ошибка: неверный тип {var_type_str} для переменной {var_name}")
                    continue
                try:
                    value = eval(right, create_context(variables, functions))
                    if var_type_str == 'i':
                        value = int(value)
                    else:
                        value = float(value)
                    variables[var_name] = (var_type_str, value)
                except NameError as e:
                    print(f"Ошибка: использование не объявленной переменной или функции в {instr}")
                    return
                except Exception as e:
                    print(f"Ошибка при вычислении {instr}: {e}")
                    return

            else:
                var_name = left
                try:
                    value = eval(right, create_context(variables, functions))
                    if var_name in variables:
                        var_type = variables[var_name][0]
                        if var_type == 'i':
                            value = int(value)
                        else:
                            value = float(value)
                    else:
                        if isinstance(value, int):
                            var_type = 'i'
                        else:
                            var_type = 'f'
                            value = float(value)
                    variables[var_name] = (var_type, value)
                except NameError as e:
                    print(f"Ошибка: использование не объявленной переменной или функции в {instr}")
                    return
                except Exception as e:
                    print(f"Ошибка при вычислении {instr}: {e}")
                    return

        elif instr.startswith('print'):
            parts = instr.split()
            if len(parts) == 1:
                if not variables:
                    print("Нет объявленных переменных")
                else:
                    for var, (typ, val) in sorted(variables.items()):
                        print(f"{var}: {val}")
            elif len(parts) == 2:
                var_name = parts[1]
                if var_name in variables:
                    print(variables[var_name][1])
                else:
                    print(f"Ошибка: переменная {var_name} не объявлена")
            else:
                print(f"Ошибка: неверная команда print: {instr}")

    variables.clear()
    functions.clear()

def main():
    """Главная функция для запуска интерпретатора."""
    if len(sys.argv) != 2:
        print("Использование: python interpreter.py <имя_файла>")
        sys.exit(1)

    filename = sys.argv[1]
    process_instructions(filename)

if __name__ == "__main__":
    main()