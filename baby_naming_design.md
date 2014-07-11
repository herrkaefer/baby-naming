# 不同字符编码及汉字数量

## GB2312-80

1981年5月1日，中华人民共和国国家标准总局发布《信息交换用汉字编码字符集——基本集》汉字库编码，简称为《GB2312—80》。其中“GB”为“国家标准”的汉语拼音缩写。1981年10月1日开始实施。

《GB2312—80》是汉字库的编码，收录了简化汉字字符6763个，特殊字符682个（其中：运算符、序号、数字、拉丁字母、日文假名、希腊字母、俄文字母、汉语拼音符号、汉语注音字母），共7445个图形字符。 

汉字库分为87区、每区94位：第16区～55区编排有3755个常用汉字，依汉语拼音字母/笔形顺序排列，称为一级字库；第56区～87区编排了3008个次常用汉字，依偏旁部首/笔画顺序排列，称为二级字库。字音是以1963年普通话审音委员会出版的《普通话异读词三次审音总表初稿》为准。字形是以1964年中华人民共和国文化部、中国文字改革委员会公布的《印刷通用汉字字形表》为准。

## GB-5

《GB—5》字符集是一个繁体汉字库，俗称为“大五码”。汉字库收录常用汉字5410个；次常用汉字7659个，共收录了汉字字符13060个。再加上特殊字符408个。一共收录了13468个汉字字符和特殊字符。 

## GBK

1995年12月1日中华人民共和国全国信息技术标准化委员会发布实施《汉字内码扩展规范》，即为“国家标准扩展字符集（GBK）”其中“GB”为“国家标准”的汉语拼音缩写，“K”为“扩展”的汉语拼音缩写。英文名称为“Chinese Internal Code Specification”。 

GBK收录了汉字（包括部首和构件）21003个，特殊符号883个。共21886个汉字和图形符号。


# 字库选择

名字包含汉字个数为1个或两个，设字库中汉字数为N，则总共可选的名字数量：$M=N+N*N$

考虑上面标准字库，则：

- GB2312: N=6763,  M=45744932

- GB-5:   N=13060, M=170576660

- GBK:    N=21003, M=441147012

即使使用最小字库，用穷举选择的方法也是不合适的。假设一天可以做500次选择，3个月的时间一共可以做45000次选择，意味着字库大小最多为212个，非常小。解决思路：

1. 先选字，再选名。用预选字库的方法，先选择汉字子集，排除掉不可能考虑的汉字，再进行组合选择
2. 不必遍历，随时终止。不要求全部遍历，可在任意时刻自行决定终止，在终止后都可以根据选择过程给出名字排序
3. 边选名，边选字。在选择过程中可以直接对字进行排除，则再不出现。
4. 建立字之间的相似关系，选择过程中，根据肯定历史，优先提供相似度高的字。相似性建立：一般性的度量并不容易，可以在建立字库时保留在原文中的一定范围的上下文关系，即某字前后几个字的相邻关系，可以认为这些字是相似的，这些组合是有意义的，选中某些字之后，可以接着给出这些组合来。

# 初步想法

- 取文集作为字库来源(如[新语丝文库](http://www.xys.org/library.html))，可以加入名字常用字字集
- 提取汉字建立字库，同时对每个字建立索引关系，保留其来源信息(文集、篇章等)，及在原文中的上下文关系，以作组合之用
- 每次给出候选组合2-4个，要求至少要否定一半，否定后的组合不再出现
- 字操作：在选择时可以直接排除字，排除掉的字再不出现。
- 肯定的组合会对其来源文集、篇章、上下文关系加分，提高后面推荐概率。否定的组合会相应减分。
- 因字库很大，及时加分，如果完全使用随机选择，选中的概率还是很小，因此应该分两步。把每次给出的候选组合分成几类，分别采用不同的策略给出：
	- 之前肯定过的名字
	- 基于之前肯定的推荐
	- 未出现过的新字
- 用户开始需要输入姓、字数限定（一个、两个、一个或两个），文集选择
- 任意时刻可以查看最佳几个名字的选择排名，可以继续选择下去
- 根据比较给出最佳名字的算法需要仔细考虑
- 选择时提供的辅助数据：字意（说文解字？），来源（给出上下文），google搜索结果前两页
- 大字，楷体


# 技术方案

- Web App: Flask + Bootstrap + free hosting
	- 交互设计：swipe or button
	- swipe refs
		- [Add Finger-Swipe Support to Webpages](http://padilicious.com/code/touchevents/)

- 字图模型
	- 字集从文本得到
	- 本质上，这里需要构建并存储一个图(V, A)，顶点$V_i$为字，边$A(i,j)$表示$V_i$到$V_j$存在context关系.
	context关系用来表示字之间的组合关系，用在文本中的相邻关系构造。（进一步的，应该考虑语义组合关系，但实现就比较复杂了。）
	- name (given name)是一个顶点序列，也可看做是一组边的序列(边数可能是0)
	- 基于文本相邻关系构造context：对字$V_i$，以$V_i$为中心，考虑一个上下文邻域范围$S_i$=[-context_length, +context_length]（但如果自然语句范围更小，则被自然语句截断）。对任意$j,k\in S_i$建立完全图，即任意两字之间都存在context。由于汉语中经常存在动词后置等现象，这里不局限于原文顺序，反向也建立连接。$A(i,j)$的值按照在文本中相邻的距离确定，即相邻的两个字为1，相隔一字为2，自己到自己为0（可以叠字）
	- 目前的存储方案：以每个char为key建立一个dict，在value里存储上下文邻域片断context['content']（即在图中和和自己相邻的所有字），边的值不显式存储，用的时候可以根据邻域片断很方便地计算得到
	- 字图模型和文本是相对稳定对应关系（当context_length固定时），因此可以事先建立好并保存，代替存储文本。

- Rating algorithm
	- 考虑：还未想到满意的算法, Elo rating system并不完全合适。
		- 负者的rating其实没有意义，因为不应再考虑，关键是对于胜者的rating
		- ELO算法和参与比赛的次数相关，这会造成不合理，对选名字，并不是获胜越多就越好
		- 这里可能应该采取的策略是：**负者淘汰，胜者保留**。针对选择结果，
		1) name pool中只保留胜者
		2) 修改字图模型：对删除的字或单字name，顶点rating设为-1，表示顶点已删除。对name负者，把对应的边放到每个顶点的禁忌列表中；对name胜者，如果在图中不存在边，则建立一条边（这个似乎并不必要，除非有办法把两个字的邻域联系起来）。 

	- rating包括character和name. 初值为0.
	- 调整算法：
		- 设一次参与比较的有k个名字，初始rating为$R_i(i=1,\dots,k)$. 
		- 比较结果可以是：某些character被否定(所在的name也直接被否定)，某些name被否定(但包含的字不被否定)，某些name被肯定.
		- 对character的rating调整规则：如果被否定，rating设为-1 (表示被删除).
		- 对name的rating调整规则为：设胜者集合W, 负者集合L, 设$$R_w = \underset{i\in W}{max}\{R_i\} $$ $$R_l = \underset{i\in L}{max}\{R_i\}$$
		则负者的rating不变；对胜者，若$R_w \le R_l$，则调整所有胜者的rating为$R_w+\Delta R$; 否则调整所有胜者的rating为$R_w$. $\Delta R$可设为0.01. (所有胜者的rating拉平，且要高于所有负者的rating)
	- name pool: 存储一定数量的name, 按rating降序排列, 最差的被淘汰(rating直接设为-1)


- Candidates generation
	- 推荐算法
		- name pool中的name的相似name
	- 全新name
		- rating >= 0随机生成即可

- Ranking
	- 对参与过选择的name，按rating排序（可能有平分）

- Associated Data
	- meaning: 字的释义
	- search_result：搜索结果
	- pronouncing: 发音
		- [Forvo API](http://api.forvo.com/): 500 request/day. Forvo API KEY: 6eca6fc7c8041970db613af5dfe710b7


# Development

## todos
- [对中文支持不好，仍用label]candidates_screen改用ListView试下
- 扩充字集，提供选择
- OSX packaging (pyinstaller)
- [done]在candidates_screen中直接去除、增加候选
- 推荐的name显示出处，上下文
- bug: checkbox选中self.options中会去掉该字！

## python for iOS

- [PyObjC ](http://www.saurik.com/id/5)
- [Can I write native iPhone apps using Python](http://stackoverflow.com/questions/43315/can-i-write-native-iphone-apps-using-python)
- cross-platform: [kivy](http://kivy.org/#home)
- [Build unsigned .ipa without Developer Account on Xcode 5](http://initcodes.blogspot.hk/2014/01/build-unsigned-ipa-without-developer.html), [video](https://www.youtube.com/watch?v=01eGo6YSPVc)


# References
- [Elo rating system](http://en.wikipedia.org/wiki/Elo_rating_system)与参加比赛次数有关，并不合适。提到[Baby name game](http://baby-namer.meteor.com/launch)用Elo rating做英文名字选择游戏。

