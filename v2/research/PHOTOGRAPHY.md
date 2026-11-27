# V2 纪实照片调研与选型记录

日期：2026-11-27。目标：先找真实且有权复用的目标区域照片；次选福海同街道/同城真实同类场景；最后才用明确标注的写实生成参考。

## 结论

本轮获得并本地校验 **13 张真实照片**：10 张宝安福海附近的桥和路、桥头菜肉市场及同泰时代广场商铺/街景（2023/2024年拍摄），3 张真实深圳南山/福田早餐产品照片（2024年拍摄）。不是新和三区目标门店实拍；不能由早于研究时点的照片断言当前门店、经营时段、销量和租金。目标新和一区/二区/三区的商家公开店铺线索有多条，但没有同时满足可获得照片、地点和授权三项要求的原图，未强行嵌入。

## 实际渠道及工具实验

| 尝试 | 结果 | 处理 |
|---|---|---|
| 普通搜索（中文地名+门店、商铺转让、食街） | 能定位新和二区部分商户、在租线索，例如万州烤鱼（新和店）、益禾堂（新和村店）、新和社区租赁。房源页面常有多张商家/经纪人照片，但未授予公开重制、再分发许可。 | 仅作为现场查看链接，不复制照片，不将挂牌广告当实地证据。 |
| Exa 语义搜索 | 找到潮州早餐、北方灌汤包、味美香面馆等目标社区候选店，以及360地图姚记逍遥胡辣汤标注9图、快乐番薯图册线索。 | 数据聚合仅用于发现；直接网页打开360/旅游目录失败，不能核实图片内容/拍摄日期/使用权。 |
| OpenRice | 新和快乐番薯分店页面可打开；地址与菜单/营业时间可读，目标店相片区只有新增相片入口，无可核实照片。页面明确保留版权。 | 对正文可引用公开事实并链接，不能复制照片。 |
| 图像搜索 | 精准地名检索仍匹配到《拐角门面设计效果图》等宽泛图集，无目标地点、拍摄日期与许可。 | 不采用，不因视觉相似便称为实拍。 |
| 政府/本地媒体 | 找到新和居民游园会与社区空间报道、福海和平夜市摄影。报道并未提供本项目明确图像再分发许可，部分照片含活动参与者/未成年人或与早餐门店不相关。 | 可供读者链接参考；不嵌入、不采集私人或未成年人可识别人像，不用节庆人流估计商业客流。 |
| Wikimedia Commons 地名及餐饮分类检索 | 通过桥和路、同泰时代广场食店、深圳早餐专题筛出逐张许可证和拍摄元数据。使用公共 MediaWiki API 和公开 960px 缩略图获取文件，遇一次429后降低频率再从明确的公开缩略图URL下载，全部有效。 | 选用开放许可实拍，保留时间戳和原照片内容，图注标明具体地点和年月。 |

## 地名与内容复核

- [福海街道机构概况（政府，2026-07-10）](https://www.baoan.gov.cn/xxgk/jgk/jdbsc/content/post_12887016.html)确认桥和路属于福海；[桥头社区便民服务站（政府）](https://wsbs.sz.gov.cn/shenzhen/project/phoneGuide?code=70000200169395646914440306)明确桥头社区桥和路交汇处。桥和路实景中“桥头市场”等店招与图片元数据吻合。
- 同泰时代广场地址用[深圳卫健委2025年名单](https://wjw.sz.gov.cn/attachment/1/1708/1708618/12756247.pdf)（打印地址为福海桥头社区同泰总部产业园）与[本地宝商场详情](https://m.bendibao.com/wangdian/dian/5784746.shtm)（桥头社区宝安大道6259号）交叉确认。不得因为个别房地产网站写成新和社区而误报。
- 另发现Wikimedia 深圳塘尾商业街（2026-09-09）的照片。逐张元数据坐标和道路名显示该组“将塘路”实际在光明区凤凰街道塘尾社区，与福海街道塘尾社区重名。相关[光明区塘尾路公开地点](https://sz.dushiquan.net/poi/18415/)及[政府社区公园名录](https://cgj.sz.gov.cn/xsmh/gysz/sqgy/content/post_10807975.html)能区分位置，故排除其作为福海附近实拍。
- 实体照片拍摄年份较早，正文图注统一“福海周边实拍”或“深圳同类产品实拍”，不得写成“新和社区门面实拍”或“当前门店”。

## 可打开的当地真实商业信息/照片线索（不嵌入）

- [OpenRice 快乐番薯（宝安新和店）](https://www.openrice.com/zh/shenzhen/r-%E5%BF%AB%E6%A8%82%E7%95%AA%E8%96%AF-%E7%A6%8F%E6%B0%B8-%E7%B2%B5%E8%8F%9C-%E5%BB%A3%E6%9D%B1-%E6%9E%9C%E6%B1%81-%E5%A5%B6%E8%8C%B6-r10328582)：页面可读取，当前未列图。
- [安居客宝安福永餐饮铺面（近期公开索引）](https://sz.sydc.anjuke.com/sp-zu/dt1004-st120642-px1-pv0/)：新和二区悦盛三路的100㎡烤鱼小炒转让广告；索引可见，不代表目前仍在租；照片授权未知。
- [安居客新和二区旺铺线索](https://sz.sydc.anjuke.com/sp-zu/dt1004-st120644-yzj20-hy9-lx4/)：益禾堂新和村店80㎡挂牌；仅是核查线索，不直接采用广告照。
- [360地图姚记逍遥胡辣汤（新和二区八巷店）](https://m.map.360.cn/m/search/detail/pid=7a98a3aa90505505)：Exa返回页面索引标注9图；直接打开失败，图像、许可及门店现状均未核实。
- [宝安湾福海和平夜市报道](https://www.baoanone.com/content204441.html)，2025-10-13，记者实拍，非新和三区，作者权利未知，正文可提供链接。
- [深圳政府在线新和基围文化陈列馆开馆](https://www.sz.gov.cn/cn/xxgk/zfxxgj/gqdt/content/post_13042340.html)，2026-10-26，真实新和社区背景影像，非餐饮门店且发布无明确复用许可，作链接参考。

## 采用素材与授权（细节为 assets/PHOTO_MANIFEST.json）

须保持被引用照片的独立版权及许可。CC BY-SA 4.0 图片保留作者、来源、许可链接；此处只下载缩放版本，内容与原时间戳未修改。图文报告作为汇编不将独立素材改授权；若做裁切／修改，该照片的衍生版本仍按其开放许可证发布并标注修改。CC0虽不要求署名，我们仍标注出处以保可追溯。

| 编号 | 素材文件 | 图注 | 作者 | 许可 | 原图档案 |
|---|---|---|---|---|---|
| P01 | qiaohe_street.jpg | 福海周边实拍：桥和路居民楼下的沿街餐饮门面（2023年8月） | JMUAIANWNC 3366688 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) | [Wikimedia档案](https://commons.wikimedia.org/wiki/File:SZ_%E6%B7%B1%E5%9C%B3_Shenzhen_%E5%AF%B6%E5%AE%89_BaoAn_%E6%A9%8B%E5%92%8C%E8%B7%AF_Qiaohe_Road_shops_n_facade_August_2023_Px3.jpg) |
| P02 | qiaohe_market.jpg | 福海周边实拍：桥头菜肉市场入口（2023年8月） | JMUAIANWNC 3366688 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) | [Wikimedia档案](https://commons.wikimedia.org/wiki/File:SZ_%E6%B7%B1%E5%9C%B3_Shenzhen_%E5%AF%B6%E5%AE%89_BaoAn_%E6%A9%8B%E5%92%8C%E8%B7%AF_Qiaohe_Road_%E6%A9%8B%E9%A0%AD%E8%8F%9C%E8%82%89%E5%B8%82%E5%A0%B4_Qiaotou_food_vegetable_market_August_2023_Px3_14.jpg) |
| P03 | qiaohe_congee.jpg | 福海周边实拍：桥和路潮汕砂锅粥店面（2023年8月） | JMUAIANWNC 3366688 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) | [Wikimedia档案](https://commons.wikimedia.org/wiki/File:SZ_%E6%B7%B1%E5%9C%B3_Shenzhen_%E5%AF%B6%E5%AE%89_BaoAn_%E6%A9%8B%E5%92%8C%E8%B7%AF_Qiaohe_Road_shop_Chiu_Shen_Bowel_Congee_Restaurant_August_2023_Px3.jpg) |
| P04 | qiaohe_noodle.jpg | 福海周边实拍：桥和路潮汕捞面店（2023年8月） | JMUAIANWNC 3366688 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) | [Wikimedia档案](https://commons.wikimedia.org/wiki/File:SZ_%E6%B7%B1%E5%9C%B3_Shenzhen_%E5%AF%B6%E5%AE%89_BaoAn_%E6%A9%8B%E5%92%8C%E8%B7%AF_Qiaohe_Road_shop_Chiushen_Noodle_Restaurant_August_2023_Px3_15.jpg) |
| P05 | qiaohe_restaurants.jpg | 福海周边实拍：桥和路餐饮及混合零售门面（2023年8月） | JMUAIANWNC 3366688 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) | [Wikimedia档案](https://commons.wikimedia.org/wiki/File:SZ_%E6%B7%B1%E5%9C%B3_Shenzhen_%E5%AF%B6%E5%AE%89_BaoAn_%E6%A9%8B%E5%92%8C%E8%B7%AF_Qiaohe_Road_shops_n_restaurant_August_2023_Px3.jpg) |
| P06 | qiaohe_bakery.jpg | 福海周边实拍：桥和路广隆蛋挞王（2023年8月） | JMUAIANWNC 3366688 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) | [Wikimedia档案](https://commons.wikimedia.org/wiki/File:SZ_%E6%B7%B1%E5%9C%B3_Shenzhen_%E5%AF%B6%E5%AE%89_BaoAn_%E6%A9%8B%E5%92%8C%E8%B7%AF_Qiaohe_Road_shop_%E5%BB%A3%E9%9A%86%E8%9B%8B%E6%92%BB%E7%8E%8B_bakery_August_2023_Px3.jpg) |
| P07 | tongtai_foodstreet_05.jpg | 福海周边实拍：同泰时代广场临街永和大王（2024年6月） | NGAON32 Hongam | [CC0](http://creativecommons.org/publicdomain/zero/1.0/deed.en) | [Wikimedia档案](https://commons.wikimedia.org/wiki/File:SZ_%E6%B7%B1%E5%9C%B3_Shenzhen_%E5%AF%B6%E5%AE%89%E5%8D%80_BaoAn_%E8%A0%94%E6%A5%AD%E8%B7%AF_Haoye_Road_%E5%90%8C%E6%B3%B0%E6%99%82%E4%BB%A3%E5%BB%A3%E5%A0%B4_Tongtai_Times_Square_mall_%E9%A3%9F%E8%A1%97_food_street_June_2024_R12S_05.jpg) |
| P08 | tongtai_snack.jpg | 福海周边实拍：同泰时代广场好特卖零食店（2024年6月） | NGAON32 Hongam | [CC0](http://creativecommons.org/publicdomain/zero/1.0/deed.en) | [Wikimedia档案](https://commons.wikimedia.org/wiki/File:SZ_%E6%B7%B1%E5%9C%B3_Shenzhen_%E5%AF%B6%E5%AE%89%E5%8D%80_BaoAn_%E8%A0%94%E6%A5%AD%E8%B7%AF_Haoye_Road_%E5%90%8C%E6%B3%B0%E6%99%82%E4%BB%A3%E5%BB%A3%E5%A0%B4_Tongtai_Times_Square_mall_shop_HotMaxx_Food_store_June_2024_R12S_02.jpg) |
| P09 | tongtai_booth.jpg | 福海周边实拍：同泰时代广场小吃摊位（2024年6月） | NGAON32 Hongam | [CC0](http://creativecommons.org/publicdomain/zero/1.0/deed.en) | [Wikimedia档案](https://commons.wikimedia.org/wiki/File:SZ_%E6%B7%B1%E5%9C%B3_Shenzhen_%E5%AF%B6%E5%AE%89%E5%8D%80_BaoAn_%E8%A0%94%E6%A5%AD%E8%B7%AF_Haoye_Road_%E5%90%8C%E6%B3%B0%E6%99%82%E4%BB%A3%E5%BB%A3%E5%A0%B4_Tongtai_Times_Square_mall_food_booth_stalls_June_2024_R12S_10.jpg) |
| P10 | tongtai_foodstreet_01.jpg | 福海周边实拍：同泰时代广场外立面（2024年6月） | NGAON32 Hongam | [CC0](https://creativecommons.org/publicdomain/zero/1.0/) | [Wikimedia档案](https://commons.wikimedia.org/wiki/File:SZ_%E6%B7%B1%E5%9C%B3_Shenzhen_%E5%AF%B6%E5%AE%89%E5%8D%80_BaoAn_%E8%A0%94%E6%A5%AD%E8%B7%AF_Haoye_Road_%E5%90%8C%E6%B3%B0%E6%99%82%E4%BB%A3%E5%BB%A3%E5%A0%B4_Tongtai_Times_Square_mall_%E9%A3%9F%E8%A1%97_food_street_June_2024_R12S_01.jpg) |
| P11 | baozi_food.jpg | 深圳同类产品实拍：南山前海湾站早起点叉烧包（2024年9月） | HHAFOL Moratim LUNG | [CC0](https://creativecommons.org/publicdomain/zero/1.0/) | [Wikimedia档案](https://commons.wikimedia.org/wiki/File:SZ_%E6%B7%B1%E5%9C%B3_Shenzhen_Metro_%E5%8D%97%E5%B1%B1%E5%8D%80_Nanshan_%E5%89%8D%E6%B5%B7%E7%81%A3%E7%AB%99_QianHaiWan_Station_shop_%E6%97%A9%E8%B5%B7%E9%BB%9E_ZaoQiDian_%E6%97%A9%E9%A4%90_breakfast_%E5%8C%85%E9%BB%9E_bao_n_food_%E5%8F%89%E7%87%92%E5%8C%85_September_2024_R12S_09.jpg) |
| P12 | sandwich_combo.jpg | 深圳同类产品实拍：福田连城新天地三明治及饮品（2024年3月） | Mam 302 iGRean | [CC0](https://creativecommons.org/publicdomain/zero/1.0/) | [Wikimedia档案](https://commons.wikimedia.org/wiki/File:SZ_%E6%B7%B1%E5%9C%B3_Shenzhen_%E7%A6%8F%E7%94%B0_Futian_%E9%80%A3%E5%9F%8E%E6%96%B0%E5%A4%A9%E5%9C%B0_Link_City_mall_%E5%A4%A7%E5%AE%B6%E6%A8%82%E5%BF%AB%E9%A4%90_Cafe_de_Coral_Restaurant_food_Salad_Sandwich_n_yellow_cup_of_milktea_March_2024_R12S_02.jpg) |
| P13 | sandwich.jpg | 深圳同类产品实拍：福田连城新天地三明治（2024年3月） | Mam 302 iGRean | [CC0](https://creativecommons.org/publicdomain/zero/1.0/) | [Wikimedia档案](https://commons.wikimedia.org/wiki/File:SZ_%E6%B7%B1%E5%9C%B3_Shenzhen_%E7%A6%8F%E7%94%B0_Futian_%E9%80%A3%E5%9F%8E%E6%96%B0%E5%A4%A9%E5%9C%B0_Link_City_mall_%E5%A4%A7%E5%AE%B6%E6%A8%82%E5%BF%AB%E9%A4%90_Cafe_de_Coral_Restaurant_food_%E6%B2%99%E5%BE%8B%E4%B8%89%E6%96%87%E6%B2%BB_Salad_Sandwich_March_2024_R12S_01.jpg) |

## 视觉选型及限制

逐张浏览全图/联系表排除不相关主体和可识别未成年人；不移除原始时间戳，不做改变事实的修饰。建议优先采用 P01（社区街景）、P02（市场）、P04/P07（餐饮门面）、P08（零食零售）、P09（小空间）、P11（叉烧包）、P12（轻食套餐）。P09严格是摊位参考，不是共享厨房证据；如果需要“分时租赁/共享设备”照片，可使用用户批准的写实生成方案并标注 AI 场景示意（不是福海真实门店）。模型和生意判断一律以研究原始证据及标明假设的数据为准。

本轮只有可见真实照片与开放许可，未通过现场拍照或用户访谈。所有具体当前门店状态须现场复核。
