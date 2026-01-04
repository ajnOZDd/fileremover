#!/bin/bash

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "  Installation de FileRemover"
echo "========================================="
echo ""

# Vérifier si on est dans le bon répertoire
if [ ! -f "setup.py" ] || [ ! -f "fileremover.py" ]; then
    echo -e "${RED}❌ Erreur: setup.py ou fileremover.py introuvable${NC}"
    echo "Exécutez ce script depuis le répertoire du projet"
    exit 1
fi

# Vérifier si pip est installé
if ! command -v pip &> /dev/null; then
    echo -e "${RED}❌ pip n'est pas installé${NC}"
    echo "Installez-le avec: sudo dnf install python3-pip"
    exit 1
fi

# Installer le package en mode éditable
echo -e "${YELLOW}📦 Installation du package...${NC}"
pip install --user -e .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Échec de l'installation du package${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Package installé${NC}"
echo ""

# S'assurer que ~/.local/bin est dans le PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "${YELLOW}⚠️  ~/.local/bin n'est pas dans votre PATH${NC}"
    echo "Ajoutez cette ligne à votre ~/.bashrc ou ~/.zshrc :"
    echo 'export PATH="$HOME/.local/bin:$PATH"'
    echo ""
    export PATH="$HOME/.local/bin:$PATH"
fi

# Installer le service menu Dolphin
echo -e "${YELLOW}🐬 Installation du menu contextuel Dolphin...${NC}"
fileremover --install-service

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Échec de l'installation du service menu${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Menu contextuel installé${NC}"
echo ""

# Reconstruire le cache des services KDE
echo -e "${YELLOW}🔄 Reconstruction du cache KDE...${NC}"
if command -v kbuildsycoca6 &> /dev/null; then
    kbuildsycoca6 &> /dev/null
    echo -e "${GREEN}✓ Cache KDE reconstruit${NC}"
elif command -v kbuildsycoca5 &> /dev/null; then
    kbuildsycoca5 &> /dev/null
    echo -e "${GREEN}✓ Cache KDE reconstruit (Plasma 5)${NC}"
else
    echo -e "${YELLOW}⚠️  kbuildsycoca6 introuvable (ce n'est pas grave)${NC}"
fi

echo ""

# Redémarrer Dolphin
echo -e "${YELLOW}🔄 Redémarrage de Dolphin...${NC}"
killall dolphin 2>/dev/null
sleep 1

# Lancer Dolphin en arrière-plan de manière détachée
nohup dolphin &> /dev/null &
disown

echo -e "${GREEN}✓ Dolphin redémarré${NC}"
echo ""

# Message de succès
echo "========================================="
echo -e "${GREEN}✅ Installation terminée avec succès !${NC}"
echo "========================================="
echo ""
echo "📝 Utilisation :"
echo "   1. Ouvrez Dolphin"
echo "   2. Clic droit sur un fichier/dossier"
echo "   3. Sélectionnez 'Supprimer (avec choix)'"
echo ""
echo "🗑️  Vous pourrez choisir entre :"
echo "   • Déplacer vers la corbeille (récupérable)"
echo "   • Supprimer définitivement (irréversible)"
echo ""