from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
class PersonPagination(PageNumberPagination):
    page_size=3
    page_query_param='page_size'
    max_page_size=10

    def get_paginated_response(self, data):
        return Response({
            'links':{
                'next':self.get_next_link(),
                'previous':self.get_previous_link(),
            },
            'total':self.page.paginator.count,
            'total_pages':self.page.paginator.num_pages,
            'current_page':self.page.number,
            'results':data
        })

