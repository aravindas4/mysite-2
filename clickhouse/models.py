from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    create_engine, Column, String, Integer, literal, DateTime, ForeignKey
)




from clickhouse_sqlalchemy import engines

uri = "clickhouse://default:@clickhouse_server/polls"

engine = create_engine(uri)
session = sessionmaker(engine)()


Base = declarative_base()

"""
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date publilshed')


    def __str__(self) -> str:
        return self.question_text

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
"""

class Question(Base):
    __tablename__ = "polls_question"
    __table_args__ = (
        engines.MergeTree(order_by=['id']), engines.Memory(),
        # {'schema': database},
    )

    id = Column("id", Integer(), primary_key=True)
    question_text = Column("question_text", String(200))
    pub_date = Column("pub_date", DateTime(),)


    
"""

class Choice(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices"
    )
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.choice_text
"""

class Choice(Base):
    __tablename__ = "polls_choice"
    __table_args__ = (
        engines.MergeTree(order_by=['id']), engines.Memory(),
        # {'schema': database},
    )

    id = Column("id", Integer(), primary_key=True)
    question_id = Column("question_id", Integer, )

    # question = relationship("Question")

    choice_text = Column("choice_text", String(200))
    votes = Column("votes", Integer(), default=0)
