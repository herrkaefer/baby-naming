#!/usr/bin/env python 
#-*- coding=utf-8 -*-
# Copyright 2014 LIU Yang <gloolar@gmail.com>

import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, DictProperty, ListProperty, StringProperty

import copy

from babyname import BabyName


Builder.load_file('namer.kv')


class NamesScreen(Screen):
    char1_1 = ObjectProperty()
    char1_2 = ObjectProperty()
    char2_1 = ObjectProperty()
    char2_2 = ObjectProperty()
    char3_1 = ObjectProperty()
    char3_2 = ObjectProperty()
    char4_1 = ObjectProperty()
    char4_2 = ObjectProperty()
    char5_1 = ObjectProperty()
    char5_2 = ObjectProperty()
    char6_1 = ObjectProperty()
    char6_2 = ObjectProperty()
    char7_1 = ObjectProperty()
    char7_2 = ObjectProperty()
    char8_1 = ObjectProperty()
    char8_2 = ObjectProperty()

    checkbox1 = ObjectProperty()
    checkbox2 = ObjectProperty()
    checkbox3 = ObjectProperty()
    checkbox4 = ObjectProperty()
    checkbox5 = ObjectProperty()
    checkbox6 = ObjectProperty()
    checkbox7 = ObjectProperty()
    checkbox8 = ObjectProperty()

    first_name = StringProperty()

    # setting = DictProperty({'firstname': '', 'selected_texts': []})
    choices = {"name_prefer": [], "name_deny": [], "character_deny": []}



    def initial_babyname(self):
        # self.babyname = BabyName(self.setting['selected_texts'], self.setting['firstname'], min_len=2, max_len=2, duplication='n', num_option=8)
        
        self.babyname = BabyName()
        self.babyname.load_last_session()

        settings_screen.setting = self.babyname.setting
        settings_screen.session = self.babyname.session
        candidates_screen.candidates = [settings_screen.setting['first_name']+name for name in list(self.babyname.candidates)]

        self.first_name = self.babyname.setting['first_name']


    def reset_screen(self):
    	
    	# reset button states
        for i in range(1,9):
            cb = getattr(self, 'checkbox'+str(i))
            cb.disabled = False
            cb.active = False
            for j in range(1,3):
                getattr(self, 'char'+str(i)+"_"+str(j)).state = 'normal'

        # get new options and display
        self.options = self.babyname.generate_options(1)[0]

        for i in range(1,9):
            for j in range(1,3):
                getattr(self, 'char'+str(i)+'_'+str(j)).text = ""

        for index_name, name in enumerate(self.options):
            for index_ch, ch in enumerate(name):
                if index_ch < 2:
                    getattr(self, 'char'+str(index_name+1)+'_'+str(index_ch+1)).text = ch


        # reset choices
        self.choices['name_prefer'] = []
        self.choices['name_deny'] = copy.deepcopy(self.options)
        self.choices['character_deny'] = []


    def next(self):

        self.babyname.adjust_by_choices(self.choices)
        candidates_screen.candidates = [settings_screen.setting['first_name']+name for name in list(self.babyname.candidates)]
        self.reset_screen()
        

    def set_active(self, cb, index):
        # print "options: %d" % len(self.options)
        # print self.options
        if cb.active:
            # print "checkbox %d checked." % index
            name = self.options[index-1]
            if not name in self.choices["name_prefer"]:
                self.choices["name_prefer"].append(name)
            if name in self.choices["name_deny"]:
                self.choices["name_deny"].remove(name)
        else:
            # print "checkbox %d unchecked." % index
            if self.options[index-1] in self.choices["name_prefer"]:
                self.choices["name_prefer"].remove(self.options[index-1])
            if not self.options[index-1] in self.choices['name_deny']:
                self.choices['name_deny'].append(self.options[index-1])
        # print "options: %d" % len(self.options)
        # print self.options


    def toggle_character(self, btn, index1, index2):
        print "button %d-%d is toggled." % (index1, index2)

        if btn.state == 'down':
            # deal with meanings
            print self.options[index1-1][index2-1]
            if not self.options[index1-1][index2-1] in self.choices['character_deny']:
                self.choices['character_deny'].append(self.options[index1-1][index2-1])
            if self.options[index1-1] in self.choices["name_prefer"]:
                self.choices["name_prefer"].remove(self.options[index1-1])
            if not self.options[index1-1] in self.choices["name_deny"]:
                self.choices["name_deny"].append(self.options[index1-1])

            # btn.background_color = [1,0,0,0.5]

            # deal with checkbox
            cb = getattr(self, 'checkbox'+str(index1))
            if cb.active:
                cb.active = False
            if not cb.disabled:
                cb.disabled = True

        else:
            if self.options[index1-1][index2-1] in self.choices['character_deny']:
                self.choices['character_deny'].remove(self.options[index1-1][index2-1])
            cb = getattr(self, 'checkbox'+str(index1))
            if cb.disabled:
                another_btn = getattr(self, 'char'+str(index1)+"_"+str(3-index2))
                if another_btn.state == 'normal':
                    cb.disabled = False


    def toggle_all_characters_in_name(self, index):
        btn1 = getattr(self, "char"+str(index)+"_1")
        btn2 = getattr(self, "char"+str(index)+"_2")

        btn1.state = 'down'
        self.toggle_character(btn1, index, 0)
        btn2.state = 'down'
        self.toggle_character(btn2, index, 1)


    
class SettingsScreen(Screen):
    
    userid_input = ObjectProperty()
    firstname_input = ObjectProperty()
    cb_duplication = ObjectProperty()

    setting = DictProperty({'selected_texts':[], 'first_name':"", 'min_len':1, 'max_len':2, 'duplication':'y', 'num_option':4, 'max_candidate':10})
    session = DictProperty({'userid': "", 'username': ""})

    def on_change_user(self, userid):

        print "user changed to %s" % userid

        if self.userid_input.text != self.session['userid']:
            names_screen.babyname.change_user(self.userid_input.text)
            self.setting = names_screen.babyname.setting
            self.session = names_screen.babyname.session

            candidates_screen.candidates = [settings_screen.setting['first_name']+name for name in list(names_screen.babyname.candidates)]
            names_screen.first_name = self.setting['first_name']

            settings_screen.reset_screen()
            names_screen.reset_screen()


    def change_setting(self):
        """on OK button pressed"""

        print "change_setting called."

        setting_changed = False
        
        # check all settings except userid
        if self.firstname_input.text != self.setting['first_name']:
            setting_changed = True

            names_screen.babyname.change_setting('first_name', self.firstname_input.text)
            self.setting['first_name'] = names_screen.babyname.setting['first_name']
            names_screen.first_name = self.setting['first_name']

        if self.cb_duplication.active:
            dup = 'y'
        else:
            dup = 'n'
        if dup != self.setting['duplication']:
            print "here!"
            setting_changed = True
            names_screen.babyname.change_setting('duplication', dup)
            self.setting['duplication'] = names_screen.babyname.setting['duplication']


        if setting_changed:
            names_screen.reset_screen()


    def reset_screen(self):
        self.firstname_input.text = self.setting['first_name']
        self.cb_duplication.active = True if self.setting['duplication'] else False


class CandidatesScreen(Screen):

    candidates = ListProperty([]*14)

    def remove_candidate(self, name):
        given_names = [name.lstrip(settings_screen.setting['first_name'])]
        names_screen.babyname.remove_candidates(given_names)
        self.candidates = [settings_screen.setting['first_name']+name for name in list(names_screen.babyname.candidates)]

    def add_candidate(self, name):
        given_names = [name.lstrip(settings_screen.setting['first_name'])]
        names_screen.babyname.add_candidates(given_names)
        self.candidates = [settings_screen.setting['first_name']+name for name in list(names_screen.babyname.candidates)]
    



# Create the screen manager
sm = ScreenManager()
names_screen = NamesScreen(name='names')
settings_screen = SettingsScreen(name='settings')
candidates_screen = CandidatesScreen(name='candidates')

sm.add_widget(settings_screen)
sm.add_widget(names_screen)
sm.add_widget(candidates_screen)


class NamerApp(App):


    def build(self):
        self.icon = 'babynaming.ico'
        names_screen.initial_babyname()
        names_screen.reset_screen()
        settings_screen.reset_screen()

        return sm

    def on_start(self):
        pass

    def on_stop(self):
        names_screen.babyname.quit()
        print "Bye."


if __name__ == '__main__':
    NamerApp().run()