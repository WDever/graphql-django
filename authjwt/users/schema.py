import graphene
import graphql_jwt

from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class Query(graphene.ObjectType):
    users = graphene.List(UserType)

    def resolve_users(self, info, **kwargs):
        return get_user_model().objects.all()


class CreateUserInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    password = graphene.String(required=True)
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        user_data = CreateUserInput(required=True)

    def mutate(self, info, user_data, **kwargs):
        if get_user_model().objects.filter(email=user_data.get("email")).exists():
            raise Exception("Email is already exist!")

        user = get_user_model()(
            email=user_data.get("email"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
        )
        user.set_password(user_data.get("password"))
        user.save()

        return CreateUser(user=user)


class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    token_auth = ObtainJSONWebToken.Field()
