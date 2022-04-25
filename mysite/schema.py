import graphene
import polls.schema

class Query(
    polls.schema.Query,
    graphene.ObjectType
):
    pass 

class Mutation(
    polls.schema.Mutation,
    graphene.ObjectType
):
    pass 

schema = graphene.Schema(query=Query, mutation=Mutation)
