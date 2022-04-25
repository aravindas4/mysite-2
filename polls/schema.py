import graphene

from .models import Question
from .types import QuestionType, ChoiceType, VoteQuestion

class Query(graphene.ObjectType):
    questions = graphene.List(QuestionType)
    question = graphene.Field(QuestionType, question_id=graphene.ID())
    # choices = graphene.List(ChoiceType)
    # choice = graphene.Field(ChoiceType, choice_id=graphene.ID())

    def resolve_questions(self, info, **kwargs):
        return Question.objects.all()

    def resolve_question(self, info, question_id):
        return Question.objects.get(pk=question_id)

    def resolve_choices(self, info, **kwargs):
        return ChoiceType.objects.all()

    def resolve_choice(self, info, choice_id):
        return ChoiceType.objects.get(pk=choice_id)

class Mutation(graphene.ObjectType):
    vote_question = VoteQuestion.Field()

