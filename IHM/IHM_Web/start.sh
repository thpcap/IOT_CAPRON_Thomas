#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v docker >/dev/null 2>&1; then
    echo "Erreur : Docker n'est pas installé ou n'est pas dans le PATH."
    exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
    echo "Erreur : le plugin Docker Compose est introuvable."
    exit 1
fi

if [[ ! -f .env ]]; then
    echo "Fichier .env absent."
    echo "Copie .env.example vers .env, puis renseigne les mots de passe."
    exit 1
fi

docker compose up --build -d

echo
echo "TempHumiX est démarré."
echo "Interface : http://localhost:8080"
echo "API docs  : http://localhost:8080/docs"
echo
echo "Logs : docker compose logs -f"
