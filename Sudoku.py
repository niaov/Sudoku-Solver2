class Grid:
    def __init__(self, col_num, row_num):
        # 初始化数独棋盘，col_num 为列数，row_num 为行数
        self.row_num = row_num
        self.col_num = col_num
        self.grid = [[0] * row_num for _ in range(col_num)]  # 创建一个 9x9 的空棋盘

    def serialize(self):
        # 序列化棋盘为字符串
        return ''.join(str(val) for row in self.grid for val in row)

    def deserialize(self, data):
        # 将字符串反序列化为数独棋盘
        if len(data) != self.row_num * self.col_num:
            raise ValueError("反序列化输入长度有误")
        for i in range(self.row_num):
            for j in range(self.col_num):
                self.grid[i][j] = int(data[i * self.col_num + j])

    def get_row_values(self, row_id):
        # 获取指定行的数值
        if not (0 <= row_id < self.row_num):
            raise IndexError("行下标越界")
        return self.grid[row_id]

    def get_col_values(self, col_id):
        # 获取指定列的数值
        if not (0 <= col_id < self.col_num):
            raise IndexError("列下标越界")
        return [self.grid[i][col_id] for i in range(self.row_num)]

    def get_block_value(self, row_id, col_id):
        # 获取指定单元格的值
        if not (0 <= row_id < self.row_num) or not (0 <= col_id < self.col_num):
            raise IndexError("行或列下标越界")
        return self.grid[row_id][col_id]

    def set_block_value(self, row_id, col_id, val):
        # 设置指定单元格的值
        if not (0 <= row_id < self.row_num) or not (0 <= col_id < self.col_num):
            raise IndexError("行或列下标越界")
        self.grid[row_id][col_id] = val

    def __eq__(self, other):
        # 检查两个棋盘是否相等（用于比较操作）
        return self.grid == other.grid

class Sudoku(Grid):
    def __init__(self, input_sudoku_value):
        # 初始化数独对象，继承自 Grid 类，固定 9x9 棋盘
        super().__init__(9, 9)  # 9x9 的数独棋盘
        while len(input_sudoku_value) > 81:
            input_sudoku_value = input_sudoku_value[:-1]  # 如果输入过长，去除多余字符
        input_sudoku_value = input_sudoku_value.ljust(81, '0')  # 如果输入过短，补齐到 81 字符
        self.deserialize(input_sudoku_value)  # 将输入反序列化为棋盘
        self.row = [set() for _ in range(9)]  # 每行的值集合
        self.col = [set() for _ in range(9)]  # 每列的值集合
        self.squ = [[set() for _ in range(3)] for _ in range(3)]  # 每个 3x3 小块的值集合
        self.in_squ_id = [[(i // 3, j // 3) for j in range(9)] for i in range(9)]  # 计算每个格子属于哪个小块
        self.solution_count = 0  # 解的数量计数器
        self.initialize_bitsets()  # 初始化行、列、小块的已使用数字

    def initialize_bitsets(self):
        # 初始化每行、列、小块中已存在的数
        for i in range(9):
            self.row[i] = set(self.get_row_values(i))
            self.col[i] = set(self.get_col_values(i))
        for row_id in range(3):
            for col_id in range(3):
                block_values = []
                for i in range(3):
                    for j in range(3):
                        cur_row = row_id * 3 + i
                        cur_col = col_id * 3 + j
                        block_values.append(self.get_block_value(cur_row, cur_col))
                        self.in_squ_id[cur_row][cur_col] = (row_id, col_id)
                self.squ[row_id][col_id] = set(block_values)

    def solve(self, ifOutputAns=True, row_id=0, col_id=0):
        # 递归回溯法解数独
        if self.solution_count > 100:
            return  # 当解的数量超过 100 时，终止

        if row_id >= 9:
            # 找到一个解，计数并输出（可选）
            self.solution_count += 1
            if ifOutputAns:
                print("第", self.solution_count, "个可能的解答如下：")
                self.print_board()
                if self.solution_count > 100:
                    print("已生成足够多的解答。")
            return

        # 计算下一个单元格的坐标
        next_row, next_col = row_id, col_id + 1
        if next_col >= 9:
            next_row, next_col = row_id + 1, 0

        # 获取当前单元格的值，如果不是空格，继续递归下一个单元格
        cur_value = self.get_block_value(row_id, col_id)
        if cur_value > 0:
            self.solve(ifOutputAns, next_row, next_col)
        else:
            # 尝试填入 1-9 的数字
            for num in range(1, 10):
                squ_row, squ_col = self.in_squ_id[row_id][col_id]
                # 如果该数字不在当前行、列和 3x3 小块中，则填入数字
                if num not in self.row[row_id] and num not in self.col[col_id] and num not in self.squ[squ_row][squ_col]:
                    self.row[row_id].add(num)
                    self.col[col_id].add(num)
                    self.squ[squ_row][squ_col].add(num)
                    self.set_block_value(row_id, col_id, num)

                    # 递归解下一个单元格
                    self.solve(ifOutputAns, next_row, next_col)

                    # 回溯，恢复单元格的状态
                    self.row[row_id].remove(num)
                    self.col[col_id].remove(num)
                    self.squ[squ_row][squ_col].remove(num)
                    self.set_block_value(row_id, col_id, 0)

    def print_board(self):
        # 打印当前棋盘状态
        for row in self.grid:
            print(" ".join(str(val) for val in row))
        print()

class SudokuTest:
    @staticmethod
    def text_sudoku(sudoku):
        # 测试序列化和反序列化
        serialized_data = sudoku.serialize()
        print(f"序列化后的数据: {serialized_data}")

        # 反序列化到新的 Sudoku 对象
        sudoku2 = Sudoku("")  # 创建空的数独对象
        sudoku2.deserialize(serialized_data)

        # 比较反序列化后的对象是否相等
        if sudoku == sudoku2:
            print("测试反序列化成功，两个对象相等！")
        else:
            print("测试反序列化失败，两个对象不相等！")

        # 测试深拷贝功能
        sudoku3 = Sudoku(sudoku.serialize())  # 通过序列化再创建对象，模拟深拷贝
        if sudoku == sudoku3:
            print("测试深拷贝成功，两个对象相等！")
        else:
            print("测试深拷贝失败，两个对象不相等！")

        # 解决数独问题
        sudoku.solve()

    @staticmethod
    def run_sudoku_test(input_value, description, expected_solution_count=1):
        # 运行数独测试，检查解的数量是否符合预期
        try:
            sudoku = Sudoku(input_value)
            Sudoku.solve(sudoku, False)
            ans = sudoku.solution_count
            if ans == expected_solution_count:
                print(f"测试通过: {description}")
            else:
                print(f"代码逻辑错误: {description}，解的数量不正确，应为 {expected_solution_count}，但得到 {ans}")
                print("程序结束。")
                exit(1)
        except Exception as e:
            print(f"发生报错: {description}，错误信息: {str(e)}")

def main():
    # lyw测试用例
    SudokuTest.run_sudoku_test(
        "017903600000080000900000507072010430000402070064370250701000065000030000005601720", "唯一解示例", 1)
    SudokuTest.run_sudoku_test(
        "006000200100700090000006075008002030020000060070400500640300000090004001002000400", "多解示例", 8)
    SudokuTest.run_sudoku_test(
        "530071000600050000098000060800600003400803001700020006000000080060000195000281000", "无解示例", 0)
    SudokuTest.run_sudoku_test(
        "ABCDE0179036000000900000507072010430000402070064370250701000065000030000005601720", "非法示例", -1)  # 非法输入
    SudokuTest.run_sudoku_test(
        "000000000000000000000000000000000000000000000000000000000000000000000000000000000", "全0示例", 101)
    SudokuTest.run_sudoku_test(
        "123456789", "长度不足示例", 101)
    SudokuTest.run_sudoku_test(
        "000000000000000000000000000000000000000000000000000000000000000000000000000000000000", "长度过大示例", 101)

    print("输入数独对象，要求长度为81位，且为数字0~9:")
    input_value = input()  # 输入数独字符串
    sudoku = Sudoku(input_value)
    SudokuTest.text_sudoku(sudoku)

if __name__ == "__main__":
    main()
