import sys
import math
from pix2text import Pix2Text
import numpy as np
import sympy
from sympy import solve as solving, latex
from latex2sympy2 import latex2sympy
import io
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QToolBar, QAction, QDockWidget,
    QColorDialog, QFontDialog, QInputDialog, QMessageBox, QListWidget,
    QLabel, QHBoxLayout, QVBoxLayout, QSplitter, QFileDialog, QFrame, QSlider,
    QPushButton
)
from PyQt5.QtGui import (
    QPainter, QPen, QBrush, QColor, QPixmap, QIcon, QCursor, QFont,
    QPainterPath, QImage
)
from PyQt5.QtCore import (
    Qt, QPoint, QRect, QSize, QRectF, QSizeF, QLineF, QPointF, QEvent
)
import re
def solve_mix(latex_text, formatter='sympy'):
    regex = r"\\begin{cases}([\s\S]*)\\end{cases}"
    matches = re.findall(regex, latex_text, re.MULTILINE)
    equations = []
    if matches:
        matches = re.split(r"\\\\(?:\[?.*?\])?", matches[0])
        for match in matches:
            ins = latex2sympy(match)
            if type(ins) == list:
                equations.extend(ins)
            else:
                equations.append(ins)
        solved = sympy.solve(equations)
    else:
        return False
    if formatter == 'latex':
        return latex(solved)
    else:
        return solved
def is_equation(latex_str):
    """
    判断LaTeX表达式是否为方程（包括等式方程和不等式方程）
    
    规则：
    - 有等号或各种不等号，且后面还有数字或字母
    - 返回True表示是方程，False表示不是方程
    
    支持的符号：
    - 等式: = 
    - 不等式: ≠, <, >, ≤, ≥, \\neq, \\lt, \\gt, \\leq, \\geq
    """
    # 预处理：移除空格
    cleaned = latex_str.replace(' ', '')
    
    # 检查是否包含等号或不等号
    has_equation_symbol = False
    equation_symbol = None
    
    # 定义所有需要检查的方程符号及其优先级（长的符号优先检查）
    equation_symbols = ['\\leq', '\\geq', '\\neq', '\\lt', '\\gt', '=', '<', '>', '≤', '≥', '≠']
    
    for symbol in equation_symbols:
        if symbol in cleaned:
            has_equation_symbol = True
            equation_symbol = symbol
            break
    
    if not has_equation_symbol:
        print("不是方程")
        return False
    
    # 分割表达式
    parts = cleaned.split(equation_symbol, 1)
    
    # 检查符号后面是否有内容
    if len(parts) < 2:
        print("不是方程")
        return False
    
    # 检查符号后面是否有内容
    after_symbol = parts[1].strip()
    if not after_symbol:  # 空字符串
        print("不是方程")
        return False
    
    # 检查是否包含至少一个数字或字母
    return bool(re.search(r'[a-zA-Z0-9]', after_symbol))

def is_binary_equation(latex_str):
    """
    判断LaTeX表达式是否为二元方程或二元不等方程
    
    返回：
    - True表示是二元方程或二元不等方程
    - False表示不是
    """
    try:
        # 预处理：移除空格
        cleaned = latex_str.replace(' ', '')
        
        # 检查是否为方程
        if not is_equation(cleaned):
            return False
        
        # 尝试将表达式转换为sympy对象
        expr = latex2sympy(cleaned)
        
        # 获取表达式中的符号变量
        variables = expr.free_symbols
        
        # 检查是否有且仅有2个不同的变量
        return len(variables) == 2
    except Exception as e:
        print(f"判断二元方程时出错: {str(e)}")
        return False
def is_calculation(latex_str):
    """
    判断LaTeX表达式是否为计算式
    
    规则：
    - 没有等号或不等号
    - 有等号但等号后面没有内容
    - 返回True表示是计算式，False表示不是计算式
    """
    # 预处理：移除空格
    cleaned = latex_str.replace(' ', '')
    
    # 检查是否包含等号或不等号
    if '=' not in cleaned and '\\neq' not in cleaned:
        return True
    
    # 分割表达式（考虑等号和不等号）
    if '=' in cleaned:
        parts = cleaned.split('=', 1)
    else:  # 处理不等号
        parts = cleaned.split('\\neq', 1)
    
    # 检查等号/不等号后面是否有内容
    if len(parts) < 2:
        return True
    
    # 检查等号/不等号后面是否有数字或字母
    after_equal = parts[1].strip()
    if not after_equal:  # 空字符串
        return True
    
    # 检查是否包含至少一个数字或字母
    return not bool(re.search(r'[a-zA-Z0-9]', after_equal))
def safe_calculate(expr_str):
    # 去除等号和末尾可能的空白字符
    #去除空格
    expr_str = expr_str.replace(" ","")

    if '=' in expr_str:
        # 确保即使表达式以等号结尾也能正确处理
        expr_str = expr_str.split('=')[0].strip()
    
    # 检查表达式是否为空
    if not expr_str:
        return "错误: 表达式为空"
    
    try:
        # 尝试计算表达式
        expr = latex2sympy(expr_str)
        print(expr)
        result = expr.evalf()
        return result
    except Exception as e:
        return f"错误: {str(e)}"
def solve_expression(expr_str):
    try:
        # 尝试解析为 LaTeX
        expr = latex2sympy(expr_str)
        solutions = sympy.solve(expr)
        return solutions
    except:
        try:
            # 如果不是 LaTeX，尝试解析为普通表达式
            expr = sympy.sympify(expr_str)
            solutions = sympy.solve(expr)
            return solutions
        except Exception as e:
            return f"解析错误: {str(e)}"
class DrawingCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        # 创建一个用于显示橡皮擦范围的独立图层
        self.eraserIndicator = QWidget(self)
        self.eraserIndicator.setGeometry(0, 0, self.width(), self.height())
        self.eraserIndicator.setStyleSheet("background-color: transparent;")
        self.eraserIndicator.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.eraserIndicator.hide()
        # 安装事件过滤器
        self.eraserIndicator.installEventFilter(self)
        
    def initUI(self):
        # 设置画布属性
        self.setMinimumSize(800, 600)
        self.setMouseTracking(True)
        
        # 初始化绘图状态
        self.drawing = False
        self.lastPoint = QPoint()
        self.currentPoint = QPoint()
        self.path = QPainterPath()
        self.tempPath = QPainterPath()
        self.selectionPath = QPainterPath()
        self.selectionRect = QRect()
        
        # 初始化绘图工具和参数
        self.tool = "brush"
        self.brushColor = QColor(0, 0, 0)
        self.brushWidth = 2
        self.shapeColor = QColor(0, 0, 0)
        self.shapeWidth = 2
        self.fillColor = QColor(255, 255, 255, 0)  # 透明填充
        
        # 创建绘图画布
        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)
        
        # 撤销/重做栈
        self.undoStack = []
        self.redoStack = []
        self.saveState()
        
    def eventFilter(self, obj, event):
        # 拦截橡皮擦指示器的绘制事件
        if obj == self.eraserIndicator and event.type() == QEvent.Paint:
            if self.tool == "eraser" and not self.drawing:
                painter = QPainter(self.eraserIndicator)
                # 获取鼠标当前位置（相对于主画布）
                cursorPos = self.mapFromGlobal(QCursor.pos())
                # 转换为相对于指示器的位置
                indicatorPos = self.eraserIndicator.mapFrom(self, cursorPos)
                # 绘制宽度为5的圆表示橡皮擦作用范围
                pen = QPen(QColor(150, 150, 150), 5, Qt.DotLine)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(indicatorPos, self.brushWidth // 2, self.brushWidth // 2)
            return True
        return super().eventFilter(obj, event)
        
    def resizeEvent(self, event):
        # 调整画布大小，保持原始内容
        newImage = QImage(event.size(), QImage.Format_RGB32)
        newImage.fill(Qt.white)
        painter = QPainter(newImage)
        painter.drawImage(QPoint(), self.image)
        self.image = newImage
        # 调整橡皮擦指示器的大小
        self.eraserIndicator.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(QPoint(), self.image)
        
        # 绘制临时路径（正在绘制的形状）
        if not self.tempPath.isEmpty():
            pen = QPen(self.shapeColor, self.shapeWidth, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(QBrush(self.fillColor))
            painter.drawPath(self.tempPath)
        
        # 绘制选区
        if not self.selectionPath.isEmpty():
            pen = QPen(QColor(0, 150, 255), 1, Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(0, 150, 255, 50)))
            painter.drawPath(self.selectionPath)
            # 绘制选框上的控制点
            self.drawControlPoints(painter)
        
        # 当使用橡皮擦工具时，在鼠标位置绘制一个表示作用范围的圆
        # 将这段代码放在所有绘制操作的最后，确保它显示在最上方
        if self.tool == "eraser" and not self.drawing:
            # 获取鼠标当前位置
            cursorPos = self.mapFromGlobal(QCursor.pos())
            # 绘制宽度为5的圆表示橡皮擦作用范围
            pen = QPen(QColor(150, 150, 150), 5, Qt.DotLine)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(cursorPos, self.brushWidth // 2, self.brushWidth // 2)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()
            self.currentPoint = event.pos()
            
            # 根据当前工具执行不同操作
            if self.tool == "brush":
                self.path = QPainterPath()
                self.path.moveTo(self.lastPoint)
            elif self.tool == "eraser":
                self.path = QPainterPath()
                self.path.moveTo(self.lastPoint)
            elif self.tool == "select":
                # 如果当前已有选择区域，且点击位置不在选择区域内，则取消选择
                if not self.selectionPath.isEmpty() and not self.selectionPath.contains(event.pos()):
                    self.selectionPath = QPainterPath()
                    self.selectionRect = QRect()
                    self.update()
                else:
                    # 开始新的选择
                    self.selectionPath = QPainterPath()
                    self.selectionPath.addRect(QRectF(self.lastPoint, QSizeF()))
            elif self.tool in ["rectangle", "ellipse", "line", "triangle"]:
                self.tempPath = QPainterPath()
                if self.tool == "line":
                    self.tempPath.moveTo(self.lastPoint)
                    self.tempPath.lineTo(self.currentPoint)
                elif self.tool == "rectangle":
                    self.tempPath.addRect(QRectF(self.lastPoint, QSizeF()))
                elif self.tool == "ellipse":
                    self.tempPath.addEllipse(QRect(self.lastPoint, QSize()))
                elif self.tool == "triangle":
                    self.updateTrianglePath()
    
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drawing:
            self.currentPoint = event.pos()
            
            if self.tool == "brush":
                self.path.lineTo(self.currentPoint)
                painter = QPainter(self.image)
                pen = QPen(self.brushColor, self.brushWidth, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                painter.setPen(pen)
                painter.drawPath(self.path)
                self.update()
            elif self.tool == "eraser":
                self.path.lineTo(self.currentPoint)
                painter = QPainter(self.image)
                # 使用白色作为橡皮擦颜色（与画布背景色相同）
                pen = QPen(Qt.white, self.brushWidth, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                painter.setPen(pen)
                painter.drawPath(self.path)
                self.update()
            elif self.tool == "select":
                self.selectionPath = QPainterPath()
                rect = QRectF(self.lastPoint, self.currentPoint)
                self.selectionPath.addRect(rect)
                self.selectionRect = rect.toRect()
                self.update()
            elif self.tool in ["rectangle", "ellipse", "line", "triangle"]:
                self.tempPath = QPainterPath()
                if self.tool == "line":
                    self.tempPath.moveTo(self.lastPoint)
                    self.tempPath.lineTo(self.currentPoint)
                elif self.tool == "rectangle":
                    self.tempPath.addRect(QRectF(self.lastPoint, self.currentPoint))
                elif self.tool == "ellipse":
                    self.tempPath.addEllipse(QRectF(self.lastPoint, self.currentPoint))
                elif self.tool == "triangle":
                    self.updateTrianglePath()
                self.update()
        
        # 当使用橡皮擦工具时，刷新指示器
        if self.tool == "eraser" and not self.drawing:
            self.eraserIndicator.update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            
            # 保存当前状态用于撤销
            self.saveState()
            
            # 如果是绘制形状工具，将临时路径绘制到画布上
            if self.tool in ["rectangle", "ellipse", "line", "triangle"]:
                painter = QPainter(self.image)
                pen = QPen(self.shapeColor, self.shapeWidth, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                painter.setPen(pen)
                painter.setBrush(QBrush(self.fillColor))
                painter.drawPath(self.tempPath)
                self.tempPath = QPainterPath()
                self.update()
        elif event.button() == Qt.RightButton and self.tool == "select" and not self.selectionPath.isEmpty():
            # 显示右键菜单
            self.showContextMenu(event.pos())
            
    def showContextMenu(self, position):
        # 创建右键菜单
        from PyQt5.QtWidgets import QMenu
        contextMenu = QMenu(self)
        
        # 添加识别公式动作
        recognizeAction = QAction("识别并计算公式", self)
        recognizeAction.triggered.connect(self.recognizeAndCalculate)
        contextMenu.addAction(recognizeAction)
        
        # 显示菜单
        contextMenu.exec_(self.mapToGlobal(position))
        
    def recognizeAndCalculate(self):
        # 检查是否有选区
        if self.selectionPath.isEmpty():
            QMessageBox.warning(self, "警告", "请先使用选择工具框选公式区域")
            return
        
        try:
            # 获取选区图像
            selectionImage = self.image.copy(self.selectionRect)
            
            # 将QImage转换为PIL的Image对象（根据pix2text文档要求）
            from PIL import Image
            width = selectionImage.width()
            height = selectionImage.height()
            
            # 确保图像格式正确
            if selectionImage.format() != QImage.Format_RGB32:
                selectionImage = selectionImage.convertToFormat(QImage.Format_RGB32)
            
            # 获取图像数据
            ptr = selectionImage.bits()
            ptr.setsize(height * width * 4)
            
            # 创建PIL Image对象
            pil_image = Image.frombuffer(
                "RGBA", 
                (width, height), 
                ptr, 
                "raw", 
                "RGBA", 
                0, 
                1
            )
            # 创建Pix2Text实例
            p2t = Pix2Text()
            
            # 识别公式
            result = p2t.recognize_formula(pil_image,return_text=True)
            print(result)
            # 解析表达式
            QMessageBox.information(self, "结果", result)
            # 如果识别结果为空
            if not result:
                QMessageBox.information(self, "结果", "未能识别出公式")
                return
            
            # 尝试计算公式结果
            try:
                if is_equation(result):
                    # 判断是否为二元方程或二元不等方程
                    if is_binary_equation(result):
                        # 调用solve_mix函数处理二元方程
                        calculation_result = solve_mix(result)
                        if calculation_result is False:
                            # 如果solve_mix返回False，使用普通求解方法
                            expr = latex2sympy(result)
                            print(expr)
                            calculation_result = sympy.solve(expr)
                    else:
                        expr = latex2sympy(result)
                        print(expr)
                        calculation_result = sympy.solve(expr)
                else:
                    calculation_result = safe_calculate(result)
            except Exception as e:
                calculation_result = f"计算错误: {str(e)}"
            
            # 显示结果对话框
            self.showFormulaResult(result, calculation_result)
            
        except Exception as e:
            print(f"处理公式时出错: {str(e)}")
            QMessageBox.critical(self, "错误", f"处理公式时出错: {str(e)}")
            
    def showFormulaResult(self, formula, result):
        # 创建结果对话框
        dialog = QWidget()
        dialog.setWindowTitle("公式识别结果")
        dialog.setGeometry(300, 300, 500, 300)
        
        layout = QVBoxLayout()
        
        # 显示原始公式
        formulaLabel = QLabel(f"识别的公式: ${formula}$")
        font = QFont()
        font.setPointSize(12)
        formulaLabel.setFont(font)
        layout.addWidget(formulaLabel)
        
        # 显示计算结果
        resultLabel = QLabel(f"计算结果: {result}")
        resultLabel.setFont(font)
        layout.addWidget(resultLabel)
        
        # 使用matplotlib显示LaTeX公式
        try:
            # 创建matplotlib图形
            fig = Figure(figsize=(5, 2))
            ax = fig.add_subplot(111)
            ax.axis('off')
            
            # 渲染LaTeX公式
            ax.text(0.5, 0.5, f"${formula}$", fontsize=20, ha='center', va='center')
            
            # 创建画布并添加到布局
            canvas = FigureCanvas(fig)
            # 将画布和图形存储为对话框的属性，确保引用有效
            dialog.canvas = canvas
            dialog.fig = fig
            layout.addWidget(canvas)
            
            # 刷新画布
            canvas.draw()
            
            # 连接对话框关闭信号到清理函数
            dialog.setAttribute(Qt.WA_DeleteOnClose)
            dialog.destroyed.connect(self.onDialogDestroyed)
        except Exception as e:
            errorLabel = QLabel(f"无法显示LaTeX公式: {str(e)}")
            layout.addWidget(errorLabel)
        
        # 添加关闭按钮
        closeBtn = QPushButton("关闭", self)
        closeBtn.clicked.connect(dialog.close)
        layout.addWidget(closeBtn)
        
        dialog.setLayout(layout)
        dialog.show()
        
        # 存储对话框引用，防止被提前回收
        self.currentDialog = dialog
    
    def cleanupMatplotlibCanvas(self, canvas):
        """清理matplotlib画布资源"""
        try:
            # 安全关闭画布
            if canvas and hasattr(canvas, 'close'):
                canvas.close()
        except Exception as e:
            print(f"清理画布时出错: {str(e)}")
    
    def onDialogDestroyed(self):
        """对话框销毁时执行的清理操作"""
        try:
            # 清理对话框相关的matplotlib资源
            if hasattr(self, 'currentDialog'):
                if hasattr(self.currentDialog, 'canvas'):
                    self.cleanupMatplotlibCanvas(self.currentDialog.canvas)
                # 清除对话框引用
                del self.currentDialog
        except Exception as e:
            print(f"对话框销毁时清理出错: {str(e)}")
    
    def updateTrianglePath(self):
        # 创建三角形路径
        self.tempPath = QPainterPath()
        dx = self.currentPoint.x() - self.lastPoint.x()
        dy = self.currentPoint.y() - self.lastPoint.y()
        
        p1 = self.lastPoint
        p2 = QPoint(self.currentPoint.x(), self.lastPoint.y())
        p3 = QPoint(self.lastPoint.x() + dx // 2, self.currentPoint.y())
        
        self.tempPath.moveTo(p1)
        self.tempPath.lineTo(p2)
        self.tempPath.lineTo(p3)
        self.tempPath.closeSubpath()
    
    def drawControlPoints(self, painter):
        # 在选框周围绘制控制点
        rect = self.selectionRect
        points = [
            rect.topLeft(), rect.topRight(),
            rect.bottomLeft(), rect.bottomRight(),
            rect.center()
        ]
        
        for point in points:
            painter.drawEllipse(point, 4, 4)
    
    def saveState(self):
        # 保存当前状态到撤销栈
        self.undoStack.append(self.image.copy())
        # 清空重做栈
        self.redoStack.clear()
        # 限制撤销栈大小
        if len(self.undoStack) > 30:
            self.undoStack.pop(0)
    
    def undo(self):
        if len(self.undoStack) > 1:
            # 将当前状态保存到重做栈
            self.redoStack.append(self.image.copy())
            # 恢复上一个状态
            self.image = self.undoStack.pop()
            self.update()
    
    def redo(self):
        if self.redoStack:
            # 保存当前状态到撤销栈
            self.undoStack.append(self.image.copy())
            # 恢复下一个状态
            self.image = self.redoStack.pop()
            self.update()
    
    def clear(self):
        # 清空画布
        self.image.fill(Qt.white)
        self.update()
        self.saveState()
    
    def setTool(self, tool):
        self.tool = tool
        # 根据工具类型控制橡皮擦指示器的显示
        if tool == "eraser":
            self.eraserIndicator.show()
            self.setMouseTracking(True)
        else:
            self.eraserIndicator.hide()
        self.update()
    
    def setBrushColor(self, color):
        self.brushColor = color
        self.shapeColor = color
    
    def setBrushWidth(self, width):
        self.brushWidth = width
        self.shapeWidth = width
    
    def setFillColor(self, color):
        self.fillColor = color
    
    def saveImage(self, filename):
        return self.image.save(filename)
    
    def loadImage(self, filename):
        newImage = QImage()
        if newImage.load(filename):
            self.image = newImage
            self.update()
            self.saveState()
            return True
        return False
    
    def scaleSelection(self, factor):
        # 缩放选区内的内容
        if not self.selectionPath.isEmpty():
            self.saveState()
            # 获取选区图像
            selectionImage = self.image.copy(self.selectionRect)
            # 缩放图像
            scaledImage = selectionImage.scaled(
                int(selectionImage.width() * factor),
                int(selectionImage.height() * factor),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            # 清除原选区
            painter = QPainter(self.image)
            painter.fillRect(self.selectionRect, Qt.white)
            # 绘制缩放后的图像
            painter.drawImage(
                self.selectionRect.topLeft(),
                scaledImage
            )
            self.update()
    
    def rotateSelection(self, angle):
        # 旋转选区内的内容
        if not self.selectionPath.isEmpty():
            self.saveState()
            # 获取选区图像
            selectionImage = self.image.copy(self.selectionRect)
            # 旋转图像
            rotatedImage = selectionImage.transformed(
                QTransform().rotate(angle)
            )
            # 清除原选区
            painter = QPainter(self.image)
            painter.fillRect(self.selectionRect, Qt.white)
            # 计算新的位置（居中）
            x = self.selectionRect.center().x() - rotatedImage.width() // 2
            y = self.selectionRect.center().y() - rotatedImage.height() // 2
            # 绘制旋转后的图像
            painter.drawImage(QPoint(x, y), rotatedImage)
            self.update()

class DrawingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle("现代绘图工具")
        self.setGeometry(100, 100, 1024, 768)
        
        # 创建主画布
        self.canvas = DrawingCanvas(self)
        self.setCentralWidget(self.canvas)
        
        # 创建菜单栏
        self.createMenuBar()
        
        # 创建工具栏
        self.createToolBars()
        
        # 创建停靠窗口
        self.createDockWidgets()
        
        # 显示窗口
        self.show()
    
    def createMenuBar(self):
        # 文件菜单
        fileMenu = self.menuBar().addMenu("文件")
        
        # 新建文件
        newAction = QAction("新建", self)
        newAction.setShortcut("Ctrl+N")
        newAction.triggered.connect(self.newFile)
        fileMenu.addAction(newAction)
        
        # 打开文件
        openAction = QAction("打开", self)
        openAction.setShortcut("Ctrl+O")
        openAction.triggered.connect(self.openFile)
        fileMenu.addAction(openAction)
        
        # 保存文件
        saveAction = QAction("保存", self)
        saveAction.setShortcut("Ctrl+S")
        saveAction.triggered.connect(self.saveFile)
        fileMenu.addAction(saveAction)
        
        fileMenu.addSeparator()
        
        # 退出应用
        exitAction = QAction("退出", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)
        
        # 编辑菜单
        editMenu = self.menuBar().addMenu("编辑")
        
        # 撤销
        undoAction = QAction("撤销", self)
        undoAction.setShortcut("Ctrl+Z")
        undoAction.triggered.connect(self.undo)
        editMenu.addAction(undoAction)
        
        # 重做
        redoAction = QAction("重做", self)
        redoAction.setShortcut("Ctrl+Y")
        redoAction.triggered.connect(self.redo)
        editMenu.addAction(redoAction)
        
        editMenu.addSeparator()
        
        # 清除画布
        clearAction = QAction("清除画布", self)
        clearAction.triggered.connect(self.clearCanvas)
        editMenu.addAction(clearAction)
        
        # 视图菜单
        viewMenu = self.menuBar().addMenu("视图")
        
        # 放大
        zoomInAction = QAction("放大", self)
        zoomInAction.setShortcut("Ctrl++")
        zoomInAction.triggered.connect(lambda: self.zoomSelection(1.1))
        viewMenu.addAction(zoomInAction)
        
        # 缩小
        zoomOutAction = QAction("缩小", self)
        zoomOutAction.setShortcut("Ctrl+-")
        zoomOutAction.triggered.connect(lambda: self.zoomSelection(0.9))
        viewMenu.addAction(zoomOutAction)
        
        viewMenu.addSeparator()
        
        # 旋转
        rotateAction = QAction("旋转", self)
        rotateAction.triggered.connect(self.rotateDialog)
        viewMenu.addAction(rotateAction)
    
    def createToolBars(self):
        # 工具工具栏
        toolToolBar = QToolBar("绘图工具", self)
        self.addToolBar(toolToolBar)
        
        # 画笔工具
        brushAction = QAction("画笔", self)
        brushAction.triggered.connect(lambda: self.setTool("brush"))
        toolToolBar.addAction(brushAction)
        
        # 矩形工具
        rectAction = QAction("矩形", self)
        rectAction.triggered.connect(lambda: self.setTool("rectangle"))
        toolToolBar.addAction(rectAction)
        
        # 椭圆工具
        ellipseAction = QAction("椭圆", self)
        ellipseAction.triggered.connect(lambda: self.setTool("ellipse"))
        toolToolBar.addAction(ellipseAction)
        
        # 直线工具
        lineAction = QAction("直线", self)
        lineAction.triggered.connect(lambda: self.setTool("line"))
        toolToolBar.addAction(lineAction)
        
        # 三角形工具
        triangleAction = QAction("三角形", self)
        triangleAction.triggered.connect(lambda: self.setTool("triangle"))
        toolToolBar.addAction(triangleAction)
        
        # 选择工具
        selectAction = QAction("选择", self)
        selectAction.triggered.connect(lambda: self.setTool("select"))
        toolToolBar.addAction(selectAction)
        
        # 橡皮工具
        eraserAction = QAction("橡皮", self)
        eraserAction.triggered.connect(lambda: self.setTool("eraser"))
        toolToolBar.addAction(eraserAction)
        
        # 编辑工具栏 - 添加撤销和重做按钮
        editToolBar = QToolBar("编辑", self)
        self.addToolBar(editToolBar)
        
        # 撤销按钮
        undoActionToolbar = QAction("撤销", self)
        undoActionToolbar.setShortcut("Ctrl+Z")
        undoActionToolbar.triggered.connect(self.undo)
        editToolBar.addAction(undoActionToolbar)
        
        # 重做按钮
        redoActionToolbar = QAction("重做", self)
        redoActionToolbar.setShortcut("Ctrl+Y")
        redoActionToolbar.triggered.connect(self.redo)
        editToolBar.addAction(redoActionToolbar)
        
        # 颜色工具栏
        colorToolBar = QToolBar("颜色", self)
        self.addToolBar(colorToolBar)
        
        # 线条颜色
        colorAction = QAction("线条颜色", self)
        colorAction.triggered.connect(self.selectColor)
        colorToolBar.addAction(colorAction)
        
        # 填充颜色
        fillAction = QAction("填充颜色", self)
        fillAction.triggered.connect(self.selectFillColor)
        colorToolBar.addAction(fillAction)
        
        # 线条宽度
        widthAction = QAction("线条宽度", self)
        widthAction.triggered.connect(self.selectWidth)
        colorToolBar.addAction(widthAction)
        
        # 添加画笔大小滑块
        widthSliderWidget = QWidget()
        widthSliderLayout = QHBoxLayout()
        widthSliderLayout.setContentsMargins(5, 0, 5, 0)
        
        widthLabel = QLabel(f"画笔大小: {self.canvas.brushWidth}")
        self.widthLabel = widthLabel
        
        widthSlider = QSlider(Qt.Horizontal)
        widthSlider.setRange(1, 50)
        widthSlider.setValue(self.canvas.brushWidth)
        widthSlider.setMinimumWidth(100)
        widthSlider.valueChanged.connect(self.onWidthSliderChanged)
        
        widthSliderLayout.addWidget(widthLabel)
        widthSliderLayout.addWidget(widthSlider)
        widthSliderWidget.setLayout(widthSliderLayout)
        colorToolBar.addWidget(widthSliderWidget)
    
    def createDockWidgets(self):
        # 创建颜色面板停靠窗口
        colorDock = QDockWidget("颜色面板", self)
        colorDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # 颜色面板内容
        colorPanel = QWidget()
        colorLayout = QVBoxLayout()
        
        # 常用颜色选择
        colors = [
            "#000000", "#FF0000", "#00FF00", "#0000FF",
            "#FFFF00", "#FF00FF", "#00FFFF", "#FFA500",
            "#800080", "#008000", "#000080", "#808080"
        ]
        
        colorGrid = QWidget()
        colorGridLayout = QHBoxLayout()
        colorGridLayout.setContentsMargins(0, 0, 0, 0)
        colorGridLayout.setSpacing(5)
        
        for color in colors:
            colorBtn = QFrame()
            colorBtn.setStyleSheet(f"background-color: {color}; border: 1px solid #CCCCCC; border-radius: 3px;")
            colorBtn.setMinimumSize(30, 30)
            colorBtn.mousePressEvent = lambda event, c=color: self.setQuickColor(c)
            colorGridLayout.addWidget(colorBtn)
        
        colorGrid.setLayout(colorGridLayout)
        colorLayout.addWidget(QLabel("常用颜色:"))
        colorLayout.addWidget(colorGrid)
        colorLayout.addStretch()
        
        colorPanel.setLayout(colorLayout)
        colorDock.setWidget(colorPanel)
        
        # 添加停靠窗口到主窗口
        self.addDockWidget(Qt.LeftDockWidgetArea, colorDock)
    
    def setTool(self, tool):
        self.canvas.setTool(tool)
    
    def selectColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.setBrushColor(color)
    
    def selectFillColor(self):
        color = QColorDialog.getColor(Qt.transparent, self, "选择填充颜色", QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self.canvas.setFillColor(color)
    
    def selectWidth(self):
        width, ok = QInputDialog.getInt(self, "线条宽度", "请输入线条宽度:", self.canvas.brushWidth, 1, 50)
        if ok:
            self.canvas.setBrushWidth(width)
    
    def setQuickColor(self, colorStr):
        color = QColor(colorStr)
        self.canvas.setBrushColor(color)
    
    def onWidthSliderChanged(self, value):
        # 更新画笔宽度和标签显示
        self.canvas.setBrushWidth(value)
        self.widthLabel.setText(f"画笔大小: {value}")
    
    def newFile(self):
        reply = QMessageBox.question(self, "确认", "是否创建新文件？当前未保存的内容将会丢失。",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.canvas.clear()
    
    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, "打开文件", "",
                                                 "图像文件 (*.png *.jpg *.jpeg *.bmp);;所有文件 (*)")
        if filename:
            self.canvas.loadImage(filename)
    
    def saveFile(self):
        filename, _ = QFileDialog.getSaveFileName(self, "保存文件", "",
                                                 "PNG图像 (*.png);;JPEG图像 (*.jpg);;BMP图像 (*.bmp)")
        if filename:
            if not self.canvas.saveImage(filename):
                QMessageBox.warning(self, "错误", "保存文件失败！")
    
    def undo(self):
        self.canvas.undo()
    
    def redo(self):
        self.canvas.redo()
    
    def clearCanvas(self):
        reply = QMessageBox.question(self, "确认", "是否清除整个画布？此操作不可撤销。",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.canvas.clear()
    
    def zoomSelection(self, factor):
        self.canvas.scaleSelection(factor)
    
    def rotateDialog(self):
        angle, ok = QInputDialog.getInt(self, "旋转", "请输入旋转角度(度):", 90, -360, 360)
        if ok:
            self.canvas.rotateSelection(angle)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 设置应用程序样式
    app.setStyle("Fusion")
    # 创建主窗口
    window = DrawingApp()
    # 运行应用程序
    sys.exit(app.exec_())