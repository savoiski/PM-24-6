import csv
import pickle
from datetime import datetime

# загрузка таблицы из файлов
def load_t(*files):
    t = {"cols": [], "types": {}, "rows": []}
    for f in files:
        try:
            if f.endswith(".csv"):
                with open(f, "r", encoding="utf-8") as file:
                    r = csv.reader(file)
                    cols = next(r)
                    if not t["cols"]:
                        t["cols"] = cols
                    elif t["cols"] != cols:
                        raise Exception("разные колонки")
                    for row in r:
                        t["rows"].append(row)
            elif f.endswith(".pkl"):
                with open(f, "rb") as file:
                    data = pickle.load(file)
                    if not t["cols"]:
                        t = data
                    else:
                        if t["cols"] != data["cols"]:
                            raise Exception("разные колонки")
                        t["rows"].extend(data["rows"])
            else:
                raise Exception("неподдерживаемый формат файла")
        except FileNotFoundError:
            print(f"файл {f} не найден")
        except Exception as e:
            print(f"ошибка при загрузке {f}: {e}")
    # определение типов
    for c in t["cols"]:
        vals = [
            row[t["cols"].index(c)]
            for row in t["rows"]
            if row[t["cols"].index(c)] != ""
        ]
        t["types"][c] = auto_type(vals)
    # конвертация типов
    t["rows"] = [conv(r, t["cols"], t["types"]) for r in t["rows"]]
    print("загружено:", t)
    return t

# определение типа
def auto_type(vals):
    for typ in [int, float]:
        try:
            [typ(v) for v in vals]
            return typ
        except:
            continue
    try:
        [datetime.strptime(v, "%Y-%m-%d %H:%M:%S") for v in vals]
        return "datetime"
    except:
        return str


# конвертация строки
def conv(row, cols, types):
    new = []
    for i, v in enumerate(row):
        c = cols[i]
        typ = types[c]
        if v == "":
            new.append(None)
            continue
        try:
            if typ == int:
                new.append(int(v))
            elif typ == float:
                new.append(float(v))
            elif typ == "datetime":
                new.append(datetime.strptime(v, "%Y-%m-%d %H:%M:%S"))
            else:
                new.append(v)
        except:
            new.append(None)
    return new


# сохранение таблицы в файлы
def save_t(t, *files, max_rows=None):
    try:
        if not files:
            raise Exception("нет файлов для сохранения")
        rows = t["rows"]
        if max_rows:
            rows = rows[:max_rows]
        for f in files:
            if f.endswith(".csv"):
                with open(f, "w", newline="", encoding="utf-8") as file:
                    w = csv.writer(file)
                    w.writerow(t["cols"])
                    for r in rows:
                        rw = [
                            v.strftime("%Y-%m-%d %H:%M:%S")
                            if isinstance(v, datetime)
                            else v
                            for v in r
                        ]
                        w.writerow(rw)
            elif f.endswith(".pkl"):
                with open(f, "wb") as file:
                    pickle.dump(t, file)
            elif f.endswith(".txt"):
                with open(f, "w", encoding="utf-8") as file:
                    file.write("\t".join(t["cols"]) + "\n")
                    for r in rows:
                        rw = "\t".join(
                            [
                                v.strftime("%Y-%m-%d %H:%M:%S")
                                if isinstance(v, datetime)
                                else str(v)
                                for v in r
                            ]
                        )
                        file.write(rw + "\n")
            else:
                print(f"неподдерживаемый формат файла {f}")
        print("сохранено в", files)
    except Exception as e:
        print("ошибка при сохранении:", e)


# вывод таблицы
def print_t(t):
    print("таблица:")
    print("\t".join(t["cols"]))
    for r in t["rows"]:
        rw = [
            v.strftime("%Y-%m-%d %H:%M:%S") if isinstance(v, datetime) else str(v)
            for v in r
        ]
        print("\t".join(rw))


# получение строки по номеру
def get_r(t, num):
    try:
        r = t["rows"][num]
        print(f"строка {num}: {r}")
        return r
    except IndexError:
        print("номер строки вне диапазона")


# получение строки по индексу
def get_r_idx(t, idx):
    try:
        r = t["rows"][idx]
        print(f"строка {idx}: {r}")
        return r
    except IndexError:
        print("индекс строки вне диапазона")


# получение типа столбца
def get_ct(t, col):
    try:
        typ = t["types"][col]
        print(f"тип столбца {col}: {typ}")
        return typ
    except KeyError:
        print("столбец не найден")


# установка типа столбца
def set_ct(t, col, typ):
    if col in t["types"]:
        t["types"][col] = typ
        idx = t["cols"].index(col)
        for r in t["rows"]:
            v = r[idx]
            if v is not None:
                try:
                    if typ == int:
                        r[idx] = int(v)
                    elif typ == float:
                        r[idx] = float(v)
                    elif typ == "datetime":
                        if isinstance(v, datetime):
                            continue
                        r[idx] = datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
                    else:
                        r[idx] = str(v)
                except:
                    r[idx] = None
        print(f"тип столбца {col} установлен в {typ}")
    else:
        print("столбец не найден")


# получение всех значений столбца
def get_v(t, col):
    try:
        idx = t["cols"].index(col)
        vals = [r[idx] for r in t["rows"]]
        print(f"значения столбца {col}: {vals}")
        return vals
    except ValueError:
        print("столбец не найден")


# получение конкретного значения
def get_val(t, row_num, col):
    try:
        idx = t["cols"].index(col)
        val = t["rows"][row_num][idx]
        print(f"значение в строке {row_num}, столбце {col}: {val}")
        return val
    except (ValueError, IndexError):
        print("неверный номер строки или столбца")


# установка всех значений столбца
def set_v(t, col, vals):
    try:
        idx = t["cols"].index(col)
        if len(vals) != len(t["rows"]):
            raise Exception("длина значений не совпадает с количеством строк")
        for i in range(len(t["rows"])):
            v = vals[i]
            if v is not None:
                typ = t["types"][col]
                try:
                    if typ == int:
                        t["rows"][i][idx] = int(v)
                    elif typ == float:
                        t["rows"][i][idx] = float(v)
                    elif typ == "datetime":
                        if isinstance(v, datetime):
                            t["rows"][i][idx] = v
                        else:
                            t["rows"][i][idx] = datetime.strptime(
                                v, "%Y-%m-%d %H:%M:%S"
                            )
                    else:
                        t["rows"][i][idx] = str(v)
                except:
                    t["rows"][i][idx] = None
            else:
                t["rows"][i][idx] = None
        print(f"значения столбца {col} обновлены")
    except ValueError:
        print("столбец не найден")
    except Exception as e:
        print("ошибка при установке значений:", e)


# установка конкретного значения
def set_val(t, row_num, col, val):
    try:
        idx = t["cols"].index(col)
        typ = t["types"][col]
        if val is not None:
            if typ == int:
                val = int(val)
            elif typ == float:
                val = float(val)
            elif typ == "datetime":
                if isinstance(val, datetime):
                    pass
                else:
                    val = datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
            else:
                val = str(val)
        t["rows"][row_num][idx] = val
        print(f"значение в строке {row_num}, столбце {col} установлено в {val}")
    except (ValueError, IndexError):
        print("неверный номер строки или столбца")


# конкатенация таблиц
def concat(t1, t2):
    if t1["cols"] != t2["cols"]:
        print("таблицы имеют разные колонки")
        return None
    t = {"cols": t1["cols"], "types": t1["types"], "rows": t1["rows"] + t2["rows"]}
    print("таблицы сконкатенированы:", t)
    return t


# разбиение таблицы на две
def split(t, index):
    t1 = {"cols": t["cols"], "types": t["types"], "rows": t["rows"][:index]}
    t2 = {"cols": t["cols"], "types": t["types"], "rows": t["rows"][index:]}
    print("таблица разбита на две:", t1, t2)
    return t1, t2


# арифметические операции
def add(t, col1, col2):
    return arith(t, col1, col2, "add")


def sub(t, col1, col2):
    return arith(t, col1, col2, "sub")


def mul(t, col1, col2):
    return arith(t, col1, col2, "mul")


def div(t, col1, col2):
    return arith(t, col1, col2, "div")


def arith(t, col1, col2, op):
    try:
        idx1 = t["cols"].index(col1)
        idx2 = t["cols"].index(col2)
        res = []
        for r in t["rows"]:
            a = r[idx1]
            b = r[idx2]
            if a is None or b is None:
                res.append(None)
                continue
            try:
                if op == "add":
                    res.append(a + b)
                elif op == "sub":
                    res.append(a - b)
                elif op == "mul":
                    res.append(a * b)
                elif op == "div":
                    res.append(a / b if b != 0 else None)
            except:
                res.append(None)
        print(f"результат {op} столбцов {col1} и {col2}: {res}")
        return res
    except ValueError:
        print("один из столбцов не найден")


# функции сравнения
def eq(t, col1, col2):
    return cmp(t, col1, col2, "eq")


def gr(t, col1, col2):
    return cmp(t, col1, col2, "gr")


def ls(t, col1, col2):
    return cmp(t, col1, col2, "ls")


def ge(t, col1, col2):
    return cmp(t, col1, col2, "ge")


def le(t, col1, col2):
    return cmp(t, col1, col2, "le")


def ne(t, col1, col2):
    return cmp(t, col1, col2, "ne")


def cmp(t, col1, col2, op):
    try:
        idx1 = t["cols"].index(col1)
        idx2 = t["cols"].index(col2)
        res = []
        for r in t["rows"]:
            a = r[idx1]
            b = r[idx2]
            if a is None or b is None:
                res.append(False)
                continue
            try:
                if isinstance(a, datetime) and isinstance(b, datetime):
                    pass
                elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
                    pass
                else:
                    a = str(a)
                    b = str(b)
                if op == "eq":
                    res.append(a == b)
                elif op == "gr":
                    res.append(a > b)
                elif op == "ls":
                    res.append(a < b)
                elif op == "ge":
                    res.append(a >= b)
                elif op == "le":
                    res.append(a <= b)
                elif op == "ne":
                    res.append(a != b)
            except:
                res.append(False)
        print(f"результат сравнения {op} столбцов {col1} и {col2}: {res}")
        return res
    except ValueError:
        print("один из столбцов не найден")


# фильтрация строк
def filter_rows(t, bool_list):
    try:
        if len(bool_list) != len(t["rows"]):
            raise Exception("длина списка не совпадает с количеством строк")
        new = [r for r, f in zip(t["rows"], bool_list) if f]
        t["rows"] = new
        print("строки отфильтрованы:", t)
    except Exception as e:
        print("ошибка при фильтрации строк:", e)

# пример использования
if __name__ == "__main__":
    # загрузка таблицы
    table = load_t("data1.csv", "data2.pkl")

    # вывод таблицы
    print_t(table)

    # сохранение таблицы
    save_t(table, "out.csv", "out.pkl", "out.txt", max_rows=100)

    # получение строки
    get_r(table, 0)

    # получение строки по индексу
    get_r_idx(table, 1)

    # получение типа столбца
    get_ct(table, "age")

    # установка типа столбца
    set_ct(table, "age", int)

    # получение значений столбца
    get_v(table, "age")

    # получение конкретного значения
    get_val(table, 0, "name")

    # установка всех значений столбца (корректная длина)
    set_v(table, "age", [25, 30, 35, 28, 32, 26])

    # установка конкретного значения
    set_val(table, 1, "name", "Иван")

    # конкатенация таблиц
    table2 = load_t("data3.csv")
    concat_table = concat(table, table2)

    # разбиение таблицы
    if concat_table:
        split1, split2 = split(concat_table, 2)

    # арифметические операции
    add(table, "age", "salary")
    sub(table, "age", "salary")
    mul(table, "age", "salary")
    div(table, "age", "salary")

    # функции сравнения
    eq_result = eq(table, "age", "salary")
    gr_result = gr(table, "age", "salary")
    ls_result = ls(table, "age", "salary")
    ge_result = ge(table, "age", "salary")
    le_result = le(table, "age", "salary")
    ne_result = ne(table, "age", "salary")

    # фильтрация строк
    filter_rows(table, gr_result)

    # вывод отфильтрованной таблицы
    print_t(table)
