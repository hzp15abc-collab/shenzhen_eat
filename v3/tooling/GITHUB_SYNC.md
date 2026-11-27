# V3 冻结研究与模型源文件同步记录

- 仓库：[hzp15abc-collab/shenzhen_eat](https://github.com/hzp15abc-collab/shenzhen_eat)，`main` 分支。
- 日期：2026-11-27。
- 本批次 28 个研究、证据、财务模型、设计原型与情景模拟器文本文件均成功写入，并逐一回读 GitHub blob SHA，与本地原始字节计算出的 Git blob SHA 完全一致。
- 大型生成物（逐月数据、完整报表 JSON、PDF、图像和二进制字体等）不在本批次；本地完整项目包及模型生成脚本保留可复算数据。根目录目标与流程、正式 PDF 构建器、独立审查、项目主页等由总控另行同步。

| 路径 | 原始字节 | 提交 SHA | 已验证 blob SHA |
|---|---:|---|---|
| `v3/research/MARKET_RENT.md` | 19849 | `87725b0c521b9bf7a2d25f4d4a0cc9db9c5aeed9` | `fe3e0416c3b4be0160625ccfc55833f42f2c34ae` |
| `v3/research/COSTS.md` | 20114 | `3f9a384bd767680d429b4d30f6a214e71c554b18` | `8a46dd027a3cb73ff7c20a0510f173c21417061b` |
| `v3/research/LABOR_CAPACITY.md` | 18922 | `28477ce1b137e89ea9f02620eff3254d7e7eebf9` | `6b6ea1c923969c28c0bcf32fdf63740983ca110e` |
| `v3/research/DELIVERY.md` | 20358 | `ee94fae8350e575e7b8c5754829e4cd06cb79f33` | `099bb828df312415ae7f0955f9e3ec05ce7dfde3` |
| `v3/evidence/market_rent.csv` | 5390 | `e5c29007395b7dff0e1e1333669620d21c13c454` | `aeff5bcc57ac6257665b83543d14f26bcf076202` |
| `v3/evidence/market_assumptions.json` | 6868 | `2440b29ced217b2a94b854f6a65ec67e31c5bb3a` | `2422514674297be697f43a3123466b8e69c7cc5c` |
| `v3/evidence/labor_capacity.json` | 16258 | `d20f76c83a9b05626d56ce47a901da27742e21c6` | `3337f83d4d9234a9398e0db4e2b8095a460b6889` |
| `v3/evidence/delivery_params.json` | 17677 | `1eecf9ab22e5e151634f69eafededd51beebb17f` | `e086690c5e968f22d38bbb087b0fbb9f25b332f4` |
| `v3/evidence/startup_costs.json` | 74756 | `1eee05776d6278bc1b2d3ac41eaef6ced0b80537` | `2db21e9917626acaab56f79aeb94cbd1d1ba6fba` |
| `v3/models/model_v3.py` | 35747 | `543f6ad6913b2e08cb202582fb8c58f09255d37d` | `8ad2122a230b4501b5c418823c5be88b1adc8784` |
| `v3/models/build_startup_costs.py` | 9030 | `49da8fd7fd5135473819fa5b123c0f69c326e170` | `d0276fd480fc2af05e52120719b8f51cdd42b027` |
| `v3/models/MODEL_SPEC.md` | 14479 | `137f187e0f61fa831f9be0cf15c2ff954c03ac6a` | `35be5c9a561c9748c4273e752affbfab3778c081` |
| `v3/models/VALIDATION.txt` | 679 | `7b4b96cd844fd3e3906b53f0e5314b466b44c654` | `d940ed57d76e9d8fad5c27ce9ee2ce0e7fe370a4` |
| `v3/models/validate_v3.py` | 3790 | `4d5e928fd78e6b605362163c047eabf5f5cf3640` | `454c6d5e50b7e24686c1947d093d998f766b66c3` |
| `v3/models/CSV_VALIDATION.txt` | 121 | `bb28be163bb49459002ac9f19cd5c0c8400947d7` | `4b71d4db58c08b7078ae541dabb8152e28a44c00` |
| `v3/models/sensitivity_v3.csv` | 8877 | `0e5ae0898f3c67b1e0223b78c8b9c739a4d62690` | `9f15e5d1dfd53fe29ed843fa6b5ec6ca9221446f` |
| `v3/models/skilled_cook_v3.py` | 2542 | `4270dca4ab347e3746699d2e6ffb3195de74a202` | `1d90ea1f21687a48636b7c8646baf72e916cbe94` |
| `v3/models/skilled_cook_sensitivity_v3.csv` | 1966 | `648b136c844d51687024b19659b85804fe5ec285` | `e072e40063ba136fbf0f29e90f28668485630334` |
| `v3/models/skilled_cook_sensitivity_v3.json` | 4493 | `b27688394a934eff29ad946e3b6b4b4ea4bc0e01` | `bf1c58008295b148298109d57a0231edfcc4988b` |
| `v3/models/unit_economics_v3.csv` | 15020 | `a8397fd8c68e02669a5e41966804978e1911a2ab` | `d8b81455760b0e9095a034115c91059938e744de` |
| `v3/design/VISUAL_BEST_PRACTICES.md` | 18051 | `be3580c1f74f889a8ef5d0e09ab245578c5132fb` | `f92280fbb260766c9aee7a91db6274a1022d21b9` |
| `v3/prototypes/build_v3_prototypes.py` | 16666 | `68652de439d087d9b388acd517cde6eecf229935` | `d97de0f76d12b67e4dca0fdf139c09535189ae96` |
| `v3/prototypes/benchmark_metrics.json` | 1583 | `6b9864bf4001c608142663056b5fe61d44cd3c63` | `7f340648fcf640e0490d290ddb41f49e599d178a` |
| `v3/design/build_explorer.py` | 39841 | `001a44809c7cc57d8c17f471af1f00e8c940780b` | `237321f396fb4bca56494654259f19c4d85c071f` |
| `v3/design/EXPLORER.md` | 3670 | `cf9e68c7094c8ec0e88b65b5b6618ffb5c9411b1` | `2bbb37c5047a498c9b1013e41043453c0048cabb` |
| `v3/design/test_explorer.py` | 4660 | `62d53018bdfd22fb39244fee7b89148dcb8846f5` | `248c71adacf3a0b180402198d4469b5a2e5da69d` |
| `v3/design/test_explorer_node.js` | 4202 | `baa08953af43db434b768c07e14054ee029884cc` | `a58f44d3a600ee4f65c7831b114af72ce8b47dd7` |
| `v3/design/EXPLORER_VALIDATION.txt` | 643 | `9846ed0142c8bd3e6a0353629361ed288942d98a` | `6210a6d88248b7d858d259a020e21e3b02e3a05e` |

结果：28/28，全部验证通过。

