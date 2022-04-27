# GraphQL APIs for mysite project
[Original project](https://docs.djangoproject.com/en/3.2/intro/tutorial01)

## Apps and thier models
 - polls: 
      Question(id, , question_text, pub_date)
      Choice(id, question_id, choice_text, votes)

## APIs: 
- In the original project, 3 APIs have been implemented

### Queries:
- List questions (unpaginated and unfiltered). 
- Detail a question. Further all associtaed choies can listed using key `choices`

### Mutations:
- Vote a choice for a question

### Misc:
- DB Used: Mysql
- Both DB and django have been dockerized
- All the requirements are placed in `requirements.txt`
