import re
from datetime import datetime
from wtforms import Form, StringField, SelectField, IntegerField, \
                    DateField, BooleanField
from wtforms.validators import *
from flask_appbuilder.fieldwidgets import BS3TextAreaFieldWidget, \
                            BS3TextFieldWidget, Select2Widget, DatePickerWidget, \
                            DateTimePickerWidget
from flask.ext.appbuilder.forms import DynamicForm
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from .models import Ward, SmsloggerLoggedmessage, Voters, Delegates, Votes
from wtforms.validators import ValidationError
from app import appbuilder, db


def get_pending():
    try:
        results = db.session.query(SmsloggerLoggedmessage).filter(
                            SmsloggerLoggedmessage.direction == 'O',
                            SmsloggerLoggedmessage.status == 'pending')
        if results.count() == 0:
            results = False
    except:
        results = False

    return results


def ward_query():
    return db.session.query(Ward)
choice = QuerySelectField('Ward', query_factory=ward_query)


def validate_telephone(form, field):
    if (len(str(field.data)) >= 1 and not re.match('^[0-9]{10,10}$', str(field.data))):
        raise ValidationError('Field must be 10 characters ')
    tel = db.session.query(Voters).filter(Voters.telephone == field.data)
    if (tel.count() >= 1):
        raise ValidationError('Field must be Unique. Number Already Used')


def validate_pin(form, field):
    if (len(field.data) >= 1 and not re.match('^[0-9]{4,8}$', field.data)):
        raise ValidationError('Field must be 4 to 8 characters')


class ElectionForm(DynamicForm):
    name = StringField(('Name'),
                             description=('Name!'),
                             validators=[DataRequired()],
                             widget=BS3TextFieldWidget())
    uuid = StringField(('UUID'),
                             validators=[DataRequired()],
                             widget=BS3TextFieldWidget())
    is_approved = BooleanField(('Vote Using Mobile No'))
    voting_starts_at_date = DateField(('DOB'),
                              description=('Date of Birth!'),
                              validators=[DataRequired()],
                              widget=DateTimePickerWidget())
    voting_ends_at_date = DateField(('DOB'),
                              description=('Date of Birth!'),
                              validators=[DataRequired()],
                              widget=DateTimePickerWidget())
    voting_extended_until_date = DateField(('DOB'),
                              description=('Date of Birth!'),
                              validators=[DataRequired()],
                              widget=DateTimePickerWidget())
    approved_at_date = DateField(('DOB'),
                              description=('Date of Birth!'),
                              validators=[DataRequired()],
                              widget=DateTimePickerWidget())
    frozen_at_date = DateField(('DOB'),
                              description=('Date of Birth!'),
                              validators=[DataRequired()],
                              widget=DateTimePickerWidget())
    archived_at_date = DateField(('DOB'),
                              description=('Date of Birth!'),
                              validators=[DataRequired()],
                              widget=DateTimePickerWidget())
    voters_frozen_at_date = DateField(('DOB'),
                              description=('Date of Birth!'),
                              validators=[DataRequired()],
                              widget=DateTimePickerWidget())
    result_tallied_at_date = DateField(('DOB'),
                              description=('Date of Birth!'),
                              validators=[DataRequired()],
                              widget=DateTimePickerWidget())
    ward_id = QuerySelectField('Ward',
                            query_factory=ward_query,
                            widget=Select2Widget())
    post_id = QuerySelectField('Ward',
                            query_factory=ward_query,
                            widget=Select2Widget())


class MyForm(DynamicForm):
    first_name = StringField(('First Name'),
                             description=('Your first Name!'),
                             validators=[DataRequired()],
                             widget=BS3TextFieldWidget())
    middle_name = StringField(('Middle Name'),
                              description=('Your Second Name!'),
                              widget=BS3TextFieldWidget())
    last_name = StringField(('Sur Name'),
                            description=('Your Sur name!'),
                            validators=[DataRequired()],
                            widget=BS3TextFieldWidget())
    date_of_birth = DateField(('DOB'),
                              description=('Date of Birth!'),
                              validators=[DataRequired()],
                              widget=DatePickerWidget())
    gender = SelectField(('Gender'),
                         choices=[(1, 'Male'), (2, 'Female')],
                         coerce=int,
                         validators=[], widget=Select2Widget())
    document_type = SelectField(('Document Type'),
                                choices=[(1, 'ID'), (2, 'Passport')],
                                coerce=int,
                                validators=[DataRequired()],
                                widget=Select2Widget())
    document_number = StringField(('Document No'),
                                  validators=[DataRequired(), Length(min=6)],
                                  widget=BS3TextFieldWidget())
    vote_mobile = BooleanField(('Vote Using Mobile No'))
    telephone = StringField(('Telephone'),
                            validators=[validate_telephone, optional()],
                            widget=BS3TextFieldWidget())
    ward = QuerySelectField('Ward',
                            query_factory=ward_query,
                            widget=Select2Widget())


class SMSForm(DynamicForm):
    DIRECTION_INCOMING = 'I'
    DIRECTION_OUTGOING = 'O'

    DIRECTION_CHOICES = [
            (DIRECTION_INCOMING, "Incoming"),
            (DIRECTION_OUTGOING, "Outgoing")]

    STATUS_SUCCESS = 'success'
    '''Outgoing STATUS types'''
    STATUS_WARNING = 'warning'
    STATUS_ERROR = 'error'
    STATUS_INFO = 'info'
    STATUS_ALERT = 'alert'
    STATUS_REMINDER = 'reminder'
    STATUS_LOGGER_RESPONSE = 'from_logger'
    STATUS_SYSTEM_ERROR = 'system_error'
    STATUS_PENDING = 'pending'

    '''Incoming STATUS types'''
    STATUS_MIXED = 'mixed'
    STATUS_PARSE_ERRROR = 'parse_error'
    STATUS_BAD_VALUE = 'bad_value'
    STATUS_INAPPLICABLE = 'inapplicable'
    STATUS_NOT_ALLOWED = 'not_allowed'

    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Success"),
        (STATUS_PENDING, "Pending"),
        (STATUS_WARNING, "Warning"),
        (STATUS_ERROR, "Error"),
        (STATUS_INFO, "Info"),
        (STATUS_ALERT, "Alert"),
        (STATUS_REMINDER, "Reminder"),
        (STATUS_LOGGER_RESPONSE, "Response from logger"),
        (STATUS_SYSTEM_ERROR, "System error"),

        (STATUS_MIXED, "Mixed"),
        (STATUS_PARSE_ERRROR, "Parse Error"),
        (STATUS_BAD_VALUE, "Bad Value"),
        (STATUS_INAPPLICABLE, "Inapplicable"),
        (STATUS_NOT_ALLOWED, "Not Allowed")]

    date = DateField(('Date'),
                     description=('Date'),
                     validators=[DataRequired()], widget=DatePickerWidget())
    direction = SelectField(('Direction'),
                            choices=DIRECTION_CHOICES,
                            validators=[], widget=Select2Widget())
    text = StringField(('Text'),
                       description=('Text'),
                       validators=[DataRequired()],
                       widget=BS3TextAreaFieldWidget())
    status = SelectField(('Status'),
                         choices=STATUS_CHOICES,
                         validators=[DataRequired()], widget=Select2Widget())
    identity = IntegerField(('Identity'),
                            validators=[validate_telephone, optional()],
                            widget=BS3TextFieldWidget())
    response_to = StringField(('Response To'),
                              widget=BS3TextFieldWidget())


def serialized_sms(p):
    y = []
    for x in p:
        z = {"to": x.identity, "message": x.text}
        y.append(z)
        x.status = SMSForm.STATUS_SUCCESS
        db.session.add(x)
        db.session.commit()
    return y


def format_number(tel_no):
    return tel_no.replace('+254', '0', 1)


def process_sms(p):
    '''check if PHONE exist & if Pin exist'''
    text = p.text
    split_text = text.split()
    pin = split_text[0]
    identity = format_number(p.identity)
    tel = db.session.query(Voters).filter_by(telephone=identity)
    if tel.count() == 1:
        pass_test = db.session.query(Voters).filter_by(telephone=identity, voter_pin=pin)
        if pass_test.count() == 1:
            split_text.pop(0)
            r = []
            for key in split_text:
                r.append(complete_voting(key, pass_test[0]))

            p.status = SMSForm.STATUS_SUCCESS
            db.session.commit()

            logged = SmsloggerLoggedmessage()
            logged.direction = SMSForm.DIRECTION_OUTGOING
            logged.text =  ", ".join(r)
            logged.identity = identity
            logged.response_to_id = p.id
            logged.status = SMSForm.STATUS_PENDING
            db.session.add(logged)
            db.session.commit()
        else:
            message = "Invalid PIN"

            logged = SmsloggerLoggedmessage()
            logged.direction = SMSForm.DIRECTION_OUTGOING
            logged.text = message
            logged.identity = identity
            logged.response_to_id = p.id
            logged.status = SMSForm.STATUS_PENDING
            db.session.add(logged)
            db.session.commit()

            p.status = SMSForm.STATUS_BAD_VALUE
            db.session.commit()
    else:
        p.status = SMSForm.STATUS_NOT_ALLOWED
        db.session.add(p)
        db.session.commit()


def complete_voting(key, voter):
    count_key = db.session.query(Delegates).filter_by(candidate_key=key)
    if count_key.count() == 1:
        d = count_key[0]
        AllowVote = False
        ward = d.elections.ward_id
        post = d.elections.posts.name
        mm = voter.ward
        E = d.elections
        N = datetime.now()
        ##CHECK ELECTION IS ACTIVE
        ##President
        if (N >= E.voting_starts_at_date and N <= E.voting_ends_at_date and E.is_approved == True):
            if post == 'Senator' and (mm.constituency.county.id==ward):
                AllowVote = True
            elif post == 'Women Representative' and (mm.constituency.county.id==ward):
                AllowVote = True
            elif post == 'Governor' and (mm.constituency.county.id==ward):
                AllowVote = True
            elif post == 'Member of Parliament' and (mm.constituency.id==ward):
                AllowVote = True
            elif post == 'County Assembly Representative' and (mm.id==ward):
                AllowVote = True
            else:
                AllowVote = False

            if AllowVote:
                '''Check if this person has voted for the same Person Before '''
                check = db.session.query(Votes).filter_by(elections=d.elections, voters=voter)
                if check.count() < 1:
                    v = Votes()
                    v.delegates = d
                    v.elections = d.elections
                    v.voters = voter
                    db.session.add(v)
                    db.session.commit()

                    return "Vote for %s was successful" % (d.voters.full_name())
                else:
                    return "You've already voted"
            else:
                return "Invalid Candidate %s" % (key)
        else:
            return "No Active Election"
