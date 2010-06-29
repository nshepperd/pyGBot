##
##    pyGBot - Versatile IRC Bot
##    Copyright (C) 2008 Morgan Lokhorst-Blight, Alex Soborov
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

import random

from elixir import *

metadata.bind = "sqlite:///markov.sqlite"

class MarkovStimulus(Entity):
    stimulus = Field(UnicodeText, primary_key=True)
    responses = ManyToMany('MarkovResponse')
    
    def __repr__(self):
        return ('<MarkovStimulus %s>' % (self.stimulus)).encode('ascii','replace')

class MarkovResponse(Entity):
    stimuli = ManyToMany('MarkovStimulus')
    response = Field(UnicodeText)

    def __repr__(self):
        return ('<MarkovResponse %s>' % (self.response)).encode('ascii','replace')
setup_all()
create_all()


################################################################################
## 
## Plugin
## 
################################################################################
from pyGBot.BasePlugin import BasePlugin

def markov_filter(message):
    return  ''.join(c for c in message.lower() if c in "abcdefghijklmnopqrstuvwxyz0123456789'. \t")

def generate_markov_pairs(message):
    message = markov_filter(message)
    for sentence in message.split(". "):
        words = sentence.split()
        while len(words) >= 4:
            yield (words[0:3],words[3])
            words.pop(0)
        yield (words, None)

def markov_store(message):
    for pair in generate_markov_pairs(message):
        me = MarkovStimulus.get_by(stimulus=unicode(" ".join(pair[0])))
        if not me:
            me = MarkovStimulus(stimulus=unicode(" ".join(pair[0])))
        resp = MarkovResponse.get_by(response=unicode(pair[1]) if pair[1] else None)
        if not resp:
            resp = MarkovResponse(response=unicode(pair[1]) if pair[1] else None)
        me.responses.append(resp)
    session.commit()

def markov_respond(message):
    sentence = random.choice(message.split(". "))
    current_output = []
    words = sentence.split()
    target = random.choice(words)
    stimuli = MarkovStimulus.query.filter(MarkovStimulus.stimulus.contains(unicode(target)))
    if stimuli.count() < 1:
        stimuli = MarkovStimulus.query
    current_output = random.choice(stimuli.all()).stimulus.split()

    while True:
        responses = MarkovStimulus.get_by(stimulus=unicode(" ".join(current_output[-3:]))).responses
        response = random.choice(responses).response
        if response:
            current_output.append(response)
        else:
            break
    return (" ".join(current_output)).encode('ascii','replace')
 
class Markov(BasePlugin):
    def __init__(self, bot, options):
        self.bot = bot
        self.active = False

    def activate(self, channel=None):
        """
        Called when the plugin is activated.
        """
	self.active = True
        return True

    def deactivate(self, channel=None):
        """
        Called when the plugin is deactivated.
        """
        self.active = False
        return True

    # Event handlers for other users
    def user_join(self, channel, username):
        pass

    def user_part(self, channel, username):
        pass

    def user_kicked(self, channel, username, kicker, message=""):
        pass

    def user_quit(self, username, reason=""):
        pass

    def user_nickchange(self, username, newname):
        pass

    # Event handlers for this bot
    def bot_connect(self):
        pass

    def bot_join(self, channel):
        pass

    def bot_part(self, channel):
        pass

    def bot_kicked(self, channel, kicker="", reason=""):
        pass

    def bot_disconnect(self):
        pass


    # Event handlers for incoming messages
    def msg_channel(self, channel, user, message):
        if self.active:
            if message.startswith(self.bot.nickname + ": "):
                self.bot.pubout(channel, markov_respond(message))
            else:
                markov_store(message)

    def msg_action(self, channel, user, message):
        pass

    def msg_private(self, user, message):
        pass

    def msg_notice(self, user, message):
        pass

    def channel_names(self, channel, nameslist):
        pass

    def timer_tick(self):
        pass
