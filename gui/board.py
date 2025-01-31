import tkinter as tk

class SudokuGUI:
    def __init__(self, master):
        self.master = master
        self.cells = {}  # 存储所有输入框
        self.selected_number = None  # 当前选中的数字
        self.showing_candidates = False  # 是否正在显示候选数
        self.candidate_labels = {}  # 存储候选数标签
        self.create_board()
        
        # 绑定Esc键
        self.master.bind('<Escape>', self.on_escape)

    def create_board(self):
        """创建数独面板"""
        # 创建主框架
        main_frame = tk.Frame(
            self.master,
            bd=2,  # 添加边框
            relief=tk.SOLID  # 实线边框
        )
        main_frame.pack(padx=10, pady=10)
        
        # 创建9个3x3的区块框架
        for block_i in range(3):
            for block_j in range(3):
                # 创建3x3区块的框架
                block_frame = tk.Frame(
                    main_frame,
                    bd=2,  # 添加边框
                    relief=tk.SOLID  # 实线边框
                )
                block_frame.grid(
                    row=block_i, 
                    column=block_j,
                    padx=3,  # 区块之间的水平间距
                    pady=3   # 区块之间的垂直间距
                )
                
                # 在每个区块中创建3x3的单元格
                for i in range(3):
                    for j in range(3):
                        # 计算实际的行列索引
                        row = block_i * 3 + i
                        col = block_j * 3 + j
                        
                        # 创建单元格框架
                        cell_frame = tk.Frame(
                            block_frame,
                            borderwidth=1,
                            relief="solid"
                        )
                        cell_frame.grid(
                            row=i, 
                            column=j,
                            padx=1,  # 单元格之间的水平间距
                            pady=1   # 单元格之间的垂直间距
                        )
                        
                        # 创建输入框
                        cell = tk.Entry(
                            cell_frame,
                            width=2,
                            justify='center',
                            font=('Arial', 18)
                        )
                        cell.pack(padx=4, pady=4)  # 增加输入框内的边距
                        
                        # 绑定验证函数
                        cell.bind('<KeyPress>', lambda e, r=row, c=col: self.validate_input(e, r, c))
                        cell.bind('<FocusOut>', lambda e, r=row, c=col: self.on_focus_out(e, r, c))
                        cell.bind('<Button-1>', lambda e, r=row, c=col: self.on_cell_click(e, r, c))
                        
                        # 存储单元格引用
                        self.cells[(row, col)] = cell
        
        # 为每个单元格创建候选数显示框架
        for i in range(9):
            for j in range(9):
                cell_frame = self.cells[(i, j)].master
                # 创建候选数标签
                candidates_label = tk.Label(
                    cell_frame,
                    text="",
                    font=('Arial', 8),
                    justify='left',
                    wraplength=50
                )
                candidates_label.pack(side='bottom')
                candidates_label.pack_forget()  # 初始隐藏
                self.candidate_labels[(i, j)] = candidates_label

        # 设置单元格的样式
        self.configure_cell_styles()

    def configure_cell_styles(self):
        """配置单元格的样式"""
        for (row, col), cell in self.cells.items():
            # 设置背景色
            if (row // 3 + col // 3) % 2 == 0:
                cell.configure(bg='#F0F0F0')  # 浅灰色背景
            else:
                cell.configure(bg='white')
            
            # 设置初始前景色
            cell.configure(fg='black')
            
            # 设置其他样式
            cell.configure(
                insertbackground='gray',  # 光标颜色
                selectbackground='#0078D7',  # 选中文本的背景色
                selectforeground='white'  # 选中文本的前景色
            )
    
    def validate_input(self, event, i, j):
        # 只允许输入1-9的数字
        if event.char in '123456789':
            # 清除当前内容并允许新输入
            self.cells[(i, j)].delete(0, tk.END)
            return True
        elif event.keysym in ['BackSpace', 'Delete']:
            return True
        elif event.keysym in ['Left', 'Right', 'Up', 'Down', 'Tab']:
            return True
        else:
            return False
    
    def on_focus_out(self, event, i, j):
        # 确保单元格中只有一个数字
        content = self.cells[(i, j)].get()
        if len(content) > 1:
            self.cells[(i, j)].delete(0, tk.END)
            self.cells[(i, j)].insert(0, content[-1])
    
    def clear_board(self):
        # 清空所有单元格
        for cell in self.cells.values():
            cell.delete(0, tk.END)
    
    def get_board(self):
        # 获取当前数独板的状态
        board = []
        for i in range(9):
            row = []
            for j in range(9):
                value = self.cells[(i, j)].get()
                row.append(int(value) if value else 0)
            board.append(row)
        return board
    
    def set_cell(self, i, j, value, highlight=False):
        """设置单元格的值，可选择是否高亮显示"""
        self.cells[(i, j)].delete(0, tk.END)
        if value != 0:
            self.cells[(i, j)].insert(0, str(value))
            if highlight:
                self.cells[(i, j)].config(fg='red')
            else:
                self.cells[(i, j)].config(fg='black')
            
            # 如果当前有选中的数字，更新高亮显示
            if self.selected_number:
                self.highlight_number(self.selected_number)
    
    def clear_highlights(self, event=None):
        """清除所有高亮显示"""
        self.selected_number = None
        # 恢复原始背景色
        for (row, col), cell in self.cells.items():
            if (row // 3 + col // 3) % 2 == 0:
                cell.configure(bg='#F0F0F0')  # 浅灰色背景
            else:
                cell.configure(bg='white')
            cell.configure(fg='black')  # 恢复文字颜色

    def on_cell_click(self, event, row, col):
        """处理单元格点击事件"""
        cell = self.cells[(row, col)]
        content = cell.get()
        
        if content:  # 如果单元格有数字
            if self.selected_number == content:
                self.clear_highlights()
                self.selected_number = None
            else:
                self.selected_number = content
                self.highlight_number(content)
        else:  # 如果是空格
            self.show_candidates_analysis(row, col)
    
    def show_candidates_analysis(self, row, col):
        """显示指定位置的候选数分析"""
        self.clear_highlights()
        board = self.get_board()
        
        # 获取初始候选数
        initial_candidates = set(range(1, 10))
        row_numbers = set(board[row])
        col_numbers = set(board[i][col] for i in range(9))
        box_numbers = set()
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                box_numbers.add(board[i][j])
        
        # 准备分析文本
        analysis = []
        
        # 分析行排除
        row_excluded = initial_candidates & row_numbers
        if row_excluded:
            analysis.append(f"行排除: {sorted(row_excluded)}")
            self.highlight_row(row, '#FFE6E6')  # 浅红色
        
        # 分析列排除
        col_excluded = initial_candidates & col_numbers
        if col_excluded:
            analysis.append(f"列排除: {sorted(col_excluded)}")
            self.highlight_column(col, '#E6FFE6')  # 浅绿色
        
        # 分析宫格排除
        box_excluded = initial_candidates & box_numbers
        if box_excluded:
            analysis.append(f"宫格排除: {sorted(box_excluded)}")
            self.highlight_box(row, col, '#E6E6FF')  # 浅蓝色
        
        # 计算最终候选数
        final_candidates = initial_candidates - row_numbers - col_numbers - box_numbers
        
        # 显示分析结果
        analysis_text = "\n".join(analysis)
        if final_candidates:
            analysis_text += f"\n可选数字: {sorted(final_candidates)}"
        else:
            analysis_text += "\n无可用数字!"
        
        # 显示候选数标签
        self.show_analysis_popup(row, col, analysis_text)
        
        # 高亮显示当前单元格
        self.cells[(row, col)].configure(bg='#FFFFD0')  # 浅黄色
    
    def show_analysis_popup(self, row, col, text):
        """显示分析弹窗"""
        popup = tk.Toplevel(self.master)
        popup.title(f"位置({row+1},{col+1})的候选数分析")
        
        # 设置弹窗位置
        cell = self.cells[(row, col)]
        x = cell.winfo_rootx()
        y = cell.winfo_rooty()
        popup.geometry(f"+{x+50}+{y+50}")
        
        # 添加分析文本
        label = tk.Label(
            popup,
            text=text,
            justify='left',
            font=('Arial', 10),
            padx=10,
            pady=10
        )
        label.pack()
        
        # 点击任意位置关闭弹窗
        popup.bind('<Button-1>', lambda e: popup.destroy())
        
        # ESC键关闭弹窗
        popup.bind('<Escape>', lambda e: popup.destroy())
    
    def highlight_row(self, row, color):
        """高亮显示整行"""
        for j in range(9):
            if not self.cells[(row, j)].get():  # 只高亮空格
                self.cells[(row, j)].configure(bg=color)
    
    def highlight_column(self, col, color):
        """高亮显示整列"""
        for i in range(9):
            if not self.cells[(i, col)].get():  # 只高亮空格
                self.cells[(i, col)].configure(bg=color)
    
    def highlight_box(self, row, col, color):
        """高亮显示3x3宫格"""
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if not self.cells[(i, j)].get():  # 只高亮空格
                    self.cells[(i, j)].configure(bg=color)
    
    def on_escape(self, event):
        """处理ESC键事件"""
        self.clear_highlights()
        # 关闭所有弹窗
        for widget in self.master.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()

    def highlight_number(self, number):
        """高亮显示与选中数字相关的单元格"""
        self.clear_highlights()  # 先清除现有的高亮
        number = int(number)
        board = self.get_board()
        
        # 获取所有可能位置的信息
        for i in range(9):
            for j in range(9):
                cell = self.cells[(i, j)]
                current_value = board[i][j]
                
                if current_value == number:
                    # 相同数字显示黄色
                    cell.configure(bg='#FFE066')  # 黄色
                elif current_value != 0:
                    # 其他数字显示灰色
                    cell.configure(bg='#E0E0E0')  # 灰色
                else:
                    # 检查是否可以放置该数字
                    if self.can_place_number(board, i, j, number):
                        # 可以放置显示绿色
                        cell.configure(bg='#98FB98')  # 浅绿色
                    else:
                        # 不能放置显示红色
                        cell.configure(bg='#FFB6C1')  # 浅红色

    def can_place_number(self, board, row, col, number):
        """检查在指定位置是否可以放置数字"""
        # 检查行
        if number in board[row]:
            return False
            
        # 检查列
        if number in [board[i][col] for i in range(9)]:
            return False
            
        # 检查3x3宫格
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if board[i][j] == number:
                    return False
        return True 