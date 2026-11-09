from django.core.management.base import BaseCommand
from business.models import Department, Ville, Quartier

class Command(BaseCommand):
    help = "Enregistre les quartiers et zones clés pour la ville de Cap-Haïtien (Département du Nord)"

    def handle(self, *args, **options):
        # 1. Département du Nord
        nord, _ = Department.objects.get_or_create(name="Nord")

        # 2. Ville de Cap-Haïtien
        # Chercher une ville existante (avec ou sans accent)
        cap_haitien = Ville.objects.filter(department=nord, name__icontains="Cap").first()
        if not cap_haitien:
            cap_haitien, _ = Ville.objects.get_or_create(department=nord, name="Cap-Haïtien")

        self.stdout.write(f"Commune cible : {cap_haitien.name} ({nord.name})")

        # 3. Liste des quartiers clés de Cap-Haïtien
        quartiers = [
            "Carenage",
            "Rival",
            "Haut du Cap",
            "Madeline",
            "Vertières",
            "Champin",
            "Petite Anse",
            "Blohaus",
            "Nan Banbou",
            "Charrier",
            "Boulevard",
            "Centre-Ville (Rue 1 à 24)"
        ]

        created_count = 0
        for name in quartiers:
            quartier, created = Quartier.objects.get_or_create(
                ville=cap_haitien,
                name=name
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"+ Quartier créé : {name}"))
            else:
                self.stdout.write(f"~ Quartier déjà existant : {name}")

        self.stdout.write(self.style.SUCCESS(
            f"Terminé avec succès : {len(quartiers)} quartiers vérifiés/enregistrés ({created_count} nouveaux) pour {cap_haitien.name}."
        ))
