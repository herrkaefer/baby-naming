#!/usr/bin/env python 
# coding=utf-8
# Copyright 2014 LIU Yang <gloolar@gmail.com>

import marshal
import os

all_text_files = {	u"诗经-国风": 'guofeng.txt', 
					u"诗经-大雅": 'daya.txt', 
					u"诗经-小雅": 'xiaoya.txt',
					u"诗经-颂": 'song.txt',
					u"古诗十九首": 'gushi19.txt',
					u"九歌": 'jiuge.txt',
					u"离骚": 'lisao.txt',
					u"苏武李陵诗": 'suli.txt',
					u"天问": 'tianwen.txt',
					u"王维诗": 'wangwei.txt',
					u"唐诗三百首": 'tang300.txt',
					u"李商隐诗选": 'lishangyin.txt',
					u"李煜词全集": 'liyu.txt',
					u"苏轼词选": 'sushici.txt',
					u"苏轼文选": 'sushiwen.txt',
					u"陶渊明文选": 'taoyuanmingwen.txt',
					u"陶渊明诗全集": 'taoyuanmingshi.txt',
					u"兰亭集序": 'lanting.txt',
					u"滕王阁序": 'tengwang.txt'
				}


def load_char_table_from_text_file(text_file, encoding='utf-8', context_length=6):
	"""generate char_table from one text file"""

	# delimiters = [u'\uff0c', u'\u3002', u'\u3001', u'\u201c', u'\u201d', u'\uff1f', u'\uff01']
	delimiters = [u'，', u'。', u'、', u'“', u'”', u'？', u'！']

	char_table = {}

	if all_text_files.get(text_file) is None:
		return {}

	filename = os.path.join(os.getcwd(), "data/txt/", all_text_files[text_file])

	if os.path.isfile(filename):

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
						context_start = max(0, index - context_length)
						context_end = min(len(phrase_c), index + context_length + 1)
						char_table[char]['context'].append({'content':   phrase_c[context_start:context_end],
															'belongsto': text_file })

	return char_table



def process_text_files(text_files=all_text_files.keys(), context_length=6, encoding='utf-8'):
	"""Create character tables and save them to disk
	char_table is essentially used to save a graph with vertex the character 
	and directed arc the context relation.
	"""
	
	for file in text_files:
		print "process %s" % file

		char_table = load_char_table_from_text_file(file, encoding, context_length)

		if len(char_table) > 0:
			# save char_table to disk
			txtfile = all_text_files[file]
			datfile = os.path.join(os.getcwd(), "data/text/", txtfile[:-4]+'.dat')
			ouf = open(datfile, 'wb')
			try:
				marshal.dump(file, ouf)
				marshal.dump(char_table, ouf)
			finally:
				ouf.close()


def load_original_char_table(selected_files=all_text_files.keys()):
	"""load char_table from disk"""

	char_table = {}

	for file in selected_files:

		if all_text_files.get(file) is None:
			print "%s is not supported yet." % file
			continue

		print "load %s" % file

		txtfile = all_text_files[file]
		datfile = os.path.join(os.getcwd(), "data/text/", txtfile[:-4]+'.dat')
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
	
	process_text_files()

	# text_files = [u"苏轼文选", u"苏轼词选"]
	# char_table = load_original_char_table(text_files)
	# print_char_table(char_table)


if __name__ == '__main__':
	main()

	

						

