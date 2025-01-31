class SudokuBoard:
    def __init__(self, board=None):
        # 初始化9x9的数独板
        self.board = [[0]*9 for _ in range(9)] if board is None else board
        # 存储每个格子的候选数
        self.candidates = {}
        self.initialize_candidates()
        # 存储解题步骤
        self.solution_steps = []
        
    def initialize_candidates(self):
        """初始化每个空格的候选数"""
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    self.candidates[(i, j)] = self.get_candidates(i, j)
    
    def get_candidates(self, row, col):
        """获取指定位置的所有候选数"""
        if self.board[row][col] != 0:
            return set()
            
        used_numbers = set()
        # 检查行
        used_numbers.update(self.board[row])
        # 检查列
        used_numbers.update(self.board[i][col] for i in range(9))
        # 检查3x3宫格
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                used_numbers.add(self.board[i][j])
                
        return set(range(1, 10)) - used_numbers
    
    def is_valid(self, row, col, num):
        """检查在指定位置放置数字是否有效"""
        # 检查行
        if num in self.board[row]:
            return False
            
        # 检查列
        if num in [self.board[i][col] for i in range(9)]:
            return False
            
        # 检查3x3宫格
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.board[i][j] == num:
                    return False
        return True
    
    def find_empty(self):
        """找到一个空位置"""
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return i, j
        return None
    
    def solve_step(self):
        """执行一步求解，返回是否找到解决方案"""
        # 1. 尝试唯一候选数法
        if self.solve_single_candidate():
            return True
            
        # 2. 尝试唯一位置法
        if self.solve_single_position():
            return True
            
        # 3. 尝试显性数对法
        if self.solve_naked_pairs():
            return True
            
        # 4. 尝试区块摒除法
        if self.solve_block_line_reduction():
            return True
            
        # 如果没有找到简单的解法，返回False
        return False
    
    def solve_single_candidate(self):
        """唯一候选数法：查找只有一个候选数的格子"""
        for pos, candidates in self.candidates.items():
            if len(candidates) == 1:
                num = candidates.pop()
                row, col = pos
                self.board[row][col] = num
                self.solution_steps.append({
                    'type': 'single_candidate',
                    'position': pos,
                    'value': num,
                    'description': f'在位置({row+1},{col+1})填入数字{num}',
                    'reason': f'该位置只有一个候选数{num}，其他数字都被行、列或宫格中的数字排除'
                })
                self.update_candidates()
                return True
        return False
    
    def solve_single_position(self):
        """唯一位置法：在行/列/宫中查找只出现一次的候选数"""
        # 检查每一行
        for row in range(9):
            for num in range(1, 10):
                positions = []
                for col in range(9):
                    if self.board[row][col] == 0 and num in self.candidates.get((row, col), set()):
                        positions.append((row, col))
                if len(positions) == 1:
                    pos = positions[0]
                    self.board[pos[0]][pos[1]] = num
                    self.solution_steps.append({
                        'type': 'single_position',
                        'position': pos,
                        'value': num,
                        'description': f'在第{row+1}行中，数字{num}只能放在位置({pos[0]+1},{pos[1]+1})'
                    })
                    self.update_candidates()
                    return True
        
        # 检查每一列
        for col in range(9):
            for num in range(1, 10):
                positions = []
                for row in range(9):
                    if self.board[row][col] == 0 and num in self.candidates.get((row, col), set()):
                        positions.append((row, col))
                if len(positions) == 1:
                    pos = positions[0]
                    self.board[pos[0]][pos[1]] = num
                    self.solution_steps.append({
                        'type': 'single_position',
                        'position': pos,
                        'value': num,
                        'description': f'在第{col+1}列中，数字{num}只能放在位置({pos[0]+1},{pos[1]+1})'
                    })
                    self.update_candidates()
                    return True
        
        # 检查每个3x3宫格
        for box_row in range(3):
            for box_col in range(3):
                for num in range(1, 10):
                    positions = []
                    for i in range(3):
                        for j in range(3):
                            row, col = box_row*3 + i, box_col*3 + j
                            if self.board[row][col] == 0 and num in self.candidates.get((row, col), set()):
                                positions.append((row, col))
                    if len(positions) == 1:
                        pos = positions[0]
                        self.board[pos[0]][pos[1]] = num
                        box_num = box_row * 3 + box_col + 1
                        self.solution_steps.append({
                            'type': 'single_position',
                            'position': pos,
                            'value': num,
                            'description': f'在第{box_num}宫格中，数字{num}只能放在位置({pos[0]+1},{pos[1]+1})'
                        })
                        self.update_candidates()
                        return True
        
        return False
    
    def solve_naked_pairs(self):
        """显性数对法：找出同一行/列/宫中两个格子具有相同的两个候选数"""
        # 检查每一行
        for row in range(9):
            pairs = {}
            for col in range(9):
                if self.board[row][col] == 0:
                    candidates = self.candidates.get((row, col), set())
                    if len(candidates) == 2:
                        candidates = tuple(sorted(candidates))
                        if candidates in pairs:
                            # 找到数对，从同一行的其他格子中删除这两个数字
                            pair_col = pairs[candidates]
                            removed = False
                            for other_col in range(9):
                                if other_col != col and other_col != pair_col and self.board[row][other_col] == 0:
                                    other_candidates = self.candidates.get((row, other_col), set())
                                    original_len = len(other_candidates)
                                    other_candidates -= set(candidates)
                                    if len(other_candidates) < original_len:
                                        removed = True
                                        self.candidates[(row, other_col)] = other_candidates
                            
                            if removed:
                                self.solution_steps.append({
                                    'type': 'naked_pairs',
                                    'position': [(row, pair_col), (row, col)],
                                    'value': list(candidates),
                                    'description': f'在第{row+1}行找到数对{candidates}，可以从其他格子删除这些数字'
                                })
                                return True
                        else:
                            pairs[candidates] = col
        
        # TODO: 添加列和宫格的检查
        return False
    
    def solve_block_line_reduction(self):
        """区块摒除法：当某个数字在一个宫格中只能出现在某一行或列时，该数字在此行或列的其他宫格中必须被删除"""
        for box_row in range(3):
            for box_col in range(3):
                for num in range(1, 10):
                    # 检查数字在当前宫格中可能的位置
                    positions = []
                    for i in range(3):
                        for j in range(3):
                            row, col = box_row*3 + i, box_col*3 + j
                            if self.board[row][col] == 0 and num in self.candidates.get((row, col), set()):
                                positions.append((row, col))
                    
                    if positions and all(pos[0] == positions[0][0] for pos in positions):
                        # 所有位置在同一行
                        row = positions[0][0]
                        removed = False
                        # 检查同一行的其他宫格
                        for other_box_col in range(3):
                            if other_box_col != box_col:
                                for j in range(3):
                                    col = other_box_col*3 + j
                                    if self.board[row][col] == 0 and num in self.candidates.get((row, col), set()):
                                        self.candidates[(row, col)].remove(num)
                                        removed = True
                    
                        if removed:
                            self.solution_steps.append({
                                'type': 'block_line_reduction',
                                'position': positions,
                                'value': num,
                                'description': f'数字{num}在第{box_row*3+box_col+1}宫格中只能出现在第{row+1}行，'
                                            f'因此可以从第{row+1}行的其他宫格中删除该数字'
                            })
                            return True
                    
                    # TODO: 添加列的检查
        return False
    
    def update_candidates(self):
        """更新所有空格的候选数"""
        self.candidates.clear()
        self.initialize_candidates()
    
    def is_solved(self):
        """检查数独是否已解决"""
        return all(0 not in row for row in self.board) 