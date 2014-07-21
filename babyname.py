#!/usr/bin/env python 
#-*- coding=utf-8 -*-
# Copyright 2014 LIU Yang <gloolar@gmail.com>

import sys
import random
import re
import marshal
import os.path

import character_tool

# reload(character_tool)
reload(sys)
sys.setdefaultencoding("utf-8")


class BabyName(object):

	setting = { 'selected_texts': [], 
				'first_name':     "",
				'min_len':        1,
				'max_len':        2,
				'duplication':    'y',
				'num_option':     4,
				'max_candidate':  10
			  }

	session = {'userid':"", 'username': ""}
	candidates = set()
	char_table = {}

	default_session = {'userid': "guest", 'username': 'guest'}
	
	# default setting for new user
	default_setting = {'selected_texts':character_tool.all_text_files.keys(), 'first_name':u"刘", 'min_len':2, 'max_len':2, 'duplication':'y', 'num_option':8, 'max_candidate':10}
	default_setting['selected_texts'] = [u"王维", u"唐诗三百首", u"李商隐诗选", u"李煜词全集", u"苏轼词选", u"陶渊明文选", u"兰亭集序", u"前后赤壁赋", u"滕王阁序"]
	

	def __init__(self):
		pass


	def load_default_session(self):
		self.setting = self.default_setting
		self.session = self.default_session
		self.candidates.clear()
		self.load_char_table(self.setting['selected_texts'])


	def load_last_session(self):
		ls_file = os.path.join(os.getcwd(), "data/session/ls")
		if os.path.isfile(ls_file):
			inf = open(ls_file, 'rb')
			try:
				last_userid = marshal.load(inf)
				if not self.load_session(last_userid):
					print "user %s load failed. load default session." % last_userid
					self.load_default_session()
			finally:
				inf.close()
		else:
			print "lsfile does not exist. load default session."
			self.load_default_session()


	def load_session(self, userid):
		user_file = os.path.join(os.getcwd(), "data/session/", userid)

		if os.path.isfile(user_file):
			inf = open(user_file, 'rb')
			try:
				self.session = marshal.load(inf)
				self.setting = marshal.load(inf)
				self.candidates = marshal.load(inf)
				self.char_table = marshal.load(inf)
			finally:
				inf.close()
			return True

		else:
			return False # no session data exists for userid


	def save_session(self):
		user_file = os.path.join(os.getcwd(), "data/session/", self.session['userid'])
		ouf = open(user_file, 'wb')
		try:
			marshal.dump(self.session, ouf)
			marshal.dump(self.setting, ouf)
			marshal.dump(self.candidates, ouf)
			marshal.dump(self.char_table, ouf)
		finally:
			ouf.close()

		# save current userid separately
		ls_file = os.path.join(os.getcwd(), "data/session/ls")
		ouf = open(ls_file, 'wb')
		try:
			marshal.dump(self.session['userid'], ouf)
		finally:
			ouf.close()

		# print "session saved for user %s" % self.session['userid']


	def quit(self):
		self.save_session()


	def create_new_user(self, userid, username=None):
		self.setting = self.default_setting
		self.session['userid'] = userid
		if username == None:
			self.session['username'] = userid
		else:
			self.session['username'] = username
		self.candidates.clear()
		self.load_char_table(self.setting['selected_texts'])
		print "new user created for %s" % self.session['userid']


	def change_user(self, userid):
		if userid != self.session['userid']:
			self.save_session()
			if not self.load_session(userid):
				self.create_new_user(userid)
				self.save_session()


	def reset_user(self, userid=None):
		if userid == None:
			userid = self.session['userid']
		self.create_new_user(userid)
		self.save_session()


	def delete_user(self, userid=None):
		if userid == None:
			userid = self.session['userid']
		if userid != 'guest':
			self.change_user('guest')
			user_file = "data/session/" + userid
			if os.path.isfile(user_file):
				try:
					os.remove(user_file)
				except OSError:
					pass


	def change_setting(self, key, value):
		if key in self.setting.keys():
			self.setting[key] = value


	def load_char_table(self, selected_texts):
		"""Load char_table from pre-stored char_tables"""
		self.char_table = character_tool.load_original_char_table(selected_texts)


	def get_available_texts(self):
		return character_tool.all_text_files.keys()


	def generate_options(self, num=1):
		"""Generate num group of options"""
		
		options = []
		
		for i in range(num):
			group = []

			# past winners
			if len(self.candidates) >= self.setting['max_candidate']:
				num_exp = min(2, self.setting['num_option']/3)
				past_winners = self.generate_past_winners(num_exp)
				group.extend(past_winners)
			else:
				num_exp = 0
				past_winners = []

			print "\npast winners: %s" % " ".join(past_winners)

			# suggestions based on self.candidates
			num_exp = (self.setting['num_option'] - len(group)) / 2
			suggested = self.generate_suggestions(num_exp)
			group.extend(suggested)

			print "suggested: %s" % " ".join(suggested)

			# random suggestions
			num_exp = (self.setting['num_option'] - len(group)) / 2
			random_suggested = self.generate_random_suggestions(num_exp)
			group.extend(random_suggested)

			print "random suggested: %s" % " ".join(random_suggested)

			# new faces (completely random combinations)
			num_exp = self.setting['num_option'] - len(group)
			new_faces = self.generate_new_faces(num_exp)
			group.extend(new_faces)

			print "new faces: %s" % " ".join(new_faces)

			random.shuffle(group)
			
			# group = [self.setting['first_name']+name for name in group]

			options.append(group)

		return options


	def generate_past_winners(self, num_exp=1):
		
		d = list(self.candidates)
		random.shuffle(d)
		num = min(num_exp, len(self.candidates))
		return d[:num]


	def is_feasible(self, first_ch, second_ch):
		"""judge if pair (first_ch, second_ch) is feasible """

		if self.char_table[first_ch]['rating']  < 0 or \
		   self.char_table[second_ch]['rating'] < 0 or \
		   (self.setting['duplication']=='n' and first_ch == second_ch) or \
		   second_ch in self.char_table[first_ch]['tabu']:
			return False
		else:
			return True


	def roulette_wheel_select(self, ch, position="both"):
		"""Use roulette wheel to select a character related to ch, 
			and construct a character pair. return [] if failed.
			ch: the given ch
			position: specify the position of ch in the returned pair
			"both":   ch as the first or second character
			"first":  ch as the first character
			"second": ch as the second character
		"""

		if not ch in self.char_table.keys():
			return []
			
		context = random.choice(self.char_table[ch]['context'])
		content = context['content']
		# belongsto = context['belongsto']

		index_ch = content.index(ch)
		radius = max(index_ch, len(content)-1-index_ch)
		if radius <= 0:
			return []
			
		distance = range(radius)
		
		fitness = [1.0/(d+len(distance)+1) for d in distance]
		# adjust the fitness of ch itself
		if self.setting['duplication'] == 'n':
			fitness[0] = 0
		else:
			fitness[0] = fitness[-1]*0.2

		# roulette wheel selection
		sum_fitness = sum(fitness)
		pick = random.uniform(0, sum_fitness)
		current = 0
		for index, d in enumerate(distance):
			current += fitness[index]
			if current > pick:
				break

		# print "selected: %d, %d" % (index, d)

		left = random.randint(0,1) # going left or right from ch?
		if left == 0 and (index_ch-d) >= 0:
			new_ch = content[index_ch-d]
		elif index_ch+d < len(content):
			new_ch = content[index_ch+d]
		else:
			new_ch = ''

		if len(new_ch) > 0:
			if position == "both":
				pair = [ch, new_ch]
				random.shuffle(pair)
				if not self.is_feasible(pair[0], pair[1]):
					pair.reverse()
					if not self.is_feasible(pair[0], pair[1]):
						pair = []

			elif position == "first":
				pair = [ch, new_ch]
				if not self.is_feasible(pair[0], pair[1]):
					pair = []

			else:
				pair = [new_ch, ch]
				if not self.is_feasible(pair[0], pair[1]):
					pair = []
		else:
			pair = []
        
		# return {'pair': pair, 'belongsto': belongsto}
		return pair


	def generate_suggestions(self, num_exp=1):
		"""Suggest names based on candidates"""

		given_names = []

		# choose some different characters in names in self.candidates
		ch_set = [ch for name in self.candidates for ch in name]
		random.shuffle(ch_set)
		ch_set = set(ch_set)
		num = min(num_exp, len(ch_set))
		chs = list(ch_set)[:num]

		# if given name length is fixed to 1
		if self.setting['min_len'] == 1 and self.setting['max_len'] == 1:
			return chs

		pos_chs = 0

		for name_cnt in range(num):

			given_name = ""

			if (self.setting['min_len'] == self.setting['max_len']):
				len_name = self.setting['min_len']
			else:
				len_name = random.randint(self.setting['min_len'], self.setting['max_len'])

			if len_name == 1: # one character name
				given_names.append(chs[pos_chs])
				pos_chs += 1
				continue

			given_name = ""

			# first two characters
			pair = self.roulette_wheel_select(chs[pos_chs], position="both")
			if pair == []:
				pos_chs += 1
				continue
			given_name += pair[0]
			given_name += pair[1]
			lastch = pair[1]

			# if len_name > 2 (seldom in Chinese names)
			for i in range(len_name-2):
				pair = self.roulette_wheel_select(lastch, position="first")
				if pair == []:
					break
				else:
					given_name += pair[1]
					lastch = pair[1]


			if len(given_name) == len_name:
				given_names.append(given_name)

			pos_chs += 1

		return given_names


	def generate_random_suggestions(self, num=1):
		"""Generate random suggestions (characters are somehow related)"""
		
		given_names = []

		for i in range(num):

			given_name = ""
			if (self.setting['min_len'] == self.setting['max_len']):
				len_name = self.setting['min_len']
			else:
				len_name = random.randint(self.setting['min_len'], self.setting['max_len'])

			# random select the first character
			ch = random.choice(self.char_table.keys())

			# first pair
			pair = self.roulette_wheel_select(ch, position="both")
			if pair == []:
				continue
			given_name += pair[0]
			given_name += pair[1]
			lastch = pair[1]

			# if len_name > 2 (seldom in Chinese names)
			for i in range(len_name-2):
				pair = self.roulette_wheel_select(lastch, position="first")
				if pair == []:
					break
				else:
					given_name += pair[1]
					lastch = pair[1]


			if len(given_name) == len_name:
				given_names.append(given_name)

		return given_names


	def generate_new_faces(self, num=1):
		"""Generate new name randomly"""

		given_names = []

		for i in range(num):

			given_name = ""
			if (self.setting['min_len'] == self.setting['max_len']):
				len_name = self.setting['min_len']
			else:
				len_name = random.randint(self.setting['min_len'], self.setting['max_len'])

			loop_cnt = 0
			while len(given_name) < len_name and loop_cnt < 100:
				loop_cnt += 1

				if len(given_name) > 0:
					feasible_chs = [ch for ch in self.char_table.keys() if self.is_feasible(given_name[-1], ch)]
				else:
					feasible_chs = [ch for ch in self.char_table.keys() if self.char_table[ch]['rating'] >= 0]

				if len(feasible_chs) > 0:
					ch = random.choice(feasible_chs)
					given_name += ch
				elif len(given_name) > 0:
					given_name = given_name[:-1] # remove the last character to set another one
				else:
					break
			
			if len(given_name) == len_name:
				given_names.append(given_name)
		
		return given_names


	def add_candidates(self, names):
		"""directly (manually) add candidates to self.candidates"""

		chinese_names = [character_tool.to_chinese(name) for name in names]

		for name in chinese_names:
			self.candidates.add(name)
			# modify char_table accordingly
			for index, ch in enumerate(name):
				if self.char_table[ch]['rating'] < 0:
					self.char_table[ch]['rating'] = 0
				if index > 0 and ch in self.char_table[name[index-1]]['tabu']:
						self.char_table[name[index-1]]['tabu'].remove(ch)


	def remove_candidates(self, names):
		"""directly (manually) remove candidates from self.candidates"""

		for name in names:
			for index, ch in enumerate(name[:-1]):
				self.char_table[ch]['tabu'].add(name[index+1])
		self.candidates -= set(names)


	def add_characters(self, chars):
		"""directly (mannually) add characters (or remove them from tabu list)"""
		for ch in chars:
			if ch in self.char_table.keys():
				if self.char_table[ch]['rating'] < 0:
					self.char_table[ch]['rating'] = 0
			else: # character not in char_table
				self.char_table[ch] = {'context':[], 'rating':0, 'tabu':set()}


	def remove_characters(self, chars):
		"""directly (mannually) taboo characters"""
		for ch in chars:
			if ch in self.char_table.keys():
				if self.char_table[ch]['rating'] >= 0:
					self.char_table[ch]['rating'] = -1
				# remove candidates including ch
				candidates_include_ch = [name for name in self.candidates if ch in name]
				self.remove_candidates(candidates_include_ch)
			else:
				self.char_table[ch] = {'context':[], 'rating':-1, 'tabu':set()}


	def get_tabu_characters(self):
		"""get list of tabooed characters"""
		return [ch for ch in self.char_table.keys() if self.char_table[ch]['rating'] < 0] 


	def adjust_by_choices(self, choices):
		"""Adjust model based on selection result
		choices := {'name_prefer': [], 'name_deny': [], 'character_deny': []}
		name is given name
		"""

		# denied characters
		denied_characters = choices['character_deny']
		denied_characters.extend([name for name in choices['name_deny'] if len(name) == 1])

		for ch in denied_characters:
			self.char_table[ch]['rating'] = -1

		# denied names with length > 1
		for name in choices['name_deny']:
			for index, ch in enumerate(name[:-1]):
				self.char_table[ch]['tabu'].add(name[index+1])

		self.candidates -= set(choices['name_deny'])

		# preferred names
		for name in choices['name_prefer']:
			self.candidates.add(name)

		self.print_candidates()
		# candidates_include_denied_char = [name for name in self.candidates if name in ]


	def print_char_table(self):
		character_tool.print_char_table(self.char_table)


	def print_candidates(self):
		print "\nCurrent candidates: %s" % " ".join(self.candidates)


def test():
	
	babyname = BabyName()
	babyname.load_last_session()
	print "load last user " + babyname.session['userid']

	new_userid = 'free'
	if not babyname.load_session(new_userid):
		print "load session for %s failed." % new_userid
		babyname.create_new_user(new_userid)
		print "create new user for " + babyname.session['userid']

	print u"\nHi, %s, 请输入喜欢的名字前的序号, 并按回车进到下一步. 结束请输入quit.\n" % babyname.session['userid']

	while 1:

		options = babyname.generate_options()
		choices = {"name_prefer": [], "name_deny": [], "character_deny": []}
		
		print u"\n请选择："
		for index, name in enumerate(options[0]):
			print "[%d]: %s" % (index, name)

		input = raw_input(u"You prefer: ")
		if "quit" in input:
			break

		input = input.replace(" ", "")
		# print input
		sels = [int(n) for n in input if int(n) >= 0 and int(n) < len(options[0])]
		non_sels = [n for n in range(len(options[0])) if not n in sels]
		choices["name_prefer"] = [options[0][s] for s in sels if 0 <= s and s < len(options[0])]
		choices["name_deny"] = [options[0][s] for s in non_sels]
		choices['character_deny'] = []

		babyname.adjust_by_choices(choices)

		# babyname.print_candidates()

	babyname.quit()




if __name__ == '__main__':
	test()

	


	