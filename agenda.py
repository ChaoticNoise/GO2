from google.appengine.api import users

from requestmodel import *

import webapp2
import member
import gig
import plan
import band
import poll
import assoc
import logging

from debug import debug_print
    
import datetime

class MainPage(BaseHandler):

    @user_required
    def get(self):    
        """ get handler for agenda view """
        self._make_page(the_user=self.user)
            
    def _make_page(self,the_user):
        """ construct page for agenda view """
        
        # find the bands this member is associated with
        the_assocs = assoc.get_confirmed_assocs_of_member(the_user)
        the_band_keys = [a.band for a in the_assocs]
        
        if the_band_keys is None or len(the_band_keys)==0:
            return self.redirect('/member_info.html?mk={0}'.format(the_user.key.urlsafe()))

        if the_user.show_long_agenda:
            num_to_put_in_upcoming=1000
        else:
            num_to_put_in_upcoming=5

        show_canceled=True
        if the_user.preferences and the_user.preferences.hide_canceled_gigs:
            show_canceled=False
            
        today_date = datetime.datetime.now()
#         the_gigs = gig.get_gigs_for_bands(the_bands, num=num_to_put_in_upcoming, start_date=today_date)
        all_gigs = gig.get_gigs_for_band_keys(the_band_keys, show_canceled=show_canceled, start_date=today_date)

        all_polls = poll.get_polls_for_band_keys(the_band_keys)

        print '\n\n{0} polls\n\n'.format(len(all_polls))

        upcoming_plans = []
        weighin_plans = []        
        poll_plans = []
        newpoll_plans = []

        all_everything = all_gigs + all_polls

        if all_everything:
            for i in range(0, len(all_everything)):
                a_gig = all_everything[i]
                the_plan = plan.get_plan_for_member_for_gig(the_user, a_gig)

                info_block={}
                info_block['the_gig_key'] = a_gig.key
                info_block['the_plan_key'] = the_plan.key
                info_block['the_member_key'] = the_user.key
                a_band_key = a_gig.key.parent()
                a_band = None
                for test_band_key in the_band_keys:
                    if test_band_key == a_band_key:
                        a_band_key = test_band_key
                        break
                if a_band_key == None:
                    logging.error('agenda.MainPage error: no band for gig')
                    continue
                info_block['the_band'] = a_band_key.get()
                info_block['the_assoc'] = assoc.get_assoc_for_band_key_and_member_key(the_user.key, a_band_key)

                if type(all_everything[i]) == poll.Poll:
                    info_block['infourl'] = 'poll_info.html?pk='
                    if the_plan.value:
                        poll_plans.append( info_block )
                    else:
                        newpoll_plans.append( info_block )
                else:
                    info_block['infourl'] = 'gig_info.html?gk='
                    if the_plan.section is None:
                        info_block['the_section'] = info_block['the_assoc'].default_section
                    else:
                        info_block['the_section'] = the_plan.section
                    if num_to_put_in_upcoming and i<num_to_put_in_upcoming and (the_plan.value or a_gig.status == 2): #include gigs for which we've weighed in or have been cancelled
                        upcoming_plans.append( info_block )
                    else:            
                        if (the_plan.value == 0 ):
                            weighin_plans.append( info_block )

        number_of_bands = len(the_band_keys)

        template_args = {
            'upcoming_plans' : upcoming_plans,
            'weighin_plans' : weighin_plans,
            'poll_plans' : poll_plans,
            'newpoll_plans' : newpoll_plans,
            'show_band' : number_of_bands>1,
            'long_agenda' : the_user.show_long_agenda,
            'the_date_formatter' : member.format_date_for_member,
            'agenda_is_active' : True
        }
        self.render_template('agenda.html', template_args)


class SwitchView(BaseHandler):
    @user_required
    def get(self):    
        """ get handler for agenda view """
        the_user=self.user
        
        if the_user.show_long_agenda:
            the_user.show_long_agenda=False
        else:
            the_user.show_long_agenda=True
        the_user.put()
        return self.redirect(self.uri_for("home"))