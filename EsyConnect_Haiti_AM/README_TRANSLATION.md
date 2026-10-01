# Guide de Traduction EsyConnect Haïti

## 🌍 Configuration Multilingue

Le projet supporte 3 langues :
- 🇫🇷 **Français** (`fr`) - Langue par défaut
- 🇭🇹 **Créole Haïtien** (`ht`) - Langue locale
- 🇺🇸 **Anglais** (`en`) - Langue internationale

## 📁 Structure des Fichiers de Traduction

```
locale/
├── fr/
│   └── LC_MESSAGES/
│       ├── django.po    # Fichiers de traduction français
│       └── django.mo    # Fichiers compilés français
├── ht/
│   └── LC_MESSAGES/
│       ├── django.po    # Fichiers de traduction créole
│       └── django.mo    # Fichiers compilés créole
└── en/
    └── LC_MESSAGES/
        ├── django.po    # Fichiers de traduction anglais
        └── django.mo    # Fichiers compilés anglais
```

## 🔧 Installation GNU Gettext

Pour Windows :
```bash
# Installer via Chocolatey
choco install gettext

# Ou télécharger manuellement
# https://mlocati.github.io/articles/gettext-iconv-windows.html
```

Pour macOS :
```bash
brew install gettext
```

Pour Linux :
```bash
sudo apt-get install gettext
```

## 📝 Utilisation des Tags de Traduction

### Dans les Templates HTML

```html
<!-- Texte simple -->
{% trans "Bonjour" %}

<!-- Avec variables -->
{% trans "Bienvenue, %(username)s" %} 

<!-- Bloc de texte -->
{% blocktrans %}
Ceci est un long texte qui nécessite une traduction
avec plusieurs lignes et variables : {{ count }} éléments.
{% endblocktrans %}

<!-- Dans les attributs -->
<button title="{% trans 'Cliquer ici' %}">
  {% trans "Envoyer" %}
</button>
```

### Dans le Code Python

```python
from django.utils.translation import gettext as _

# Texte simple
message = _("Bonjour le monde")

# Avec variables
message = _("Bienvenue, %(username)s") % {'username': user.username}

# Texte pluriel
message = ngettext(
    "Il y a %(count)s élément",
    "Il y a %(count)s éléments",
    count
) % {'count': count}
```

## 🔄 Commandes de Traduction

### Extraire les textes à traduire
```bash
# Pour toutes les langues
python manage.py makemessages -l fr -l ht -l en

# Pour une langue spécifique
python manage.py makemessages -l fr
```

### Compiler les traductions
```bash
# Pour toutes les langues
python manage.py compilemessages

# Pour une langue spécifique
python manage.py compilemessages --locale=fr
```

### Mettre à jour les traductions
```bash
# Mettre à jour les fichiers .po existants
python manage.py makemessages --no-obsolete -l fr -l ht -l en
```

## 🎨 Sélecteur de Langue

Le sélecteur de langue est intégré dans la navigation avec :
- **Icônes de drapeaux** 🇫🇷🇭🇹🇺🇸
- **Design moderne** avec Alpine.js
- **Transition fluide** entre les langues
- **Indication de langue active**

## 📋 Exemples de Traduction

### Français → Créole
- "Tableau de bord" → "Tablo bò"
- "Entreprises" → "Antrepriz"
- "Rechercher" → "Chèche"
- "Bienvenue" → "Byenvini"

### Français → Anglais
- "Tableau de bord" → "Dashboard"
- "Entreprises" → "Businesses"
- "Rechercher" → "Search"
- "Bienvenue" → "Welcome"

## 🚀 Bonnes Pratiques

1. **Toujours utiliser `{% trans %}`** pour les textes courts
2. **Utiliser `{% blocktrans %}`** pour les textes longs avec variables
3. **Éviter le HTML** dans les chaînes de traduction
4. **Tester toutes les langues** après modifications
5. **Maintenir la cohérence** des termes techniques

## 🔍 Débogage

### Vérifier les traductions manquantes
```bash
python manage.py makemessages --no-obsolete --all
```

### Forcer le rechargement des traductions
```bash
# Redémarrer le serveur de développement
python manage.py runserver
```

### Vérifier la langue active
```python
from django.utils import translation
print(translation.get_language())
```

## 📞 Support

Pour toute question sur la traduction :
- Documentation Django : https://docs.djangoproject.com/en/stable/topics/i18n/translation/
- Support projet : contact@esyconnect.ht
