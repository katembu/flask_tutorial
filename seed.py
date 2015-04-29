from app import appbuilder, db
from app.models import *
import names
import radar
from random import randint

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

x = 1300
y = 0
'''
while y < x:
    logged = Voters()
    logged.first_name = names.get_first_name()
    logged.middle_name = names.get_first_name()
    logged.last_name = names.get_last_name()
    logged.gender = randint(1,2)
    logged.telephone = random_with_N_digits(10)
    logged.vote_mobile = True
    logged.voter_pin = random_with_N_digits(4)
    logged.document_type = randint(1,2)
    logged.document_number = random_with_N_digits(12)
    logged.date_of_birth = radar.random_datetime(start='1940-05-24', stop='1997-05-24')
    logged.ward_id = randint(1,1300)

    db.session.add(logged)
    db.session.commit()
    y+=1

'''
vx = db.session.query(Voters)
for x in vx:
    v = Votes()
    try:
        v.candidate_id = randint(1,2)
        v.election_id = 1
        v.voters = x
        db.session.add(v)
        db.session.commit()
    except:
        print "pass"
