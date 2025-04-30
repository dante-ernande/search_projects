# -*- coding: utf-8 -*-

import sys
import os
import time
import random
import logging
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QHeaderView

from cache import files
from consult import Consulta

import qdarktheme

# descripton

resume = "📝 O aplicativo é uma ferramenta para consulta de projetos armazenados em um banco de dados MySQL,\n" \
"utilizando PyMySQL para comunicação com o banco. Ele carrega configurações a partir de um arquivo \n" \
"config.ini, estabelece conexão com o banco e executa consultas baseadas em um termo de pesquisa fornecido pelo usuário.\n" \
"\nFuncionalidades principais:\n" \
"       Leitura de Configurações: Obtém informações do banco de dados a partir do 🔒 config.ini.\n" \
"       Consulta ao Banco de Dados: Pesquisa projetos no banco, retornando informações como nome, título, data de backup e caminho.\n" \
"       Pesquisa Inteligente: Permite buscar projetos específicos ou listar todos quando a pesquisa é '***'.\n" \
"       Registro de Logs: Usa logging para registrar eventos, incluindo erros e quantidade de resultados retornados.\n" \
"       Gerenciamento Seguro de Conexão: Utiliza with pymysql.connect... para garantir que as conexões sejam fechadas corretamente.\n" \
"\n⚙️   Caso não encontre projetos ou haja erro de conexão, retorna mensagens de status 'noProjects' ou 'noServer'."

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Ui_Form(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        IMAGE_DIR = os.path.join(BASE_DIR, "images")
        
        self.termo = 0
        pixmap = QPixmap(os.path.join(IMAGE_DIR, "3vetorzero.png"))

    
        self.setWindowTitle("Search Projects")
        self.setWindowIcon(QIcon(os.path.join(IMAGE_DIR, "discover.png")))

        self.setGeometry(100, 100, 900, 600)
        qdarktheme.setup_theme()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Tema Selection
        self.combo_box = QComboBox()
        self.combo_box.addItems(qdarktheme.get_themes())
        self.combo_box.currentTextChanged.connect(qdarktheme.setup_theme)
        
        # Pesquisa
        self.lineEdit = QLineEdit()
        self.lineEdit.setPlaceholderText("Pesquisar...")
        self.lineEdit.setClearButtonEnabled(True)
        self.lineEdit.setCompleter(QCompleter(files))
        self.lineEdit.returnPressed.connect(self.onPressed)

        self.logo = QLabel()
        self.logo.setGeometry(QtCore.QRect(20, 20, 150, 150))
        self.logo.setPixmap(pixmap)
        
        # Labels
        self.label = QLabel(resume)
        self.historico = QLabel("💾")
        self.historico.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse)  # Permite clicar em links
        self.historico.linkActivated.connect(self.onHistoricoClicked)
        self.aviso = QLabel("📌 Para visualizar todos os projetos, digite '<b>***</b>' e pressione ENTER")
        self.about = QLabel("© 2025 <b>Vetorzero/lobo</b>. Todos os direitos reservados.")

        # Tabela
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["Produto", "Título", "Data Backup", "Caminho"])
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Layouts
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.logo)
        
        
        top_layout.addWidget(self.label)
        top_layout.addStretch()
        top_layout.addWidget(self.combo_box)
        
        
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.lineEdit)
        
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.aviso)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.historico)
        main_layout.addWidget(self.tableWidget)
        main_layout.addWidget(self.about)

    def onPressed(self):
        try:
            termoPesquisa = self.lineEdit.text()
            logging.info(f"✅ Pesquisa iniciada: {termoPesquisa}")
            saida = Consulta.result(termoPesquisa)
            logging.info(f"Resultado da pesquisa: {saida}")
            self.loadData(saida)
            # self.historico.setText(f"[{termoPesquisa}] " + self.historico.text())
            link = f'<a href="{termoPesquisa}">{termoPesquisa}</a>'
            self.historico.setText(link + " | " + self.historico.text())
        except Exception as e:
            logging.error(f"Erro ao pesquisar: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro durante a pesquisa:\n{str(e)}")

    # Adiciona um evento para capturar cliques no histórico
    def onHistoricoClicked(self, url):
        self.lineEdit.setText(url)
        self.onPressed()  # Reexecuta a pesquisa


    def loadData(self, pesquisa):
        if not self.valid(pesquisa):
            return
        self.tableWidget.setRowCount(0)
        for row_idx, termo in enumerate(sorted(pesquisa, key=lambda x: x["product"].lower())):
            self.tableWidget.insertRow(row_idx)
            for col_idx, key in enumerate(["product", "title", "backup_date", "path"]):
                self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(termo[key])))
        
    def valid(self, pesquisa):
        if pesquisa in ['noProjects', 'noServer'] or not pesquisa:
            QMessageBox.critical(self, 'Erro', 'Nenhum projeto encontrado ou problema de conexão.')
            return False
        return True

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        ui = Ui_Form()
        ui.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"Erro fatal: {str(e)}", exc_info=True)
        QMessageBox.critical(None, "Erro Crítico", f"Ocorreu um erro inesperado:\n{str(e)}")
        time.sleep(3)  # Dá tempo para ler o erro antes de fechar
