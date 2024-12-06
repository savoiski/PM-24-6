import csv
import pickle
from datetime import datetime

# загрузка таблицы из файлов
def load_table(*files, auto_detect=True):
    t = {'cols': [], 'types': {}, 'rows': []}
    for f in files:
        try:
            if f.endswith('.csv'):
                with open(f, 'r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    cols = next(reader)
                    if not t['cols']:
                        t['cols'] = cols
                    elif t['cols'] != cols:
                        raise Exception(f'Файл {f} имеет разные колонки')
                    for row in reader:
                        t['rows'].append(row)
            elif f.endswith('.pkl'):
                with open(f, 'rb') as file:
                    data = pickle.load(file)
                    if not t['cols']:
                        t = data
                    else:
                        if t['cols'] != data['cols']:
                            raise Exception(f'Файл {f} имеет разные колонки')
                        t['rows'].extend(data['rows'])
            else:
                raise Exception(f'Неподдерживаемый формат файла: {f}')
        except FileNotFoundError:
            print(f'Файл {f} не найден')
        except Exception as e:
            print(f'Ошибка при загрузке {f}: {e}')
    if auto_detect:
        for c in t['cols']:
            idx = t['cols'].index(c)
            vals = [row[idx] for row in t['rows'] if row[idx] != '']
            t['types'][c] = auto_type(vals)
        t['rows'] = [convert_row(r, t['cols'], t['types']) for r in t['rows']]
    print('загружено:', t)
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
        [datetime.strptime(v, '%Y-%m-%d %H:%M:%S') for v in vals]
        return 'datetime'
    except:
        return str

# конвертация строки
def convert_row(row, cols, types):
    new = []
    for i, v in enumerate(row):
        c = cols[i]
        typ = types[c]
        if v == '':
            new.append(None)
            continue
        try:
            if typ == int:
                new.append(int(v))
            elif typ == float:
                new.append(float(v))
            elif typ == 'datetime':
                new.append(datetime.strptime(v, '%Y-%m-%d %H:%M:%S'))
            else:
                new.append(v)
        except:
            new.append(None)
    return new

# сохранение таблицы в файлы
def save_table(t, *files, max_rows=None):
    try:
        if not files:
            raise Exception('Нет файлов для сохранения')
        rows = t['rows']
        if max_rows:
            rows = rows[:max_rows]
        for f in files:
            if f.endswith('.csv'):
                with open(f, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(t['cols'])
                    for r in rows:
                        rw = [v.strftime('%Y-%m-%d %H:%M:%S') if isinstance(v, datetime) else v for v in r]
                        writer.writerow(rw)
            elif f.endswith('.pkl'):
                with open(f, 'wb') as file:
                    pickle.dump(t, file)
            elif f.endswith('.txt'):
                with open(f, 'w', encoding='utf-8') as file:
                    file.write('\t'.join(t['cols']) + '\n')
                    for r in rows:
                        rw = '\t'.join([v.strftime('%Y-%m-%d %H:%M:%S') if isinstance(v, datetime) else str(v) for v in r])
                        file.write(rw + '\n')
            else:
                print(f'Неподдерживаемый формат файла {f}')
        print('сохранено в', files)
    except Exception as e:
        print('ошибка при сохранении:', e)

# вывод таблицы
def print_table(t):
    print('таблица:')
    print('\t'.join(t['cols']))
    for r in t['rows']:
        rw = [v.strftime('%Y-%m-%d %H:%M:%S') if isinstance(v, datetime) else str(v) for v in r]
        print('\t'.join(rw))

# получение строк по номерам
def get_rows_by_number(t, start, stop=None, copy_table=False):
    try:
        if stop is not None:
            selected = t['rows'][start:stop]
        else:
            selected = [t['rows'][start]]
        if copy_table:
            new_table = {'cols': t['cols'][:], 'types': t['types'].copy(), 'rows': [r[:] for r in selected]}
            print('получена копия строк:', new_table)
            return new_table
        else:
            # создание представления (зависит от требований, здесь просто возвращаем ссылки)
            view_table = {'cols': t['cols'], 'types': t['types'], 'rows': selected}
            print('получены строки:', view_table)
            return view_table
    except IndexError:
        print('номер строки вне диапазона')
    except Exception as e:
        print('ошибка при получении строк:', e)

# получение строк по индексам первого столбца
def get_rows_by_index(t, *vals, copy_table=False):
    try:
        idx = t['cols'][0]
        selected = [r for r in t['rows'] if r[0] in vals]
        if copy_table:
            new_table = {'cols': t['cols'][:], 'types': t['types'].copy(), 'rows': [r[:] for r in selected]}
            print('получена копия строк:', new_table)
            return new_table
        else:
            view_table = {'cols': t['cols'], 'types': t['types'], 'rows': selected}
            print('получены строки:', view_table)
            return view_table
    except Exception as e:
        print('ошибка при получении строк по индексам:', e)

# получение типов столбцов
def get_column_types(t, by_number=True):
    try:
        if by_number:
            types = list(t['types'].values())
        else:
            types = t['types'].copy()
        print('типы столбцов:', types)
        return types
    except Exception as e:
        print('ошибка при получении типов столбцов:', e)

# установка типов столбцов
def set_column_types(t, types_dict, by_number=True):
    try:
        if by_number:
            for idx, typ in types_dict.items():
                col = t['cols'][idx]
                t['types'][col] = typ
                # конвертация типов
                for r in t['rows']:
                    v = r[idx]
                    if v is not None:
                        try:
                            if typ == int:
                                r[idx] = int(v)
                            elif typ == float:
                                r[idx] = float(v)
                            elif typ == 'datetime':
                                if isinstance(v, datetime):
                                    continue
                                r[idx] = datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
                            else:
                                r[idx] = str(v)
                        except:
                            r[idx] = None
        else:
            for col, typ in types_dict.items():
                if col in t['types']:
                    t['types'][col] = typ
                    idx = t['cols'].index(col)
                    for r in t['rows']:
                        v = r[idx]
                        if v is not None:
                            try:
                                if typ == int:
                                    r[idx] = int(v)
                                elif typ == float:
                                    r[idx] = float(v)
                                elif typ == 'datetime':
                                    if isinstance(v, datetime):
                                        continue
                                    r[idx] = datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
                                else:
                                    r[idx] = str(v)
                            except:
                                r[idx] = None
                else:
                    raise Exception(f'Столбец {col} не найден')
        print('типы столбцов обновлены:', t['types'])
    except Exception as e:
        print('ошибка при установке типов столбцов:', e)

# получение значений столбца
def get_values(t, column=0):
    try:
        if isinstance(column, int):
            idx = column
            col = t['cols'][idx]
        else:
            col = column
            idx = t['cols'].index(col)
        vals = [r[idx] for r in t['rows']]
        print(f'значения столбца {col}: {vals}')
        return vals
    except IndexError:
        print('номер столбца вне диапазона')
    except ValueError:
        print('столбец не найден')
    except Exception as e:
        print('ошибка при получении значений столбца:', e)

# получение одного значения из столбца (для таблицы с одной строкой)
def get_value(t, column=0):
    try:
        if len(t['rows']) != 1:
            raise Exception('таблица должна содержать ровно одну строку')
        return get_values(t, column)[0]
    except Exception as e:
        print('ошибка при получении значения:', e)

# установка значений столбца
def set_values(t, values, column=0):
    try:
        if isinstance(column, int):
            idx = column
            col = t['cols'][idx]
        else:
            col = column
            idx = t['cols'].index(col)
        if len(values) != len(t['rows']):
            raise Exception('длина значений не совпадает с количеством строк')
        typ = t['types'][col]
        for i in range(len(t['rows'])):
            v = values[i]
            if v is not None:
                try:
                    if typ == int:
                        t['rows'][i][idx] = int(v)
                    elif typ == float:
                        t['rows'][i][idx] = float(v)
                    elif typ == 'datetime':
                        if isinstance(v, datetime):
                            t['rows'][i][idx] = v
                        else:
                            t['rows'][i][idx] = datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
                    else:
                        t['rows'][i][idx] = str(v)
                except:
                    t['rows'][i][idx] = None
            else:
                t['rows'][i][idx] = None
        print(f'значения столбца {col} обновлены')
    except ValueError:
        print('столбец не найден')
    except Exception as e:
        print('ошибка при установке значений столбца:', e)

# установка одного значения (для таблицы с одной строкой)
def set_value(t, value, column=0):
    try:
        if len(t['rows']) != 1:
            raise Exception('таблица должна содержать ровно одну строку')
        set_values(t, [value], column)
    except Exception as e:
        print('ошибка при установке значения:', e)

# конкатенация таблиц
def concat(t1, t2):
    try:
        if t1['cols'] != t2['cols']:
            raise Exception('Таблицы имеют разные колонки')
        new = {'cols': t1['cols'], 'types': t1['types'].copy(), 'rows': t1['rows'] + t2['rows']}
        print('таблицы сконкатенированы:', new)
        return new
    except Exception as e:
        print('ошибка при конкатенации таблиц:', e)

# разбиение таблицы на две
def split_table(t, row_number):
    try:
        if row_number < 0 or row_number > len(t['rows']):
            raise Exception('номер строки для разбиения вне диапазона')
        t1 = {'cols': t['cols'], 'types': t['types'].copy(), 'rows': t['rows'][:row_number]}
        t2 = {'cols': t['cols'], 'types': t['types'].copy(), 'rows': t['rows'][row_number:]}
        print('таблица разбита на две:', t1, t2)
        return t1, t2
    except Exception as e:
        print('ошибка при разбиении таблицы:', e)

# арифметические операции
def add(t, col1, col2):
    return arith(t, col1, col2, 'add')

def sub(t, col1, col2):
    return arith(t, col1, col2, 'sub')

def mul(t, col1, col2):
    return arith(t, col1, col2, 'mul')

def div(t, col1, col2):
    return arith(t, col1, col2, 'div')

def arith(t, col1, col2, op):
    try:
        idx1 = t['cols'].index(col1)
        idx2 = t['cols'].index(col2)
        typ1 = t['types'][col1]
        typ2 = t['types'][col2]
        if typ1 not in [int, float] and typ1 != 'bool':
            raise Exception(f'Столбец {col1} не поддерживает арифметические операции')
        if typ2 not in [int, float] and typ2 != 'bool':
            raise Exception(f'Столбец {col2} не поддерживает арифметические операции')
        res = []
        for r in t['rows']:
            a = r[idx1]
            b = r[idx2]
            if a is None or b is None:
                res.append(None)
                continue
            try:
                if op == 'add':
                    res.append(a + b)
                elif op == 'sub':
                    res.append(a - b)
                elif op == 'mul':
                    res.append(a * b)
                elif op == 'div':
                    res.append(a / b if b != 0 else None)
                else:
                    res.append(None)
            except:
                res.append(None)
        print(f'результат {op} столбцов {col1} и {col2}: {res}')
        return res
    except ValueError:
        print('один из столбцов не найден')
    except Exception as e:
        print('ошибка при выполнении арифметической операции:', e)

# функции сравнения
def eq(t, col1, col2):
    return compare(t, col1, col2, 'eq')

def gr(t, col1, col2):
    return compare(t, col1, col2, 'gr')

def ls(t, col1, col2):
    return compare(t, col1, col2, 'ls')

def ge(t, col1, col2):
    return compare(t, col1, col2, 'ge')

def le(t, col1, col2):
    return compare(t, col1, col2, 'le')

def ne(t, col1, col2):
    return compare(t, col1, col2, 'ne')

def compare(t, col1, col2, op):
    try:
        idx1 = t['cols'].index(col1)
        idx2 = t['cols'].index(col2)
        typ1 = t['types'][col1]
        typ2 = t['types'][col2]
        res = []
        for r in t['rows']:
            a = r[idx1]
            b = r[idx2]
            if a is None or b is None:
                res.append(False)
                continue
            try:
                if isinstance(a, datetime) and isinstance(b, datetime):
                    pass
                elif isinstance(a, (int, float, bool)) and isinstance(b, (int, float, bool)):
                    pass
                else:
                    a = str(a)
                    b = str(b)
                if op == 'eq':
                    res.append(a == b)
                elif op == 'gr':
                    res.append(a > b)
                elif op == 'ls':
                    res.append(a < b)
                elif op == 'ge':
                    res.append(a >= b)
                elif op == 'le':
                    res.append(a <= b)
                elif op == 'ne':
                    res.append(a != b)
            except:
                res.append(False)
        print(f'результат сравнения {op} столбцов {col1} и {col2}: {res}')
        return res
    except ValueError:
        print('один из столбцов не найден')
    except Exception as e:
        print('ошибка при выполнении сравнения:', e)

# фильтрация строк
def filter_rows(t, bool_list, copy_table=False):
    try:
        if len(bool_list) != len(t['rows']):
            raise Exception('длина списка не совпадает с количеством строк')
        if copy_table:
            new_rows = [r[:] for r, f in zip(t['rows'], bool_list) if f]
            new_table = {'cols': t['cols'][:], 'types': t['types'].copy(), 'rows': new_rows}
            print('фильтрованная копия таблицы:', new_table)
            return new_table
        else:
            t['rows'] = [r for r, f in zip(t['rows'], bool_list) if f]
            print('строки отфильтрованы:', t)
    except Exception as e:
        print('ошибка при фильтрации строк:', e)

# слияние таблиц
def merge_tables(t1, t2, by_number=True):
    try:
        if by_number:
            # слияние по номеру строки
            max_len = max(len(t1['rows']), len(t2['rows']))
            new_rows = []
            for i in range(max_len):
                row1 = t1['rows'][i] if i < len(t1['rows']) else [None]*len(t1['cols'])
                row2 = t2['rows'][i] if i < len(t2['rows']) else [None]*len(t2['cols'])
                merged_row = row1 + row2
                new_rows.append(merged_row)
            new_cols = t1['cols'] + t2['cols']
            new_types = {**t1['types'], **t2['types']}
            new_table = {'cols': new_cols, 'types': new_types, 'rows': new_rows}
            print('таблицы слиты по номеру:', new_table)
            return new_table
        else:
            # слияние по значению индекса (первый столбец)
            idx1 = t1['cols'][0]
            idx2 = t2['cols'][0]
            dict1 = {r[0]: r for r in t1['rows']}
            dict2 = {r[0]: r for r in t2['rows']}
            all_keys = set(dict1.keys()).union(set(dict2.keys()))
            new_cols = t1['cols'] + [col for col in t2['cols'] if col != idx2]
            new_types = {**t1['types'], **{k: v for k, v in t2['types'].items() if k != idx2}}
            new_rows = []
            for key in all_keys:
                row1 = dict1.get(key, [None]*len(t1['cols']))
                row2 = dict2.get(key, [None]*len(t2['cols']))
                merged_row = row1 + [v for i, v in enumerate(row2) if t2['cols'][i] != idx2]
                new_rows.append(merged_row)
            new_table = {'cols': new_cols, 'types': new_types, 'rows': new_rows}
            print('таблицы слиты по индексу:', new_table)
            return new_table
    except Exception as e:
        print('ошибка при слиянии таблиц:', e)

# пример использования
if __name__ == "__main__":
    # Загрузка файлов (для Google Colab используйте функции загрузки файлов, см. ниже)
    table = load_table('data1.csv', 'data2.pkl')

    # Вывод таблицы
    print_table(table)

    # Сохранение таблицы
    save_table(table, 'out.csv', 'out.pkl', 'out.txt', max_rows=100)

    # Получение строки по номеру
    get_rows_by_number(table, 0)

    # Получение строки по индексу
    get_rows_by_index(table, 1, 2)

    # Получение типов столбцов
    get_column_types(table, by_number=False)

    # Установка типов столбцов
    set_column_types(table, {'age': int, 'salary': float}, by_number=False)

    # Получение значений столбца
    get_values(table, 'age')

    # Получение одного значения (для таблицы с одной строкой)
    # set_rows = load_table('single_row.csv')  # пример загрузки таблицы с одной строкой
    # get_value(set_rows, 'age')

    # Установка значений столбца
    set_values(table, [25, 30, 35, 28, 32, 26], 'age')

    # Установка одного значения (для таблицы с одной строкой)
    # set_value(set_rows, 28, 'age')  # пример

    # Конкатенация таблиц
    table2 = load_table('data3.csv')
    concat_table = concat(table, table2)

    # Разбиение таблицы
    if concat_table:
        split1, split2 = split_table(concat_table, 3)

    # Арифметические операции
    add(table, 'age', 'salary')
    sub(table, 'age', 'salary')
    mul(table, 'age', 'salary')
    div(table, 'age', 'salary')

    # Функции сравнения
    eq_result = eq(table, 'age', 'salary')
    gr_result = gr(table, 'age', 'salary')
    ls_result = ls(table, 'age', 'salary')
    ge_result = ge(table, 'age', 'salary')
    le_result = le(table, 'age', 'salary')
    ne_result = ne(table, 'age', 'salary')

    # Фильтрация строк
    filter_rows(table, gr_result)

    # Вывод отфильтрованной таблицы
    print_table(table)

    # Слияние таблиц
    merged_table = merge_tables(table, table2, by_number=False)
    print_table(merged_table)

# Дополнительно: Загрузка файлов в Google Colab

try:
    from google.colab import files
    uploaded = files.upload()
    for f in uploaded.keys():
        print(f'Загружен файл: {f}')
except ImportError:
    pass
