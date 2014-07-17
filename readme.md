# Baby naming

The app is developed for the purpose of naming my forthcoming baby ^_^ Strongly wish it works!

# Features

- No "八字"! No "五行"! No "运势"! No "星座"! No such shit!
- Characters are chosen from (famous) texts. You can add your own texts.
	- current supported texts: "国风", "大雅", "小雅", "颂", "古诗十九首", "九歌", "离骚", "苏武李陵诗", "天问", "王维", "唐诗三百首", "李商隐诗选", "李煜词全集", "苏轼词选", "陶渊明文选", "兰亭集序", "前后赤壁赋", "滕王阁序"
- Names are generated and what you need to do is just selecting those you prefer.
- Suggest names based on your preferrd names.
- Random names are also given in the options and a surprise is expected.
- Characters and names you do not want to use could be removed and will not appear again.


# Dependencies

tested under Python 2.7 and [kivy 1.8.0](http://kivy.org/).

# Usage

- main.py is the entry file for kivy.

on mac:

	# switch to the app directory
	kivy main.py

on Windows:

	# run kivy.bat
	# switch to the app directory
	python main.py

- babyname.py is the module dealing with baby name generation, feedback by choice, setting, user management, etc.
- character_tool.py is the module for preprocessing texts

".txt" texts should be processed before using by babyname.py. To add a text:

- put txt file in data/txt and encoded with "gbk" or "gb2312".
- in "character_tool.py", modify variable all_text_files to add your text.
- run "python character_tool.py"
- in "babyname.py", modify default_setting['selected_texts'] in class BabyName to include the texts you want to use.

# todo

- add data support
	- google search result of names
	- show character meaning if needed
	- show sources of suggested names
- UI improvement
- packaging for iOS and Android