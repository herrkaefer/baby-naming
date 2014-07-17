#!/usr/bin/env python 
#-*- coding=utf-8 -*-
# Copyright 2014 LIU Yang <gloolar@gmail.com>


import marshal

all_text_files = {	u"国风": 'guofeng.txt', 
					u"大雅": 'guofeng.txt', 
					u"小雅": 'xiaoya.txt',
					u"颂": 'song.txt',
					u"古诗十九首": 'gushi19.txt',
					u"九歌": 'jiuge.txt',
					u"离骚": 'lisao.txt',
					u"苏武李陵诗": 'Su-Li.txt',
					u"天问": 'tianwen.txt',
					u"王维": 'wangwei1.txt',
					u"唐诗三百首": 'tang300.txt',
					u"李商隐诗选": 'Li-Shangyin.txt',
					u"李煜词全集": 'Li-Yu.txt',
					u"苏轼词选": 'Su-Shi.txt',
					u"陶渊明文选": 'taoyuanming.txt',
					u"兰亭集序": 'lanting.txt',
					u"前后赤壁赋": 'chibifu.txt',
					u"滕王阁序": 'tengwang.txt'

				}


def load_char_table_from_text_file(text_file, coding='gbk', context_length=6):
	"""generate char_table from one text file"""

	delimiters = [u'\uff0c', u'\u3002', u'\u3001', u'\u201c', u'\u201d', u'\uff1f', u'\uff01']

	char_table = {}

	if not text_file in all_text_files:
		return char_table

	filename = all_text_files[text_file]
	text = open("data/txt/"+filename).read().decode(coding).splitlines()
	
	for line in text:
		for d in delimiters:
			line = line.replace(d, '*')
		# print line
		line = line.split('*')
		
		for phrase in line:
			phrase_c = to_chinese(phrase)
			# print phrase_c + " -- "

			for index, char in enumerate(phrase_c):

				if is_chinese(char):
					if not char in char_table.keys(): # new character
						char_table[char] = {'context':[], 'rating':0, 'tabu':set()}
					
					# grab context in text
					context_start = max(0, index - context_length)
					context_end = min(len(phrase_c), index + context_length + 1)
					char_table[char]['context'].append({'content':   phrase_c[context_start:context_end],
														'belongsto': text_file })

	return char_table



def process_text_files(text_files=all_text_files.keys(), context_length=6):
	"""Create character tables and save them to disk
	char_table is essentially used to save a graph with vertex the character 
	and directed arc the context relation.
	"""
	
	for file in text_files:
		print "process %s" % file

		char_table = load_char_table_from_text_file(file, 'gbk', context_length)

		if len(char_table) > 0:
			# save char_table to disk
			filename = all_text_files[file]
			ouf = open("data/text/"+filename[:-4]+'.dat', 'wb')
			marshal.dump(file, ouf)
			marshal.dump(char_table, ouf)		
			ouf.close()


def load_original_char_table(selected_files=all_text_files.keys()):
	"""load char_table from disk"""

	char_table = {}

	for file in selected_files:

		if not file in all_text_files:
			print "%s does not exist." % file
			continue

		print "load %s" % file

		filename = all_text_files[file]
		inf = open("data/text/"+filename[:-4]+'.dat', 'rb')
		text_title = marshal.load(inf)
		new_char_table = marshal.load(inf)

		# merge new_char_table to char_table
		for key, value in new_char_table.items():
			if char_table.has_key(key):
				char_table[key]['context'] += value['context']
			else:
				char_table[key] = value

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


if __name__ == '__main__':

	# text_files = [u"test1", u"test2"]

	process_text_files()

	# char_table = load_original_char_table(text_files)

	# print_char_table(char_table)

						

