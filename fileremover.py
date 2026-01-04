#!/usr/bin/env python3
"""
File Deleter - Application pour supprimer des fichiers avec choix corbeille/définitif
Compatible avec KDE Plasma (Dolphin)
Version PyQt6
"""

import os
import sys
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QPushButton, 
                             QLabel, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

try:
    from send2trash import send2trash
except ImportError:
    send2trash = None


class DeleteDialog(QDialog):
    """Dialogue pour choisir le type de suppression"""
    
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        self.choice = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Supprimer le fichier")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Label avec le nom du fichier
        filename = os.path.basename(self.filepath)
        label = QLabel(f"Que voulez-vous faire avec :\n\n{filename}")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        # Bouton Corbeille
        btn_trash = QPushButton("🗑️ Déplacer vers la corbeille")
        btn_trash.setMinimumHeight(50)
        btn_trash.clicked.connect(self.move_to_trash)
        layout.addWidget(btn_trash)
        
        # Bouton Suppression définitive
        btn_permanent = QPushButton("⚠️ Supprimer définitivement")
        btn_permanent.setMinimumHeight(50)
        btn_permanent.setStyleSheet("background-color: #d32f2f; color: white;")
        btn_permanent.clicked.connect(self.delete_permanently)
        layout.addWidget(btn_permanent)
        
        # Bouton Annuler
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setMinimumHeight(40)
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)
        
        self.setLayout(layout)
    
    def move_to_trash(self):
        """Déplace le fichier vers la corbeille"""
        if send2trash is None:
            QMessageBox.critical(self, "Erreur", 
                "Le module 'send2trash' n'est pas installé.\n"
                "Installez-le avec: pip install send2trash")
            return
        
        try:
            send2trash(self.filepath)
            self.choice = "trash"
            QMessageBox.information(self, "Succès", 
                f"Fichier déplacé vers la corbeille:\n{os.path.basename(self.filepath)}")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du déplacement:\n{e}")
    
    def delete_permanently(self):
        """Supprime définitivement le fichier"""
        reply = QMessageBox.question(self, "Confirmation",
            "⚠️ Cette action est IRRÉVERSIBLE !\n\n"
            "Êtes-vous sûr de vouloir supprimer définitivement ce fichier ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if os.path.isdir(self.filepath):
                    shutil.rmtree(self.filepath)
                else:
                    os.remove(self.filepath)
                self.choice = "permanent"
                QMessageBox.information(self, "Succès", 
                    f"Fichier supprimé définitivement:\n{os.path.basename(self.filepath)}")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression:\n{e}")


class FileDeleterApp(QApplication):
    """Application principale"""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("File Deleter")
    
    def run(self, filepath=None):
        """Lance le dialogue de suppression"""
        if filepath is None:
            # Ouvre un dialogue pour choisir un fichier
            filepath, _ = QFileDialog.getOpenFileName(None, 
                "Choisir un fichier à supprimer", 
                str(Path.home()))
            
            if not filepath:
                return 0
        
        if not os.path.exists(filepath):
            QMessageBox.critical(None, "Erreur", f"Le fichier n'existe pas:\n{filepath}")
            return 1
        
        dialog = DeleteDialog(filepath)
        dialog.exec()
        return 0


def install_dolphin_service():
    """Installe le service menu pour Dolphin (KDE)"""
    service_content = """[Desktop Entry]
Type=Service
X-KDE-ServiceTypes=KonqPopupMenu/Plugin
MimeType=all/all;
Actions=delete_choice;

[Desktop Action delete_choice]
Name=Supprimer (avec choix)
Icon=edit-delete
Exec=filedeleter %f
"""
    
    # Chemin du service menu KDE
    service_dir = Path.home() / ".local/share/kservices5/ServiceMenus"
    service_dir.mkdir(parents=True, exist_ok=True)
    
    service_file = service_dir / "filedeleter.desktop"
    
    try:
        with open(service_file, 'w') as f:
            f.write(service_content)
        print(f"✓ Service menu installé: {service_file}")
        print("  Redémarrez Dolphin pour voir les changements")
        return True
    except Exception as e:
        print(f"✗ Erreur lors de l'installation: {e}")
        return False


def main():
    """Point d'entrée principal"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--install-service":
            install_dolphin_service()
            return 0
        else:
            # Un fichier est passé en argument
            filepath = sys.argv[1]
            app = FileDeleterApp(sys.argv)
            return app.run(filepath)
    else:
        # Mode interactif
        app = FileDeleterApp(sys.argv)
        return app.run()


if __name__ == "__main__":
    sys.exit(main())