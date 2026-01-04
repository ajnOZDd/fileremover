#!/bin/bash

# ==========================
# Script Git Pro Max Auto
# ==========================

# Vérifier qu'on est dans un dépôt Git
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Erreur : Ce dossier n'est pas un dépôt Git."
    exit 1
fi

echo "==============================="
echo "💻 Git Pro Max Auto"
echo "==============================="

# Vérifier s'il y a des changements
changes=$(git status --porcelain)

if [[ -n "$changes" ]]; then
    echo "⚡ Changements détectés : ajout automatique"
    git add .
    
    # Type de commit
    echo ""
    echo "Choisissez le type de commit :"
    echo "1) feat (nouvelle fonctionnalité)"
    echo "2) fix (correction de bug)"
    echo "3) refactor (refactorisation / nettoyage)"
    echo "4) docs (documentation)"
    read -p "Choix (1-4) [1] : " commit_type
    commit_type=${commit_type:-1}
    
    case $commit_type in
        1) type="feat" ;;
        2) type="fix" ;;
        3) type="refactor" ;;
        4) type="docs" ;;
        *) type="feat" ;;
    esac

    # Message de commit
    read -p "Entrez le message de commit : " message
    if [[ -z "$message" ]]; then
        echo "Aucun message, commit annulé."
    else
        git commit -m "$type: $message"
        echo "✅ Commit créé : $type: $message"
    fi
else
    echo "✅ Aucun changement détecté. Pas de commit nécessaire."
fi

# Demander si release
read -p "Voulez-vous créer une release ? (y/n) : " create_release
if [[ "$create_release" != "y" ]]; then
    echo "Fin du script sans release."
    exit 0
fi

# Récupérer dernier tag
last_tag=$(git describe --tags --abbrev=0 2>/dev/null)
if [[ -z "$last_tag" ]]; then
    last_tag="v0.0.0"
fi
echo "Dernier tag : $last_tag"

# Extraire numéros
IFS='.' read -r major minor patch <<<"${last_tag#v}"

# Choix type d'incrément
echo ""
echo "Type d'incrément pour la release :"
echo "1) patch (vX.Y.Z → vX.Y.(Z+1))"
echo "2) minor (vX.Y.Z → vX.(Y+1).0)"
echo "3) major (vX.Y.Z → v(X+1).0.0)"
read -p "Choix (1-3) [1] : " inc_type
inc_type=${inc_type:-1}

case $inc_type in
    1) patch=$((patch+1)) ;;
    2) minor=$((minor+1)); patch=0 ;;
    3) major=$((major+1)); minor=0; patch=0 ;;
    *) patch=$((patch+1)) ;;
esac

new_tag="v$major.$minor.$patch"
echo "📦 Nouveau tag généré : $new_tag"

# Pré-remplir message de release pour le commit si aucun commit a été fait
if [[ -z "$changes" ]]; then
    echo "⚡ Aucun commit effectué, commit pré-rempli pour version $new_tag"
    git commit --allow-empty -m "chore: release $new_tag"
fi

# Créer le tag
git tag -a "$new_tag" -m "Release $new_tag"
echo "✅ Tag $new_tag créé."

# Push main et tag
git push origin main
git push origin "$new_tag"

echo "🚀 Push terminé avec le tag $new_tag !"
