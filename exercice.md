# TP : Sécuriser un dépôt Python avec les hooks pre-commit

Projet fil rouge : NOVA SERVICES

## 1. Analyse du code volontairement imparfait (section 3)

### 1. Problèmes de qualité du code

`import os` n'est pas utilisé, `password` est déclaré mais jamais utilisé, la fonction mélange saisie, calcul et affichage, il n'y a aucune gestion d'erreur et pas de typage.

### 2. Risques de sécurité

Le mot de passe est codé en dur, et `eval()` est appelé sur une entrée utilisateur.

### 3. Pourquoi `eval()` est dangereux sur une entrée non fiable

Il exécute n'importe quel code Python. Par exemple, `__import__('os').system('del ...')` entraîne une exécution de code arbitraire (RCE).

### 4. Pourquoi un mot de passe ne doit pas être stocké dans le code source

Il reste dans l'historique Git pour toujours, tous ceux qui ont accès au dépôt peuvent le lire, il fuit dans les forks et les sauvegardes, et on ne peut pas le changer sans redéployer.

### 5. Première correction proposée

Lire le secret depuis une variable d'environnement et remplacer `eval()` par une liste blanche d'opérations autorisées.

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

## 4. Politique de sécurisation du code NOVA SERVICES (section 10)

### 4.1 Contrôles obligatoires

| Contrôle | Périmètre | Local (pre-commit) | CI | Bloquant |
|---|---|---|---|---|
| `trailing-whitespace`, `end-of-file-fixer`, `check-yaml` | Tous les dépôts | Oui | Oui | Oui |
| `check-added-large-files` | Tous les dépôts | Oui | Oui | Oui |
| `detect-secrets` | Tous les dépôts | Oui | Oui | Oui |
| `bandit -ll` (sévérité moyenne et haute) | Dépôts Python | Oui | Oui | Oui |
| Tests unitaires rapides (`pytest`) | Dépôts Python | Oui | Oui | Oui |
| Suite de tests complète | Dépôts Python | Non | Oui | Oui |
| `pip-audit` | Dépôts Python | Oui | Oui | Oui en CI, peut être désactivé en local si le service est indisponible |

Les contrôles communs (format, fichiers volumineux, secrets) s'appliquent à l'API Python, à l'outil d'administration et aux scripts d'automatisation. Les contrôles Python (Bandit, pytest, pip-audit) s'appliquent aux dépôts contenant du code Python.

### 4.2 Contrôles locaux et CI

- Chaque développeur installe les hooks avec `pre-commit install` dès le clonage du dépôt.
- La CI exécute `pre-commit run --all-files`, la suite de tests complète et `pip-audit`, car un hook local peut être absent ou contourné (`--no-verify`, `core.hooksPath`).
- La branche `main` est protégée côté serveur : pas de push direct, pull request obligatoire, CI verte et une approbation de revue requises avant fusion.

### 4.3 Conditions de blocage

Un commit ou une pull request est bloqué si :

- un secret potentiel non qualifié est détecté ;
- Bandit remonte une alerte de sévérité moyenne ou haute ;
- un test échoue ;
- une dépendance présente une vulnérabilité connue avec un correctif disponible ;
- un fichier de plus de 500 Ko est ajouté.

### 4.4 Traitement des faux positifs

- Toute détection est examinée avant d'être déclarée faux positif.
- Un vrai secret n'est jamais ajouté au baseline : il est retiré du code, révoqué ou renouvelé, puis l'historique est nettoyé si nécessaire.
- Un faux positif `detect-secrets` est validé avec `detect-secrets audit .secrets.baseline` ; le baseline modifié passe obligatoirement en revue de code.
- Une exception Bandit utilise `# nosec <ID>` accompagné d'un commentaire de justification.

### 4.5 Responsable de la validation des exceptions

- Le responsable sécurité (ou un référent sécurité désigné par équipe) valide chaque exception.
- Chaque exception est tracée (fichier, règle, justification, validateur, date) et réexaminée tous les trimestres.
- Une dépendance vulnérable sans correctif disponible fait l'objet d'une exception temporaire avec mesure de contournement (désactivation de la fonctionnalité, filtrage des entrées, remplacement de la bibliothèque) et une date de réexamen.

### 4.6 Mise à jour des outils

- Le référent sécurité est responsable des versions des hooks.
- Une fois par mois, il lance `pre-commit autoupdate` sur une branche dédiée, vérifie le résultat de `pre-commit run --all-files` puis ouvre une pull request.
- Les versions des hooks restent épinglées (`rev`) pour garantir des résultats reproductibles.

### 4.7 Preuve de correction d'une vulnérabilité

La correction est prouvée par la pull request associée : le commit de correction, un test qui couvre le cas, la CI verte et le contrôle qui ne remonte plus l'alerte.

## 5. Indicateurs de suivi (section 12)

| Indicateur | Source | Propriétaire | Fréquence | Seuil d'alerte | Action déclenchée |
|---|---|---|---|---|---|
| Taux de dépôts configurés (dépôts avec `.pre-commit-config.yaml` versionné / dépôts concernés) | Inventaire des dépôts GitHub | Responsable sécurité | Mensuelle | Inférieur à 90 % | Relance des équipes concernées et accompagnement à la mise en place |
| Délai médian de correction (temps entre la détection et la fusion de la correction) | Issues et pull requests GitHub, rapports CI | Lead développeur | Mensuelle | Supérieur à 7 jours pour une vulnérabilité haute | Priorisation dans le sprint suivant et escalade au responsable sécurité |
| Nombre d'exceptions actives (entrées de baseline et `# nosec` validées) | `.secrets.baseline`, recherche `# nosec` dans le code | Responsable sécurité | Trimestrielle | Hausse de plus de 20 % ou exception non réexaminée depuis 3 mois | Revue des exceptions, suppression de celles qui ne sont plus justifiées |

Ces indicateurs s'interprètent avec leur contexte : une hausse des détections peut refléter une meilleure couverture des contrôles plutôt qu'une dégradation.

## 6. Questions de compréhension (section 13)

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
