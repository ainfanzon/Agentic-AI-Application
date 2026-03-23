import sys
import os

# 1. DYNAMIC PATHING: Find the absolute path to the project root
# This moves up one level from 'scripts/' to 'autonomous_analyst/'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

# Insert it at the beginning of the path so it takes priority
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# 2. IMPORTS (Standard Libraries)
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                             QHBoxLayout, QWidget, QPushButton, QLabel)
from PySide6.QtCore import Qt
import seaborn as sns

# 3. SWARM IMPORT: Now that pathing is set, this will work
try:
    from services.agent_orchestrator.graph import app
    print(f"Swarm Graph found at: {ROOT_DIR}")
except ImportError as e:
    print(f"AICA Critical Error: Could not find 'services' folder in {ROOT_DIR}")
    print(f"Actual sys.path: {sys.path[:3]}") # Debugging info
    sys.exit(1)

# ... [Rest of your SwarmWindow class remains the same] ...
class SwarmWindow(QMainWindow):
    def __init__(self, langgraph_app):
        super().__init__()
        self.setWindowTitle("Swarm Intelligence: Interactive DAG Explorer")
        self.resize(1100, 850)
        self.app = langgraph_app
        
        # Interaction State
        self.selected_node = None
        self.pos = {}
        self.G = nx.DiGraph()

        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # UI Header
        header = QHBoxLayout()
        header.addWidget(QLabel("DRAG NODES TO REORGANIZE"))
        btn_export = QPushButton("📸 SAVE PNG")
        btn_export.clicked.connect(self.export_png)
        header.addWidget(btn_export)
        layout.addLayout(header)

        # Setup Figure
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        
        # Connect Matplotlib Events
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)

        self.init_graph()

    def init_graph(self):
        """Build initial graph and positions."""
        graph_info = self.app.get_graph()
        for edge in graph_info.edges:
            self.G.add_edge(edge.source, edge.target)
        
        # Initial layout
        self.pos = nx.spring_layout(self.G, k=1.8, iterations=60)
        self.update_plot()

    def update_plot(self):
        """Redraws the graph efficiently."""
        self.ax.clear()
        
        # Force a clean, professional aesthetic for the demo
        sns.set_theme(style="white")
        self.ax.set_facecolor('#f8f9fa')

        # Node Color Mapping
        colors = []
        for node in self.G.nodes():
            n = node.lower()
            if "memory" in n: colors.append("#c2e5fc")
            elif "__start__" in n: colors.append("#d9fae7")
            elif "__end__" in n: colors.append("#fabab4")
            elif "planner" in n: colors.append("#fcefb8")
            else: colors.append("#f3e3fa")

        # Use draw() with the specific axis to avoid global overhead
        nx.draw(
            self.G, self.pos, ax=self.ax, with_labels=True, 
            labels={n: n.replace("__", "").replace("_", " ").title() for n in self.G.nodes()},
            node_color=colors, node_size=3500, font_size=8, font_weight="bold",
            edge_color="#bdc3c7", width=1.5, arrowsize=18, 
            connectionstyle='arc3, rad=0.1', # Reduced radius for faster rendering
            arrowstyle='-|>'
        )
        
        self.ax.set_axis_off()
        
        # CRITICAL: Use draw_idle instead of draw. 
        # It requests a redraw but doesn't block the current event loop.
        self.canvas.draw_idle()

    # --- Interaction Logic ---
    def on_press(self, event):
        if event.inaxes != self.ax: return
        # Check if click is near a node
        for node, (x, y) in self.pos.items():
            distance = ((x - event.xdata)**2 + (y - event.ydata)**2)**0.5
            if distance < 0.1:  # Threshold for "picking" a node
                self.selected_node = node
                break

    def on_release(self, event):
        self.selected_node = None

    def on_motion(self, event):
        # Only process if a node is grabbed and we are inside the plot area
        if self.selected_node is not None and event.inaxes == self.ax:
            new_x, new_y = event.xdata, event.ydata
            old_x, old_y = self.pos[self.selected_node]

            # THROTTLING: Only redraw if the movement is more than 0.02 units
            # This prevents thousands of tiny updates from hanging the CPU
            distance_moved = ((new_x - old_x)**2 + (new_y - old_y)**2)**0.5
            
            if distance_moved > 0.02:
                self.pos[self.selected_node] = [new_x, new_y]
                self.update_plot()

    def export_png(self):
        self.fig.savefig("custom_swarm_layout.png", dpi=300, bbox_inches='tight')
        print("💾 Saved custom layout.")

if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    window = SwarmWindow(app)
    window.show()
    sys.exit(qt_app.exec())
