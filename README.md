# Sécuriser un dépôt Python avec pre-commit

TP Pilotage et amélioration continue de la sécurité, projet fil rouge NOVA SERVICES.

Ce dépôt exécute automatiquement des contrôles de qualité et de sécurité avant chaque commit.

## Contrôles

| Hook | Rôle |
|---|---|
| `trailing-whitespace` | Supprime les espaces en fin de ligne |
| `end-of-file-fixer` | Garantit un saut de ligne en fin de fichier |
| `check-added-large-files` | Bloque les fichiers de plus de 500 Ko |
| `check-yaml` | Vérifie la syntaxe YAML |
| `bandit -ll` | Détecte les pratiques Python dangereuses (sévérité moyenne et haute) |
| `detect-secrets` | Détecte les secrets potentiels (baseline : `.secrets.baseline`) |
| `pytest` | Exécute les tests unitaires |
| `pip-audit` | Recherche les vulnérabilités connues dans `requirements.txt` |

## Prérequis

Python 3.12, pip et Git.

## Installation

```powershell
git clone <url-du-depot>
cd <nom-du-depot>
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # Linux / macOS : source .venv/bin/activate
python -m pip install -r requirements-dev.txt
pre-commit install
Copy-Item .env.example .env          # Linux / macOS : cp .env.example .env
```

Renseigner ensuite `APP_PASSWORD` dans `.env`. Ce fichier n'est jamais commité.

## Utilisation

```powershell
pre-commit run --all-files   # tous les contrôles sur tout le dépôt
pytest -q                    # tests unitaires
pip-audit -r requirements.txt
```

L'environnement virtuel doit être activé lors des commits : les hooks `pytest` et `pip-audit` utilisent les outils installés dans `.venv`.

## Documentation

- `exercice.md` : analyse du code, problèmes détectés, audit des dépendances, politique de sécurisation, indicateurs et réponses aux questions.
- `Pre-commit-screen.docx` : captures des exécutions (commit bloqué, test en échec, audit, vérification complète).
