import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QLineEdit, QTextEdit, QLabel, QDialog, QVBoxLayout,
    QFormLayout, QDialogButtonBox, QMessageBox
)
from PyQt5.QtCore import Qt
import numpy as np
from AssociationRules import AssociationRulesSolve, get_2dlist_print


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
        self.setWindowTitle("关联规则挖掘答案生成v1.1 by CMJ")
        
        # 左侧布局
        left_layout = QVBoxLayout()
        self.load_data_button = QPushButton("读取数据")
        self.calculate_button1 = QPushButton("开始计算（强关联规则）")
        self.calculate_button2 = QPushButton("开始计算（判定树）")
        self.load_data_button.clicked.connect(self.load_data)
        self.calculate_button1.clicked.connect(self.calculate1)
        self.calculate_button2.clicked.connect(self.calculate2)
        self.dropdown1 = QComboBox()
        self.dropdown2 = QComboBox()

        self.input2 = QLineEdit()
        self.input2.setText('0.25')
        self.input3 = QLineEdit()
        self.input3.setText('0.5')
        self.input4 = QLineEdit()
        self.input4.setText('2')
        self.input5 = QLineEdit()
        self.input6 = QLineEdit()
        self.input_count = QLineEdit()
        self.input_count.setText('Count')
        self.label_count = QLabel('统计数列的关键字：')
        self.label_SAR = QLabel('强关联规则输出的列：')
        self.label_DTR = QLabel('判定树目标输出列：')
        self.label_state = QLabel('等待数据读取...')

        
        self.label0 = QLabel('右侧输入数据，\n按列合并成一列')
        self.label2 = QLabel('最小支持度阈值：')
        self.label3 = QLabel('最小置信度阈值：')
        self.label4 = QLabel('解频繁几项集：')
        self.label5 = QLabel('作者v C13333317043')

        left_layout.addWidget(self.label0)
        left_layout.addWidget(self.load_data_button)
        left_layout.addWidget(self.label_count)
        left_layout.addWidget(self.input_count)


        left_layout.addWidget(self.label_SAR)
        left_layout.addWidget(self.dropdown1)
        left_layout.addWidget(self.label_state)
        left_layout.addWidget(self.label2)
        left_layout.addWidget(self.input2)
        left_layout.addWidget(self.label3)
        left_layout.addWidget(self.input3)
        left_layout.addWidget(self.label4)
        left_layout.addWidget(self.input4)
        left_layout.addWidget(self.calculate_button1)
        left_layout.addWidget(self.label_DTR)
        left_layout.addWidget(self.dropdown2)
        left_layout.addWidget(self.calculate_button2)
        left_layout.addWidget(self.label5)
        
        # 右侧布局
        right_layout = QVBoxLayout()
        self.display_textbox1 = QTextEdit()
        self.display_textbox2 = QTextEdit()
        self.display_textbox2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.display_textbox2.setLineWrapMode(QTextEdit.NoWrap)
        self.display_textbox2.setReadOnly(1)
        right_layout.addWidget(self.display_textbox1)
        right_layout.addWidget(self.display_textbox2)
        
        # 主布局
        # main_layout = QHBoxLayout()
        # main_layout.addLayout(left_layout)
        # main_layout.addLayout(right_layout)

        # self.setFixedSize(800, 500)

        # self.setLayout(main_layout)

        left_widget = QWidget()
        right_widget = QWidget()
        
        left_widget.setLayout(left_layout)
        right_widget.setLayout(right_layout)
        
        # 设置固定大小
        left_widget.setFixedWidth(250)
        right_widget.setFixedWidth(700)
        
        # 将 QWidget 添加到主布局中
        main_layout = QHBoxLayout()
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
        # 设置主窗口的布局
        self.setLayout(main_layout)
        
        # 设置窗口标题和大小，并使其大小不可改变
        # self.setWindowTitle('布局比例示例')
        self.setFixedSize(1000, 700)  # 设置固定大小
        
        self.show()
        self.success = False
    
    def load_data(self):
        # dialog = DataInputDialog(self)
        # if dialog.exec_() == QDialog.Accepted:
        #     data1 = dialog.getInputs()
        #     self.dropdown.addItem(data1)
        #     self.display_textbox1.setText(data1)
            # self.display_textbox2.setText(data2)
        count_label = self.input_count.text()
        txt_now = self.display_textbox1.toPlainText()
        lines = txt_now.splitlines()
        lines = [s for s in lines if s]
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
            


        self.dropdown1.clear()
        self.dropdown2.clear()
        for head in self.SAR.heads[:-1]:
            self.dropdown1.addItem(head)
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
        QMessageBox.question(self, '提示', f'数据读取成功！表格列数：{cols}', QMessageBox.Ok, QMessageBox.Ok)
        self.success = True
        self.cols = cols


    def calculate1(self):
        if not self.success:
            QMessageBox.question(self, '提示', '数据未读取！', QMessageBox.Ok, QMessageBox.Ok)
            return


        try:
            s_th = float(self.input2.text())
            c_th = float(self.input3.text())
            SAR_deg = int(self.input4.text())
            SAR_id = self.dropdown1.currentIndex()
        except:
            self.label_state.setText(f'输入参数格式错误！')
            QMessageBox.question(self, '提示', '输入参数格式错误！', QMessageBox.Ok, QMessageBox.Ok)
            return
        


        


        try:
            print(s_th, c_th, SAR_deg, SAR_id)
            q1_res = self.SAR.solveQ1(s_th=s_th,     # 最小支持度阈值
                            c_th=c_th,      # 最小置信度阈值
                            SAR_id=SAR_id,      # 要求的强关联规则输出的列对应id
                            SAR_deg=SAR_deg,     # 解频繁n项集 
                            )
            # print(q1_res)

            # print(q2_res)
            
            res = q1_res
            dialog1 = TextDisplayDialog(res, "第一题答案")
            dialog1.exec_()
        except:
            self.label_state.setText(f'计算失败，对象未创建！')
            QMessageBox.question(self, '提示', '计算失败，对象未创建！', QMessageBox.Ok, QMessageBox.Ok)

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
            print(DTR_id)

            q2_res = self.SAR.solveQ2(DTR_id=DTR_id)
            # print(q2_res)
            
            res = q2_res
            dialog1 = TextDisplayDialog(res, "第二题答案")
            dialog1.exec_()
        except:
            self.label_state.setText(f'计算失败，对象未创建！')
            QMessageBox.question(self, '提示', '计算失败，对象未创建！', QMessageBox.Ok, QMessageBox.Ok)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())