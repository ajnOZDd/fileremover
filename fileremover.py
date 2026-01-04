#!/usr/bin/env python3
import os
import sys
import shutil
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QPushButton,
    QLabel, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt

try:
    from send2trash import send2trash
except ImportError:
    send2trash = None


# --------------------------------------------------
# Dialogue principal
# --------------------------------------------------
class DeleteDialog(QDialog):
    def __init__(self, filepaths):
        super().__init__()
        self.filepaths = filepaths
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Supprimer des fichiers")
        self.setMinimumWidth(420)

        layout = QVBoxLayout()

        # Texte résumé
        count = len(self.filepaths)
        label = QLabel(
            f"Vous êtes sur le point de supprimer :\n\n"
            f"🗂️ {count} élément(s)\n\n"
            f"Que voulez-vous faire ?"
        )
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)

        # Bouton corbeille
        btn_trash = QPushButton("🗑️ Tout déplacer vers la corbeille")
        btn_trash.setMinimumHeight(48)
        btn_trash.clicked.connect(self.move_all_to_trash)
        layout.addWidget(btn_trash)

        # Bouton suppression définitive
        btn_delete = QPushButton("⚠️ Supprimer définitivement")
        btn_delete.setMinimumHeight(48)
        btn_delete.setStyleSheet("background:#c62828;color:white;font-weight:bold;")
        btn_delete.clicked.connect(self.delete_all)
        layout.addWidget(btn_delete)

        # Annuler
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)

        self.setLayout(layout)

    # --------------------------------------------------
    def move_all_to_trash(self):
        if send2trash is None:
            QMessageBox.critical(
                self, "Erreur",
                "Le module send2trash n'est pas installé.\n\n"
                "Installez-le avec : pip install send2trash"
            )
            return

        errors = []
        for path in self.filepaths:
            try:
                send2trash(path)
            except Exception as e:
                errors.append(f"{path}\n{e}")

        if errors:
            QMessageBox.warning(
                self, "Erreurs",
                "Certains fichiers n'ont pas pu être déplacés :\n\n" +
                "\n\n".join(errors)
            )
        else:
            QMessageBox.information(
                self, "Succès",
                "Tous les fichiers ont été déplacés vers la corbeille."
            )

        self.accept()

    # --------------------------------------------------
    def delete_all(self):
        reply = QMessageBox.question(
            self,
            "Confirmation définitive",
            "⚠️ CETTE ACTION EST IRRÉVERSIBLE ⚠️\n\n"
            f"Supprimer définitivement {len(self.filepaths)} élément(s) ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        errors = []
        for path in self.filepaths:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception as e:
                errors.append(f"{path}\n{e}")

        if errors:
            QMessageBox.warning(
                self, "Erreurs",
                "Certains fichiers n'ont pas pu être supprimés :\n\n" +
                "\n\n".join(errors)
            )
        else:
            QMessageBox.information(
                self, "Succès",
                "Suppression définitive terminée."
            )

        self.accept()


# --------------------------------------------------
# Application
# --------------------------------------------------
class FileRemoverApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("File Remover")

    def run(self, filepaths):
        dialog = DeleteDialog(filepaths)
        dialog.exec()
        return 0


# --------------------------------------------------
# Dolphin ServiceMenu pour Plasma 6
# --------------------------------------------------
def install_dolphin_service():
    service_content = """[Desktop Entry]
Type=Service
MimeType=all/all;
Actions=delete_choice;

[Desktop Action delete_choice]
Name=Supprimer (avec choix)
Name[fr]=Supprimer (avec choix)
Icon=edit-delete
Exec=fileremover %F
"""

    # Chemin correct pour Plasma 6
    service_dir = Path.home() / ".local/share/kio/servicemenus"
    service_dir.mkdir(parents=True, exist_ok=True)

    service_file = service_dir / "fileremover.desktop"
    service_file.write_text(service_content)
    
    # Rendre le fichier exécutable (recommandé pour Plasma 6)
    service_file.chmod(0o755)

    print("✓ Service Dolphin installé :", service_file)
    print("→ Redémarre Dolphin pour voir le nouveau menu contextuel")
    print("→ Clic droit sur un fichier → 'Supprimer (avec choix)'")
    return 0


# --------------------------------------------------
def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--install-service":
            return install_dolphin_service()

        filepaths = [p for p in sys.argv[1:] if os.path.exists(p)]

        if not filepaths:
            return 0

        app = FileRemoverApp(sys.argv)
        return app.run(filepaths)

    # Mode manuel (optionnel)
    app = FileRemoverApp(sys.argv)
    path, _ = QFileDialog.getOpenFileName(
        None, "Choisir un fichier", str(Path.home())
    )
    if path:
        return app.run([path])
    return 0


if __name__ == "__main__":
    sys.exit(main())