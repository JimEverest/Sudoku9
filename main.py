import tkinter as tk
from tkinter import filedialog, messagebox
from gui.board import SudokuGUI
from solver.board import SudokuBoard
import csv

class SudokuApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("数独求解器")
        
        # 创建主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=10, pady=10)
        
        # 创建左侧数独板
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, padx=10)
        
        # 创建数独界面
        self.gui = SudokuGUI(left_frame)
        
        # 创建控制按钮
        self.create_controls(left_frame)
        
        # 创建右侧步骤显示面板
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        # 创建步骤显示区域
        self.create_step_display(right_frame)
        
        self.solver = None
        self.step_counter = 0  # 添加步骤计数器
        
    def create_controls(self, parent):
        control_frame = tk.Frame(parent)
        control_frame.pack(pady=10)
        
        # 添加导入按钮
        import_button = tk.Button(control_frame, text="导入CSV", command=self.import_csv)
        import_button.pack(side=tk.LEFT, padx=5)
        
        solve_button = tk.Button(control_frame, text="求解", command=self.solve)
        solve_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = tk.Button(control_frame, text="清空", command=self.clear)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        step_button = tk.Button(control_frame, text="下一步", command=self.next_step)
        step_button.pack(side=tk.LEFT, padx=5)
    
    def create_step_display(self, parent):
        """创建步骤显示面板"""
        # 创建标题
        tk.Label(parent, text="解题步骤", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # 创建文本显示区域
        self.step_text = tk.Text(parent, width=40, height=20, wrap=tk.WORD)
        self.step_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置标签样式
        self.step_text.tag_configure('method', font=('Arial', 10, 'bold'), foreground='blue')
        self.step_text.tag_configure('detail', font=('Arial', 10))
        
        # 添加滚动条
        scrollbar = tk.Scrollbar(parent, command=self.step_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.step_text.config(yscrollcommand=scrollbar.set)
        
        # 清除步骤按钮
        clear_steps_button = tk.Button(parent, text="清除步骤", command=self.clear_steps)
        clear_steps_button.pack(pady=5)
    
    def add_step(self, step_info):
        """添加一个解题步骤到显示面板"""
        self.step_counter += 1  # 增加步骤计数
        
        # 插入步骤编号
        self.step_text.insert(tk.END, f"\n步骤 {self.step_counter}:\n", 'method')
        
        # 插入使用的方法
        method_name = {
            'single_candidate': '唯一候选数法',
            'single_position': '唯一位置法',
            'naked_pairs': '显性数对法',
            'block_line_reduction': '区块摒除法'
        }.get(step_info['type'], '未知方法')
        
        self.step_text.insert(tk.END, f"使用方法：{method_name}\n", 'method')
        
        # 插入详细说明
        self.step_text.insert(tk.END, f"具体操作：{step_info['description']}\n", 'detail')
        
        # 插入推理依据
        if 'reason' in step_info:
            self.step_text.insert(tk.END, f"推理依据：{step_info['reason']}\n", 'detail')
        
        self.step_text.see(tk.END)  # 自动滚动到最新步骤
    
    def clear_steps(self):
        """清除所有步骤"""
        self.step_text.delete(1.0, tk.END)
        self.step_counter = 0  # 重置步骤计数器
    
    def import_csv(self):
        """导入CSV文件"""
        file_path = filedialog.askopenfilename(
            title="选择CSV文件",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            # 尝试不同的编码方式
            encodings = ['utf-8-sig', 'utf-8', 'gbk']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        reader = csv.reader(file)
                        board = []
                        for row in reader:
                            # 转换每一行的数据，空值转为0
                            number_row = []
                            for cell in row:
                                # 移除所有不可见字符
                                cell = ''.join(c for c in cell if c.isprintable()).strip()
                                if cell == '':
                                    number_row.append(0)
                                else:
                                    try:
                                        num = int(cell)
                                        # 允许0-9的数字
                                        if 0 <= num <= 9:
                                            number_row.append(num)
                                        else:
                                            messagebox.showerror("错误", f"数值必须在1-9之间: {cell}")
                                            return
                                    except ValueError:
                                        # 跳过无效的数值，视为空格
                                        number_row.append(0)
                        
                            # 确保每行都有9个数字，不足的补0
                            while len(number_row) < 9:
                                number_row.append(0)
                            # 如果超过9个数字，只取前9个
                            number_row = number_row[:9]
                            board.append(number_row)
                        
                        # 确保有9行数据，不足的补充空行
                        while len(board) < 9:
                            board.append([0] * 9)
                        # 如果超过9行，只取前9行
                        board = board[:9]
                        
                        # 清空当前数独板并填入新数据
                        self.clear()
                        for i in range(9):
                            for j in range(9):
                                if board[i][j] != 0:
                                    self.gui.set_cell(i, j, board[i][j])
                        
                        # 如果成功读取，就跳出循环
                        break
                except UnicodeDecodeError:
                    # 如果是最后一种编码方式还失败，则报错
                    if encoding == encodings[-1]:
                        raise
                    continue
                    
        except Exception as e:
            messagebox.showerror("错误", f"导入CSV文件时出错：{str(e)}")
    
    def solve(self):
        """完整求解数独"""
        board = self.gui.get_board()
        self.solver = SudokuBoard(board)
        self.clear_steps()
        
        step_count = 1
        # 不断执行单步求解直到完成
        while not self.solver.is_solved():
            self.gui.clear_highlights()  # 清除之前的高亮
            if not self.solver.solve_step():
                self.add_step({
                    'type': 'error',
                    'description': '无法找到下一步解法！'
                })
                tk.messagebox.showinfo("提示", "当前无法找到下一步解法！")
                break
            
            # 更新界面
            for step in self.solver.solution_steps:
                pos = step['position']
                value = step['value']
                self.gui.set_cell(pos[0], pos[1], value, highlight=True)
                self.add_step(step)
                
            self.solver.solution_steps.clear()
    
    def next_step(self):
        """执行单步求解"""
        if self.solver is None:
            board = self.gui.get_board()
            self.solver = SudokuBoard(board)
            self.clear_steps()
        
        self.gui.clear_highlights()  # 清除之前的高亮
        
        if not self.solver.is_solved():
            if self.solver.solve_step():
                # 更新界面显示最后一步的结果
                step = self.solver.solution_steps[-1]
                pos = step['position']
                value = step['value']
                self.gui.set_cell(pos[0], pos[1], value, highlight=True)
                self.add_step(step)
                
                self.solver.solution_steps.clear()
            else:
                self.add_step({
                    'type': 'error',
                    'description': '无法找到下一步解法！'
                })
                tk.messagebox.showinfo("提示", "当前无法找到下一步解法！")
        else:
            self.add_step({
                'type': 'complete',
                'description': '数独已解决！'
            })
            tk.messagebox.showinfo("提示", "数独已解决！")
    
    def clear(self):
        self.gui.clear_board()
        self.clear_steps()
        self.solver = None
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SudokuApp()
    app.run() 