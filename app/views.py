import calendar
from random import randint
import json
from flask.ext.appbuilder.models.sqla.interface import SQLAInterface
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder import ModelView, AppBuilder, expose, BaseView, \
                                 has_access
from flask_appbuilder.views import SimpleFormView
from flask_appbuilder.charts.views import DirectChartView, DirectByChartView, GroupByChartView
from flask_appbuilder.models.group import aggregate_count, aggregate_sum
from flask.ext.babelpkg import lazy_gettext as _
from flask import flash, request, render_template
from app import appbuilder, db
from .models import *
from .forms import *
from .utils import generateIdentifier


def pretty_month_year(value):
    return calendar.month_name[value.month] + ' ' + str(value.year)


def pretty_year(value):
    return str(value.year)


class Sms(BaseView):

    default_view = 'incoming'

    @expose('/incoming/', methods=['GET', 'POST'])
    def incoming(self):
        # do something with param1
        # and return to previous page or index

        if request.method == 'POST':

            '''get the phone number that sent the SMS.'''
            if "from" in request.form and request.form['from']:
                sender = request.form["from"]
            if "message" in request.form and request.form["message"]:
                message = request.form["message"]

            if len(sender) > 0 and len(message) > 0:
                '''LOG SMS INTO INCOMING SMS DATABASES'''
                logged = SmsloggerLoggedmessage()
                logged.direction = SMSForm.DIRECTION_INCOMING
                logged.text = message
                logged.identity = sender
                logged.status = SMSForm.STATUS_PENDING
                db.session.add(logged)
                db.session.commit()
                process_sms(logged)
                success = "true"
            else:
                success = "false"

            reply = {"payload": {"success": success}}
            return json.dumps(reply)
        if request.method == 'GET':

            if request.args.get('task'):
                action = request.args.get('task')
                if action == 'send':
                    '''Querry SMS to send'''
                    p = get_pending()
                    if p:
                        payload = {
                          "payload": {
                            "task": "send",
                            "messages": serialized_sms(p)
                          }
                        }
                        return json.dumps(payload)
                    else:
                        pass
        pass


class ScopeView(ModelView):
    datamodel = SQLAInterface(Scope)
    add_columns = edit_columns = ['name']


class PostView(ModelView):
    datamodel = SQLAInterface(Post)
    list_columns = add_columns = edit_columns = ['name', 'scope']


class CountiesView(ModelView):
    datamodel = SQLAInterface(County)
    list_columns = ['name']


class ConstituencyView(ModelView):
    datamodel = SQLAInterface(Constituency)
    list_columns = ['name', 'county']


class WardView(ModelView):
    datamodel = SQLAInterface(Ward)
    list_columns = ['name', 'constituency', 'constituency.county']


class PartyView(ModelView):
    datamodel = SQLAInterface(Party)
    list_columns = ['name', 'short_name']


class SmsloggerView(ModelView):
    datamodel = SQLAInterface(SmsloggerLoggedmessage)
    base_order = ('date', 'desc')
    show_title = "SMS Log"
    add_form = SMSForm
    page_size = 20
    list_columns = ['identity', 'direction', 'text', 'status', 'date']


class VotersView(ModelView):
    datamodel = SQLAInterface(Voters)
    add_form = MyForm
    edit_form = MyForm
    add_columns = ['first_name', 'middle_name', 'last_name', 'gender',
                   'date_of_birth', 'document_type', 'document_number',
                   'ward', 'vote_mobile', 'telephone']
    edit_columns = ['first_name', 'middle_name', 'last_name', 'gender',
                    'date_of_birth', 'document_type', 'document_number',
                    'ward', 'vote_mobile', 'telephone']
    list_columns = ['full_name', 'telephone', 'ward', 'ward.constituency',
                    'ward.constituency.county']

    def post_add(self, item):
        if item.vote_mobile:
            item.voter_pin = randint(1000, 9999)
            db.session.commit()

            '''PUT this in Outgoing DB'''
            message = "Welcome %s. Youve been registered as voter in %s. "\
                      "Your Mobile voting pin is: %s " % \
                      (item, item.ward, item.voter_pin)

            logged = SmsloggerLoggedmessage()
            logged.direction = SMSForm.DIRECTION_OUTGOING
            logged.text = message
            logged.identity = item.telephone
            logged.status = SMSForm.STATUS_PENDING
            db.session.add(logged)
            db.session.commit()


class DelegatesView(ModelView):
    datamodel = SQLAModel(Delegates)
    validators_columns = {'pk_election': [EqualTo('pk_delegate',
                           message='fields must match')]}
    add_columns = ['voters', 'elections', 'photo']
    edit_columns = ['voters', 'elections']
    list_columns = ['candidate_key', 'photo_img', 'voters', 'posts', 'voters.ward',
                    'voters.ward.constituency', 'voters.ward.constituency.county', 'elections']
    show_fieldsets = [
        ('Personal Information', {'fields': ['voters', 'voters.gender', 'elections', 'photo_img']}),
        (
            'Description',
            {'fields': ['elections'], 'expanded': True}),
    ]

    def post_add(self, item):

        p = item.elections.posts.name.upper()
        item.candidate_key = p[0]+str(generateIdentifier())
        db.session.commit()

    def post_update(self, item):
        p = item.elections.posts.name.upper()
        item.candidate_key = p[0]+str(item.id)
        db.session.commit()


class ElectionView(ModelView):
    datamodel = SQLAInterface(Election)
    list_columns = ['name', 'posts', 'area']
    label_columns = {'wards': _('AREA')}
    add_columns = ['name', 'posts', 'wards', 'voting_starts_at_date', 'voting_ends_at_date',
                   'is_approved']
    edit_columns = ['name', 'posts', 'wards', 'voting_starts_at_date', 'voting_ends_at_date',
                    'is_approved']
    related_views = [DelegatesView]


class VotersChartView(GroupByChartView):
    datamodel = SQLAModel(Voters)
    chart_title = 'Registered Voters'
    label_columns = VotersView.label_columns
    chart_type = 'BarChart'
    search_columns = ['gender', 'ward']

    definitions = [
        {
            'label': 'County',
            'group': 'county',
            'series': [(aggregate_count, 'ward')]
        },
        {
            'label': 'Constituency',
            'group': 'constituency',
            'series': [(aggregate_count, 'ward')]
        },
        {
            'label': 'Gender',
            'group': 'gender',
            'series': [(aggregate_count, 'ward')]
        }
    ]


class SMSReportChartView(GroupByChartView):
    datamodel = SQLAModel(SmsloggerLoggedmessage)
    chart_title = 'SMS Report'
    label_columns = SmsloggerView.label_columns
    search_columns = ['direction']

    definitions = [
        {
            'label': 'Direction',
            'group': 'direction',
            'series': [(aggregate_count, 'direction')]
        },
        {
            'label': 'Date',
            'group': 'mdate',
            'series': [(aggregate_count, 'direction')]
        },
        {
            'label': 'Outgoing',
            'group': 'outgoing',
            'series': [(aggregate_count, 'direction')]
        }
    ]


class MyView(BaseView):
    route_base = "/election"
    default_view = 'results'

    @expose('/result/')
    @has_access
    def results(self):
        el = db.session.query(Election)
        # do something with param1
        # and return it
        # return param1
        # do something with param1
        # and render template with param
        # param1 = 'Goodbye %s' % (param1)
        # self.update_redirect()
        self.update_redirect()
        return self.render_template('method3.html', param1=el)

    @expose('/show/<string:param1>')
    def show(self, param1):
        p = db.session.query(Election).filter_by(uuid=param1)
        if p.count() == 1:
            el = p[0]
            info = {"election": el}
            results = db.session.query(func.count(Votes.candidate_id).label('votecount'), Votes.elections, Votes.delegates.label('d')).filter_by(elections=el).group_by(Votes.candidate_id)
            print results
            name = el.name
            '''Get Delegates Votesself.update_redirect() '''
            return self.render_template('results.html',
                               result=results, info=info)
        else:
            return "Erro"


db.create_all()
appbuilder.add_view_no_menu(MyView())


appbuilder.add_view(VotersView, "Voters", category="Settings")
appbuilder.add_view(DelegatesView, "Delegates", category="Settings")
appbuilder.add_view(ElectionView, "Elections", category="Settings")
appbuilder.add_view(PartyView, " Political Party", category="Settings")
appbuilder.add_view(ScopeView, " Scopes", category="Settings")
appbuilder.add_view(PostView, " Post", category="Settings")
appbuilder.add_view(CountiesView, "Counties", category="Settings")
appbuilder.add_view(ConstituencyView, "Constituency", category="Settings")
appbuilder.add_view(WardView, "Ward", category="Settings")
appbuilder.add_view(SmsloggerView, "SMS LOGGER", category="Settings")
appbuilder.add_view(VotersChartView, "Voters Registered", category="Reports")
appbuilder.add_view(SMSReportChartView, "SMS Report", category="Reports")
# appbuilder.add_view(MyView, "Election Results", category="Reports")

appbuilder.add_link("Election Results", href='/election/result', category='Reports')
appbuilder.add_view_no_menu(Sms())
