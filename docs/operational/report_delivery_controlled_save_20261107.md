# 第6批第一部分：交付检查与受控保存

状态：第6批第一部分开发与独立验收完成；本任务已获自主验收并本地关闭授权，集成／关闭事实以主board／Git为准，不推送。真实资料只读，隔离数据库和文件验证，不自动正式发行。第二部分发行包／异机验收未实施。

## 范围

- 选定内部工作版本与同源客户副本，服务器汇总内容、Matrix覆盖、来源、保密与两份Word视觉审核。
- 本项目原稿允许明确的精确版本内容复核；跨项目区域仍需当前项目证据，确定冲突和缺失结果不被勾选消除。
- 现有publication gateway复用staging、SHA、文件身份与History；只保存审核的现成字节，不重新生成。
- 有限receipt是保存阶段及恢复的唯一权威；authoring JSON投影operation及结果。每个可见文件动作前持久化意图。
- 两文件不声称数据库/文件全原子。部分保存如实显示，恢复只完成未保存项；归属不明停止，保留资料。
- 同项目现有写锁及未完成receipt互斥其他文件写入，恢复同一操作不重新授权更大范围。

## 验收

公开API与页面验证配对、审核失效、显式确认、History、重复请求、部分失败/断线恢复。文件边界验证占用、DB提交失败、身份/manifest/重解析漂移与receipt篡改。新客户Word预览实际逐页检查；保存字节等于审核字节、History等于旧文件；真实原件SHA不变。发行包和异机验收留后续。

## 实现与开发验证

`ReportDelivery`收口交付检查/显式保存/同操作恢复；目的地只由项目ID、已注册workspace、配置根、manifest与目录身份解析，不接收客户端文件路径。报告生成模板、费用资料不牵连保存现成成果。

授权intent先durable提交现authoring JSON，再建立唯一文件receipt；若进程在两者之间中断，恢复只从已提交intent重建同operation，重新核验来源/审核/目的地。receipt记录动作前staging inode与SHA、旧目标inode、确定History位置；新目标只有同时证明owned identity+SHA才可补登记。客户项失败不撤销已保存内部项，也不把部分完成显示为全部完成。旧无receipt发布调用继续原异常回滚语义。

项目writer guard在原锁内以配置数据库的只读短连接检查pending投影，不改变请求session的提交/退出顺序，不建DB、目录、租约或迁移。各文件完成后投影durable提交，整套完成后才释放receipt阻塞。来源/Matrix/实际PDF或目标字节变化使旧保存预览失效。

开发切片已验证真实子进程在归档及目标硬链接后`os._exit`，重启按已登记身份续跑；相同字节但不同inode不被认领；receipt不可变意图/越界staging被拒绝。公开API由真实来源/结果/审核接口建立成功配对，不手工制造passed状态；开发测试的Word／转换边界替身与下述QA真实Word验收分别记录。

QA发现的动作前空History窗口已修复：先记录本operation唯一staging及History路径，再创建staging并登记其inode；复制后刷盘和核验，完整旧文件以hardlink进入History后才撤下旧目标，不再生成空History占位。staged receipt写失败可复用同一临时文件，归档与新目标hardlink后真实进程退出均可恢复。若进程在staging创建与inode登记之间中断，保留唯一已知路径并明确阻塞，不猜测归属、不另建文件或盲删。

明确初始化占位（本系统Conclusions待写句、`[To be assigned]`、`[To be confirmed]`）以具体Word区域位置列为`content_incomplete`；整稿内容确认返回422且不推进版本。历史修订说明出现draft一词不因此失效，不擅自要求所有签名／空白表格都填写。

## 独立验收记录与证据边界

精确产品／测试subject：`97ac12a7e9f0e2880f505dd2ac1e663d87ef8814`。Reviewer与独立QA已完成相关审查／验收；本次文档收尾不改变产品或测试字节，尚未宣称已集成或已关闭。

| 检查 | 实际结果 |
|---|---|
| 初轮受影响Python矩阵 | d822：488通过、6失败；6项legacy API夹具缺少隔离DB，不隐去失败。02a仅修复真实隔离DB夹具。 |
| 最终97ac受影响重验 | workspace／delivery／document-review共39通过，pytest39.34秒；包括此前失败文件的10项。经Reviewer核对复用其余未变化的已通过检查。488与39有重叠，不能相加为独立测试总数，亦不是全仓pytest重跑。 |
| 前端／构建 | Report Workspace 15文件／140测试通过；TypeScript与Vite构建通过，顺序运行。Starlette/httpx既有弃用提示非断言失败。 |
| 真实Word | 正常页面触发Microsoft Word只读渲染；Internal6页、Customer3页各自产生精确PDF。独立QA与Reviewer分别查看全部9页，无目标标题／表格孤立、截断或重叠；已有模板留白／窄列不被宣传为通用最佳版式。 |
| 保密检查 | Reviewer在验收页面逐项审核实际PNG与2个静态PBrush OLE部件的精确哈希；未激活OLE或宏。结论仅限这些具体部件，不自动批准任意嵌入对象或所有材料字段。 |
| 显式确认与真实失败 | 打开保存确认后Escape不写文件／状态；真实Win32客户文件占用使Internal committed、Customer archiving，页面如实显示partial与同操作Resume，不显示整套成功。 |
| 跨进程恢复与重放 | 停止并重启同DB／run，partial与operation不变；释放测试锁后页面Resume完成同一操作。已保存Internal的mtime与archive路径不变；两份保存SHA等于各自审核稿，History等于旧文件，无空档案／重复归档／stage遗留。completed resume返回200，revision28与完整公开状态不变。 |
| 原资料与保真 | 最终198份原资料／历史与本批隔离副本及2份登记模板哈希不变。032保留工作稿全文字节一致；031加密容器SHA变化但60个解密OOXML部件逐个字节一致（032为56个），不能仅因加密容器差异判定内容变动。 |

验收成功案例为独立合成项目，人工明确完成虚构的Purpose／Conclusions／人员等字段；这不是软件自动撰写这些业务结论的证明。真实032／031来源可保真载入，但未确认的旧测量、Pass及特殊接受仍待核，覆盖不完整时禁止保存。

保留失败证据：completed replay的一次QA探针已通过公开状态相等比较，但额外要求内部receipt文件mtime不变而失败。原失败未删除；复核证明receipt原始SHA不变、输出与History的字节／inode／mtime／路径均不变。内部相同字节的原子metadata重写不属于用户文件重生成，不为该非阻塞项扩大修改。

保留证据位于本机`tmp/report_batch6_20261107/`：`final_qa.md`为独立PASS；`qa_97ac12a7/`保留自动测试日志；`actual_visual/`保留各自DOCX／PDF／全页PNG与哈希清单；`root_ui_acceptance.md`为实际操作记录；`actual_saved_pair_150614.json`、`actual_completed_resume_durable_verification.json`及`final_actual_visual_sha_verification.json`核对保存、重放与最终渲染字节。较早progress文档明确只是当时进度，最终结论以`final_qa.md`为准。只正常退出本批拥有的API／Vite／测试锁，证据及数据库保留。

## 剩余边界

- 第二部分发行包／异机Office、路径和资源验证未实施；本机隔离验收不替代异机资格。
- 既有批量装配UI不能指定已存在的结果／附录目标；本次经明确交接，用公开preview／apply绑定唯一实际目标，表格数9→9、无重复附录。因此不宣称全部装配为纯页面路径。相关交互与既有复选框尺寸留后续，不混入当前产品修复。
- 受控保存不是两文件与数据库的全原子事务；partial／恢复保护是实际契约。无法证明staging归属仍停止并保留文件，需要查核，不自动清理。
- 正式实验室发行、未确认的业务决定及真实项目资料覆盖均不在本批授权内。本开发任务已获自主验收并本地关闭授权，不增加人工关闭门禁；执行事实以主board／Git为准，不推送。
