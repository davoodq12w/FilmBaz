from rest_framework.views import APIView, Response, Request
from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class FilmBazAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @extend_schema(exclude=True)
    def get(self, request: Request, *args, **kwargs):
        return Response(data={"Error": "the GET method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(exclude=True)
    def post(self, request: Request, *args, **kwargs):
        return Response(data={"Error": "the POST method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(exclude=True)
    def patch(self, request: Request, *args, **kwargs):
        return Response(data={"Error": "the PATCH method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(exclude=True)
    def put(self, request: Request, *args, **kwargs):
        return Response(data={"Error": "the PUT method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(exclude=True)
    def delete(self, request: Request, *args, **kwargs):
        return Response(data={"Error": "the DELETE method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
