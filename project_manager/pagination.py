from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    """
    Pagination personnalisée avec des informations supplémentaires.
    """
    page_size = 2  # Nombre de projet par page
    page_size_query_param = 'page_size'  # Permet de modifier la taille des pages via un paramètre
    max_page_size = 50  # Limite maximale de la taille des pages

    def get_paginated_response(self, data):
        """
        Retourne une réponse paginée personnalisée.
        """
        return Response({
            'total_count': self.page.paginator.count,  # Nombre total de projet
            'total_pages': self.page.paginator.num_pages,  # Nombre total de pages
            'current_page': self.page.number,  # Numéro de la page actuelle
            'next': self.get_next_link(),  # Lien vers la page suivante
            'previous': self.get_previous_link(),  # Lien vers la page précédente
            'results': data,  # Données pour la page actuelle
        })