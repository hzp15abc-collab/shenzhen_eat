# 最佳实践库（检索、阅读、落地规则）
采集日期 2026-11-27；专业方法来源是海外权威机构，使用其市场研究/图表/财务方法，不直接套用海外税制和地方监管。

## 商业研究
- 来源：美国小企业管理局（SBA）商业规划指南，https://www.sba.gov/counseling/plan-your-business/ 。方法包含市场研究、竞争分析、按一次性费用与月费拆创业资金、测算盈亏平衡。用于本项目：统一证据表、标记推断、设保守/基础/较佳三个情景，固定成本与变动成本分开，固定成本÷每单贡献=保本订单，产品组合用加权贡献。现金储备单独建模，不将押金当作当期费用，不把老板无薪工作当利润。
- 需求调研的两级结构：区域统计作为规模上界；面向整个商业街普通公众，采用匿名、汇总客流计数与自愿成年消费者调查。记录日期、天气、统一计数区间、样本量、是否工作日；停止记录个人身份或任何未成年人移动轨迹。真实销售小试应记录交易总数、自然复购、退货、商品成本及废弃，不以好评数替代。
- 同类竞争按产品、价格、卫生、排队/交付时间、营业时段、渠道、社区服务评估；每个商户/商铺以名称地址和原始平台ID去重。租金广告与实付分开，转让费未披露不填0，索引更新不代表挂牌发布时间。严格区分街道、社区及同名地块。
- 5P不是五段独立陈述：Product（产品及产能），Price（价格及贡献），Place（空间及流量），Promotion（成人购买决策、透明公示及邻里信任），People（所有客户群、老板/合伙人/员工知识与能力）。对每个经营模式填写同一字段，防止只比较表面营业额。
- 把需求×转化×复购作为情景参数而非现场已测数据；避免循环重复计算复购和交易量。模型复算要覆盖边界（零订单、毛利恶化、旺淡季、退出、租约、现金不足及业主机会成本）。

## 易读可访问图文报告
- UK Government Analysis Function, Accessible charts checklist，2023-05-02，https://analysisfunction.civilservice.gov.uk/policy-store/charts-a-checklist/ 。借鉴：减少背景纹理、无意义3D和背景；清晰单位、坐标、系列名称；字体清楚，标签水平；控制辅助网格；让读者一眼看懂图的含义。
- UK Government Analysis Function, data visualisation colours，2021-11-23，2026-02-12更新，https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-colours-in-charts/ 。实施：颜色不能单独承载事实/估算/风险信息，同时使用词语和直接标注，保持对比度。
- UK Government Analysis Function, design and accessibility testing，https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-testing-dashboards-for-design-and-accessibility/ 。借鉴：指标优先级、留白、少量一致字体及配色、表格作为图表数据备份，输出可读数值。
- 项目设计标准：封面+一页决策总览；章节用“为什么/看到什么/意味着什么/什么仍未确定”的顺序；讲清营业额、毛利、实际利润、现金流、回本的区别；每张图有单位、时间、数据范围和来源/假设；事实/情景/待验证不同文字标签。门店/产品图为概念示意时明确，不伪装本地实拍。地图示意仅商业商圈类型与公开商业设施，不制作学生路线。采用手机可读字号及足够留白。
- 技术候选：matplotlib 公开项目 https://github.com/matplotlib/matplotlib ；WeasyPrint 项目和样张库 https://github.com/Kozea/WeasyPrint 、https://github.com/CourtBouillon/weasyprint-samples 。当前采用已实测中文输出的 ReportLab，图表可直接由财务CSV再生；渲染最终 PDF 检查每页字体、重叠、边距、图表与页脚，再做独立数字复核。
