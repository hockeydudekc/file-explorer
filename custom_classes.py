from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys

class CheckableComboBox(QComboBox):
	def __init__(self):
		super().__init__()
		self._changed = False

		self.view().pressed.connect(self.handleItemPressed)

	def setItemChecked(self, index, checked=False):
		item = self.model().item(index, self.modelColumn()) # QStandardItem object

		if checked:
			item.setCheckState(Qt.Checked)
		else:
			item.setCheckState(Qt.Unchecked)

	def handleItemPressed(self, index):
		item = self.model().itemFromIndex(index)

		if item.checkState() == Qt.Checked:
			item.setCheckState(Qt.Unchecked)
		else:
			item.setCheckState(Qt.Checked)
		self._changed = True


	def hidePopup(self):
		if not self._changed:
			super().hidePopup()
		self._changed = False

	def itemChecked(self, index):
		item = self.model().item(index, self.modelColumn())
		return item.checkState() == Qt.Checked




class RangeSlider(QWidget):
    clickedValue = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent)

        self.first_position = 1
        self.second_position = 8

        self.opt = QStyleOptionSlider()
        self.opt.minimum = 0
        self.opt.maximum = 117

        self.setTickPosition(QSlider.TicksAbove)
        self.setTickInterval(1)

        self.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed, QSizePolicy.Slider)
        )

    def setRangeLimit(self, minimum: int, maximum: int):
        self.opt.minimum = minimum
        self.opt.maximum = maximum

    def setRange(self, start: int, end: int):
        self.first_position = start
        self.second_position = end

    def getRange(self):
        return (self.first_position, self.second_position)

    def setTickPosition(self, position: QSlider.TickPosition):
        self.opt.tickPosition = position

    def setTickInterval(self, ti: int):
        self.opt.tickInterval = ti

    def paintEvent(self, event: QPaintEvent):

        painter = QPainter(self)

        # Draw rule
        self.opt.initFrom(self)
        self.opt.rect = self.rect()
        self.opt.sliderPosition = 0
        self.opt.subControls = QStyle.SC_SliderGroove | QStyle.SC_SliderTickmarks

        #   Draw GROOVE
        self.style().drawComplexControl(QStyle.CC_Slider, self.opt, painter)

        #  Draw INTERVAL

        # color = self.palette().color(QPalette.Highlight)
        # color.setAlpha(160)
        # painter.setBrush(QBrush(color))
        # painter.setPen(Qt.NoPen)

        self.opt.sliderPosition = self.first_position
        x_left_handle = (
            self.style()
            .subControlRect(QStyle.CC_Slider, self.opt, QStyle.SC_SliderHandle)
            .right()
        )

        self.opt.sliderPosition = self.second_position
        x_right_handle = (
            self.style()
            .subControlRect(QStyle.CC_Slider, self.opt, QStyle.SC_SliderHandle)
            .left()
        )

        groove_rect = self.style().subControlRect(
            QStyle.CC_Slider, self.opt, QStyle.SC_SliderGroove
        )

        selection = QRect(
            x_left_handle,
            groove_rect.y(),
            x_right_handle - x_left_handle,
            groove_rect.height(),
        ).adjusted(-1, 1, 1, -1)

        # painter.drawRect(selection)

        # Draw first handle

        self.opt.subControls = QStyle.SC_SliderHandle
        self.opt.sliderPosition = self.first_position
        self.style().drawComplexControl(QStyle.CC_Slider, self.opt, painter)

        # Draw second handle
        self.opt.sliderPosition = self.second_position
        self.style().drawComplexControl(QStyle.CC_Slider, self.opt, painter)

    def mousePressEvent(self, event: QMouseEvent):

        self.opt.sliderPosition = self.first_position
        self._first_sc = self.style().hitTestComplexControl(
            QStyle.CC_Slider, self.opt, event.pos(), self
        )

        self.opt.sliderPosition = self.second_position
        self._second_sc = self.style().hitTestComplexControl(
            QStyle.CC_Slider, self.opt, event.pos(), self
        )

    def mouseMoveEvent(self, event: QMouseEvent):

        distance = self.opt.maximum - self.opt.minimum

        pos = self.style().sliderValueFromPosition(
            0, distance, event.pos().x(), self.rect().width()
        )

        if self._first_sc == QStyle.SC_SliderHandle:
            if pos <= self.second_position:
                dif = self.first_position - pos
                self.first_position = pos
                self.second_position -= dif
                self.update()
                self.clickedValue.emit(self.first_position)
                return

        if self._second_sc == QStyle.SC_SliderHandle:
            if pos >= self.first_position:
                self.second_position = pos
                self.update()
        self.clickedValue.emit(self.second_position+1000)
        
    def sizeHint(self):
        """ override """
        SliderLength = 84
        TickSpace = 5

        w = SliderLength
        h = self.style().pixelMetric(QStyle.PM_SliderThickness, self.opt, self)

        if (
            self.opt.tickPosition & QSlider.TicksAbove
            or self.opt.tickPosition & QSlider.TicksBelow
        ):
            h += TickSpace

        return (
            self.style()
            .sizeFromContents(QStyle.CT_Slider, self.opt, QSize(w, h), self)
            .expandedTo(QApplication.globalStrut())
        )

class DragDropWidget(QPushButton):

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.full_title = "unassigned"
        self.file_path = None
        self.file_type = -1
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            mime_data = QMimeData()
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.setHotSpot(event.pos())
            drag.exec_(Qt.MoveAction)

    def new_text(self):
        return self.full_title

if __name__ == "__main__":

    app = QApplication(sys.argv)

    w = RangeSlider()
    w.show()

    # q = QSlider()
    # q.show()

    app.exec_()