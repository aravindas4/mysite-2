from email.policy import default
import graphene

from .models import Question
from .types import QuestionType, ChoiceType, VoteQuestion
# from graphene_django import DjangoListField

class Query(graphene.ObjectType):
    questions = graphene.List(
        QuestionType,
        resolver=QuestionType.resolve
    )
    question = graphene.Field(QuestionType, question_id=graphene.ID())
    # choices = graphene.List(ChoiceType)
    # choice = graphene.Field(ChoiceType, choice_id=graphene.ID())

    

    # def resolve_questions(self, info):
        # import ipdb; ipdb.set_trace()
        # return Query.paginate_qs(
        #     Question.objects.all()
        # )
        # print("resolve questions")
        # return Question.objects.all()

    def resolve_question(self, info, question_id):
        return Question.objects.get(pk=question_id)

    def resolve_choices(self, info, **kwargs):
        return ChoiceType.objects.all()

    def resolve_choice(self, info, choice_id):
        return ChoiceType.objects.get(pk=choice_id)

    def resolve(self, next, root, info, **args):
        # import ipdb; ipdb.set_trace()
        print(args)
        # print(kwargs)
        print("SOMMMMMMM")
        # modify the qs for pagination
        # individual resolvers
        pass


class Mutation(graphene.ObjectType):
    vote_question = VoteQuestion.Field()
