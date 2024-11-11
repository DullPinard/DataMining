import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QLineEdit, QTextEdit, QLabel, QDialog, QVBoxLayout,
    QFormLayout, QDialogButtonBox, QMessageBox, QTableWidget, QTableWidgetItem,
    QMenu, QAction
)
from PyQt5.QtCore import Qt
import numpy as np
from AssociationRules import AssociationRulesSolve
from itertools import product
from utils import get_rules_comb, get_2dlist_print, comb_same_lines


update_str = \
"""**v1.2版本更新内容如下：**
一、修复了判定树出现冗余节点的问题。
二、优化了数据读取获得列的方式，添加了统计列关键字的设置。
三、支持关联规则生成的范围设置，可以添加不同变量的范围从而更加便捷。
四、优化了连续两次计算判定树结果相同的bug
**v1.3版本更新内容如下：**
一、修复了计算强关联规则时对于计算上一阶阈值都不满足要求的时候下一阶还会输出强关联规则。
二、添加了示例数据的读取。
python写的exe打包都比较大，请见谅=`~`=
"""

help_str = \
"""***使用说明***
一、首先准备好数据，然后按照列合并成一列输入到数据输入栏，设置统计数列的关键字（一般为Count），然后点击读取数据。
二、设置两个阈值，然后在右下角表格中添加关联规则，按右键添加，可以设置不同阶数的关联规则，每个变量也可以限定取值范围（本列构成的集合），all表示输入数据的所有列。
三、点击“开始计算（强关联规则）”会弹出对话框结果，所有结果全部抄上即可满分
四、基于信息增益的判定树求取，先选择判定树期望的输出，然后点击计算“开始计算（判定树）”即可
"""

class TextDisplayDialog(QDialog):
    def __init__(self, text, diagname):
        super().__init__()
        self.setWindowTitle(diagname)
        self.setGeometry(200, 200, 1000, 1000)
        
        # 创建一个 QTextEdit 实例并设置文本
        self.text_edit = QTextEdit(self)
        self.text_edit.setText(text)
        self.text_edit.setReadOnly(True)  # 设置为只读模式
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.text_edit.setLineWrapMode(QTextEdit.NoWrap)
        
        # 创建一个垂直布局并将 QTextEdit 添加进去
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        
        # 设置窗口的布局
        self.setLayout(layout)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("关联规则挖掘答案生成v1.2 by CMJ")
        
        # 左侧布局
        left_layout = QVBoxLayout()
        self.load_data_button = QPushButton("读取数据")
        self.calculate_button1 = QPushButton("开始计算\n（强关联规则）")
        self.calculate_button2 = QPushButton("开始计算\n（判定树）")
        self.example_button = QPushButton("示例数据")
        self.help_button = QPushButton("帮助")
        self.load_data_button.clicked.connect(self.load_data)
        self.calculate_button1.clicked.connect(self.calculate1)
        self.calculate_button2.clicked.connect(self.calculate2)
        self.help_button.clicked.connect(self.help)
        self.example_button.clicked.connect(self.load_example)
        # self.dropdown1 = QComboBox()
        self.dropdown2 = QComboBox()

        self.input2 = QLineEdit()
        self.input2.setText('0.25')
        self.input3 = QLineEdit()
        self.input3.setText('0.5')
        # self.input4 = QLineEdit()
        # self.input4.setText('2')
        self.input5 = QLineEdit()
        self.input6 = QLineEdit()
        self.input_count = QLineEdit()
        self.input_count.setText('Count')
        self.label_count = QLabel('统计数列的关键字：')
        # self.label_SAR = QLabel('强关联规则输出列：')
        self.label_DTR = QLabel('判定树输出列：')
        self.label_state = QLabel('等待数据读取...')
        self.label_state.setStyleSheet("""
                            QLabel {
                                border: 2px solid #000;
                                padding: 5px;
                                border-radius: 5px;
                            }
                        """)

        self.display_textbox1 = QTextEdit()
        
        self.label0 = QLabel('输入数据：')
        self.label2 = QLabel('最小支持度阈值：')
        self.label3 = QLabel('最小置信度阈值：')
        # self.label4 = QLabel('解频繁几项集：')
        self.label5 = QLabel('作者v:\n C13333317043')

        
        left_layout.addWidget(self.label0)
        left_layout.addWidget(self.display_textbox1)
        left_layout.addWidget(self.load_data_button)
        left_layout.addWidget(self.label_count)
        left_layout.addWidget(self.input_count)

        # left_layout.addWidget(self.label_SAR)
        # left_layout.addWidget(self.dropdown1)
        
        left_layout.addWidget(self.label2)
        left_layout.addWidget(self.input2)
        left_layout.addWidget(self.label3)
        left_layout.addWidget(self.input3)
        # left_layout.addWidget(self.label4)
        # left_layout.addWidget(self.input4)
        left_layout.addWidget(self.calculate_button1)
        left_layout.addWidget(self.label_DTR)
        left_layout.addWidget(self.dropdown2)
        left_layout.addWidget(self.calculate_button2)
        
        left_layout.addWidget(self.example_button)
        left_layout.addWidget(self.label5)

        
        # 右侧布局
        right_layout = QVBoxLayout()
        self.label_table = QLabel('选择关联规则对应的集合：')
        self.label_data = QLabel('数据读取的结果：')
        # 添加选择的表格
        self.table_widget = QTableWidget(self)
        # self.table_widget.setRowCount(1)
        # self.table_widget.setColumnCount(1)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)

        self.display_textbox2 = QTextEdit()
        self.display_textbox2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.display_textbox2.setLineWrapMode(QTextEdit.NoWrap)
        self.display_textbox2.setReadOnly(1)
        # right_layout.addWidget(self.display_textbox1)

        right_layout.addWidget(self.label_state)
        right_layout.addWidget(self.label_data)
        right_layout.addWidget(self.display_textbox2)
        right_layout.addWidget(self.label_table)
        right_layout.addWidget(self.table_widget)
        right_layout.addWidget(self.help_button)
        
        
        # 主布局
        # main_layout = QHBoxLayout()
        # main_layout.addLayout(left_layout)
        # main_layout.addLayout(right_layout)

        self.setFixedSize(950, 700)

        # self.setLayout(main_layout)

        left_widget = QWidget()
        right_widget = QWidget()
        
        left_widget.setLayout(left_layout)
        right_widget.setLayout(right_layout)
        
        # 设置固定大小
        left_widget.setFixedWidth(200)
        right_widget.setFixedWidth(700)
        
        # 将 QWidget 添加到主布局中
        main_layout = QHBoxLayout()
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
        # 设置主窗口的布局
        self.setLayout(main_layout)
        
        # 设置窗口标题和大小，并使其大小不可改变
        # self.setWindowTitle('布局比例示例')
        # self.setFixedSize(1000, 700)  # 设置固定大小
        
        self.show()

        QMessageBox.question(self, '更新内容', update_str, QMessageBox.Ok, QMessageBox.Ok)
        QMessageBox.question(self, '使用帮助', help_str, QMessageBox.Ok, QMessageBox.Ok)
        self.success = False

    def help(self):
        QMessageBox.question(self, '使用帮助', help_str, QMessageBox.Ok, QMessageBox.Ok)

    def load_data(self):
        # dialog = DataInputDialog(self)
        # if dialog.exec_() == QDialog.Accepted:
        #     data1 = dialog.getInputs()
        #     self.dropdown.addItem(data1)
        #     self.display_textbox1.setText(data1)
            # self.display_textbox2.setText(data2)
        count_label = self.input_count.text()
        self.count_label = count_label
        txt_now = self.display_textbox1.toPlainText()
        lines = txt_now.splitlines()
        lines = [s.strip() for s in lines if s.strip()]
        cols = -1

        try:
            cols = len(lines) // (len(lines) - lines.index(count_label))
            out_mat = np.array(lines).reshape(cols, -1)
        except:
            print(count_label)
            self.label_state.setText(f'未找到统计数关键字：{count_label}')
            QMessageBox.question(self, '提示', f'未找到统计数关键字：{count_label}', QMessageBox.Ok, QMessageBox.Ok)
            return 
        
        try:
            self.SAR = AssociationRulesSolve(cols, data=lines)
        except:
            self.label_state.setText(f'数据读取失败！')
            QMessageBox.question(self, '提示', '数据读取失败！', QMessageBox.Ok, QMessageBox.Ok)
            return
        if self.SAR.success:
            print('创建成功')
            self.label_state.setText(f'数据读取成功！表格列数：{cols}')
            


        # self.dropdown1.clear()
        self.dropdown2.clear()
        for head in self.SAR.heads[:-1]:
            # self.dropdown1.addItem(head)
            self.dropdown2.addItem(head)
        # cols = int(self.input1.text())
        # s_th = float(self.input2.text())
        # c_th = float(self.input3.text())


        out_mat_str = get_2dlist_print(out_mat.T)
        self.display_textbox2.setText(out_mat_str)
        # SAR_deg = float(self.input4.text())
        # SAR_id = float(self.input5.text())
        # self.ARS = AssociationRulesSolve(s_th, c_th, SAR_id, SAR_deg)
        print(lines)
        # print(self.display_textbox1.toPlainText(), cols, s_th, c_th, SAR_deg, SAR_id)

        self.success = True
        self.cols = cols
        self.table_rows = 1
        # 初始化选中关联规则的表格
        self.table_widget.setRowCount(cols-1)
        self.table_widget.setColumnCount(cols-1)

        for i in range(self.table_widget.rowCount()):
            for j in range(self.table_widget.columnCount()):
                item = QTableWidgetItem("")
                self.table_widget.setItem(i, j, item)

        for i in range(self.table_widget.rowCount()):
            self.table_widget.setRowHeight(i, 10)  # 设置行高为30像素
        # for j in range(self.table_widget.columnCount()):
        #     self.table_widget.setColumnWidth(j, 100)  # 设置列宽为100像素
        # self.table_widget.setHorizontalHeaderLabels([f'P_{i+1}[S, w]' for i in range(cols)])
        self.table_widget.setHorizontalHeaderLabels([f'' for i in range(cols-1)])
        self.table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self.show_context_menu)

        QMessageBox.question(self, '提示', f'数据读取成功！表格列数：{cols}', QMessageBox.Ok, QMessageBox.Ok)

    def show_context_menu(self, position):

        index = self.table_widget.indexAt(position)
        if not index.isValid():
            return

        # 检查该列已经存在的
        col = index.column()
        heads_his = []
        for i in range(self.table_widget.rowCount()):
            itemtxt = self.table_widget.item(i, col).text()
            if itemtxt:
                heads_his.append(itemtxt)

        # 创建菜单
        menu = QMenu()

        # 添加一些选项
        # actions = ["Option1", "Option2", "Option3", "Delete"]
        if 'all' in heads_his:
            actions = ["删除", '删除本列', '删除全部']
        else:
            actions = self.SAR.heads + ['all', "删除", '删除本列', '删除全部']
            for hh in heads_his:
                actions.pop(actions.index(hh))

        

        for action_text in actions:
            action = QAction(action_text, self)
            action.triggered.connect(lambda checked, text=action_text: self.menu_action(text, index))
            menu.addAction(action)

        # 显示菜单
        menu.exec_(self.table_widget.viewport().mapToGlobal(position))


        # 更新表头
        col_notnan = []
        for j in range(self.table_widget.columnCount()):
        
            rows = []
            for i in range(self.table_widget.rowCount()):
                itemtxt = self.table_widget.item(i, j).text()
                if itemtxt:
                    rows.append(itemtxt)

            if rows:
                col_notnan.append(j)

        

        table_head = ['' for i in range(self.cols)]
        for i, col in enumerate(col_notnan):
            label_now = f'P_{i+1}[S, w]'
            if i == len(col_notnan) - 1 and len(col_notnan) > 1:
                label_now = '=>' + label_now
            elif i != 0:
                label_now = '^ ' + label_now 
                
            table_head[col] = label_now
            
        self.table_widget.setHorizontalHeaderLabels(table_head)


        # 如果加入了 all 删除其他的把all放到第一个
        col = index.column()
        heads_his = []
        for i in range(self.table_widget.rowCount()):
            itemtxt = self.table_widget.item(i, col).text()
            if itemtxt:
                heads_his.append(itemtxt)

        # print(heads_his)
        if 'all' in heads_his:
            for i in range(self.table_widget.rowCount()):
                
                item = QTableWidgetItem("all" if i == 0 else "")
                self.table_widget.setItem(i, col, item)

    def menu_action(self, text, index):
        if text == "删除":
            # 清空单元格
            self.table_widget.item(index.row(), index.column()).setText("")

        elif text == "删除本列":
            for i in range(self.table_widget.rowCount()):
                item = QTableWidgetItem("")
                self.table_widget.setItem(i, index.column(), item)

        elif text == "删除全部":
            for i in range(self.table_widget.rowCount()):
                for j in range(self.table_widget.columnCount()):
                    item = QTableWidgetItem("")
                    self.table_widget.setItem(i, j, item)
        else:
            # 设置单元格内容
            self.table_widget.item(index.row(), index.column()).setText(text)

        # self.print_table_contents()

    def calculate1(self):
        if not self.success:
            QMessageBox.question(self, '提示', '数据未读取！', QMessageBox.Ok, QMessageBox.Ok)
            return

        try:
            s_th = float(self.input2.text())
            c_th = float(self.input3.text())
            # SAR_deg = int(self.input4.text())
            # SAR_id = self.dropdown1.currentIndex()
        except:
            self.label_state.setText(f'输入参数格式错误！')
            QMessageBox.question(self, '提示', '输入参数格式错误！', QMessageBox.Ok, QMessageBox.Ok)
            return
        
        if not (0 < s_th < 1):
            QMessageBox.question(self, '提示', '最小支持度阈值的取值范围要在0~1之间', QMessageBox.Ok, QMessageBox.Ok)
            return
        
        if not (0 < c_th < 1):
            QMessageBox.question(self, '提示', '最小置信度阈值的取值范围要在0~1之间', QMessageBox.Ok, QMessageBox.Ok)
            return
        # try:
        # 读取表格的行列
        cols_ids = []
        for j in range(self.table_widget.columnCount()):
            col_ids = []
            for i in range(self.table_widget.rowCount()):
                ij_str = self.table_widget.item(i, j).text()
                if ij_str not in col_ids and ij_str != '' and ij_str != 'all':
                    col_ids.append(self.SAR.heads.index(ij_str))

                if ij_str == 'all':
                    col_ids = [i for i in range(len(self.SAR.heads) - 1)]

            if col_ids:
                cols_ids.append(col_ids)

        print(cols_ids)
        SAR_deg = len(cols_ids) - 1
        if SAR_deg < 2:
            QMessageBox.question(self, '提示', '只能求解频繁二项集及以上的项集！', QMessageBox.Ok, QMessageBox.Ok)
            return 
        
        if SAR_deg > self.cols - 1:
            QMessageBox.question(self, '提示', f'最多求解频繁{self.cols - 1}项集！', QMessageBox.Ok, QMessageBox.Ok)
            return 


        # 获取所有的组合模式
        list_comb = get_rules_comb(cols_ids)
        if not list_comb:
            QMessageBox.question(self, '提示', '输入的规则模式无任何可能的组合！', QMessageBox.Ok, QMessageBox.Ok)
            return

        count_label = self.input_count.text()
        if count_label != self.SAR.heads[-1]:
            self.label_state.setText(f'未找到统计数关键字：{count_label}')
            QMessageBox.question(self, '提示', f'未找到统计数关键字：{count_label}', QMessageBox.Ok, QMessageBox.Ok)
            return 

        rules = []
        infos = []
        info_now = ''
        for comb in list_comb:
            # print(comb)
            data_now = []
            for cbnum in comb:
                data_now.append([self.SAR.heads[cbnum]] + self.SAR.data[cbnum])

            # 输出此类别的表头：
            data_now.append([count_label] + self.SAR.data[-1])
            if len(list_comb) > 1:
                info_now = info_now + '讨论 '
                for i, cbnum in enumerate(comb):
                    label_now = f'{self.SAR.heads[cbnum]}[S, w]'
                    if i == len(comb) - 1 and len(comb) > 1:
                        label_now = '=>' + label_now
                    elif i != 0:
                        label_now = '^ ' + label_now 

                    info_now = info_now + label_now

                info_now = info_now + ' 的情况：\n'
                
                # 合并相同行
                last_labels = [data_now[i][1:] for i in range(len(data_now)) if i < len(data_now) - 1]
                last_labels = np.array(last_labels).T
                last_counts = np.array([data_now[-1][1:]]).T.astype('int')
                last_labels, last_counts = comb_same_lines(np.array(last_labels), last_counts)
                last_labels = np.array(last_labels).T.tolist()
                last_counts = np.array(last_counts).T.astype('int').tolist()
                data_now_new = last_labels + last_counts
                for i in range(len(data_now)):
                    data_now_new[i] = [data_now[i][0]] + data_now_new[i]

                data_now = data_now_new
                info_now += '\n' + get_2dlist_print(np.array(data_now).T.tolist()) + '\n'

            # print(data_now)
            SAR_now = AssociationRulesSolve(len(data_now), data=data_now)
            SAR_now.solveQ1(s_th=s_th,    
                            c_th=c_th,              
                            SAR_id=len(comb) - 1,     
                            SAR_deg=len(comb) - 1,        # 解频繁n项集 
                            )
            info_now = info_now + SAR_now.info + '\n'
            info_now = info_now + '------------------------------------------------------------\n'
            rules = rules + SAR_now.selected_segs

        if len(list_comb) > 1:
            if not rules:
                info_now = info_now + '综合以上所有情况，未找到任何符合要求的强关联规则。\n'    
            else:
                info_now = info_now + '综合以上所有情况，所有符合要求的强关联规则如下：\n' 
                for rule in rules:
                    print(rule)
                    info_now = info_now + rule + '\n'

        dialog1 = TextDisplayDialog(info_now, "第一题答案")
        dialog1.exec_()

    def calculate2(self):
        if not self.success:
            QMessageBox.question(self, '提示', '数据未读取！', QMessageBox.Ok, QMessageBox.Ok)
            return

        try:
            DTR_id = self.dropdown2.currentIndex()
        except:
            self.label_state.setText(f'输入参数格式错误！')
            QMessageBox.question(self, '提示', '输入参数格式错误！', QMessageBox.Ok, QMessageBox.Ok)
            return
        
        try:
            q2_res = self.SAR.solveQ2(DTR_id=DTR_id)
            # print(q2_res)
            
            res = q2_res
            dialog1 = TextDisplayDialog(res, "第二题答案")
            dialog1.exec_()
        except:
            self.label_state.setText(f'计算失败，对象未创建！')
            QMessageBox.question(self, '提示', '计算失败，对象未创建！', QMessageBox.Ok, QMessageBox.Ok)

    def load_example(self):

        with open('./data/1_5.csv', 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()

        lines = [s.strip() for s in lines if s.strip()]

        count_label = 'Count'
        try:
            cols = len(lines) // (len(lines) - lines.index(count_label))
            out_mat = np.array(lines).reshape(cols, -1)
        except:
            print(count_label)
            self.label_state.setText(f'未找到统计数关键字：{count_label}')
            QMessageBox.question(self, '提示', f'未找到统计数关键字：{count_label}', QMessageBox.Ok, QMessageBox.Ok)
            return 
        
        try:
            self.SAR = AssociationRulesSolve(cols, data=lines)
        except:
            self.label_state.setText(f'数据读取失败！')
            QMessageBox.question(self, '提示', '数据读取失败！', QMessageBox.Ok, QMessageBox.Ok)
            return
        if self.SAR.success:
            print('创建成功')
            self.label_state.setText(f'数据读取成功！表格列数：{cols}')
            


        # self.dropdown1.clear()
        self.dropdown2.clear()
        for head in self.SAR.heads[:-1]:
            # self.dropdown1.addItem(head)
            self.dropdown2.addItem(head)
        # cols = int(self.input1.text())
        # s_th = float(self.input2.text())
        # c_th = float(self.input3.text())


        out_mat_str = get_2dlist_print(out_mat.T)
        self.display_textbox2.setText(out_mat_str)
        # SAR_deg = float(self.input4.text())
        # SAR_id = float(self.input5.text())
        # self.ARS = AssociationRulesSolve(s_th, c_th, SAR_id, SAR_deg)
        print(lines)
        # print(self.display_textbox1.toPlainText(), cols, s_th, c_th, SAR_deg, SAR_id)

        self.success = True
        self.cols = cols
        self.table_rows = 1
        # 初始化选中关联规则的表格
        self.table_widget.setRowCount(cols-1)
        self.table_widget.setColumnCount(cols-1)

        for i in range(self.table_widget.rowCount()):
            for j in range(self.table_widget.columnCount()):
                item = QTableWidgetItem("")
                self.table_widget.setItem(i, j, item)

        for i in range(self.table_widget.rowCount()):
            self.table_widget.setRowHeight(i, 10)  # 设置行高为30像素
        # for j in range(self.table_widget.columnCount()):
        #     self.table_widget.setColumnWidth(j, 100)  # 设置列宽为100像素
        # self.table_widget.setHorizontalHeaderLabels([f'P_{i+1}[S, w]' for i in range(cols)])
        self.table_widget.setHorizontalHeaderLabels([f'' for i in range(cols-1)])
        self.table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self.show_context_menu)


        self.input2.setText('0.2')
        self.input3.setText('0.75')
        
        col_notnan = [0, 1, 2, 3]
        table_head = ['' for i in range(self.cols)]
        for i, col in enumerate(col_notnan):
            label_now = f'P_{i+1}[S, w]'
            if i == len(col_notnan) - 1 and len(col_notnan) > 1:
                label_now = '=>' + label_now
            elif i != 0:
                label_now = '^ ' + label_now 
                
            table_head[col] = label_now
            
        self.table_widget.setHorizontalHeaderLabels(table_head)

        self.table_widget.item(0, 0).setText('all')
        self.table_widget.item(0, 1).setText('all')
        self.table_widget.item(0, 2).setText('Age')
        self.table_widget.item(0, 3).setText('all')

        QMessageBox.question(self, '提示', f'示例数据导入成功！表格列数：{cols}', QMessageBox.Ok, QMessageBox.Ok)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
