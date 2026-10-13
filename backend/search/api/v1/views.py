from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser

from .serializers import SearchResponseSerializer
from search.services.engine import SearchEngine


class GlobalSearchView(APIView):

    permission_classes = [IsAdminUser]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="q",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="search",
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=SearchResponseSerializer,
                description="نتایج جستجو",
            ),
        },
    )
    def get(self, request):

        query = request.query_params.get("q", "").strip()

        if not query:
            return Response({
                "query": "",
                "total": 0,
                "results": [],
            })

        results = SearchEngine.search(
            query=query,
            user=request.user,
        )

        return Response({
            "query": query,
            "total": len(results),
            "results": results,
        })