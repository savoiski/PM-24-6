import csv
import pickle
from datetime import datetime

# класс для шахматной доски
class Board:
    def __init__(self):
        self.board = self.init_board()
        self.move_count = 0
        self.history = []
        self.current_player = 'white'
        self.castling_rights = {'white': {'K': True, 'Q': True}, 'black': {'K': True, 'Q': True}}
        self.en_passant = None  # позиция для взятия на проходе

    # инициализация доски
    def init_board(self):
        return [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p']*8,
            ['.']*8,
            ['.']*8,
            ['.']*8,
            ['.']*8,  
            ['P']*8,
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]

    # вывод доски
    def print_board(self):
        cols = '  A B C D E F G H'
        print(cols)
        for i in range(8):
            row = ' '.join(self.board[i])
            print(f"{8-i} {row} {8-i}")
        print(cols)

    # перемещение фигуры
    def move_piece(self, start, end):
        s_col, s_row = self.parse_pos(start)
        e_col, e_row = self.parse_pos(end)
        piece = self.board[s_row][s_col]
        target = self.board[e_row][e_col]

        if piece == '.':
            print('Нет фигуры на позиции', start)
            return False

        if not self.is_valid_move(piece, s_row, s_col, e_row, e_col):
            print('Некорректный ход')
            return False

        # сохранение состояния для отката
        self.history.append((self.board.copy(), self.castling_rights.copy(), self.en_passant))

        # обработка специальных ходов
        self.handle_special_moves(piece, s_row, s_col, e_row, e_col)

        # выполнение хода
        self.board[e_row][e_col] = piece
        self.board[s_row][s_col] = '.'
        self.move_count += 1

        # смена игрока
        self.current_player = 'black' if self.current_player == 'white' else 'white'

        return True

    # разбор позиции
    def parse_pos(self, pos):
        col = ord(pos[0].upper()) - ord('A')
        row = 8 - int(pos[1])
        return col, row

    # базовая проверка хода
    def is_valid_move(self, piece, s_r, s_c, e_r, e_c):
        # упрощённая проверка: не переходит ли на себя
        if self.current_player == 'white' and piece.islower():
            return False
        if self.current_player == 'black' and piece.isupper():
            return False

        # простая проверка на выход за границы доски
        if not (0 <= e_r < 8 and 0 <= e_c < 8):
            return False

        # можно добавить больше проверок для каждой фигуры
        return True

    # обработка специальных ходов
    def handle_special_moves(self, piece, s_r, s_c, e_r, e_c):
        # обработка рокировки
        if piece.upper() == 'K' and abs(e_c - s_c) == 2:
            if e_c > s_c:
                # короткая рокировка
                self.board[s_r][7] = '.'
                self.board[s_r][5] = 'R' if piece.isupper() else 'r'
            else:
                # длинная рокировка
                self.board[s_r][0] = '.'
                self.board[s_r][3] = 'R' if piece.isupper() else 'r'

        # обработка взятия на проходе
        if piece.upper() == 'P':
            if e_c != s_c and self.board[e_r][e_c] == '.':
                # пешка взяла на проходе
                self.board[s_r][e_c] = '.'

        # обновление рокировки и взятия на проходе
        self.update_castling(piece, s_r, s_c, e_r, e_c)

    # обновление прав рокировки и взятия на проходе
    def update_castling(self, piece, s_r, s_c, e_r, e_c):
        # удаление прав рокировки, если король или ладья ходят
        if piece.upper() == 'K':
            self.castling_rights[self.current_player]['K'] = False
            self.castling_rights[self.current_player]['Q'] = False
        if piece.upper() == 'R':
            if s_c == 0:
                self.castling_rights[self.current_player]['Q'] = False
            if s_c == 7:
                self.castling_rights[self.current_player]['K'] = False

        # установка взятия на проходе
        if piece.upper() == 'P' and abs(e_r - s_r) == 2:
            self.en_passant = (e_r + (1 if piece.isupper() else -1), e_c)
        else:
            self.en_passant = None

    # откат хода
    def undo_move(self):
        if not self.history:
            print('Нет ходов для отката')
            return False
        self.board, self.castling_rights, self.en_passant = self.history.pop()
        self.move_count -= 1
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        print('Ход откатан')
        return True

    # сохранение игры
    def save_game(self, file):
        try:
            with open(file, 'wb') as f:
                pickle.dump({
                    'board': self.board,
                    'move_count': self.move_count,
                    'history': self.history,
                    'current_player': self.current_player,
                    'castling_rights': self.castling_rights,
                    'en_passant': self.en_passant
                }, f)
            print('Игра сохранена в', file)
        except Exception as e:
            print('Ошибка сохранения:', e)

    # загрузка игры
    def load_game(self, file):
        try:
            with open(file, 'rb') as f:
                data = pickle.load(f)
                self.board = data['board']
                self.move_count = data['move_count']
                self.history = data['history']
                self.current_player = data['current_player']
                self.castling_rights = data['castling_rights']
                self.en_passant = data['en_passant']
            print('Игра загружена из', file)
        except Exception as e:
            print('Ошибка загрузки:', e)

# класс для управления игрой
class Game:
    def __init__(self):
        self.board = Board()

    # запуск игры
    def start(self):
        while True:
            self.board.print_board()
            move = input(f"{self.board.current_player} ход (например, E2 E4) или 'exit': ")
            if move.lower() == 'exit':
                print('Игра завершена')
                break
            elif move.lower() == 'undo':
                self.board.undo_move()
                continue
            elif move.lower().startswith('save'):
                _, file = move.split()
                self.board.save_game(file)
                continue
            elif move.lower().startswith('load'):
                _, file = move.split()
                self.board.load_game(file)
                continue
            try:
                start, end = move.split()
                self.board.move_piece(start, end)
            except:
                print('Некорректный ввод')

    # загрузка из файла полной нотации
    def load_full_notation(self, file):
        try:
            with open(file, 'r') as f:
                moves = f.read().strip().split()
                for i in range(0, len(moves), 2):
                    start = moves[i]
                    end = moves[i+1]
                    player = 'white' if i % 4 == 0 else 'black'
                    if self.board.move_piece(start, end):
                        self.board.history.append((player, start, end))
            print('Партия загружена из полной нотации')
        except Exception as e:
            print('Ошибка загрузки полной нотации:', e)

    # загрузка из файла сокращённой нотации
    def load_short_notation(self, file):
        try:
            with open(file, 'r') as f:
                moves = f.read().strip().split()
                for move in moves:
                    print(f'Ход: {move} (не реализовано)')
            print('Партия загружена из сокращённой нотации')
        except Exception as e:
            print('Ошибка загрузки сокращённой нотации:', e)

# загрузка файлов в Google Colab
def upload_files():
    try:
        from google.colab import files
        uploaded = files.upload()
        return list(uploaded.keys())
    except:
        return []

# пример использования
if __name__ == "__main__":
    game = Game()
    files = upload_files()
    while True:
        choice = input("Действия: 1 - играть, 2 - загрузить полную нотацию, 3 - загрузить сокращённую нотацию, 4 - выход: ")
        if choice == '1':
            game.start()
        elif choice == '2':
            if not files:
                print('Загрузите файлы')
            else:
                file = input(f'Доступные файлы: {files}\nВведите имя файла: ')
                game.load_full_notation(file)
        elif choice == '3':
            if not files:
                print('Загрузите файлы')
            else:
                file = input(f'Доступные файлы: {files}\nВведите имя файла: ')
                game.load_short_notation(file)
        elif choice == '4':
            print('Выход')
            break
        else:
            print('Неверный выбор')
