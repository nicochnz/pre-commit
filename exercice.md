### 1. Problèmes de qualité du code

`import os` n'est pas utilisé, `password` est déclaré mais jamais utilisé, la fonction mélange saisie, calcul et affichage, il n'y a aucune gestion d'erreur et pas de typage.

### 2. Risques de sécurité

Le mot de passe est codé en dur, et `eval()` est appelé sur une entrée utilisateur.

### 3. Pourquoi `eval()` est dangereux sur une entrée non fiable

Il exécute n'importe quel code Python. Par exemple, `__import__('os').system('del ...')` entraîne une exécution de code arbitraire (RCE).

### 4. Pourquoi un mot de passe ne doit pas être stocké dans le code source

Il reste dans l'historique Git pour toujours, tous ceux qui ont accès au dépôt peuvent le lire, il fuit dans les forks et les sauvegardes, et on ne peut pas le changer sans redéployer.

### 5. Première correction proposée

Lire le secret depuis une variable d'environnement.

## 2. Problèmes détectés par les hooks et corrections

| Problème | Hook qui l'a détecté | Correction appliquée |
|---|---|---|
| Mot de passe codé en dur dans `app.py` | `detect-secrets` (Secret Keyword) | Secret déplacé dans `.env` (ignoré par Git), lu avec `os.getenv` via `python-dotenv`, `.env.example` versionné sans valeur |
| `eval()` sur une entrée utilisateur | `bandit` (B307) | Remplacé par `calculate()` qui n'autorise que `add`, `subtract`, `multiply`, `divide` |
| `.venv/` indexé par erreur (fichiers de plus de 500 Ko) | `check-added-large-files` | `git rm -r --cached .venv` et ajout de `.venv/` au `.gitignore` |
| Fichiers sans saut de ligne final | `end-of-file-fixer` | Correction automatique par le hook, fichiers ajoutés de nouveau |
| Test modifié pour échouer (`== 6` au lieu de `== 5`) | `pytest` (hook local) | Commit bloqué tant que le test échouait, test rétabli |

## 3. Audit des dépendances (section 7.2)

Commande : `pip-audit -r requirements.txt`

Résultat : `No known vulnerabilities found`

| Élément | Résultat |
|---|---|
| Paquet concerné | `python-dotenv` |
| Version résolue | `1.2.4` |
| ID de vulnérabilité | Aucun |
| Version corrigée | Sans objet |
| Impact potentiel | Aucun impact connu à la date de l'audit (15/10/2026) |
| Action envisagée | Aucune correction nécessaire. Conserver le hook `pip-audit` pour détecter les futures vulnérabilités et verrouiller la version (`python-dotenv==1.2.4`) |

Limite : "aucune vulnérabilité connue" ne signifie pas que la dépendance est sûre, seulement qu'aucune vulnérabilité n'est référencée aujourd'hui dans les bases consultées.


## 4. Questions de compréhension (section 13)

### 1. Qu'est-ce qu'un hook pre-commit ?

Un script exécuté automatiquement par Git avant la création d'un commit. S'il échoue, le commit est refusé. Le framework `pre-commit` permet de déclarer ces scripts dans un fichier versionné.

### 2. Quelle différence entre un contrôle local et un contrôle CI ?

Le contrôle local donne un retour immédiat au développeur mais peut être absent ou contourné. Le contrôle CI s'exécute côté serveur, sur un environnement maîtrisé, et peut être rendu obligatoire avant la fusion.

### 3. Pourquoi versionner `.pre-commit-config.yaml` ?

Pour que toute l'équipe et la CI appliquent exactement les mêmes règles et versions d'outils, et pour tracer chaque changement de règle.

### 4. Pourquoi `detect-secrets` peut-il produire des faux positifs ?

Il repose sur des motifs (mots-clés, entropie élevée) et non sur la connaissance du contexte : une valeur fictive, un hash ou un identifiant aléatoire peuvent ressembler à un secret.

### 5. Pourquoi un baseline ne doit-il pas servir à ignorer des secrets réels ?

Le secret resterait dans le code et l'historique, donc exploitable. Le baseline ne sert qu'à tracer des faux positifs vérifiés ; un vrai secret doit être retiré et révoqué.

### 6. Quel risque présente `eval()` sur une entrée non fiable ?

Une exécution de code arbitraire : l'utilisateur peut lire des fichiers, lancer des commandes système ou exfiltrer des données avec les droits de l'application.

### 7. Pourquoi un fichier `.env` doit-il être exclu du dépôt ?

Il contient les valeurs réelles des secrets de l'environnement local. Une fois commité, il est visible par tous ceux qui ont accès au dépôt et reste dans l'historique.

### 8. Pourquoi une variable d'environnement ne suffit-elle pas à sécuriser un secret ?

Elle peut fuiter dans les logs, les dumps de processus ou les messages d'erreur, et n'offre ni chiffrement, ni rotation, ni contrôle d'accès, ni audit. En production, il faut un gestionnaire de secrets.

### 9. Différence entre analyse de code et audit des dépendances ?

L'analyse de code (Bandit) examine le code écrit par l'équipe pour repérer des pratiques dangereuses. L'audit des dépendances (pip-audit) compare les bibliothèques tierces et leurs versions à une base de vulnérabilités connues.

### 10. Pourquoi exécuter les tests en CI même si un hook local existe ?

Le hook peut être non installé, contourné, ou s'exécuter dans un environnement différent. La CI garantit une exécution systématique et reproductible avant la fusion.

### 11. Comment empêcher réellement les pushes directs sur `main` ?

Par une règle côté serveur : protection de branche ou ruleset GitHub interdisant le push direct, imposant une pull request, une CI réussie et une approbation de revue.

### 12. Quels indicateurs pour suivre l'efficacité du dispositif ?

Taux de dépôts configurés, taux de contrôles CI réussis, nombre de secrets détectés, nombre de vulnérabilités ouvertes, délai médian de correction, nombre d'exceptions actives (voir section 5).
