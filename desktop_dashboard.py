import sys
import json
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTableView, QPushButton, QLineEdit, QFormLayout, QGroupBox,
    QHeaderView, QMessageBox
)
from PySide6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PySide6.QtCore import Qt, QTimer

DB_PATH = "pierre_quant.db"
AGENT_REGISTRY_PATH = "agent_registry.json"
GATEWAY_SIGNAL_PATH = "gateway_signal.log"

# --- QSS Styling ---
CYBERPUNK_QSS = """
QMainWindow {
    background-color: #0a0a0a;
}
QWidget {
    background-color: #0a0a0a;
    color: #e4e4e7;
    font-family: "Courier New", monospace;
    font-size: 13px;
}
QGroupBox {
    border: 1px solid #1e293b;
    border-radius: 4px;
    margin-top: 1.5ex;
    font-weight: bold;
    color: #00ff41;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 3px;
}
QTableView {
    background-color: #060910;
    gridline-color: #1e293b;
    border: 1px solid #1e293b;
    color: #e4e4e7;
    selection-background-color: #00d4ff;
    selection-color: #0a0a0a;
}
QHeaderView::section {
    background-color: #121826;
    color: #00ff41;
    border: 1px solid #1e293b;
    padding: 4px;
    font-weight: bold;
}
QPushButton {
    background-color: #121826;
    border: 1px solid #00ff41;
    color: #00ff41;
    padding: 6px;
    border-radius: 3px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #00ff41;
    color: #0a0a0a;
}
QPushButton#deleteBtn {
    border: 1px solid #ff003c;
    color: #ff003c;
}
QPushButton#deleteBtn:hover {
    background-color: #ff003c;
    color: #0a0a0a;
}
QLineEdit {
    background-color: #060910;
    border: 1px solid #1e293b;
    color: #00d4ff;
    padding: 4px;
}
QLineEdit:focus {
    border: 1px solid #00d4ff;
}
QLabel#agentLabel {
    color: #00d4ff;
    padding: 2px;
}
"""

class CyberpunkDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JENNY // TACTICAL TERMINAL")
        self.resize(1000, 600)

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(DB_PATH)
        if not self.db.open():
            QMessageBox.critical(self, "Database Error", f"Could not open database {DB_PATH}")
            sys.exit(1)

        self.init_ui()

        # Setup polling for agent registry
        self.agent_timer = QTimer(self)
        self.agent_timer.timeout.connect(self.update_agent_registry)
        self.agent_timer.start(2000) # Poll every 2 seconds

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # --- LEFT PANEL (Portfolio & Management) ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Portfolio Table
        self.model = QSqlTableModel(self, self.db)
        self.model.setTable("watchlist")
        self.model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model.select()

        self.model.setHeaderData(0, Qt.Horizontal, "Ticker")
        self.model.setHeaderData(1, Qt.Horizontal, "Shares")
        self.model.setHeaderData(2, Qt.Horizontal, "Avg Cost")
        self.model.setHeaderData(3, Qt.Horizontal, "Currency")

        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.clicked.connect(self.on_table_click)

        portfolio_group = QGroupBox("PORTFOLIO INVENTORY")
        pg_layout = QVBoxLayout()
        pg_layout.addWidget(self.table_view)
        portfolio_group.setLayout(pg_layout)
        left_layout.addWidget(portfolio_group)

        # Ticker Management Form
        manage_group = QGroupBox("TICKER MANAGEMENT")
        manage_layout = QVBoxLayout()

        form_layout = QFormLayout()
        self.input_ticker = QLineEdit()
        self.input_shares = QLineEdit()
        self.input_cost = QLineEdit()
        self.input_currency = QLineEdit()

        form_layout.addRow("Ticker:", self.input_ticker)
        form_layout.addRow("Shares:", self.input_shares)
        form_layout.addRow("Avg Cost:", self.input_cost)
        form_layout.addRow("Currency:", self.input_currency)
        manage_layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("ADD / UPDATE")
        self.btn_delete = QPushButton("DELETE")
        self.btn_delete.setObjectName("deleteBtn")

        self.btn_add.clicked.connect(self.add_or_update_ticker)
        self.btn_delete.clicked.connect(self.delete_ticker)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_delete)
        manage_layout.addLayout(btn_layout)

        manage_group.setLayout(manage_layout)
        left_layout.addWidget(manage_group)

        main_layout.addWidget(left_panel, stretch=3)

        # --- RIGHT PANEL (Agent Registry) ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        agent_group = QGroupBox("SWARM REGISTRY")
        self.agent_layout = QVBoxLayout()
        self.agent_layout.setAlignment(Qt.AlignTop)

        self.agent_labels = {}

        agent_group.setLayout(self.agent_layout)
        right_layout.addWidget(agent_group)

        main_layout.addWidget(right_panel, stretch=1)

        self.update_agent_registry()

    def on_table_click(self, index):
        row = index.row()
        self.input_ticker.setText(str(self.model.data(self.model.index(row, 0))))
        self.input_shares.setText(str(self.model.data(self.model.index(row, 1))))
        self.input_cost.setText(str(self.model.data(self.model.index(row, 2))))
        self.input_currency.setText(str(self.model.data(self.model.index(row, 3))))

    def emit_gateway_signal(self):
        try:
            with open(GATEWAY_SIGNAL_PATH, "a") as f:
                f.write("REFRESH_SWARM\n")
            print("[SIGNAL] Emitted REFRESH_SWARM to Gateway.")
        except Exception as e:
            print(f"[ERROR] Failed to emit signal: {e}")

    def add_or_update_ticker(self):
        ticker = self.input_ticker.text().strip().upper()
        if not ticker: return

        shares = self.input_shares.text().strip()
        cost = self.input_cost.text().strip()
        currency = self.input_currency.text().strip().upper()

        query = QSqlQuery(self.db)
        query.prepare("SELECT * FROM watchlist WHERE ticker = :ticker")
        query.bindValue(":ticker", ticker)
        query.exec()

        if query.next():
            # Update
            q2 = QSqlQuery(self.db)
            q2.prepare("UPDATE watchlist SET shares=:shares, avg_cost=:cost, currency=:currency WHERE ticker=:ticker")
            q2.bindValue(":shares", shares)
            q2.bindValue(":cost", cost)
            q2.bindValue(":currency", currency)
            q2.bindValue(":ticker", ticker)
            q2.exec()
        else:
            # Insert
            q2 = QSqlQuery(self.db)
            q2.prepare("INSERT INTO watchlist (ticker, shares, avg_cost, currency) VALUES (:ticker, :shares, :cost, :currency)")
            q2.bindValue(":ticker", ticker)
            q2.bindValue(":shares", shares)
            q2.bindValue(":cost", cost)
            q2.bindValue(":currency", currency)
            q2.exec()

        self.model.select()
        self.emit_gateway_signal()

    def delete_ticker(self):
        ticker = self.input_ticker.text().strip().upper()
        if not ticker: return

        query = QSqlQuery(self.db)
        query.prepare("DELETE FROM watchlist WHERE ticker=:ticker")
        query.bindValue(":ticker", ticker)
        query.exec()

        self.input_ticker.clear()
        self.input_shares.clear()
        self.input_cost.clear()
        self.input_currency.clear()

        self.model.select()
        self.emit_gateway_signal()

    def update_agent_registry(self):
        if not os.path.exists(AGENT_REGISTRY_PATH):
            return

        try:
            with open(AGENT_REGISTRY_PATH, 'r') as f:
                data = json.load(f)

            # Keep track of updated agents
            seen = set()

            for agent, info in data.items():
                seen.add(agent)
                status = info.get("status", "Unknown")
                task = info.get("task", "")

                text = f"[{agent}]\nStatus: {status}\nTask: {task}\n"

                if agent in self.agent_labels:
                    self.agent_labels[agent].setText(text)
                else:
                    lbl = QLabel(text)
                    lbl.setObjectName("agentLabel")
                    self.agent_labels[agent] = lbl
                    self.agent_layout.addWidget(lbl)

            # Remove agents no longer in registry
            to_remove = []
            for agent in self.agent_labels:
                if agent not in seen:
                    lbl = self.agent_labels[agent]
                    self.agent_layout.removeWidget(lbl)
                    lbl.deleteLater()
                    to_remove.append(agent)

            for agent in to_remove:
                del self.agent_labels[agent]

        except Exception as e:
            print(f"Error reading agent registry: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(CYBERPUNK_QSS)
    window = CyberpunkDashboard()
    window.show()
    sys.exit(app.exec())
