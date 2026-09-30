from rest_framework import pagination
from rest_framework.response import Response

class MoviePageNumberPagination(pagination.PageNumberPagination):
    page_size=5
    page_size_query_param = 'page_size'
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.page_size,
            'page_number': self.page.number,
            'results': data,
        })
    