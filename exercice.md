  Questions
  1. Identifiez les problèmes de qualité du code :
  import os n'est pas utilisé, password est déclaré mais jamais utilisé, la fonction mélange saisie, calcul et affichage, il n'y a aucune gestion d'erreur et pas de typage.
  2. Identifiez les risques de sécurité :
  Le password est codé en dur, et eval() est appelé sur une entrée utilisateur.
  3. Expliquez pourquoi eval() est dangereux lorsqu'il est utilisé sur une entrée non fiable :
  Il exécute n'importe quel code Python. Par exemple, __import__('os').system('del
     ...') entraîne une exécution de code arbitraire (RCE).
  4. Expliquez pourquoi un mot de passe ne doit pas être stocké dans le code source : il reste dans l'historique Git pour toujours, tous ceux qui ont accès au dépôt peuvent le lire, il fuit dans les forks et les sauvegardes, et on ne peut pas le changer sans redéployer.
  5. Proposez une première correction, sans installer encore de hook : lire le secret depuis une variable d'environnement.
