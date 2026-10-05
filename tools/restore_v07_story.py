"""One-off v0.7 checkpoint restoration. Removed by its workflow after a successful commit."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORY_PATH = ROOT / "game/data/story.json"

ADDITIONS = {'p00_entry': [('p00_entry_l009', 'n', '雨势比预报里更大。我贴着墙走到旧站侧门，门边临时支着一张塑料桌，桌上压着今晚最后一批领取登记表。'),
               ('p00_entry_l010', 'n', '值班的人核对了我的短信，说柜里的东西下午已经搬完，纸箱在出口内侧，十点前签字就行。'),
               ('p00_entry_l011', 'p', '还来得及。'),
               ('p00_entry_l012', 'n', '我把这句话当成对取物流程的确认。直到那一刻，我都没有问今晚还有谁会来，也没有翻通讯录找三年前的名字。'),
               ('p00_entry_l013', 'n', '手机上酒店发来入住提醒，明早的车票也安静躺在行程里。这个晚上原本只有三个动词：取走、入住、离开。'),
               ('p00_entry_l014', 'n', '旧站却比记忆里小了很多。封起来的售票口、拆下一半的线路图、墙上新贴的移交说明，把过去压缩成几块还没来得及搬走的牌子。'),
               ('p00_entry_l015', 'n', '我站在檐下甩了甩袖口的水，想起那箱书里还有展览留下的相框和留言册。那封信只是其中一件我早就知道存在、却一直没有处理的东西。'),
               ('p00_entry_l016', 'n', '如果今晚碰不到任何熟人，我也会把箱子带走。想到这里，我反而松了口气，至少不用给这次回来编一个更浪漫的理由。'),
               ('p00_entry_l017', 'n', '侧门后的灯一盏接一盏亮着。我沿着临时指示箭头往站台方向走，鞋底在湿地上留下很浅的印子。'),
               ('p00_entry_l018', 'n', '箭头最后指向熟悉的雨棚。我抬头时，先看见长椅旁放着一个纸袋，然后才听见有人叫住我。'),
               ('p00_entry_l019', 'n', '站台深处传来纸箱拖动的声音。我加快了一点脚步，却仍只是为了赶上领取时间。'),
               ('p00_entry_l020', 'n', '直到熟悉的声音穿过雨幕，这趟返城才多出一个完全不在行程里的名字。')],
 's01_arrival': [('s01_arrival_l013', 'n', '她说完“三年”以后，目光先落到我手里的空布袋，又落到出口方向，像是在确认我确实是来办事的。'),
                 ('s01_arrival_l014', 'p', '你等很久了吗？'),
                 ('s01_arrival_l015', 'h', '没有。我那边已经登记完了。雨太大，想等小一点再走。'),
                 ('s01_arrival_l016', 'n', '这回答替我们省掉了一个误会。她不是在这里等我，我也不是按约定赶来；只是同一场雨把两个办完或没办完事情的人留在了旧站。'),
                 ('s01_arrival_l017', 'n', '她脚边的纸袋比照片里那只旧帆布包新得多，边缘贴着书店的封箱标签。我注意到以后，很快把视线收了回来。'),
                 ('s01_arrival_l018', 'p', '我收到的是清库通知。下午才看到。'),
                 ('s01_arrival_l019', 'h', '我也是。店里那个旧号码早停用了，他们绕了一圈才找到现在的联系方式。'),
                 ('s01_arrival_l020', 'n', '“现在的联系方式”几个字很轻，却把三年从一句概括变成了确实发生过的时间。'),
                 ('s01_arrival_l021', 'n', '我想问她换了什么号码、搬去了哪里，又觉得这些问题不能一次全部挤出来。于是先把滴水的布袋从手腕上解下来。'),
                 ('s01_arrival_l022', 'p', '先找个不漏雨的地方吧。'),
                 ('s01_arrival_l023', 'h', '右边那块干。左边的地砖会晃。'),
                 ('s01_arrival_l024', 'n', '她还记得这里哪块砖会晃。我也记得。我们谁都没有拿这件小事证明什么，只一起往右边挪了一步。'),
                 ('s01_arrival_l025', 'n', '她没有问我为什么三年没回来。我也没有抢着用一句“工作忙”堵住这个问题。'),
                 ('s01_arrival_l026', 'n', '真正需要说的事显然不会因为站在同一块雨棚下就自动变得容易。')],
 's01_platform': [('s01_platform_l011', 'n', '墙上的旧时刻表还停在停运前最后一个月。几处班次被红笔圈掉，下面补了一张“设备移交中，请勿进入”的白纸。'),
                  ('s01_platform_l012', 'h', '以前你每次都从那边翻过去。'),
                  ('s01_platform_l013', 'p', '现在看起来会直接被请出去。'),
                  ('s01_platform_l014', 'h', '说明你终于学会看告示了。'),
                  ('s01_platform_l015', 'n', '她的语气和从前差不多，距离却没有因此消失。我能接住这句玩笑，也知道不能顺势假装我们从未断过联系。'),
                  ('s01_platform_l016', 'n', '出口有人推着最后一车纸箱经过。胶轮压过接缝，工作人员念了几个柜号，其中一个正是我的。'),
                  ('s01_platform_l017', 'p', '看来真搬出来了。'),
                  ('s01_platform_l018', 'h', '先别急。还要签字。'),
                  ('s01_platform_l019', 'n', '我点头，把手机上的通知重新打开。她没有替我带路，只在我找不到临时登记点时朝柱子后面指了一下。'),
                  ('s01_platform_l020', 'n', '这种分寸让我安心了一点。熟悉还在，但没有自动替代这三年的空白。'),
                  ('s01_platform_l021', 'p', '你来拿的是照片？'),
                  ('s01_platform_l022', 'n', '她看向纸袋。这个问题终于把我们的注意力从“好久不见”移到今晚真正摆在面前的东西上。'),
                  ('s01_platform_l023', 'h', '照片是站务下午从旧库房找出来的。里面还有几张展签。'),
                  ('s01_platform_l024', 'n', '我点头。原来她和我一样，都是被一条临时通知叫回这里收拾旧东西的人。')],
 's02_reunion': [('s02_reunion_l013', 'h', '不只一张。还有几张展签和底片袋，店里说能留就留。'),
                 ('s02_reunion_l014', 'n', '她把纸袋口撑开一点。里面按年份分了几个薄信封，每个角上都写着日期，字比三年前更利落。'),
                 ('s02_reunion_l015', 'p', '你还在那家书店？'),
                 ('s02_reunion_l016', 'h', '还在这一行。店搬过一次，人也换了不少。'),
                 ('s02_reunion_l017', 'n', '她没有继续解释。我也没有马上追问“为什么不告诉我”。我们都很清楚，没有联系的人没有资格要求对方主动汇报生活。'),
                 ('s02_reunion_l018', 'n', '我把长椅上的一小块水擦掉，给纸袋腾出更平的地方。她说了声谢谢，把照片重新夹好。'),
                 ('s02_reunion_l019', 'h', '你那箱东西应该更多。以前展览撤得急，很多书都是你直接塞进去的。'),
                 ('s02_reunion_l020', 'p', '我记得只有几本。'),
                 ('s02_reunion_l021', 'h', '你对“几本”的理解一直很宽。'),
                 ('s02_reunion_l022', 'n', '这一次我笑出了声。笑完以后，气氛没有突然变回三年前，只是没那么绷紧了。'),
                 ('s02_reunion_l023', 'n', '她把靠雨棚内侧的位置让出半步，又没有替我决定要不要站过去。选择似乎从很小的地方就已经开始。'),
                 ('s02_reunion_l024', 'n', '我看着她被雨打湿一点的袖口，又看向出口的登记桌。先问她，还是先把自己的事情办完，都不会只是表面顺序。'),
                 ('s02_reunion_l025', 'n', '雨沿着棚边落得更密。我们都往里面靠了一点，却仍留着能清楚看见彼此动作的距离。'),
                 ('s02_reunion_l026', 'n', '我终于意识到，接下来最重要的不是把过去一次说完，而是先决定怎样对待眼前这个人。')],
 's02_care': [('s02_care_l012', 'h', '晚班不固定。这个月我主要负责新书上架和活动区，闭店的时候反而比较晚。'),
              ('s02_care_l013', 'n', '她翻到一张店内活动照片。靠窗的小桌边坐着几个读者，墙上贴着手写的推荐卡，没有一处和我记忆里的旧店完全一样。'),
              ('s02_care_l014', 'p', '你写这些推荐？'),
              ('s02_care_l015', 'h', '一半。字最丑的那几张不是我。'),
              ('s02_care_l016', 'n', '我顺着她指的方向看过去，没有问哪几张是她的。她自己翻到下一张，给我看刚换好的儿童区和一排被搬低的书架。'),
              ('s02_care_l017', 'h', '以前总觉得店小是缺点。后来发现，小一点也能把每个角落照顾到。'),
              ('s02_care_l018', 'p', '听起来你挺喜欢现在的地方。'),
              ('s02_care_l019', 'h', '有喜欢的，也有想辞职的时候。正常。'),
              ('s02_care_l020', 'n', '她说得很平。我意识到自己刚才差一点把“还在书店工作”理解成一种等待或停滞，其实她已经换过店面、职责和生活节奏。'),
              ('s02_care_l021', 'p', '我刚才问得像在核对你过得好不好。'),
              ('s02_care_l022', 'h', '那就别核对。你想知道什么可以直接问。'),
              ('s02_care_l023', 'n', '我想了想，只问她最近哪件事最费时间。她说是月底盘点，然后反问我这一趟会待多久。'),
              ('s02_care_l024', 'n', '我没有把明早离开的车票藏起来。至少从这一刻起，关心她的近况不该以隐瞒自己的安排为代价。'),
              ('s02_care_l025', 'h', '明天上午我休息，下午才去店里。你不用因为我改行程。'),
              ('s02_care_l026', 'n', '她先把这句话说出来，像是在把“关心”与“需要负责我的时间”分开。我记下了这个区别。')],
 's02_business': [('s02_business_l012', 'n', '登记桌上放着两支笔，一支断水。我试了两下，许澄把另一支推到桌边，却没有替我填任何一项。'),
                  ('s02_business_l013', 'p', '姓名、柜号、件数……就这些？'),
                  ('s02_business_l014', 'h', '还有确认外包装。底下如果湿了，可以现在换箱。'),
                  ('s02_business_l015', 'n', '我蹲下检查纸箱四角。胶带很新，底部没有水印。她站在一旁照着灯，没有催我，也没有帮我做本该自己确认的事。'),
                  ('s02_business_l016', 'n', '流程很快。签完名字以后，工作人员在清单上划掉柜号，提醒我们十点前离开站内区域。'),
                  ('s02_business_l017', 'p', '这样就算办完了。'),
                  ('s02_business_l018', 'h', '嗯。'),
                  ('s02_business_l019', 'n', '一句“嗯”之后又安静下来。先办事确实让我省去了几分钟尴尬，也把刚才可以继续的话题一起搁在了原地。'),
                  ('s02_business_l020', 'n', '我没有立刻补一句“其实我也想问你近况”。如果只是因为气氛变冷才临时补救，那仍然像在处理流程。'),
                  ('s02_business_l021', 'p', '你的日期分完了吗？'),
                  ('s02_business_l022', 'h', '还差两张。你愿意照灯就照灯，别替我猜年份。'),
                  ('s02_business_l023', 'n', '我把手机光线调暗一点，按她报出的顺序移动。我们先把眼前的事情做完，关系没有因此变好，也没有彻底关上。'),
                  ('s02_business_l024', 'n', '等最后一张照片装回纸袋，她才抬头看我。那一眼像是在问：现在还有没有别的话要说。'),
                  ('s02_business_l025', 'h', '你箱子搬过来以后，椅子还能坐两个人。'),
                  ('s02_business_l026', 'n', '这已经是一个继续留下来的邀请，但它很有限。我没有把它解释成更多。')],
 's02_boxes': [('s02_boxes_l011', 'n', '纸箱里最旧的是两册地方摄影集，书脊已经起毛。我翻到借展标签，背面还贴着当年临时写的编号。'),
               ('s02_boxes_l012', 'h', '这两本不是书店的，你可以带走。'),
               ('s02_boxes_l013', 'p', '我记得一本是你借我的。'),
               ('s02_boxes_l014', 'h', '借你三年，按我们店的规则早该赔了。'),
               ('s02_boxes_l015', 'n', '她嘴上这么说，还是把那本书放回我这一侧。纸箱里的东西被慢慢分成“我的”“她的”“该丢的”三堆。'),
               ('s02_boxes_l016', 'n', '破掉的相框被单独靠在柱脚，完好的几个重新套进纸袋。没有哪件东西因为旧就必须保存，也没有哪件东西因为过去尴尬就一定要扔。'),
               ('s02_boxes_l017', 'p', '留言册呢？'),
               ('s02_boxes_l018', 'h', '你留着。里面大部分留言本来就是给那次展览的。'),
               ('s02_boxes_l019', 'n', '我把册子拿起来，封底夹着一张褪色的场地图。三年前我们用红笔标过照片位置，现在只剩几个模糊的圈。'),
               ('s02_boxes_l020', 'n', '许澄看了一眼，没有翻留言。她继续核对清单，把属于书店的最后一只相框装好。'),
               ('s02_boxes_l021', 'h', '这样就齐了。'),
               ('s02_boxes_l022', 'n', '她把清单折起来时，纸袋内侧露出另一只更小的信封。和底片袋不同，它没有日期标签。'),
               ('s02_boxes_l023', 'n', '我先认出了信封的纸，再认出右上角那道被雨水晕开的痕迹。胸口像被旧站里迟到三年的广播轻轻敲了一下。'),
               ('s02_boxes_l024', 'n', '许澄也注意到我的视线。她没有顺势拆开，只把那只信封单独拿了出来。'),
               ('s02_boxes_l025', 'p', '这封信也在清单上？'),
               ('s02_boxes_l026', 'h', '不在。所以我才想先问你。')],
 's03_letter': [('s03_letter_l013', 'n', '我没有打开它，也不需要打开才能知道里面大概写了什么。那晚我写了三遍开头，最后留下的是最不像承诺的一版。'),
                ('s03_letter_l014', 'n', '当时外地的入职通知突然提前，我得在一周内报到。住处、试用期、之后会不会回江城，全都没有确定。'),
                ('s03_letter_l015', 'n', '我本来想告诉她这些，又在每一句后面补上“等稳定一点”。写到最后，连什么时候再联系都变成了模糊的以后。'),
                ('s03_letter_l016', 'n', '把信夹进留言册时，我给自己的解释是：等车票、合同和住处都确定，再把一件完整的事告诉她。'),
                ('s03_letter_l017', 'n', '后来工作稳定了，新的住处也找到了。那封信却留在这里。原先关于“不确定”的理由结束以后，我又开始害怕解释为什么拖了这么久。'),
                ('s03_letter_l018', 'n', '所以真正没有完成的，不只是一次寄信。每过一个月，我都在重复一次“再晚一点说”。'),
                ('s03_letter_l019', 'h', '如果你认识，就先拿好。这里太潮。'),
                ('s03_letter_l020', 'n', '她说的是纸。我却下意识把手收紧了一点，仿佛只要不让信受潮，就能暂时把里面那段迟到的说明也保存完整。'),
                ('s03_letter_l021', 'p', '谢谢。'),
                ('s03_letter_l022', 'n', '我把信放在箱盖最干燥的地方，没有拆，也没有塞回书页。这个动作至少承认，它已经重新回到今天。'),
                ('s03_letter_l023', 'n', '许澄没有催。她把纸袋放到腿边，等我自己决定要不要把那个“澄”字和她联系起来。'),
                ('s03_letter_l024', 'n', '雨声填满了几秒钟。接下来的一句话，会决定她知道多少，也会决定我今晚是不是又把解释推到以后。'),
                ('s03_letter_l025', 'n', '我看着封口，知道自己现在拥有的是解释的机会，不是要求她理解的资格。'),
                ('s03_letter_l026', 'n', '如果继续沉默，这个选择也会成为新的事实，不能再归咎给三年前的雨。')],
 's03_honest': [('s03_honest_l010', 'p', '那时候公司把报到时间提前了。我以为自己只是先去几个月，等试用期结束就回来一次。'),
                ('s03_honest_l011', 'h', '所以你写了信。'),
                ('s03_honest_l012', 'p', '写了。可我不敢写“你等我”，也不敢写“别等我”。我觉得哪一种都像替你做决定。'),
                ('s03_honest_l013', 'h', '不替我决定，和什么都不告诉我，是两回事。'),
                ('s03_honest_l014', 'n', '她的声音没有抬高。这句话却比责备更准确。我点头，没有拿当时的慌乱替自己减轻责任。'),
                ('s03_honest_l015', 'p', '后来住处和工作都稳定了。我还是没联系。那部分已经不能怪报到时间。'),
                ('s03_honest_l016', 'h', '嗯。'),
                ('s03_honest_l017', 'n', '她只应了一声。我第一次觉得，这个简单的“嗯”比“没关系”更合适，因为这件事确实还没有到可以轻易过去的时候。'),
                ('s03_honest_l018', 'p', '我不是想用这封信证明当时有多认真。它只能证明我写过，又没有送出去。'),
                ('s03_honest_l019', 'h', '这句话我听得懂。'),
                ('s03_honest_l020', 'n', '她看了一眼信封，没有伸手。我也没有把它递过去，继续让封口保持原样。'),
                ('s03_honest_l021', 'h', '等以后真要看，我们再决定在哪里看。不是今天为了把气氛变好就拆。'),
                ('s03_honest_l022', 'p', '好。'),
                ('s03_honest_l023', 'n', '这不是原谅，也不是重新开始的约定。只是我们终于对三年前发生过什么有了同一个事实起点。'),
                ('s03_honest_l024', 'n', '我把信收进口袋内侧，封口朝上。接下来如果还要谈，就该谈现在能做到什么，而不是让一封旧信替我们说完。'),
                ('s03_honest_l025', 'h', '今晚先到这里也可以。你承认是你写的，已经比让我猜强。'),
                ('s03_honest_l026', 'n', '她给的是暂停，不是结论。我把这两个词在心里分开，终于没有急着问她现在怎么看我。')],
 's03_deferred': [('s03_deferred_l011', 'n', '我把纸箱里的书重新压平，动作比需要的慢。许澄没有盯着我看，只把两只相框套进保护袋。'),
                  ('s03_deferred_l012', 'h', '你不用现在编一个完整版本。'),
                  ('s03_deferred_l013', 'p', '我知道。'),
                  ('s03_deferred_l014', 'h', '但以后如果要说，别只告诉我“事情很复杂”。复杂也可以一件一件说。'),
                  ('s03_deferred_l015', 'n', '我点头。她没有得到信的作者这个事实，所以她的判断只能停在“我认识字迹，却暂时不解释”。这是我这次选择留下的边界。'),
                  ('s03_deferred_l016', 'n', '我不能在心里把她的耐心理解成已经知道，也不能因为她没追问，就把沉默当成默认接受。'),
                  ('s03_deferred_l017', 'p', '如果我回去以后还没想好，也会告诉你我还没想好。'),
                  ('s03_deferred_l018', 'h', '这比消失好。'),
                  ('s03_deferred_l019', 'n', '她说完继续整理东西，语气没有变软。那句比较也让我听见了过去留下的真实重量。'),
                  ('s03_deferred_l020', 'n', '我摸到口袋里的信封，确定边角没有折。它现在更像一项未完成的谈话，而不是可以永久封存的纪念品。'),
                  ('s03_deferred_l021', 'p', '我不会今晚拆。'),
                  ('s03_deferred_l022', 'h', '那是你的决定。'),
                  ('s03_deferred_l023', 'n', '她没有说“我们的决定”，因为她还不知道信里写给谁。这个称呼上的距离很小，却必须保留。'),
                  ('s03_deferred_l024', 'n', '我们把剩下的旧物继续分完。暂停解释不等于路线停住，今晚仍然可以做一些不需要猜测的事。'),
                  ('s03_deferred_l025', 'h', '等你真准备说的时候，别从“那都过去了”开始。'),
                  ('s03_deferred_l026', 'n', '我记住这句话。过去会过去，但它留下的空白仍然需要现在的人来处理。')],
 's03_archive': [('s03_archive_l010', 'n', '我重新数了一遍纸箱里的东西：书七本、留言册一本、两个空相框。属于书店的照片和完好相框已经全部进了她的纸袋。'),
                 ('s03_archive_l011', 'n', '信封在我外套内袋，和手机分开放着。这个位置之后没有再变，直到我们离开车站。'),
                 ('s03_archive_l012', 'h', '箱子要封吗？'),
                 ('s03_archive_l013', 'p', '先不封死。等走的时候再贴。'),
                 ('s03_archive_l014', 'n', '我把胶带头折出一小截，免得临走时找不到。许澄把废掉的相框搬到回收标记旁，回来时顺手拍掉袖口上的灰。'),
                 ('s03_archive_l015', 'p', '这些照片你明天就带回店里？'),
                 ('s03_archive_l016', 'h', '不急。先带回家。店里周一才整理旧展资料。'),
                 ('s03_archive_l017', 'n', '她说“回家”时很自然。我也第一次具体意识到，她现在有一个我不知道地址的家，有自己的下班路线和第二天安排。'),
                 ('s03_archive_l018', 'n', '这种不知道不需要立刻补齐。知道她会带着自己的东西回到自己的生活里，已经足够让今晚从旧展览里向前挪一步。'),
                 ('s03_archive_l019', 'h', '你住哪边？'),
                 ('s03_archive_l020', 'p', '先去酒店。明早再走。'),
                 ('s03_archive_l021', 'n', '这一次我直接说了明早离开的安排，没有等她从行李或车票里猜。她点头，把这个事实收下。'),
                 ('s03_archive_l022', 'n', '整理结束后，两个人的东西都明确归了位。接下来真正难处理的只剩谈话本身。'),
                 ('s03_archive_l023', 'n', '出口的工作人员开始收起登记桌，提醒我们还有十分钟。我们把箱子往门口方向挪了一段。'),
                 ('s03_archive_l024', 'n', '位置变了，谈话也要继续往前。没有哪件旧物再需要被当作拖延开口的借口。')],
 's04_open': [('s04_open_l010', 'n', '高一点的信任没有让问题消失，只让我们可以少绕一层。我把手机上的车票页面给她看了一眼，又马上锁屏。'),
              ('s04_open_l011', 'p', '明早九点。今晚不需要赶最后一班车，只需要在站里关门前出去。'),
              ('s04_open_l012', 'h', '那就别把剩下这点时间也排成任务。'),
              ('s04_open_l013', 'n', '她把“任务”两个字说得很轻。我才发现自己从进站开始一直在数时间：登记几分钟、搬箱几分钟、解释又要几分钟。'),
              ('s04_open_l014', 'p', '我习惯先想怎么把事情做完。'),
              ('s04_open_l015', 'h', '聊天不一定有“做完”。'),
              ('s04_open_l016', 'p', '那我先说一件没做完的。'),
              ('s04_open_l017', 'n', '她没有追问是哪一件，只等我自己往下说。这个等待和三年前不同——不是无限期留在原地，而是现在愿意给我几分钟。'),
              ('s04_open_l018', 'p', '我回来之前没有计划见你。见到以后，我想把今晚剩下的时间留给我们两个。'),
              ('s04_open_l019', 'h', '可以。前提是你明天该走还是走，不用为了证明什么临时改票。'),
              ('s04_open_l020', 'n', '我应了一声。她把“愿意聊”和“要求留下”清楚分开，这让接下来的谈话有了一个不需要表演牺牲的起点。'),
              ('s04_open_l021', 'h', '你可以慢慢说，但别只挑听起来最好听的那部分。'),
              ('s04_open_l022', 'n', '我点头。信任给我的不是更轻松的路线，而是更直接承担完整事实的机会。')],
 's04_reserved': [('s04_reserved_l010', 'n', '我把明早的车票时间直接告诉她。她听完只点了点头，没有因为我会离开就立刻要求一个解释。'),
                  ('s04_reserved_l011', 'p', '今晚我原本没安排见任何人。'),
                  ('s04_reserved_l012', 'h', '我知道。我们是碰巧遇见。'),
                  ('s04_reserved_l013', 'n', '“碰巧”把这次重逢放回它真实的位置。不是命运替我们修好什么，也不是谁偷偷守了三年。'),
                  ('s04_reserved_l014', 'p', '但我现在想聊一会儿。'),
                  ('s04_reserved_l015', 'h', '可以。只是如果你又不知道怎么说，就直接说不知道。'),
                  ('s04_reserved_l016', 'n', '她把纸袋抱在膝上，没有像高信任时那样主动追问。我必须自己决定拿出多少明确的话，而不是等她给我台阶。'),
                  ('s04_reserved_l017', 'p', '我明白。'),
                  ('s04_reserved_l018', 'h', '还有，别因为明天要走就一次答应很多。'),
                  ('s04_reserved_l019', 'p', '那我只答应能做到的。'),
                  ('s04_reserved_l020', 'n', '这句话暂时没有换来笑。她只是往长椅另一端挪了一点，给我们留出能继续说话、也能随时停下来的距离。'),
                  ('s04_reserved_l021', 'h', '如果说到一半不想说了，也可以停。至少告诉我你在停。'),
                  ('s04_reserved_l022', 'n', '她把暂停的规则也说清楚。低一点的信任需要更多边界，这并不等于谈话已经失败。')],
 's04_waiting': [('s04_waiting_l023', 'n', '确认号码以后，我们都没有立刻发第二条消息。屏幕暗下去，站台重新只剩雨声和远处收拾设备的碰撞声。'),
                 ('s04_waiting_l024', 'h', '我不是要求你每天报到。'),
                 ('s04_waiting_l025', 'p', '我知道。'),
                 ('s04_waiting_l026', 'h', '我只是希望，如果你想继续联系，就别把“以后再说”当成默认设置。忙可以说忙，不想聊也可以说不想聊。'),
                 ('s04_waiting_l027', 'n', '她把边界说得很具体，没有让我猜什么频率才算在意，也没有给自己安排一个必须随时等待的角色。'),
                 ('s04_waiting_l028', 'p', '那我到住处后发一条。明早上车前也会说一声。'),
                 ('s04_waiting_l029', 'h', '两条就够。明天之后再看我们有没有想聊的。'),
                 ('s04_waiting_l030', 'n', '我把这个约定记进手机备忘录，又觉得太像工作清单，最后只在心里重复了一遍。她看见我的动作，没忍住笑。'),
                 ('s04_waiting_l031', 'h', '你是不是又在记任务？'),
                 ('s04_waiting_l032', 'p', '差点。'),
                 ('s04_waiting_l033', 'h', '那就删掉。记得做就行。'),
                 ('s04_waiting_l034', 'n', '我把刚打到一半的提醒删了。不是因为约定不重要，而是这件事不需要靠形式证明认真。'),
                 ('s04_waiting_l035', 'n', '她随后说起明天下午要给新到的书贴标签，晚上可能还要替同事半个班。那些琐碎安排让我第一次听见她现在生活的具体声音。'),
                 ('s04_waiting_l036', 'n', '我也只说自己的明早：退房、坐车、回去处理积下来的工作。没有承诺很快搬回来，也没有把一次重逢夸成生活转折。'),
                 ('s04_waiting_l037', 'h', '这样就挺好。至少我们现在知道明天各自在做什么。'),
                 ('s04_waiting_l038', 'n', '她说完看向纸袋里的照片。我顺着她的视线看过去，下一段话终于可以从“现在”回到那张我们都记得、却记得不完全一样的旧照片。'),
                 ('s04_waiting_l039', 'n', '她把纸袋提起来试了试重量，又重新放下。今晚之后，这些照片会回到她的家，而不是继续留在旧站替谁保存过去。'),
                 ('s04_waiting_l040', 'p', '那张没给我的照片，你现在还想留着吗？'),
                 ('s04_waiting_l041', 'h', '先留着。要不要给你看，是另一件事。'),
                 ('s04_waiting_l042', 'n', '我笑了一下，没有伸手。这个回答正好把下一段谈话的边界画出来：可以一起回忆，所有权仍属于她。')]}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prompt_text(node: dict) -> str:
    scene_id = node["id"]
    return f"""# v0.7 Scene expansion request — {scene_id}

Purpose: {node.get("dramatic_purpose", "")}

Expand the existing scene in Chinese without changing the route graph, state effects, chapter order, or existing line IDs.
Preserve all existing lines exactly, especially lines already bound to voice assets. Add concrete actions, environment details, motives and consequences rather than abstract explanation.

Hard facts:
- Modern fictional Jiangcheng, old station closing on a rainy night.
- The player is a 25-year-old adult who returned to collect stored books; meeting Xu Cheng was not planned.
- Xu Cheng is a 23-year-old adult bookstore worker with her own home, work schedule and decisions.
- The player knows from the opening that he wrote the unsent letter. Xu Cheng only knows this after q02_honest or later q04_revisit.
- The envelope remains unopened and in the player's possession after the letter scene.
- Old photos belong to Xu Cheng and do not prove that she waited for the player.
- Do not turn nostalgia into a demand for romantic repayment.
- Keep the existing four choices, 16 routes, two endings, and affection/trust/truth_known state model.
- q04 repair may affect what happens next but may not erase earlier choices.

This request is the v0.7 restoration/expansion pass for {scene_id}. Review character voice, timeline, item ownership and branch knowledge after writing.
"""


def write_prompt(node: dict) -> None:
    scene_id = node["id"]
    relative = Path("prompts/script/v07") / f"{scene_id}_v1.md"
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(prompt_text(node), encoding="utf-8")
    node["draft_prompt"] = relative.as_posix()
    node["draft_prompt_sha256"] = sha256(path)
    node["draft_prompt_id"] = "_".join(relative.relative_to("prompts").with_suffix("").parts)
    node["review_status"] = "v07_restored_expansion_candidate"


def append_lines(node: dict, planned: list[tuple[str, str, str]]) -> tuple[int, int]:
    existing = {line["id"]: line for line in node.get("lines", [])}
    added_lines = 0
    added_chars = 0
    for line_id, speaker, text in planned:
        if line_id in existing:
            current = existing[line_id]
            if current.get("speaker") != speaker or current.get("text") != text:
                raise SystemExit(f"Conflicting restored line: {line_id}")
            continue
        node["lines"].append({"id": line_id, "speaker": speaker, "text": text})
        added_lines += 1
        added_chars += len(text)
    return added_lines, added_chars


def update_docs(added_lines: int, added_chars: int, scene_ids: list[str]) -> None:
    world = ROOT / "docs/WORLD.md"
    text = world.read_text(encoding="utf-8")
    marker = "## v0.7 新增事实边界"
    if marker not in text:
        text += (
            "\n\n" + marker + "\n\n"
            "v0.7 将三年前离城动机具体化：主角当时收到外地工作的提前报到通知，需要在一周内离开；"
            "他因住处、试用期与回城时间都未确定而写下但没有送出信，后来生活稳定后仍继续拖延联系。"
            "这解释行为动机，不免除其长期沉默的责任。信封今晚始终未拆。\n"
        )
        world.write_text(text, encoding="utf-8")

    characters = ROOT / "docs/CHARACTERS.md"
    text = characters.read_text(encoding="utf-8")
    marker = "v0.7 离城动机"
    if marker not in text:
        text += (
            "\n\n### " + marker + "\n\n"
            "主角三年前因外地工作提前报到而匆忙离开。真正的关系缺口来自：他把“不确定时不敢承诺”"
            "逐渐变成了长期不沟通。扩写时不得把工作安排写成自动免责理由。\n"
        )
        characters.write_text(text, encoding="utf-8")

    report = ROOT / "docs/V07_RESTORE_REPORT.md"
    report.write_text(
        "# v0.7 剧情恢复批次 A\n\n"
        "日期：2026-10-05（北京时间）\n\n"
        "本批次把此前工作会话中“前三章及中段分支两轮扩写”的已确认方向重新落到远端仓库，"
        "并保持既有路线结构与关键配音文本不变。\n\n"
        f"- 修改场景：{len(scene_ids)} 个\n"
        f"- 新增正文行：{added_lines} 行\n"
        f"- 新增正文字符：{added_chars}（按 Python `len(text)` 汇总，含标点）\n"
        "- 新增状态：0\n"
        "- 新增选择：0\n"
        "- 删除既有台词：0\n"
        "- 修改既有语音绑定台词：0\n"
        "- 路线目标：仍为 16 条；Normal / True 两个结局保持不变\n\n"
        "涉及场景：`" + "`, `".join(scene_ids) + "`。\n\n"
        "本批次是恢复 checkpoint，不代表 v0.7 完成。下一步先审查第三章后的合流知识、物品、时间与称呼，"
        "再进入 ch04 扩写。\n",
        encoding="utf-8",
    )

    checkpoint = ROOT / "docs/WORK_CHECKPOINT.md"
    text = checkpoint.read_text(encoding="utf-8")
    text = text.replace(
        "- [ ] 恢复并提交前三章及中段分支的 v0.7 内容，使远端仓库真正达到此前工作断点。",
        "- [x] 恢复并提交前三章及中段分支的 v0.7 内容，使远端仓库真正达到此前工作断点。",
    )
    batch = (
        "\n\n## 2026-10-05 恢复批次 A\n\n"
        f"- 恢复 {len(scene_ids)} 个场景，新增 {added_lines} 行 / {added_chars} 字符。\n"
        "- 既有语音绑定台词未改字；四次选择、16 路线、两个结局与三个状态保持原结构。\n"
        "- 同步新增 v0.7 Scene Prompt，并更新 Prompt Registry。\n"
        "- 流程修复的 Windows CI 37246212831 已通过；本批剧情将在后续 Windows checkpoint 再跑完整验收。\n"
        "- 下一条任务：检查第三章后的知识、物品、时间、称呼和配音绑定，再进入 ch04。\n"
    )
    if "## 2026-10-05 恢复批次 A" not in text:
        text += batch
    checkpoint.write_text(text, encoding="utf-8")


def main() -> None:
    story = json.loads(STORY_PATH.read_text(encoding="utf-8"))
    nodes = {node["id"]: node for node in story["nodes"]}
    missing = sorted(set(ADDITIONS) - set(nodes))
    if missing:
        raise SystemExit("Missing target scenes: " + ", ".join(missing))

    all_existing_ids = {
        line["id"]
        for node in story["nodes"]
        for line in node.get("lines", [])
    }
    planned_ids = [line_id for lines in ADDITIONS.values() for line_id, _, _ in lines]
    if len(planned_ids) != len(set(planned_ids)):
        raise SystemExit("Duplicate IDs inside v0.7 restoration plan")
    conflicts = sorted(set(planned_ids) & all_existing_ids)
    if conflicts:
        for scene_id, planned in ADDITIONS.items():
            append_lines(nodes[scene_id], planned)
        print(f"Idempotent rerun: {len(conflicts)} planned IDs already exist.")
    else:
        total_lines = total_chars = 0
        for scene_id, planned in ADDITIONS.items():
            added_lines, added_chars = append_lines(nodes[scene_id], planned)
            total_lines += added_lines
            total_chars += added_chars
        if total_chars < 6000:
            raise SystemExit(f"Restoration batch unexpectedly small: {total_chars} characters")
        print(f"Restored {total_lines} lines / {total_chars} characters.")

    for scene_id in ADDITIONS:
        write_prompt(nodes[scene_id])

    story["status"] = "v07_alpha_expansion_recovered_through_ch03"
    STORY_PATH.write_text(json.dumps(story, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    added_lines = sum(len(lines) for lines in ADDITIONS.values())
    added_chars = sum(len(text) for lines in ADDITIONS.values() for _, _, text in lines)
    update_docs(added_lines, added_chars, list(ADDITIONS))
    print(f"v0.7 restoration prepared for {len(ADDITIONS)} scenes.")


if __name__ == "__main__":
    main()
