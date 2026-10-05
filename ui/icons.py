"""Vector Icon Provider for Lumination.

Draws crisp, modern Microsoft Office/Fluent-style vector icons using QPainter and QIcon.
Zero emojis, zero external file dependencies, perfectly crisp on high-DPI displays.
"""

from __future__ import annotations
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QPolygonF, QPainterPath
from PySide6.QtCore import Qt, QPointF, QRectF


def create_undo_icon(color: str = "#334155", size: int = 24) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    path = QPainterPath()
    path.moveTo(size * 0.75, size * 0.70)
    path.cubicTo(size * 0.75, size * 0.35, size * 0.40, size * 0.35, size * 0.30, size * 0.45)
    painter.drawPath(path)

    arrow = QPainterPath()
    arrow.moveTo(size * 0.42, size * 0.32)
    arrow.lineTo(size * 0.25, size * 0.45)
    arrow.lineTo(size * 0.42, size * 0.58)
    painter.drawPath(arrow)

    painter.end()
    return QIcon(pix)


def create_redo_icon(color: str = "#334155", size: int = 24) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    path = QPainterPath()
    path.moveTo(size * 0.25, size * 0.70)
    path.cubicTo(size * 0.25, size * 0.35, size * 0.60, size * 0.35, size * 0.70, size * 0.45)
    painter.drawPath(path)

    arrow = QPainterPath()
    arrow.moveTo(size * 0.58, size * 0.32)
    arrow.lineTo(size * 0.75, size * 0.45)
    arrow.lineTo(size * 0.58, size * 0.58)
    painter.drawPath(arrow)

    painter.end()
    return QIcon(pix)


def create_add_point_icon(color: str = "#2563eb", size: int = 24) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 1.8)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    painter.drawEllipse(QRectF(size * 0.15, size * 0.15, size * 0.70, size * 0.70))
    painter.drawLine(QPointF(size * 0.5, size * 0.30), QPointF(size * 0.5, size * 0.70))
    painter.drawLine(QPointF(size * 0.30, size * 0.5), QPointF(size * 0.70, size * 0.5))

    painter.end()
    return QIcon(pix)


def create_delete_icon(color: str = "#dc2626", size: int = 24) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    painter.drawRect(QRectF(size * 0.28, size * 0.38, size * 0.44, size * 0.48))
    painter.drawLine(QPointF(size * 0.20, size * 0.38), QPointF(size * 0.80, size * 0.38))
    painter.drawRect(QRectF(size * 0.40, size * 0.24, size * 0.20, size * 0.14))
    painter.drawLine(QPointF(size * 0.42, size * 0.46), QPointF(size * 0.42, size * 0.76))
    painter.drawLine(QPointF(size * 0.58, size * 0.46), QPointF(size * 0.58, size * 0.76))

    painter.end()
    return QIcon(pix)


def create_zoom_in_icon(color: str = "#334155", size: int = 24) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 1.8)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    painter.drawEllipse(QRectF(size * 0.15, size * 0.15, size * 0.50, size * 0.50))
    painter.drawLine(QPointF(size * 0.55, size * 0.55), QPointF(size * 0.82, size * 0.82))
    painter.drawLine(QPointF(size * 0.40, size * 0.26), QPointF(size * 0.40, size * 0.54))
    painter.drawLine(QPointF(size * 0.26, size * 0.40), QPointF(size * 0.54, size * 0.40))

    painter.end()
    return QIcon(pix)


def create_zoom_out_icon(color: str = "#334155", size: int = 24) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 1.8)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    painter.drawEllipse(QRectF(size * 0.15, size * 0.15, size * 0.50, size * 0.50))
    painter.drawLine(QPointF(size * 0.55, size * 0.55), QPointF(size * 0.82, size * 0.82))
    painter.drawLine(QPointF(size * 0.26, size * 0.40), QPointF(size * 0.54, size * 0.40))

    painter.end()
    return QIcon(pix)


def create_reset_view_icon(color: str = "#334155", size: int = 24) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    painter.drawLine(QPointF(size * 0.20, size * 0.35), QPointF(size * 0.20, size * 0.20))
    painter.drawLine(QPointF(size * 0.20, size * 0.20), QPointF(size * 0.35, size * 0.20))
    painter.drawLine(QPointF(size * 0.80, size * 0.35), QPointF(size * 0.80, size * 0.20))
    painter.drawLine(QPointF(size * 0.80, size * 0.20), QPointF(size * 0.65, size * 0.20))
    painter.drawLine(QPointF(size * 0.20, size * 0.65), QPointF(size * 0.20, size * 0.80))
    painter.drawLine(QPointF(size * 0.20, size * 0.80), QPointF(size * 0.35, size * 0.80))
    painter.drawLine(QPointF(size * 0.80, size * 0.65), QPointF(size * 0.80, size * 0.80))
    painter.drawLine(QPointF(size * 0.80, size * 0.80), QPointF(size * 0.65, size * 0.80))

    painter.end()
    return QIcon(pix)


def create_bluetooth_icon(color: str = "#2563eb", size: int = 24) -> QIcon:
    """Crisp Bluetooth vector symbol."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    # Bluetooth rune
    path = QPainterPath()
    path.moveTo(size * 0.32, size * 0.32)
    path.lineTo(size * 0.68, size * 0.68)
    path.lineTo(size * 0.50, size * 0.84)
    path.lineTo(size * 0.50, size * 0.16)
    path.lineTo(size * 0.68, size * 0.32)
    path.lineTo(size * 0.32, size * 0.68)
    painter.drawPath(path)

    painter.end()
    return QIcon(pix)


def create_chevron_left_icon(color: str = "#475569", size: int = 16) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    path = QPainterPath()
    path.moveTo(size * 0.65, size * 0.20)
    path.lineTo(size * 0.35, size * 0.50)
    path.lineTo(size * 0.65, size * 0.80)
    painter.drawPath(path)

    painter.end()
    return QIcon(pix)


def create_chevron_right_icon(color: str = "#475569", size: int = 16) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    path = QPainterPath()
    path.moveTo(size * 0.35, size * 0.20)
    path.lineTo(size * 0.65, size * 0.50)
    path.lineTo(size * 0.35, size * 0.80)
    painter.drawPath(path)

    painter.end()
    return QIcon(pix)
