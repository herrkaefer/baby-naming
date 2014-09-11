#!/usr/bin/env python 
# coding=utf-8
# Copyright 2014 LIU Yang <gloolar@gmail.com>

import marshal
import os

txt_dir = "data/txt/"
dat_dir = "data/text/"


def load_char_table_from_text_file(text_file, context_range=[6,6], encoding='utf-8'):
	"""generate char_table from one text file"""

	# delimiters = [u'\uff0c', u'\u3002', u'\u3001', u'\u201c', u'\u201d', u'\uff1f', u'\uff01']
	delimiters = [u'，', u'。', u'、', u'“', u'”', u'？', u'！']

	char_table = {}
	filename = os.path.join(os.getcwd(), txt_dir, text_file)
	text = open(filename).read().decode(encoding).splitlines()
	
	for line in text:
		for d in delimiters:
			line = line.replace(d, delimiters[0])
		# print line
		line = line.split(delimiters[0])
		
		for phrase in line:
			phrase_c = to_chinese(phrase)
			# print phrase_c + " -- "

			for index, char in enumerate(phrase_c):

				if is_chinese(char):
					if not char in char_table.keys(): # new character
						char_table[char] = {'context':[], 'rating':0, 'tabu':set()}
					
					# grab context in text
					context_start = max(0, index - context_range[0])
					context_end = min(len(phrase_c), index + context_range[1] + 1)
					if (context_end > context_start + 1): # at least two characters
						char_table[char]['context'].append({'content':   phrase_c[context_start:context_end],
														'belongsto': text_file })

	return char_table


def process_text_files(text_files, context_range=[6,6], encoding='utf-8'):
	"""Create character tables and save them to disk
	char_table is essentially used to save a graph with vertex the character 
	and directed arc the context relation.
	"""
	if text_files is None or len(text_files) == 0:
		text_files = [f for f in os.listdir(txt_dir) if os.path.isfile(os.path.join(txt_dir,f)) and f.endswith('.txt')]

	for txtfile in text_files:
		print "process %s" % txtfile

		char_table = load_char_table_from_text_file(txtfile, context_range, encoding)

		if len(char_table) > 0:
			# save char_table to disk
			title = txtfile[:-4]
			datfile = os.path.join(os.getcwd(), dat_dir, title+'.dat')
			ouf = open(datfile, 'wb')
			try:
				marshal.dump(title, ouf)
				marshal.dump(char_table, ouf)
				print "saved in %s" % datfile
			finally:
				ouf.close()


def load_original_char_table(selected_files):
	"""load char_table from disk"""

	if selected_files is None or len(selected_files) == 0:
		selected_files = [os.path.join(os.getcwd(), dat_dir, f) for f in os.listdir(dat_dir) if os.path.isfile(os.path.join(dat_dir,f)) and f.endswith('.dat')]

	char_table = {}

	for datfile in selected_files:
		print "load %s" % datfile
		inf = open(datfile, 'rb')
		try:
			text_title = marshal.load(inf)
			new_char_table = marshal.load(inf)

			# merge new_char_table to char_table
			for key, value in new_char_table.items():
				if char_table.has_key(key):
					char_table[key]['context'] += value['context']
					char_table[key]['rating'] = max(char_table[key]['rating'], value['rating'])
					char_table[key]['tabu'] = char_table[key]['tabu'].union(value['tabu'])
				else:
					char_table[key] = value
		finally:
			inf.close()

	return char_table


def is_chinese(uchar):
	"""judge Chinese character """

	if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
		return True
	else:
		return False


def to_chinese(ustring):
	"""Convert string to include only Chinese characters"""
	
	re_string = ""
	for char in ustring:
		if is_chinese(char):
			re_string += char
			# print char
		# elif char==u"\n":
		# 	print "period!"
	return re_string


def print_char_table(char_table):

	for ch, value in char_table.items():
		print "%s: " % ch
		print "    context: "
		for con in value['context']:
			print "             content: " + con['content']
			print "             belongsto: " + con['belongsto']
		print "    rating: %d" % value['rating']
		print "    tabu: %s" % " ".join(value['tabu'])
	print "total characters: %d" % len(char_table) 


def main():
	
	process_text_files(None, [0,1])

	# char_table = load_original_char_table(None)

	# print_char_table(char_table)


if __name__ == '__main__':
	main()

	

						

