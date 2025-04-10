import sys

def create_context(variables, functions, global_context=None):
    if global_context is None:
        global_context = {}
        for var, (typ, val) in variables.items():
            global_context[var] = val
        for func, (args, expr) in functions.items():
            global_context[func] = lambda *vals, expr=expr, args=args: eval(expr, global_context, dict(zip(args, vals)))
    return global_context

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
            if '(' not in instr or ')' not in instr:
                print(f"Ошибка: неверное определение функции: {instr}")
                continue
            name_args, expr = instr.split(':', 1)
            expr = expr.strip()
            name = name_args.split('(')[0].strip()
            args_str = name_args[name_args.index('(')+1:name_args.index(')')].strip()
            args = [arg.strip() for arg in args_str.split(',')] if args_str else []
            functions[name] = (args, expr)

        elif '=' in instr:
            left, right = instr.split('=', 1)
            left = left.strip()
            right = right.strip()

            if '(' in left and ')' in left:
                var_name = left.split('(')[0].strip()
                var_type = left[left.index('(')+1:left.index(')')].strip()
                if var_type not in ['i', 'f']:
                    print(f"Ошибка: неверный тип {var_type}")
                    continue
                try:
                    context = create_context(variables, functions)
                    value = eval(right, context)
                    if var_type == 'i':
                        value = int(value)
                    else:
                        value = float(value)
                    variables[var_name] = (var_type, value)
                except NameError as e:
                    print(f"Ошибка: необъявленная переменная или функция в {instr}")
                    return
                except Exception as e:
                    print(f"Ошибка при вычислении {instr}: {e}")
                    return
            else:
                var_name = left
                try:
                    context = create_context(variables, functions)
                    value = eval(right, context)
                    if var_name in variables:
                        var_type = variables[var_name][0]
                        value = int(value) if var_type == 'i' else float(value)
                    else:
                        if isinstance(value, int) and value == int(value):
                            var_type = 'i'
                        else:
                            var_type = 'f'
                            value = float(value)
                    variables[var_name] = (var_type, value)
                except NameError as e:
                    print(f"Ошибка: необъявленная переменная или функция в {instr}")
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
                        print(f"{var} = {val}")
            elif len(parts) == 2:
                var_name = parts[1]
                if var_name in variables:
                    print(variables[var_name][1])
                else:
                    print(f"Ошибка: переменная {var_name} не объявлена")

    variables.clear()
    functions.clear()

def main():
    if len(sys.argv) != 2:
        print("Использование: python interpreter.py <имя_файла>")
        sys.exit(1)
    process_instructions(sys.argv[1])

if __name__ == "__main__":
    main()
