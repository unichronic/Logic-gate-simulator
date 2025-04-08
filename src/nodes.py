


import os
import json
import uuid
from PyQt5.QtWidgets import (QWidget, QGraphicsScene, QGraphicsView, QGraphicsItem,
                            QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsPathItem,
                            QGraphicsTextItem, QLineEdit, QPushButton, QVBoxLayout,
                            QHBoxLayout, QGraphicsProxyWidget, QFileDialog, QInputDialog)
from PyQt5.QtCore import Qt, QPointF, QRectF, QSizeF, QMimeData, QByteArray
from PyQt5.QtGui import QPen, QBrush, QColor, QPainterPath, QFont, QPainter, QCursor
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp


NODE_WIDTH = 150
NODE_HEIGHT = 100
SOCKET_RADIUS = 8
GRID_SIZE = 20
GRID_COLOR = QColor(50, 50, 50, 150)

class Socket(QGraphicsEllipseItem):
    """Socket for connecting nodes"""
    
    INPUT = 0
    OUTPUT = 1
    
    def __init__(self, parent, socket_type, index=0):
        """
        Initialize a socket
        
        Args:
            parent: The parent node
            socket_type: Either Socket.INPUT or Socket.OUTPUT
            index: Index of the socket (used for positioning multiple sockets)
        """
        super().__init__(parent)
        
        self.node = parent
        self.socket_type = socket_type
        self.index = index
        
        
        self.connection = None if socket_type == Socket.INPUT else []
        
        
        self.setRect(-SOCKET_RADIUS, -SOCKET_RADIUS, SOCKET_RADIUS * 2, SOCKET_RADIUS * 2)
        if socket_type == Socket.INPUT:
            self.setBrush(QBrush(QColor(0, 100, 200)))
            self.setPen(QPen(QColor(0, 70, 150), 1))
        else:
            self.setBrush(QBrush(QColor(0, 180, 0)))
            self.setPen(QPen(QColor(0, 130, 0), 1))
        
        
        self.updatePosition()
        
        
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.LeftButton)
    
    def updatePosition(self):
        """Update the socket position based on its type and index"""
        
        
        node_width = NODE_WIDTH
        node_height = NODE_HEIGHT
        
        
        
        if self.socket_type == Socket.INPUT:
            total_sockets = self.node.getInputCount()
        else:
            total_sockets = self.node.getOutputCount()
        
        
        min_socket_spacing = 30  
        
        
        available_height = node_height - 50  
        socket_spacing = max(min_socket_spacing, available_height / max(1, total_sockets - 1)) if total_sockets > 1 else available_height
        
        if self.socket_type == Socket.INPUT:
            x = 0
            if total_sockets == 1:
                y = node_height / 2  
            else:
                start_y = (node_height - socket_spacing * (total_sockets - 1)) / 2
                y = start_y + (self.index * socket_spacing)
        else:  
            x = node_width
            if total_sockets == 1:
                y = node_height / 2  
            else:
                start_y = (node_height - socket_spacing * (total_sockets - 1)) / 2
                y = start_y + (self.index * socket_spacing)
        
        self.setPos(x, y)
    
    def isInput(self):
        """Check if this socket is an input socket"""
        
        return self.socket_type == Socket.INPUT
    
    def isOutput(self):
        """Check if this socket is an output socket"""
        
        return self.socket_type == Socket.OUTPUT
    
    def isConnected(self):
        """Check if this socket is connected to another socket"""
        
        if self.socket_type == Socket.INPUT:
            return self.connection is not None
        else:
            return len(self.connection) > 0
    
    def setConnection(self, connection):
        """Set the connection for this socket"""
        
        if self.socket_type == Socket.INPUT:
            self.connection = connection
        else:
            
            if connection is None:
                self.connection = []
            elif connection not in self.connection:
                self.connection.append(connection)
        
        
        self.node.updateConnectionIndicators()
    
    def removeConnection(self, connection):
        """Remove a specific connection from an output socket"""
        if self.socket_type == Socket.OUTPUT and connection in self.connection:
            self.connection.remove(connection)
            
            self.node.updateConnectionIndicators()
            
    def getConnections(self):
        """Get all connections for this socket"""
        if self.socket_type == Socket.INPUT:
            return [self.connection] if self.connection else []
        else:
            return self.connection
    
    def mousePressEvent(self, event):
        """Handle mouse press events for creating connections"""
        
        
        
        views = self.scene().views()
        if views:
            node_editor = views[0].node_editor
            node_editor.startConnection(self)
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events for completing connections"""
        
        
        
        views = self.scene().views()
        if views:
            node_editor = views[0].node_editor
            node_editor.endConnection()
        super().mouseReleaseEvent(event)
    
    def hoverEnterEvent(self, event):
        """Highlight socket on hover"""
        
        if self.socket_type == Socket.INPUT:
            self.setBrush(QBrush(QColor(0, 150, 255)))
        else:
            self.setBrush(QBrush(QColor(0, 255, 0)))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Reset socket appearance when hover ends"""
        
        if self.socket_type == Socket.INPUT:
            self.setBrush(QBrush(QColor(0, 100, 200)))
        else:
            self.setBrush(QBrush(QColor(0, 180, 0)))
        super().hoverLeaveEvent(event)

class Connection(QGraphicsPathItem):
    """Connection between two sockets"""
    
    def __init__(self, scene, source_socket=None, dest_socket=None):
        """
        Initialize a connection
        
        Args:
            scene: The graphics scene
            source_socket: The source socket (output)
            dest_socket: The destination socket (input)
        """
        super().__init__()
        
        self.scene = scene
        self.source_socket = source_socket
        self.dest_socket = dest_socket
        
        
        self.setPen(QPen(QColor(0, 180, 0), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptedMouseButtons(Qt.LeftButton)
        
        
        scene.addItem(self)
        
        
        if source_socket and dest_socket:
            self.updatePath()
    
    def mouseDoubleClickEvent(self, event):
        """Handle double-click to disconnect"""
        if event.button() == Qt.LeftButton:
            
            self.remove()
            
            
            views = self.scene.views()
            if views:
                for view in views:
                    if hasattr(view, 'node_editor'):
                        view.node_editor.setUnsavedChanges(True)
                        
                        view.node_editor.saveState()
                        break
            
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)
    
    def updatePath(self):
        """Update the connection path between sockets"""
        
        if not self.source_socket or not self.dest_socket:
            return
        
        
        source_pos = self.source_socket.mapToScene(self.source_socket.boundingRect().center())
        dest_pos = self.dest_socket.mapToScene(self.dest_socket.boundingRect().center())
        
        
        path = QPainterPath()
        path.moveTo(source_pos)
        
        
        ctrl1 = QPointF(source_pos.x() + 100, source_pos.y())
        ctrl2 = QPointF(dest_pos.x() - 100, dest_pos.y())
        
        path.cubicTo(ctrl1, ctrl2, dest_pos)
        self.setPath(path)
    
    def remove(self):
        """Remove the connection and references to it"""
        
        
        source_node = None
        dest_node = None
        
        
        if self.source_socket:
            source_node = self.source_socket.node
            self.source_socket.removeConnection(self)
            
        if self.dest_socket:
            dest_node = self.dest_socket.node
            self.dest_socket.setConnection(None)
        
        
        self.scene.removeItem(self)

class Node(QGraphicsRectItem):
    """Base class for nodes in the editor"""
    
    def __init__(self, scene, title="Node", inputs=1, outputs=1):
        """
        Initialize a node
        
        Args:
            scene: The graphics scene
            title: Node title
            inputs: Number of input sockets
            outputs: Number of output sockets
        """
        super().__init__()
        
        self.scene = scene
        self.title = title
        self.id = str(uuid.uuid4())
        
        
        self.setRect(0, 0, NODE_WIDTH, NODE_HEIGHT)
        self.setBrush(QBrush(QColor(60, 60, 60, 230)))
        self.setPen(QPen(QColor(20, 20, 20), 2))
        
        
        self.header = QGraphicsRectItem(0, 0, NODE_WIDTH, 30, self)
        self.header.setBrush(QBrush(QColor(80, 80, 80, 230)))
        self.header.setPen(QPen(QColor(20, 20, 20), 1))
        
        
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        
        self.title_item = QGraphicsTextItem(title, self)
        self.title_item.setDefaultTextColor(QColor(255, 255, 255))
        self.title_item.setFont(QFont("Arial", 10, QFont.Bold))
        
        
        title_width = self.title_item.boundingRect().width()
        title_height = self.title_item.boundingRect().height()
        title_x = (NODE_WIDTH - title_width) / 2
        title_y = (30 - title_height) / 2  
        self.title_item.setPos(title_x, title_y)
        
        
        self.input_sockets = []
        self.output_sockets = []
        
        
        self.input_indicator = None
        self.output_indicator = None
        
        self.createSockets(inputs, outputs)
        self.createConnectionIndicators()
        
        
        scene.addItem(self)
    
    def createConnectionIndicators(self):
        """Create indicators that show connection status"""
        indicator_radius = 5
        
        
        if self.getInputCount() > 0:
            self.input_indicator = QGraphicsEllipseItem(
                5, 35,  
                indicator_radius * 2, indicator_radius * 2, 
                self
            )
            self.input_indicator.setBrush(QBrush(QColor(180, 0, 0)))  
            self.input_indicator.setPen(QPen(Qt.NoPen))  
        
        
        if self.getOutputCount() > 0:
            self.output_indicator = QGraphicsEllipseItem(
                NODE_WIDTH - 15, 35,  
                indicator_radius * 2, indicator_radius * 2, 
                self
            )
            self.output_indicator.setBrush(QBrush(QColor(180, 0, 0)))  
            self.output_indicator.setPen(QPen(Qt.NoPen))  
    
    def updateConnectionIndicators(self):
        """Update the connection indicators based on current connection status"""
        
        
        if self.input_indicator:
            
            all_inputs_connected = all(socket.isConnected() for socket in self.input_sockets)
            self.input_indicator.setBrush(QBrush(
                QColor(0, 180, 0) if all_inputs_connected else QColor(180, 0, 0)
            ))
        
        
        if self.output_indicator:
            output_connected = any(socket.isConnected() for socket in self.output_sockets)
            self.output_indicator.setBrush(QBrush(
                QColor(0, 180, 0) if output_connected else QColor(180, 0, 0)
            ))
    
    def createSockets(self, inputs, outputs):
        """Create the specified number of input and output sockets"""
        
        
        for i in range(inputs):
            socket = Socket(self, Socket.INPUT, i)
            self.input_sockets.append(socket)
        
        
        for i in range(outputs):
            socket = Socket(self, Socket.OUTPUT, i)
            self.output_sockets.append(socket)
    
    def getInputValue(self, index):
        """
        Get the value from an input socket
        
        Args:
            index: Index of the input socket
            
        Returns:
            Boolean value from the connected node, or None if not connected
        """
        if index < len(self.input_sockets):
            socket = self.input_sockets[index]
            if socket.isConnected() and socket.connection and socket.connection.source_socket:
                source_node = socket.connection.source_socket.node
                source_index = source_node.output_sockets.index(socket.connection.source_socket)
                return source_node.getOutputValue(source_index)
        return None
    
    def getOutputValue(self, index):
        """
        Get the value from an output socket
        
        Args:
            index: Index of the output socket
            
        Returns:
            Boolean value calculated by the node
        """
        
        return False
    
    def getInputCount(self):
        """Get the number of input sockets"""
        
        return len(self.input_sockets)
    
    def getOutputCount(self):
        """Get the number of output sockets"""
        
        return len(self.output_sockets)
    
    def itemChange(self, change, value):
        """Handle item changes such as movement"""
        
        if change == QGraphicsItem.ItemPositionHasChanged:
            
            for socket in self.input_sockets:
                if socket.isConnected():
                    socket.connection.updatePath()
                    
            
            for socket in self.output_sockets:
                if socket.isConnected():
                    for connection in socket.getConnections():
                        if connection:
                            connection.updatePath()
            
            
            
            for socket in self.output_sockets:
                for connection in socket.getConnections():
                    if connection and connection.dest_socket:
                        dest_node = connection.dest_socket.node
                        
                        dest_node.update()
                        
                        
                        if isinstance(dest_node, OutputNode):
                            index = dest_node.input_sockets.index(connection.dest_socket)
                            dest_node.getInputValue(index)
            
            
            views = self.scene.views()
            if views:
                node_editor = views[0].node_editor
                node_editor.saveState()
        
        return super().itemChange(change, value)
    
    def toJson(self):
        """Convert node to JSON serializable dict"""
        
        return {
            "id": self.id,
            "type": self.__class__.__name__,
            "pos_x": self.pos().x(),
            "pos_y": self.pos().y()
        }

class InputNode(Node):
    """Input node with editable value"""
    
    def __init__(self, scene):
        super().__init__(scene, "Input", 0, 1)
        
        
        self.input_field = QLineEdit("0")
        self.input_field.setMaximumWidth(80)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: 
                color: white;
                border: 1px solid 
                border-radius: 3px;
                padding: 3px;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        self.input_field.textChanged.connect(self.valueChanged)
        
        
        self.input_field.setMaxLength(1)
        self.input_field.setValidator(QRegExpValidator(QRegExp("[01]")))
        
        
        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.setWidget(self.input_field)
        
        
        x = (NODE_WIDTH - self.input_field.width()) / 2
        y = (NODE_HEIGHT - self.input_field.height()) / 2 + 5  
        self.proxy.setPos(x, y)
        
        
        self.value = False
        
        
        self.updateConnectionIndicators()
    
    def updateConnectionIndicators(self):
        """Override to only show output indicator for InputNode"""
        
        if self.output_indicator:
            output_connected = any(socket.isConnected() for socket in self.output_sockets)
            self.output_indicator.setBrush(QBrush(
                QColor(0, 180, 0) if output_connected else QColor(180, 0, 0)
            ))
    
    def valueChanged(self, text):
        """Handle input field value changes"""
        
        try:
            
            old_value = self.value
            if text.lower() in ["true", "1"]:
                self.value = True
            else:
                self.value = False
            
            
            if old_value != self.value:
                
                views = self.scene.views()
                if views:
                    node_editor = views[0].node_editor
                    node_editor.setUnsavedChanges(True)
                    
                    node_editor.saveState()
                
                
                self.propagateUpdate()
            
        except Exception as e:
            print(f"Error updating value: {str(e)}")
    
    def propagateUpdate(self):
        """Propagate update to all connected nodes"""
        visited = set()  
        nodes_to_update = set()
        
        
        for socket in self.output_sockets:
            if socket.isConnected():
                for connection in socket.getConnections():
                    if connection and connection.dest_socket:
                        dest_node = connection.dest_socket.node
                        self._collectNodesToUpdate(dest_node, visited, nodes_to_update)
        
        
        for node in nodes_to_update:
            
            node.update()
            
            
            if isinstance(node, OutputNode):
                for i in range(len(node.input_sockets)):
                    
                    node.getInputValue(i)
    
    def _collectNodesToUpdate(self, node, visited, nodes_to_update):
        """Recursively collect all nodes that need to be updated"""
        if node in visited:
            return
        
        visited.add(node)
        nodes_to_update.add(node)
        
        
        for socket in node.output_sockets:
            if socket.isConnected():
                for connection in socket.getConnections():
                    if connection and connection.dest_socket:
                        dest_node = connection.dest_socket.node
                        self._collectNodesToUpdate(dest_node, visited, nodes_to_update)
    
    def getOutputValue(self, index):
        """Get the output value"""
        
        return self.value
    
    def toJson(self):
        """Convert to JSON serializable dict with additional properties"""
        
        data = super().toJson()
        data["value"] = "1" if self.value else "0"
        return data
    
    def fromJson(self, data):
        """Load from JSON data"""
        
        self.input_field.setText(data.get("value", "0"))

class OutputNode(Node):
    """Output node that displays the result"""
    
    def __init__(self, scene):
        super().__init__(scene, "Output", 1, 0)
        
        
        self.value_text = QGraphicsTextItem("0", self)
        self.value_text.setDefaultTextColor(QColor(255, 255, 255))
        self.value_text.setFont(QFont("Arial", 24, QFont.Bold))
        
        
        self.updateValuePosition()
        
        
        self.updateConnectionIndicators()
    
    def updateValuePosition(self):
        """Update the position of the value text to keep it centered"""
        rect = self.value_text.boundingRect()
        x = (NODE_WIDTH - rect.width()) / 2
        
        y = 35 + (NODE_HEIGHT - 35 - rect.height()) / 2
        self.value_text.setPos(x, y)
    
    def updateConnectionIndicators(self):
        """Override to only show input indicator for OutputNode"""
        
        if self.input_indicator:
            
            input_connected = any(socket.isConnected() for socket in self.input_sockets)
            self.input_indicator.setBrush(QBrush(
                QColor(0, 180, 0) if input_connected else QColor(180, 0, 0)
            ))
    
    def getOutputValue(self, index):
        """Not used for output nodes"""
        
        return None
    
    def getInputValue(self, index):
        """Get input value and update the display"""
        
        value = super().getInputValue(index)
        
        
        if value is not None:
            self.value_text.setPlainText(str(int(value)))
        else:
            self.value_text.setPlainText("0")
        
        
        self.updateValuePosition()
        
        return value

class WriteOutputNode(OutputNode):
    """Output node that can write results to a file"""
    
    def __init__(self, scene):
        super().__init__(scene)
        self.title = "Write Output"
        self.title_item.setPlainText(self.title)
        
        
        
        self.updateValuePosition()
        
        
        self.write_button = QPushButton("Write")
        self.write_button.setMaximumWidth(80)
        self.write_button.setStyleSheet("""
            QPushButton {
                background-color: 
                color: white;
                border: 1px solid 
                border-radius: 3px;
                padding: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: 
            }
            QPushButton:pressed {
                background-color: 
            }
        """)
        self.write_button.clicked.connect(self.writeOutput)
        
        
        self.button_proxy = QGraphicsProxyWidget(self)
        self.button_proxy.setWidget(self.write_button)
        
        self.button_proxy.setPos((NODE_WIDTH - self.write_button.width()) / 2, NODE_HEIGHT - 30)
        
        
        self.updateTitlePosition()
    
    def updateTitlePosition(self):
        """Update the position of the title text"""
        title_width = self.title_item.boundingRect().width()
        title_height = self.title_item.boundingRect().height()
        title_x = (NODE_WIDTH - title_width) / 2
        title_y = (30 - title_height) / 2  
        self.title_item.setPos(title_x, title_y)
    
    def updateValuePosition(self):
        """Override to position value text higher up to accommodate button"""
        rect = self.value_text.boundingRect()
        x = (NODE_WIDTH - rect.width()) / 2
        
        y = 35 + (NODE_HEIGHT - 35 - 30 - rect.height()) / 2 - 5
        self.value_text.setPos(x, y)
    
    def getInputValue(self, index):
        """Override to ensure display updates immediately"""
        value = super().getInputValue(index)
        
        self.updateValuePosition()
        return value
    
    def writeOutput(self):
        """Write the current output value to a file"""
        
        value = self.getInputValue(0)
        
        if value is not None:
            
            filePath, _ = QFileDialog.getSaveFileName(
                None, "Save Output", "", "Text Files (*.txt);;All Files (*)"
            )
            
            if filePath:
                try:
                    with open(filePath, 'w') as f:
                        f.write(f"Logic Gate Output: {int(value)}\n\n")
                        
                        
                        equation = self.deriveEquation()
                        if equation:
                            f.write(f"Logic Equation: {equation}")
                except Exception as e:
                    print(f"Error writing to file: {str(e)}")
    
    def deriveEquation(self):
        """Derive the logic equation from the connected circuit"""
        
        if not self.input_sockets or not self.input_sockets[0].isConnected():
            return "No connected circuit"
        
        
        input_socket = self.input_sockets[0]
        if not input_socket.connection or not input_socket.connection.source_socket:
            return "No connected circuit"
        
        source_node = input_socket.connection.source_socket.node
        
        
        input_node_map = {}
        
        
        visited = set()
        equation = self._buildEquation(source_node, visited, input_node_map)
        return equation
    
    def _buildEquation(self, node, visited, input_node_map):
        """Recursively build the equation for a node"""
        
        if node.id in visited:
            return "(...)"
        
        visited.add(node.id)
        
        if isinstance(node, InputNode):
            
            if node.id not in input_node_map:
                
                letter = chr(65 + len(input_node_map))  
                if len(input_node_map) >= 26:  
                    letter = f"Input_{len(input_node_map) + 1}"
                input_node_map[node.id] = letter
            
            
            return input_node_map[node.id]
        
        elif isinstance(node, AndNode):
            
            inputs = []
            for i in range(node.getInputCount()):
                if i < len(node.input_sockets) and node.input_sockets[i].isConnected():
                    socket = node.input_sockets[i]
                    if socket.connection and socket.connection.source_socket:
                        source = socket.connection.source_socket.node
                        input_eq = self._buildEquation(source, visited.copy(), input_node_map)
                        inputs.append(input_eq)
            
            if not inputs:
                return "0"  
            
            
            inputs = [f"({inp})" if ' ' in inp and not (inp.startswith('(') and inp.endswith(')')) else inp for inp in inputs]
            
            
            return " * ".join(inputs)
        
        elif isinstance(node, OrNode):
            
            inputs = []
            for i in range(node.getInputCount()):
                if i < len(node.input_sockets) and node.input_sockets[i].isConnected():
                    socket = node.input_sockets[i]
                    if socket.connection and socket.connection.source_socket:
                        source = socket.connection.source_socket.node
                        input_eq = self._buildEquation(source, visited.copy(), input_node_map)
                        inputs.append(input_eq)
            
            if not inputs:
                return "0"  
            
            
            inputs = [f"({inp})" if ' ' in inp and not (inp.startswith('(') and inp.endswith(')')) else inp for inp in inputs]
            
            
            return " + ".join(inputs)
        
        elif isinstance(node, NotNode):
            
            if node.getInputCount() > 0 and node.input_sockets[0].isConnected():
                socket = node.input_sockets[0]
                if socket.connection and socket.connection.source_socket:
                    source = socket.connection.source_socket.node
                    input_eq = self._buildEquation(source, visited.copy(), input_node_map)
                    
                    if ' ' in input_eq:
                        return f"!({input_eq})"
                    else:
                        return f"!{input_eq}"
            
            return "1"  
        
        elif isinstance(node, NandNode):
            
            inputs = []
            for i in range(node.getInputCount()):
                if i < len(node.input_sockets) and node.input_sockets[i].isConnected():
                    socket = node.input_sockets[i]
                    if socket.connection and socket.connection.source_socket:
                        source = socket.connection.source_socket.node
                        input_eq = self._buildEquation(source, visited.copy(), input_node_map)
                        inputs.append(input_eq)
            
            if not inputs:
                return "1"  
            
            
            inputs = [f"({inp})" if ' ' in inp and not (inp.startswith('(') and inp.endswith(')')) else inp for inp in inputs]
            
            
            return f"!({' * '.join(inputs)})"
        
        elif isinstance(node, NorNode):
            
            inputs = []
            for i in range(node.getInputCount()):
                if i < len(node.input_sockets) and node.input_sockets[i].isConnected():
                    socket = node.input_sockets[i]
                    if socket.connection and socket.connection.source_socket:
                        source = socket.connection.source_socket.node
                        input_eq = self._buildEquation(source, visited.copy(), input_node_map)
                        inputs.append(input_eq)
            
            if not inputs:
                return "1"  
            
            
            inputs = [f"({inp})" if ' ' in inp and not (inp.startswith('(') and inp.endswith(')')) else inp for inp in inputs]
            
            
            return f"!({' + '.join(inputs)})"
        
        elif isinstance(node, XorNode):
            
            inputs = []
            for i in range(node.getInputCount()):
                if i < len(node.input_sockets) and node.input_sockets[i].isConnected():
                    socket = node.input_sockets[i]
                    if socket.connection and socket.connection.source_socket:
                        source = socket.connection.source_socket.node
                        input_eq = self._buildEquation(source, visited.copy(), input_node_map)
                        inputs.append(input_eq)
            
            if not inputs:
                return "0"  
            
            if len(inputs) == 1:
                return inputs[0]  
            
            
            if len(inputs) == 2:
                a, b = inputs
                if ' ' in a:
                    a = f"({a})"
                if ' ' in b:
                    b = f"({b})"
                return f"{a} ^ {b}"
            
            
            result = inputs[0]
            for i in range(1, len(inputs)):
                a = result
                b = inputs[i]
                if ' ' in a:
                    a = f"({a})"
                if ' ' in b:
                    b = f"({b})"
                result = f"{a} ^ {b}"
            return result
        
        elif isinstance(node, XnorNode):
            
            inputs = []
            for i in range(node.getInputCount()):
                if i < len(node.input_sockets) and node.input_sockets[i].isConnected():
                    socket = node.input_sockets[i]
                    if socket.connection and socket.connection.source_socket:
                        source = socket.connection.source_socket.node
                        input_eq = self._buildEquation(source, visited.copy(), input_node_map)
                        inputs.append(input_eq)
            
            if not inputs:
                return "1"  
            
            if len(inputs) == 1:
                
                input_eq = inputs[0]
                if ' ' in input_eq:
                    return f"!({input_eq})"
                else:
                    return f"!{input_eq}"
            
            
            if len(inputs) == 2:
                a, b = inputs
                if ' ' in a:
                    a = f"({a})"
                if ' ' in b:
                    b = f"({b})"
                return f"!({a} ^ {b})"
            
            
            result = inputs[0]
            for i in range(1, len(inputs)):
                a = result
                b = inputs[i]
                if ' ' in a:
                    a = f"({a})"
                if ' ' in b:
                    b = f"({b})"
                if i == len(inputs) - 1:
                    
                    result = f"!({a} ^ {b})"
                else:
                    
                    result = f"{a} ^ {b}"
            return result
        
        
        return f"Node_{node.id[:4]}"

class LogicGateNode(Node):
    """Base class for logic gate nodes"""
    
    
    _symbol_cache = {}
    
    def __init__(self, scene, title, inputs=2, outputs=1):
        super().__init__(scene, title, inputs, outputs)
        
        
        symbol_text = self.getSymbolText()
        
        
        self.symbol_text = QGraphicsTextItem(symbol_text, self)
        self.symbol_text.setDefaultTextColor(QColor(220, 220, 220))
        self.symbol_text.setFont(QFont("Arial", 20, QFont.Bold))
        
        
        self.updateSymbolPosition()
    
    def updateSymbolPosition(self):
        """Position the symbol in the center of the node body"""
        rect = self.symbol_text.boundingRect()
        x = (NODE_WIDTH - rect.width()) / 2
        
        y = 35 + (NODE_HEIGHT - 35 - rect.height()) / 2
        self.symbol_text.setPos(x, y)
    
    def getSymbolText(self):
        """Get the symbol text for the logic gate"""
        return "?"

class AndNode(LogicGateNode):
    """AND gate node"""
    
    def __init__(self, scene):
        super().__init__(scene, "AND")
    
    def getSymbolText(self):
        
        return "∧"
    
    def getOutputValue(self, index):
        """Implement AND logic"""
        
        input1 = self.getInputValue(0)
        input2 = self.getInputValue(1)
        
        if input1 is None or input2 is None:
            return None
        
        return input1 and input2

class OrNode(LogicGateNode):
    """OR gate node"""
    
    def __init__(self, scene):
        super().__init__(scene, "OR")
    
    def getSymbolText(self):
        
        return "∨"
    
    def getOutputValue(self, index):
        """Implement OR logic"""
        
        input1 = self.getInputValue(0)
        input2 = self.getInputValue(1)
        
        if input1 is None or input2 is None:
            return None
        
        return input1 or input2

class NotNode(LogicGateNode):
    """NOT gate node"""
    
    def __init__(self, scene):
        super().__init__(scene, "NOT", 1, 1)
    
    def getSymbolText(self):
        
        return "¬"
    
    def getOutputValue(self, index):
        """Implement NOT logic"""
        
        input_val = self.getInputValue(0)
        
        if input_val is None:
            return None
        
        return not input_val

class NandNode(LogicGateNode):
    """NAND gate node"""
    
    def __init__(self, scene):
        super().__init__(scene, "NAND")
    
    def getSymbolText(self):
        
        return "⊼"
    
    def getOutputValue(self, index):
        """Implement NAND logic"""
        
        input1 = self.getInputValue(0)
        input2 = self.getInputValue(1)
        
        if input1 is None or input2 is None:
            return None
        
        return not (input1 and input2)

class NorNode(LogicGateNode):
    """NOR gate node"""
    
    def __init__(self, scene):
        super().__init__(scene, "NOR")
    
    def getSymbolText(self):
        
        return "⊽"
    
    def getOutputValue(self, index):
        """Implement NOR logic"""
        
        input1 = self.getInputValue(0)
        input2 = self.getInputValue(1)
        
        if input1 is None or input2 is None:
            return None
        
        return not (input1 or input2)

class XorNode(LogicGateNode):
    """XOR gate node"""
    
    def __init__(self, scene):
        super().__init__(scene, "XOR")
    
    def getSymbolText(self):
        
        return "⊕"
    
    def getOutputValue(self, index):
        """Implement XOR logic"""
        
        input1 = self.getInputValue(0)
        input2 = self.getInputValue(1)
        
        if input1 is None or input2 is None:
            return None
        
        return input1 != input2

class XnorNode(LogicGateNode):
    """XNOR gate node"""
    
    def __init__(self, scene):
        super().__init__(scene, "XNOR")
    
    def getSymbolText(self):
        
        return "⊙"
    
    def getOutputValue(self, index):
        """Implement XNOR logic"""
        
        input1 = self.getInputValue(0)
        input2 = self.getInputValue(1)
        
        if input1 is None or input2 is None:
            return None
        
        return input1 == input2

class GridGraphicsView(QGraphicsView):
    """Graphics view with grid background and drop handling"""
    
    def __init__(self, scene, node_editor):
        super().__init__(scene)
        self.node_editor = node_editor
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setAcceptDrops(True)
        
        
        self.setDragMode(QGraphicsView.RubberBandDrag)
        
        
        self.dragging_item = False
        self.is_selecting = False
        self.selection_start = QPointF()
        
        
        self.first_node_added = False
    
    def drawBackground(self, painter, rect):
        """Draw a grid in the background"""
        super().drawBackground(painter, rect)
        painter.fillRect(rect, self.backgroundBrush())

        
        bg_color = self.backgroundBrush().color()
        
        if bg_color.lightnessF() < 0.5:
             grid_color = QColor(60, 60, 60, 150) 
        else:
             grid_color = QColor(220, 220, 220, 150) 
        
        
        painter.save()
        
        
        painter.setPen(QPen(grid_color, 1, Qt.SolidLine))
        
        
        left = int(rect.left()) - (int(rect.left()) % GRID_SIZE)
        top = int(rect.top()) - (int(rect.top()) % GRID_SIZE)
        
        
        x = left
        while x < rect.right():
            painter.drawLine(x, rect.top(), x, rect.bottom())
            x += GRID_SIZE
        
        
        y = top
        while y < rect.bottom():
            painter.drawLine(rect.left(), y, rect.right(), y)
            y += GRID_SIZE
        
        
        painter.restore()
    
    def mousePressEvent(self, event):
        """Track when we start dragging items or selection"""
        if event.button() == Qt.LeftButton:
            item_under_cursor = self.itemAt(event.pos())
            if item_under_cursor and isinstance(item_under_cursor, Node):
                self.dragging_item = True
                
                super().mousePressEvent(event)
            elif not self.node_editor.temp_connection:
                
                self.is_selecting = True
                self.selection_start = self.mapToScene(event.pos())
                super().mousePressEvent(event)
            else:
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Pass mouse move events to the node editor for connection drawing and handle selection"""
        if self.node_editor.viewMouseMoveEvent(event):
            return  
        
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events and mark unsaved changes if we were dragging a node or rubber band"""
        if self.dragging_item:
            self.node_editor.setUnsavedChanges(True)
            self.dragging_item = False
        
        if self.is_selecting:
            self.is_selecting = False
            
        
        if self.node_editor.temp_connection:
            self.node_editor.endConnection()
            event.accept()
            return
        
        super().mouseReleaseEvent(event)
    
    def dragEnterEvent(self, event):
        """Accept drag events if they contain text (our node type)"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)
    
    def dragMoveEvent(self, event):
        """Accept the move action during drag"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)
    
    def dropEvent(self, event):
        """Handle the drop event to create a node"""
        if event.mimeData().hasText():
            node_type_name = event.mimeData().text()
            
            
            if node_type_name in self.node_editor.node_types:
                
                if not self.first_node_added:
                    self.setCursor(Qt.WaitCursor)
                
                node_class = self.node_editor.node_types[node_type_name]
                
                
                drop_pos = self.mapToScene(event.pos())
                
                node = node_class(self.scene())
                
                node.setPos(drop_pos.x() - NODE_WIDTH / 2, drop_pos.y() - NODE_HEIGHT / 2)
                
                
                node.updateConnectionIndicators()
                
                
                self.node_editor.saveState()
                
                
                self.node_editor.setUnsavedChanges(True)
                
                
                if not self.first_node_added:
                    self.first_node_added = True
                    self.setCursor(Qt.ArrowCursor)
                
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            super().dropEvent(event)

class NodeEditor(QWidget):
    """Widget for editing nodes and connections"""
    
    def __init__(self):
        super().__init__()
        
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 5000, 5000)
        
        
        
        
        
        self.view = GridGraphicsView(self.scene, self)
        
        
        
        layout.addWidget(self.view)
        
        
        self.temp_connection = None
        self.source_socket = None
        
        
        self.history = []
        self.history_index = -1
        self.clipboard = []
        
        
        self.file_path = None
        self.unsaved_changes = False
        
        
        self.node_types = {
            "InputNode": InputNode,
            "OutputNode": OutputNode,
            "WriteOutputNode": WriteOutputNode,
            "AndNode": AndNode,
            "OrNode": OrNode,
            "NotNode": NotNode,
            "NandNode": NandNode,
            "NorNode": NorNode,
            "XorNode": XorNode,
            "XnorNode": XnorNode
        }
        
        
        self._preloadFonts()
    
    def _preloadFonts(self):
        """Preload fonts to avoid lag on first node creation"""
        
        
        temp_text = QGraphicsTextItem("Preload Font")
        temp_text.setFont(QFont("Arial", 20, QFont.Bold))
        temp_text.setFont(QFont("Arial", 10, QFont.Bold))
        
        
        temp_text.document().idealWidth()
        
        
        for symbol in ["∧", "∨", "¬", "⊼", "⊽", "⊕", "⊙"]:
            temp_symbol = QGraphicsTextItem(symbol)
            temp_symbol.setFont(QFont("Arial", 20, QFont.Bold))
            temp_symbol.document().idealWidth()
    
    def mouseMoveEvent(self, event):
        """Handle mouse movement for connection creation"""
        
        if self.temp_connection:
            
            scene_pos = self.view.mapToScene(event.pos())
            self.updateConnection(scene_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)
            
    
    def viewMouseMoveEvent(self, event):
        """Handle mouse movement in the view for updating connections"""
        if self.temp_connection:
            scene_pos = self.view.mapToScene(event.pos())
            self.updateConnection(scene_pos)
            event.accept()
            return True
        return False
    
    def startConnection(self, socket):
        """Start creating a connection from a socket"""
        if self.temp_connection: 
            self.scene.removeItem(self.temp_connection)
            self.temp_connection = None
            self.source_socket = None

        if socket.isOutput():
            self.source_socket = socket
            
            self.temp_connection = Connection(self.scene, source_socket=socket) 
            
            self.updateConnection(socket.mapToScene(socket.boundingRect().center())) 
        elif socket.isInput(): 
             if socket.isConnected():
                
                self.temp_connection = socket.connection 
                self.source_socket = self.temp_connection.source_socket 
                socket.setConnection(None) 
                self.temp_connection.dest_socket = None 
                
                self.updateConnection(socket.mapToScene(socket.boundingRect().center())) 

    def updateConnection(self, scene_pos):
        """Update temporary connection path when dragging to scene position"""
        if self.temp_connection and self.source_socket:
            source_pos = self.source_socket.mapToScene(self.source_socket.boundingRect().center())
            path = QPainterPath(source_pos)
            dx = scene_pos.x() - source_pos.x()
            dy = scene_pos.y() - source_pos.y()
            ctrl1 = QPointF(source_pos.x() + dx * 0.5, source_pos.y()) 
            ctrl2 = QPointF(source_pos.x() + dx * 0.5, scene_pos.y())
            path.cubicTo(ctrl1, ctrl2, scene_pos)
            self.temp_connection.setPath(path)

    def endConnection(self):
        """Complete or cancel the current connection attempt"""
        if not self.temp_connection or not self.source_socket:
            return 

        
        target_pos = self.view.mapToScene(self.view.mapFromGlobal(QCursor.pos()))
        item_under_cursor = self.scene.itemAt(target_pos, self.view.transform())

        target_socket = None
        if isinstance(item_under_cursor, Socket):
            target_socket = item_under_cursor
            
        
        if (target_socket and target_socket.isInput() and 
            target_socket.node != self.source_socket.node and
            not target_socket.isConnected()): 

            
            self.temp_connection.dest_socket = target_socket
            self.source_socket.setConnection(self.temp_connection)
            target_socket.setConnection(self.temp_connection)
            self.temp_connection.updatePath() 
            
            
            if isinstance(self.source_socket.node, InputNode):
                self.source_socket.node.propagateUpdate()
            else:
                
                target_socket.node.update()
                if isinstance(target_socket.node, OutputNode):
                    index = target_socket.node.input_sockets.index(target_socket)
                    target_socket.node.getInputValue(index)
            
            
            self.source_socket.node.updateConnectionIndicators()
            target_socket.node.updateConnectionIndicators()
            
            
            self.saveState()
                    
            self.setUnsavedChanges(True)
        else:
            
            self.scene.removeItem(self.temp_connection)

        
        self.temp_connection = None
        self.source_socket = None

    
    
    

    def mouseReleaseEvent(self, event):
        """Handle mouse release to finalize connection dragging"""
        if self.temp_connection:
            self.endConnection()
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def undo(self):
        """Undo the last action"""
        
        if self.history_index > 0:
            self.history_index -= 1
            
            
            state = self.history[self.history_index]
            self.loadFromJson(state)
            
            
            self.setUnsavedChanges(True)
    
    def redo(self):
        """Redo the last undone action"""
        
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            
            
            state = self.history[self.history_index]
            self.loadFromJson(state)
            
            
            self.setUnsavedChanges(True)
    
    def saveState(self):
        """Save current state to history"""
        
        
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        
        state = self.saveToJson()
        self.history.append(state)
        self.history_index = len(self.history) - 1
        
        
        if len(self.history) > 20:
            self.history = self.history[-20:]
            self.history_index = len(self.history) - 1
    
    def cut(self):
        """Cut selected nodes to clipboard"""
        
        
        self.copy()
        
        
        self.delete()
    
    def copy(self):
        """Copy selected nodes to clipboard"""
        
        self.clipboard = []
        
        
        selected_nodes = []
        for item in self.scene.selectedItems():
            if isinstance(item, Node):
                selected_nodes.append(item)
        
        
        self.clipboard = []
        
        
        for node in selected_nodes:
            self.clipboard.append({
                "type": node.__class__.__name__,
                "pos_x": node.pos().x(),
                "pos_y": node.pos().y()
            })
    
    def paste(self):
        """Paste nodes from clipboard"""
        
        if not self.clipboard:
            return
        
        
        self.saveState()
        
        
        for item in self.scene.selectedItems():
            item.setSelected(False)
        
        
        for node_data in self.clipboard:
            node_type = node_data["type"]
            
            if node_type in self.node_types:
                node_class = self.node_types[node_type]
                node = node_class(self.scene)
                
                
                node.setPos(node_data["pos_x"] + 20, node_data["pos_y"] + 20)
                
                
                node.setSelected(True)
        
        
        self.setUnsavedChanges(True)
    
    def delete(self):
        """Delete selected items"""
        
        
        self.saveState()
        
        
        selected_items = self.scene.selectedItems()
        
        
        affected_nodes = set()
        for item in selected_items:
            if isinstance(item, Connection):
                if item.source_socket:
                    affected_nodes.add(item.source_socket.node)
                if item.dest_socket:
                    affected_nodes.add(item.dest_socket.node)
                item.remove()
        
        
        for item in selected_items:
            if isinstance(item, Node):
                
                for socket in item.input_sockets + item.output_sockets:
                    if socket.isConnected():
                        for conn in socket.getConnections():
                            if conn:
                                
                                if socket.isInput() and conn.source_socket:
                                    affected_nodes.add(conn.source_socket.node)
                                elif socket.isOutput() and conn.dest_socket:
                                    affected_nodes.add(conn.dest_socket.node)
                                conn.remove()
                
                
                self.scene.removeItem(item)
                if item in affected_nodes:
                    affected_nodes.remove(item)
        
        
        for node in affected_nodes:
            node.updateConnectionIndicators()
        
        
        self.setUnsavedChanges(True)
    
    def saveToJson(self):
        """Save the current node editor state to JSON"""
        
        data = {
            "nodes": [],
            "connections": []
        }
        
        
        for item in self.scene.items():
            if isinstance(item, Node):
                node_data = item.toJson()
                data["nodes"].append(node_data)
        
        
        for item in self.scene.items():
            if isinstance(item, Connection) and item.source_socket and item.dest_socket:
                connection_data = {
                    "source_node": item.source_socket.node.id,
                    "source_socket": item.source_socket.index,
                    "dest_node": item.dest_socket.node.id,
                    "dest_socket": item.dest_socket.index
                }
                data["connections"].append(connection_data)
        
        return data
    
    def loadFromJson(self, data):
        """Load node editor state from JSON"""
        
        
        self.scene.clear()
        self.temp_connection = None
        self.source_socket = None
        
        
        nodes = {}
        
        
        for node_data in data.get("nodes", []):
            node_type = node_data.get("type")
            node_id = node_data.get("id")
            
            if node_type in self.node_types:
                node_class = self.node_types[node_type]
                node = node_class(self.scene)
                
                
                node.setPos(node_data.get("pos_x", 0), node_data.get("pos_y", 0))
                
                
                node.id = node_id
                
                
                nodes[node_id] = node
                
                
                if hasattr(node, "fromJson"):
                    node.fromJson(node_data)
        
        
        for conn_data in data.get("connections", []):
            source_node_id = conn_data.get("source_node")
            source_socket_idx = conn_data.get("source_socket")
            dest_node_id = conn_data.get("dest_node")
            dest_socket_idx = conn_data.get("dest_socket")
            
            if (source_node_id in nodes and dest_node_id in nodes and
                source_socket_idx < len(nodes[source_node_id].output_sockets) and
                dest_socket_idx < len(nodes[dest_node_id].input_sockets)):
                
                source_socket = nodes[source_node_id].output_sockets[source_socket_idx]
                dest_socket = nodes[dest_node_id].input_sockets[dest_socket_idx]
                
                
                connection = Connection(self.scene, source_socket, dest_socket)
                source_socket.setConnection(connection)
                dest_socket.setConnection(connection)
                connection.updatePath()
        
        
        for node in nodes.values():
            node.updateConnectionIndicators()
    
    def setFilePath(self, path):
        """Set the file path for this editor"""
        
        self.file_path = path
    
    def getFilePath(self):
        """Get the file path for this editor"""
        
        return self.file_path
    
    def setUnsavedChanges(self, value):
        """Set the unsaved changes flag"""
        
        self.unsaved_changes = value
    
    def hasUnsavedChanges(self):
        """Check if there are unsaved changes"""
        
        return self.unsaved_changes
