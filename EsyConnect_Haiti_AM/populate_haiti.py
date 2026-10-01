import os
import django
from django.utils.text import slugify

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EsyConnect_Haiti_AM.settings')
django.setup()

from business.models import Department, Ville  # Ajuste le nom de l'application si nécessaire

def run():
    print("Début du chargement des départements et des villes d'Haïti...")

    # Dictionnaire complet des 10 départements avec leurs principales communes/villes
    haiti_data = {
        "Nord": {
            "code": "HT-ND",
            "villes": ["Cap-Haïtien", "Limonade", "Milot", "Plaine-du-Nord", "Quartier-Morin", "Grande-Rivière-du-Nord"]
        },
        "Ouest": {
            "code": "HT-OU",
            "villes": ["Port-au-Prince", "Delmas", "Pétion-Ville", "Carrefour", "Tabarre", "Croix-des-Bouquets"]
        },
        "Artibonite": {
            "code": "HT-AR",
            "villes": ["Gonaïves", "Saint-Marc", "Verrettes", "Petite-Rivière-de-l'Artibonite", "Gros-Morne"]
        },
        "Sud": {
            "code": "HT-SD",
            "villes": ["Les Cayes", "Aquin", "Port-Salut", "Camp-Perrin", "Saint-Louis-du-Sud"]
        },
        "Centre": {
            "code": "HT-CT",
            "villes": ["Hinche", "Mirebalais", "Lascahobas", "Maïssade"]
        },
        "Nord-Est": {
            "code": "HT-NE",
            "villes": ["Fort-Liberté", "Ouanaminthe", "Trou-du-Nord", "Terrier-Rouge"]
        },
        "Nord-Ouest": {
            "code": "HT-NO",
            "villes": ["Port-de-Paix", "Saint-Louis-du-Nord", "Jean-Rabel", "Môle-Saint-Nicolas"]
        },
        "Sud-Est": {
            "code": "HT-SE",
            "villes": ["Jacmel", "Marigot", "Bainet", "Belle-Anse"]
        },
        "Grand'Anse": {
            "code": "HT-GA",
            "villes": ["Jérémie", "Anse-d'Hainault", "Pestel", "Corail"]
        },
        "Nippes": {
            "code": "HT-NP",
            "villes": ["Miragoâne", "Petite-Rivière-de-Nippes", "Anse-à-Veau", "Baradères"]
        }
    }

    for dept_name, info in haiti_data.items():
        # Kreyasyon oswa rekipere depatman
        dept, created = Department.objects.get_or_create(name=dept_name)
        if created:
            print(f"Département créé : {dept_name}")
        else:
            print(f"Département déjà existant : {dept_name}")

        # Ajoute komin/vil ki asosye yo
        for ville_name in info["villes"]:
            ville, v_created = Ville.objects.get_or_create(
                department=dept,
                name=ville_name
            )
            if v_created:
                print(f"  -> Ville créée : {ville_name}")

    print("Félicitations ! Tous les départements et les communes d'Haïti sont connectés avec succès.")

if __name__ == "__main__":
    run()