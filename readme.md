# Baby naming

Select a Chinese name for my baby. 

No "八字"! No "五行"! No "运势"! No "星座"!

Features:

- Characters are chosen from (famous) texts. You can add your own texts.
	- current support texts: "国风", "大雅", "小雅", "颂", "古诗十九首", "九歌", "离骚", "苏武李陵诗", "天问", "王维", "唐诗三百首", "李商隐诗选", "李煜词全集", "苏轼词选", "陶渊明文选", "兰亭集序", "前后赤壁赋", "滕王阁序"
- Names are generated and what you need to do is just selecting those you prefer.
- Suggest names based on your preferrd names.
- Random names are also given in the options and a surprise is expected.
- Characters and names you do not want to use could be removed and will not appear again.


# Dependencies

tested under Python 2.7 and [kivy 1.8.0](http://kivy.org/).

# Usage

- main.py is the entry file for kivy
- babyname.py is the module dealing with baby name generation, feedback by choice, setting, user management, etc.
- character_tool.py is the module for preprocessing texts


# todo

- data support
	- google search result of names
	- show character meaning if needed
	- show sources of suggested names
- packaging for iOS and Android