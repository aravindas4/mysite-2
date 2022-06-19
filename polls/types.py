import graphene
from graphene_django.types import DjangoObjectType

from .models import Question, Choice


class ListMeta(graphene.Interface):
    limit = graphene.Int(required=True)
    offset = graphene.Int(required=True)
    count = graphene.Int(required=True)
    hasNext = graphene.Int(required=True)
    hasPrevious = graphene.Int(required=True)


class ListFilterType(graphene.Enum):
    BOOL = "bool"
    STRING = "string"
    INTEGER = "integer"
    DATE = "date"
    DATETIME = "datetime"
    TIME = "time"
    RANGE = "range"

class ListFilter(graphene.ObjectType):
    field = graphene.String()
    value_for_display = graphene.String()
    data_type = graphene.Field(ListFilterType)

class SearchKeyword(graphene.ObjectType):
    key = graphene.String()
    value_for_display = graphene.String()


from django.db.models import CharField, Q
class BaseList(graphene.ObjectType):

    @classmethod
    def resolve(cls, root, info, *args, **kwargs):
        limit = kwargs.get('limit')
        offset = kwargs.get('offset')
        filters = kwargs.get('filters', [])
        other_filters = kwargs.get('other_filters', {})
        seachables = kwargs.get('seachables', [])
        sort = kwargs.get('sort')

        field_model = cls.detail_type._meta.model

        final_filters = {}
        if filters is not None:
            for _filter in filters:
                field_type = field_model._meta.get_field(_filter["field"])

                if isinstance(field_type, CharField):
                    final_filters[_filter["field"] + "__icontains"] = _filter["value"]
                else:
                    final_filters.update[
                        _filter["field"]: _filter["value"]
                    ]

        seach_qs = Q()

        if seachables is not None:
            for seachable in seachables:
                if seachable["key"] == "default":
                    for field in cls.search_key_field_map[seachable["key"]]:
                        seach_qs.add(Q(**{field: seachable["value"]}), Q.OR)


        order_by_field = 'pk'

        if sort is not None:
            if sort['field'] == 'id':
                order_by_field = 'pk'
            elif sort['field'] != 'pk':
                order_by_field = sort["field"]

            if sort["order"] == 'DESC':
                order_by_field = f"-{order_by_field}"
        


        qs = cls.get_queryset().filter(**final_filters, **other_filters).filter(
            seach_qs
        ).order_by(order_by_field).distinct()
        
        count = qs.count()
        objects = qs[offset: limit+offset]
        obj = cls(limit=limit, offset=offset, objects=objects, count=count)
        obj.hasNext = limit + offset < count
        obj.hasPrevious = offset > 0
        return obj

    @classmethod
    def get_queryset(cls):
        class_model = cls.detail_type._meta.model
        return class_model.objects.all()


from graphql import GraphQLError

class DetailMixin:
    lookup_field = "pk"

    @classmethod
    def resolve(cls, *args, **kwargs):
        filters = {}
        filters[cls.lookup_field] = kwargs["id"]

        try:
            obj = cls._meta.model.objects.filter(**filters).get()
        except cls._meta.model.DoesNotExist:
            raise GraphQLError("Object Does Not Exist")

        return obj



class ChoiceType(DetailMixin, DjangoObjectType):
    class Meta:
        model = Choice
        fields = ("id", "choice_text", "votes", "question")


class ChoiceList(BaseList):
    detail_type = ChoiceType

    objects = graphene.List(detail_type, required=True)

    class Meta:
        interfaces = (ListMeta,)
    
    # @classmethod
    # def resolve(cls, info, *args, **kwargs):
    #     return super().resolve(info, *args, **kwargs)
    


class QuestionType(DetailMixin, DjangoObjectType):
    paginated_choices = graphene.Field(
        'polls.types.ChoiceList',
        limit=graphene.Argument(graphene.Int, default_value=10),
        offset=graphene.Argument(graphene.Int, default_value=0),
    )

    choices = graphene.List(ChoiceType)

    class Meta:
        model = Question
        only_fields = ("id", "question_text", "pub_date", "choices")

    def resolve_choices(self, info, *args, **kwargs):
        return self.choices.all()
    
    def resolve_paginated_choices(self, info, *args, **kwargs):
        filters = kwargs.get('other_filters', {})
        filters.update({"question_id": self.pk})
        kwargs["other_filters"] = filters
        return ChoiceList.resolve(ChoiceList, info, *args, **kwargs)

class QuestionList(BaseList):
    detail_type = QuestionType

    objects = graphene.List(detail_type, required=True)
    filters = graphene.List(ListFilter)
    seachables = graphene.List(SearchKeyword)

    filter_options = [
        ListFilter(
            field="question_text", 
            value_for_display="Question", 
            data_type=ListFilterType.STRING
        ),
        ListFilter(
            field="pub_date",
            value_for_display="Published On",
            data_type=ListFilterType.DATETIME
        )
    ]

    search_key_field_map = {
        "default": ["question_text__icontains"]
    }

    search_options = [
        SearchKeyword(
            key="default",
            value_for_display="Default"
        )
    ]

    class Meta:
        interfaces = (ListMeta,)
    
    def resolve_seachables(self, info, *args, **kwargs):
        return self.search_options

    def resolve_filters(self, info, *args, **kwargs):
        return self.filter_options



class VoteQuestionInput(graphene.InputObjectType):
    question_id = graphene.ID(required=True)
    choice_id = graphene.ID(required=True)


class VoteQuestion(graphene.Mutation):
    class Arguments:
        input = VoteQuestionInput(required=True)

    question = graphene.Field(QuestionType)

    @classmethod
    def mutate(cls, root, info, input):
        question = Question.objects.get(pk=input.question_id)
        choice = question.choices.all().get(pk=input.choice_id)
        choice.votes += 1
        choice.save()

        return VoteQuestion(question=question)


class QuestionInput(graphene.InputObjectType):
    id = graphene.ID()
    question_text = graphene.String()

class QuestionsInput(graphene.InputObjectType):
    questions = graphene.List(QuestionInput, required=True)

from django import forms
class QuestionForm(forms.ModelForm):
    pub_date = forms.DateTimeField(required=False)
    class Meta:
        model = Question
        fields = ("id", "question_text", "pub_date")

class ChoiceForm(forms.ModelForm):
    question = forms.IntegerField(required=False)

    class Meta:
        model = Choice
        fields = ("id", "choice_text", "question")


class StatusMessage(graphene.ObjectType):
    field = graphene.String()
    message = graphene.String(required=True)

class StatusInfo(graphene.ObjectType):
    success = graphene.Boolean(required=True)
    messages = graphene.List(StatusMessage, required=True)

    @classmethod
    def fail(cls, messages=None):
        if messages is None:
            messages = []
        return StatusInfo(success=False, messages=messages)

    @classmethod
    def ok(cls, messages=None):
        if messages is None:
            messages = []
        return StatusInfo(success=True, messages=messages)


class MutateQuestions(graphene.Mutation):
    status = graphene.Field(StatusInfo, required=True)
    objects = graphene.List(QuestionType)
    class Arguments:
        input = QuestionsInput(required=True)


    def verify_input(data):
        error_messages = []

        for ind, data in enumerate(data):
            _id = data.get('id')

            if _id is None:  #Create
                obj = Question.objects.filter(pk=_id).first()

                if obj is not None:
                    error_messages.append({
                        "id": ind,
                        "key": "id",
                        "message": f"Question with id# {_id} already exists"
                    })
                else:
                    question_form = QuestionForm(data=data)
                    if not question_form.is_valid():
                        error_messages.extend(
                            [
                                {
                                    "id": ind,
                                    "key": key,
                                    "message": value.get_json_data()[0]["message"]
                                } for key, value in question_form.errors.items()
                            ]
                        )
            else: # Update
                obj = Question.objects.filter(pk=_id).first()

                if obj is None:
                    error_messages.append({
                        "id": ind,
                        "key": "id",
                        "message": f"Question with id# {_id} does not exist"
                    })
                else:
                    question_form = QuestionForm(data=data, instance=obj)
                    if not question_form.is_valid():
                        error_messages.extend(
                            [
                                {
                                    "id": ind,
                                    "key": key,
                                    "message": value.get_json_data()[0]["message"]
                                } for key, value in question_form.errors.items()
                            ]
                        )

        return error_messages

    @classmethod
    def mutate(cls, root, info, input):

        questions_data = input.get("questions")
        error_messages = MutateQuestions.verify_input(questions_data)

        if len(error_messages) > 0:
            messages = []
            for err_msg in error_messages:
                messages.append(
                    StatusMessage(
                        field=f"{err_msg['id']}#{err_msg['key']}",
                        message=err_msg["message"]
                    )
                )
            return cls(
                status=StatusInfo.fail(messages=messages),
                objects=[]
            )
        
        result = []
        for question_data in questions_data:
            _id = question_data.get("id")

            if _id is None:
                result.append(Question.objects.create(**question_data))
            else:
                result.append(
                    Question.objects.filter(pk=_id).update(**question_data)
                )

        messages = [StatusMessage(message="Question are mutated successfully")]
        return cls(status=StatusInfo.ok(messages=messages), objects=result)


class ChoiceInput(graphene.InputObjectType):
    choice_text = graphene.String(required=True)

class QuestionWithChoicesInput(QuestionInput):
    choices = graphene.List(ChoiceInput, required=False)


class CreateQuestion(graphene.Mutation):
    status = graphene.Field(StatusInfo, required=True)
    object = graphene.Field(QuestionType)

    class Arguments:
        input = QuestionWithChoicesInput(required=True)

    @classmethod
    def mutate(cls, root, info, input):
        print(input)
        chocies_data = input.pop("choices", [])
        question_data = input
        error_messages = []

        # validate question data
        question_data.pop("id", None)

        question_form = QuestionForm(data=question_data)

        messages = []
        if not question_form.is_valid():
           question_errors = [
                {
                    "key": key,
                    "message": value.get_json_data()[0]["message"]
                } for key, value in question_form.errors.items()
           ]

           error_messages.extend(question_errors)

        for ind, choice_data in enumerate(chocies_data):
            choice_form = ChoiceForm(data=choice_data)

            if not choice_form.is_valid():
                choice_errors = [
                    {
                        "parent_key": "choices",
                        "id": ind,
                        "key": key,
                        "message": value.get_json_data()[0]["message"]
                    } for key, value in choice_form.errors.items()
                ]

                error_messages.extend(choice_errors)

        if len(error_messages) > 0:
            print(error_messages)
            for err_msg in error_messages:
                if "parent_key" in err_msg:
                    parent_key = f"{err_msg['parent_key']}#"
                else:
                    parent_key = ""
                
                if "id" in err_msg:
                    _id = f"{err_msg['id']}#"
                else:
                    _id = ""

                final_message = f"{parent_key}{_id}{err_msg['key']}"
                messages.append(
                    StatusMessage(
                        field=f"{final_message}",
                        message=err_msg["message"]
                    )
                )
            return cls(
                status=StatusInfo.fail(messages=messages),
                object=None
            )

        question = Question.objects.create(**question_data)
        messages = [StatusMessage(message="Question Created succesfully")]

        for choice_data in chocies_data:
            Choice.objects.create(
                **choice_data,
                question_id=question.id
            )
        
        return cls(
            status=StatusInfo.ok(messages=messages), 
            object=question
        )


class IDsInput(graphene.InputObjectType):
    pks = graphene.List(graphene.String, required=True)


def purify(pks):
    result = []
    for pk in pks:
        if pk.isdigit():
            pk = int(pk)
    
        result.append(pk)

    return result

class DeleteQuestions(graphene.Mutation):
    status = graphene.Field(StatusInfo, required=True)

    class Arguments:
        input = IDsInput(required=True)

    @classmethod
    def mutate(cls, root, info, input):
        result = Question.objects.filter(pk__in=purify(input["pks"])).delete()

        if result[0] > 0:
            messages = [StatusMessage(message="Objects were deleted successfully.")]
        else:
            messages = [StatusMessage(message="No objects were deleted.")]

        return cls(
            status=StatusInfo.ok(messages=messages)
        )
