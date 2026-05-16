# ConnLab Phase 6 瀹炴柦鏂规锛歄utlook Email Package Intake銆丄pplication Form Selection And Human Confirmation

> 鏈増鏍规嵁鐪熷疄涓氬姟琛ュ厖杩涜鏇存柊锛欳onnLab 椤圭洰鐨勭湡瀹炶捣鐐归€氬父涓嶆槸鍗曠嫭鐨?Word 鐢宠鍗曪紝鑰屾槸瀹㈡埛/鍐呴儴 requestor 閫氳繃 Outlook 鍙戦€佺殑涓€灏侀偖浠躲€傞偖浠朵腑鍙兘鍖呭惈鐢宠鍗曘€佽鏍间功銆佸浘鐗囥€佽ˉ鍏呰鏄庢垨澶氫釜鍊欓€夌敵璇峰崟銆侾hase 6 搴斿洿缁曗€滈偖浠跺寘瀵煎叆 鈫?闄勪欢鍒楄〃 鈫?浜哄伐閫夋嫨鐢宠鍗?鈫?瑙ｆ瀽鑽夌 鈫?浜哄伐纭 鈫?鍒涘缓椤圭洰鈥濋噸鏋?intake 杈圭晫銆?
---

## 0. 鏈増鍏抽敭淇

鐩歌緝涓婁竴鐗?`Real Email/Word Intake And Human Confirmation`锛屾湰鐗堝仛鍑轰互涓嬭皟鏁达細

1. **Phase 6 涓荤嚎浠庘€淓mail/Word Intake鈥濈粏鍖栦负鈥淥utlook 閭欢鍖呭鍏?+ 鐢宠鍗曢€夋嫨 + 浜哄伐纭鈥濄€?*
2. **鏄庣‘涓€浠界敵璇峰崟鍒涘缓涓€涓」鐩?*锛屼笉鑳界畝鍗曡璁℃垚鈥滀竴灏侀偖浠?= 涓€涓」鐩€濄€?3. **鏂板 `IntakePackage 鈫?IntakeAsset 鈫?IntakeCase` 缁撴瀯**锛屾敮鎸佷竴灏侀偖浠堕噷娌℃湁鐢宠鍗曘€佷竴涓敵璇峰崟銆佸涓敵璇峰崟涓夌鎯呭喌銆?4. **淇濈暀鐩存帴瀵煎叆 Word 鐢宠鍗曠殑鐗规畩鍏ュ彛**锛屼絾鍐呴儴浠嶈蛋缁熶竴 Intake 娴佺▼銆?5. **鏂板 OfficeFacade / Office Integration Boundary**锛岀粺涓€绠＄悊 Outlook銆乄ord銆丒xcel 鐩稿叧璇诲彇銆佹彁鍙栥€佽浆鎹㈠拰鍚庣画 COM fallback锛岄伩鍏嶅悇鍔熻兘妯″潡鍚勮嚜鎿嶄綔 Office銆?6. **Phase 6 鏆備笉鍋?Outlook Inbox 鑷姩鎵弿鎴?Outlook COM 鑷姩璇诲彇褰撳墠閭**锛屽厛鏀寔鐢ㄦ埛瀵煎叆 `.msg` 鏂囦欢锛岄檷浣庝笌鐢ㄦ埛姝ｅ湪浣跨敤鐨?Outlook 鍐茬獊椋庨櫓銆?7. **Parser hardening 浠嶆槸蹇呰鍒囩墖**锛屼絾瀹冩湇鍔′簬閭欢鍖?intake锛岃€屼笉鏄嫭绔嬫垚涓?Phase 6 涓荤嚎銆?8. **楂橀闄╀换鍔″繀椤绘媶灏忔墽琛?*锛歚.msg` 瀵煎叆鍏堝仛鍘熸枃浠跺叆搴撳拰鏈€灏?metadata锛屽啀鍋氶檮浠舵彁鍙栵紝鏈€鍚庡仛鐪熷疄鏍锋湰鍏煎銆?9. **Phase 6 UI 涓嶄竴娆℃€у仛瀹屾暣 Intake Review**锛欼nbox銆丳ackage Detail銆丆ase Review 鍒嗕换鍔¤惤鍦般€?10. **TASK_026 鍙缓绔?Office 杈圭晫鍜?Word gateway 鏈€灏忚鍙栬兘鍔?*锛孍xcel 鍙繚鐣欒竟鐣屽崰浣嶏紝涓嶆彁鍓嶅疄鐜版祴璇曠粨鏋滄垨 workbook 涓氬姟璇诲彇銆?
---

## 1. 褰撳墠鐘舵€佸垽鏂?
鏍规嵁褰撳墠椤圭洰璁″垝锛孭hase 5 宸插畬鎴愶紝Phase 6A 宸茶鏄庣‘鎵瑰噯骞舵縺娲伙紝褰撳墠 active task 涓?`TASK_027B_OUTLOOK_MSG_ATTACHMENT_EXTRACTION`銆?
宸插畬鎴愪富绾胯兘鍔涳細

- FastAPI + SQLite + SQLAlchemy 鍩虹銆?- Project / ApplicationForm / SampleInfo / Precheck / LTR / Folder 棰嗗煙鍩虹銆?- DOCX application form parser 鍒濈増銆?- deterministic precheck engine 鍒濈増銆?- LTR 娉ㄥ唽涓?folder preview/generation銆?- React + TypeScript 鍓嶇 shell銆佸乏渚у鑸€侀」鐩垪琛ㄣ€侀」鐩?workbench stepper銆?- Phase 5 鏂囨。銆佹瀯寤哄拰娴嬭瘯瀹堝崼銆?
褰撳墠鍏抽敭闄愬埗锛?
- 褰撳墠 intake 鏇存帴杩戔€滈」鐩唴涓婁紶 DOCX 鍚庣洿鎺ヨ惤搴撯€濓紝娌℃湁鈥滆В鏋愮粨鏋滃彧鏄崏绋裤€佷汉宸ョ‘璁ゅ悗鎵嶆垚涓烘潈濞佹暟鎹€濈殑杈圭晫銆?- 褰撳墠 parser 瀵圭湡瀹?Word 琛ㄥ崟浠嶄笉澶熺ǔ锛岀壒鍒槸 header/footer銆佸悎骞跺崟鍏冩牸銆佸鏍囩鍚屽崟鍏冩牸銆佹牱鍝佽〃澶村埆鍚嶃€?- 褰撳墠 FileAsset 寮虹粦瀹?Project锛屾棤娉曡嚜鐒惰〃杈锯€滆繕娌℃湁椤圭洰銆佸厛鏀跺埌涓€灏侀偖浠?涓€缁勯檮浠垛€濈殑 Intake Inbox銆?- 褰撳墠娴佺▼娌℃湁琛ㄨ揪鈥滀竴灏侀偖浠跺涓檮浠躲€佸浠界敵璇峰崟鍊欓€夈€佷汉宸ラ€夋嫨鍏朵腑涓€浠界敵璇峰崟寮€鍚」鐩€濈殑涓氬姟瑙勫垯銆?- 褰撳墠 PrecheckEngine 鏀寔 `registered_attachments` 鍙傛暟锛屼絾 service 杩愯 precheck 鏃舵病鏈夋妸椤圭洰闄勪欢浼犺繘鍘汇€?- 褰撳墠鍓嶇 `ProjectWorkbenchPage.tsx` 宸茶緝閲嶏紝Phase 6 缁х画鍔?UI 鍓嶅簲鎷嗗嚭 Intake 椤甸潰涓?review components銆?
---

## 2. 鐪熷疄涓氬姟闇€姹傞噸杩?
鐪熷疄涓氬姟鍏ュ彛濡備笅锛?
```text
Outlook 閭欢
  鈹溾攢鈹€ 閭欢涓婚 / 鍙戜欢浜?/ 鏀朵欢浜?/ 鎶勯€佷汉 / 姝ｆ枃
  鈹溾攢鈹€ 闄勪欢 1锛歐ord 鐢宠鍗曞€欓€?  鈹溾攢鈹€ 闄勪欢 2锛歅DF 瑙勬牸涔?/ 瀹㈡埛瑙勮寖 / supporting document
  鈹溾攢鈹€ 闄勪欢 3锛氬浘鐗?/ 閭欢绛惧悕鍥?/ 鍏朵粬鏉愭枡
  鈹斺攢鈹€ 鍙兘瀛樺湪澶氫釜 Word 鐢宠鍗曪紝鎴栧畬鍏ㄦ病鏈夌敵璇峰崟
```

褰撳墠浜哄伐娴佺▼鏄細

```text
1. 浜哄伐浠?Outlook 閭欢涓彟瀛橀檮浠躲€?2. 浜哄伐鍒ゆ柇鍝竴涓?Word 鏂囦欢鏄敵璇峰崟銆?3. 浜哄伐鎵撳紑骞剁‘璁?Word 鐢宠鍗曘€?4. 涓€浠界敵璇峰崟鍒涘缓涓€涓」鐩€?5. 鍐嶈繘鍏?LTR銆佹枃浠跺す銆丳recheck銆丮atrix銆乀est Record銆丷eport 绛夊悗缁祦绋嬨€?```

鏈熸湜杞欢娴佺▼鏄細

```text
1. 鐢ㄦ埛瀵煎叆 Outlook 閭欢鏂囦欢锛屼紭鍏堟敮鎸?.msg銆?2. 绯荤粺璇诲彇閭欢鍏冩暟鎹拰姝ｆ枃銆?3. 绯荤粺鎻愬彇闄勪欢骞跺舰鎴愰檮浠跺垪琛ㄣ€?4. 绯荤粺鑷姩鏍囪鍙兘鐨勭敵璇峰崟銆佽鏍间功銆佸浘鐗囥€佸叾浠栨敮鎾戦檮浠躲€?5. 鐢ㄦ埛浜哄伐閫夋嫨鍏朵腑涓€浠界敵璇峰崟銆?6. 绯荤粺瑙ｆ瀽璇ョ敵璇峰崟锛岀敓鎴愰」鐩崏绋裤€?7. 鐢ㄦ埛浜哄伐纭 / 淇鑽夌銆?8. 绯荤粺鍒涘缓 Project + ApplicationForm + SampleInfo銆?9. 绯荤粺鎶婇偖浠躲€佺敵璇峰崟銆佽鏍间功鍜屾敮鎾戦檮浠剁櫥璁颁负椤圭洰璧勪骇銆?10. 椤圭洰杩涘叆鐜版湁 Precheck / LTR / Folder 娴佺▼銆?```

鐗规畩鍏ュ彛锛?
```text
鐢ㄦ埛涔熷彲浠ヤ笉瀵煎叆閭欢锛岀洿鎺ュ鍏?Word 鐢宠鍗曞紑鍚」鐩€?```

璇ョ壒娈婂叆鍙ｄ笉搴斿彟璧蜂竴濂楅€昏緫锛岃€屽簲鍦ㄥ唴閮ㄥ垱寤轰竴涓?`source_type = direct_application_form` 鐨?IntakePackage锛屽苟鑷姩鎶婅 Word 鏂囦欢鏍囪涓?selected application form銆?
---

## 3. Phase 6 鍊欓€夋帓搴忔洿鏂?
| 鍊欓€?| 浠峰€?| 椋庨櫓 | 渚濊禆 | 鏇存柊鍚庡缓璁?|
|---|---:|---:|---|---|
| 6A Real Email/Word Intake + Human Confirmation | 鏈€楂?| 涓珮 | 闇€瑕侀偖浠跺寘妯″瀷銆侀檮浠堕€夋嫨銆佹渶灏?parser 鍔犲浐銆乺eview UI | **浣滀负 Phase 6 涓荤嚎锛屼絾鍛藉悕鍜岃寖鍥村崌绾т负 Outlook Email Package Intake + Application Form Selection** |
| 6B Application Form Parser Hardening | 楂?| 涓?| 渚濊禆鐪熷疄琛ㄥ崟鏍锋湰 | 鎶藉彇蹇呰鍒囩墖骞跺叆 6A锛涘畬鏁?6B 鍙綔涓?Phase 7 |
| 6C Folder Template Configuration UX | 涓?| 浣庝腑 | 渚濊禆纭鍚庣殑椤圭洰鏁版嵁鏇寸ǔ瀹?| Phase 6 鍚庡啀鍋?|
| 6D Precheck Rule Expansion | 楂?| 涓?| 渚濊禆閭欢鍏冩暟鎹€侀檮浠躲€乸arser 鍜岀‘璁ゆ暟鎹彲闈?| 涓嶅缓璁厛鍋氾紱Phase 6 鍙鐣欐暟鎹粨鏋勫拰灏戦噺 bridge |

鎺ㄨ崘缁撹锛?
```text
Phase 6 = Outlook Email Package Intake
        + Application Form Selection
        + Human Confirmation
        + Direct Word Form Import
        + OfficeFacade Boundary
        + 鏈€灏?6B Parser Hardening 鍒囩墖

Phase 7 = 瀹屾暣 6B Parser Hardening 鎴?6C Folder Template Configuration UX
Phase 8 = 6D Precheck Rule Expansion
```

---

## 4. Phase 6 鏍稿績鐩爣

Phase 6 鍙В鍐充竴涓牳蹇冮棶棰橈細

```text
鐪熷疄璇锋眰鏉愭枡杩涘叆绯荤粺鍚庯紝蹇呴』鍏堝舰鎴愬彲瀹￠槄鑽夌锛?鍙湁缁忎汉宸ョ‘璁ゅ悗锛屾墠鍒涘缓/鏇存柊 Project + ApplicationForm + SampleInfo锛?骞惰繘鍏?Precheck / LTR / Folder 娴佺▼銆?```

鍚屾椂锛孭hase 6 瑕佸缓绔嬮暱鏈熷彲鎵╁睍鐨?intake 杈圭晫锛?
```text
Request Source
  鈹溾攢鈹€ Outlook .msg email package
  鈹溾攢鈹€ Direct Word application form
  鈹斺攢鈹€ Future: Outlook selected item / mailbox integration

缁熶竴杩涘叆锛?IntakePackage -> IntakeAsset -> Application Form Selection -> IntakeCase -> Review Draft -> Confirm Project
```

褰撳墠娴佺▼灏嗕粠锛?
```text
Create Project -> Upload DOCX -> Parsed data immediately persisted -> Precheck
```

鍗囩骇涓猴細

```text
Import Email Package / Import Word Form
      鈫?Extract Assets
      鈫?Select Application Form
      鈫?Parse Draft
      鈫?Human Review / Correction
      鈫?Confirm
      鈫?Create Project + ApplicationForm + SampleInfo + FileAssets
      鈫?Precheck -> LTR -> Folder
```

---

## 5. 鍏抽敭鏋舵瀯鍘熷垯

### 5.1 涓€灏侀偖浠朵笉鏄竴涓」鐩?
蹇呴』閬垮厤锛?
```text
EmailPackage = Project
```

鐪熷疄瑙勫垯鏄細

```text
涓€灏侀偖浠跺彲浠ユ病鏈夌敵璇峰崟銆?涓€灏侀偖浠跺彲浠ユ湁涓€浠界敵璇峰崟銆?涓€灏侀偖浠跺彲浠ユ湁澶氫唤鐢宠鍗曘€?涓€浠借纭鐨勭敵璇峰崟鍒涘缓涓€涓」鐩€?```

鍥犳寤鸿缁撴瀯鏄細

```text
IntakePackage             # 涓€娆″鍏ョ殑閭欢鍖呮垨鐩存帴鐢宠鍗曞寘
  鈹溾攢鈹€ IntakeAsset[]       # 閭欢鍘熶欢銆侀檮浠躲€佺洿鎺ヤ笂浼犳枃浠?  鈹斺攢鈹€ IntakeCase[]        # 姣忎釜 case 瀵瑰簲涓€浠借閫変腑鐨勭敵璇峰崟
        鈹斺攢鈹€ confirm 鍚庡垱寤?Project
```

### 5.2 Parser output 涓嶆槸鏉冨▉鏁版嵁

Parser 鐨勭粨鏋滃彧鑳芥槸 draft锛?
```text
parser output -> IntakeDraft -> human review -> confirm -> domain tables
```

绂佹锛?
```text
parser output -> directly create ApplicationForm / SampleInfo
```

### 5.3 Office 鎿嶄綔蹇呴』闆嗕腑鍦?OfficeFacade

绂佹鍚勬ā鍧楃洿鎺ユ搷浣?Office锛?
```text
Intake 妯″潡鑷繁璇?Outlook
Report 妯″潡鑷繁寮€ Word
Matrix 妯″潡鑷繁寮€ Excel
Test Record 妯″潡鑷繁寮€ Excel
Precheck 妯″潡鑷繁璇?Word
```

蹇呴』缁熶竴璧帮細

```text
backend/infrastructure/office/
```

杩欐牱鍙互閬垮厤锛?
- Word/Excel/Outlook COM 瀹炰緥娉勬紡銆?- 鏂囦欢琚攣瀹氥€?- 绋嬪簭璇叧闂敤鎴锋鍦ㄦ墦寮€鐨?Word/Excel/Outlook銆?- 涓嶅悓妯″潡浣跨敤涓嶅悓涓存椂鐩綍銆佸浠界洰褰曘€佽矾寰勭瓥鐣ャ€?- Office 閿欒澶勭悊鍜屾棩蹇楀垎鏁ｃ€?- 鎵撳寘鍚?Office 鍏煎鎬ч棶棰橀毦浠ュ畾浣嶃€?
### 5.4 Phase 6 浼樺厛瑙ｆ瀽 `.msg` 鏂囦欢锛屼笉鐩存帴鎺у埗 Outlook 瀹㈡埛绔?
Phase 6 鏀寔锛?
```text
鐢ㄦ埛浠?Outlook 鍙﹀瓨 .msg锛屾垨鎷栧叆 .msg 鏂囦欢銆?ConnLab 瑙ｆ瀽 .msg 鏂囦欢銆佹彁鍙栨鏂囧拰闄勪欢銆?```

Phase 6 涓嶅仛锛?
```text
鑷姩鎵弿 Outlook Inbox
鑷姩璇诲彇褰撳墠閫変腑閭欢
鑷姩鏍囪閭欢宸插鐞?鑷姩绉诲姩閭欢
鑷姩鍙戦€侀偖浠?```

鍚庣画纭疄闇€瑕?Outlook COM 鏃讹紝涔熷繀椤讳粠 OfficeFacade 鐨?Outlook gateway 杩涘叆銆?
---

## 6. OfficeFacade / Office Integration Boundary 璁捐

### 6.1 鎺ㄨ崘鐩綍

```text
backend/
  infrastructure/
    office/
      __init__.py
      office_facade.py
      office_lifecycle.py
      outlook_msg_gateway.py
      word_document_gateway.py
      excel_workbook_gateway.py
      models.py

  application/
    intake_package_service.py
    intake_confirmation_service.py

  domain/
    intake_models.py

  modules/
    intake/
      application_form_classifier.py
      application_form_parser.py
```

### 6.2 OfficeFacade 璐ｄ换

OfficeFacade 搴旇礋璐ｏ細

```text
1. 璇诲彇 .msg 閭欢鏂囦欢銆?2. 鎻愬彇 subject / sender / recipients / cc / sent time / body text銆?3. 鎻愬彇闄勪欢鍒板彈鎺?intake 鐩綍銆?4. 璇嗗埆闄勪欢鍩虹绫诲瀷锛歞ocx / pdf / xlsx / image / unknown銆?5. 璇诲彇 Word docx 鐨勬鏂囥€佽〃鏍笺€乭eader銆乫ooter銆?6. 浠呬繚鐣?Excel workbook gateway 杈圭晫鍗犱綅锛涘畬鏁?Excel 璇诲彇涓嶅睘浜?Phase 6A 涓荤嚎銆?7. 鍚庣画蹇呰鏃剁粺涓€绠＄悊 pywin32 COM 鐢熷懡鍛ㄦ湡銆?```

OfficeFacade 涓嶈礋璐ｏ細

```text
1. 涓嶅垱寤?Project銆?2. 涓嶅啓 ApplicationForm / SampleInfo銆?3. 涓嶅喅瀹氫笟鍔′笂鏈€缁堝摢涓€浠芥枃浠朵竴瀹氭槸鐢宠鍗曘€?4. 涓嶈繍琛?Precheck銆?5. 涓嶇敓鎴?LTR 鎴栭」鐩枃浠跺す銆?6. 涓嶄粠 UI 鐩存帴璋冪敤銆?```

### 6.3 闃插啿绐佸師鍒?
```text
1. 浼樺厛浣跨敤鏂囦欢绾цВ鏋愬簱锛屼笉鍚姩 Office 绋嬪簭銆?   .docx -> python-docx
   .xlsx -> openpyxl
   .msg  -> msg / ole parser

2. 鎵€鏈夊鍏ユ枃浠跺厛澶嶅埗鍒?data/intake锛屽啀瑙ｆ瀽鍓湰銆?
3. Word/Excel/Outlook COM 鍙兘浣滀负 fallback銆?
4. COM 鐢熷懡鍛ㄦ湡蹇呴』闆嗕腑鍦?OfficeLifecycleManager銆?
5. 涓氬姟妯″潡绂佹鐩存帴 Dispatch Word/Excel/Outlook銆?
6. COM fallback 浣跨敤鐙珛瀹炰緥锛屼笉澶嶇敤鐢ㄦ埛姝ｅ湪鎵撳紑鐨?Office 搴旂敤銆?
7. 鎵€鏈?COM 鎿嶄綔蹇呴』锛?   Visible = False
   DisplayAlerts = False
   ReadOnly = True
   finally Quit

8. Phase 6 涓嶇洿鎺ユ帶鍒剁敤鎴?Outlook 瀹㈡埛绔紝鍙В鏋愮敤鎴峰鍏ョ殑 .msg 鏂囦欢銆?```

### 6.4 鎺ュ彛鑽夋

```python
class OfficeFacade:
    def import_outlook_msg(self, source_path: Path, target_dir: Path) -> ImportedMailPackage:
        ...

    def read_word_document(self, source_path: Path) -> WordDocumentSnapshot:
        ...

    def classify_file(self, source_path: Path) -> OfficeFileClassification:
        ...
```

TASK_026 鐨勮惤鍦拌竟鐣岋細

```text
蹇呴』瀹炵幇锛?- OfficeFileClassification 鏁版嵁缁撴瀯銆?- WordDocumentSnapshot 鏁版嵁缁撴瀯銆?- WordDocumentGateway.read_word_document() 鐨?docx 鏂囦欢绾ц鍙栥€?- OfficeFacade.classify_file()銆?- OfficeFacade.read_word_document()銆?- OutlookMsgGateway / ExcelWorkbookGateway 鐨勫彈鎺ц竟鐣屽崰浣嶃€?
涓嶅緱瀹炵幇锛?- .msg 闄勪欢鎻愬彇銆?- intake 鏁版嵁搴撹〃銆?- Project / ApplicationForm / SampleInfo 鍒涘缓銆?- Excel 娴嬭瘯缁撴灉璇诲彇銆?- Outlook COM 鑷姩鍖栥€?```

```python
@dataclass(frozen=True, slots=True)
class ImportedMailPackage:
    subject: str | None
    sender_name: str | None
    sender_email: str | None
    recipients: list[str]
    cc: list[str]
    sent_at: datetime | None
    body_text: str | None
    attachments: list[ImportedMailAttachment]
```

```python
@dataclass(frozen=True, slots=True)
class ImportedMailAttachment:
    original_name: str
    stored_path: Path
    extension: str
    size_bytes: int
    sha256: str
    content_id: str | None = None
```

```python
@dataclass(frozen=True, slots=True)
class WordDocumentSnapshot:
    paragraphs: list[str]
    tables: list[list[list[str]]]
    headers: list[str]
    footers: list[str]
    raw_text: str
```

---

## 7. 寤鸿鏂板棰嗗煙瀵硅薄

### 7.1 IntakePackage

琛ㄧず涓€娆″鍏ョ殑涓氬姟璇锋眰鍖咃紝鍙潵婧愪簬 Outlook `.msg`銆佺洿鎺?Word 鐢宠鍗曘€佸悗缁?Outlook selected item 鎴栦汉宸ョ櫥璁般€?
寤鸿瀛楁锛?
```text
package_id
source_type: outlook_msg | direct_application_form | manual | future_outlook_item
status: imported | needs_application_form_selection | ready_for_review | partially_confirmed | confirmed | rejected
source_original_name
source_stored_path
subject
sender_name
sender_email
recipients_json
cc_json
received_at
body_text
created_at
updated_at
notes
```

鐘舵€佽鏄庯細

```text
imported
  閭欢鎴栨枃浠跺凡瀵煎叆锛岃祫浜у凡淇濆瓨銆?
needs_application_form_selection
  宸叉湁闄勪欢鍒楄〃锛屼絾杩樻病鏈夐€夊畾鐢宠鍗曪紱鍙兘娌℃湁鍊欓€夛紝涔熷彲鑳芥湁澶氫釜鍊欓€夈€?
ready_for_review
  宸查€夊畾鐢宠鍗曞苟鐢熸垚 IntakeCase / IntakeDraft銆?
partially_confirmed
  涓€灏侀偖浠朵腑宸叉湁閮ㄥ垎鐢宠鍗曠敓鎴愰」鐩紝浣嗕粛鏈夊叾浠栧€欓€夊彲缁х画澶勭悊銆?
confirmed
  鎵€鏈夐渶瑕佸鐞嗙殑 case 宸茬‘璁ゃ€?
rejected
  璇ラ偖浠跺寘鎴栫敵璇峰崟琚汉宸ユ爣璁颁负涓嶅鐞嗐€?```

### 7.2 IntakeAsset

IntakeAsset 鐢ㄤ簬鈥滈」鐩皻鏈‘璁ゅ墠鈥濈殑鏂囦欢鐧昏锛屼笉鐩存帴澶嶇敤 Project-scoped FileAsset銆?
寤鸿瀛楁锛?
```text
asset_id
package_id
original_name
stored_path
extension
mime_type
size_bytes
sha256
asset_role: unknown | email_source | application_form_candidate | selected_application_form | specification | supporting_attachment | inline_image | ignored
candidate_score
content_id
created_at
```

鍏稿瀷瑙掕壊锛?
```text
Word 鐢宠鍗曞€欓€?-> application_form_candidate
琚汉宸ラ€変腑鐨?Word 鐢宠鍗?-> selected_application_form
PDF 瑙勬牸涔?-> specification
閭欢绛惧悕鍥剧墖 -> inline_image / ignored
鍏朵粬鏉愭枡 -> supporting_attachment
鍘熷 .msg -> email_source
```

### 7.3 IntakeCase

涓€浠借閫変腑鐨勭敵璇峰崟瀵瑰簲涓€涓?IntakeCase锛沜onfirm 鍚庡垱寤轰竴涓?Project銆?
寤鸿瀛楁锛?
```text
case_id
package_id
selected_form_asset_id
status: draft_created | needs_review | confirmed | rejected
confirmed_project_id
created_at
updated_at
reviewer_notes
```

閲嶈瑙勫垯锛?
```text
涓€灏侀偖浠跺彲浠ュ垱寤哄涓?IntakeCase銆?姣忎釜 IntakeCase 鏈€澶?confirm 鎴愪竴涓?Project銆?Project 涓嶇洿鎺ョ粦瀹氭暣灏侀偖浠讹紝鑰屾槸缁戝畾纭鍚庣殑 IntakeCase銆?```

### 7.4 IntakeDraft

淇濆瓨 parser 杈撳嚭鍜屼汉宸ヤ慨姝ｈ崏绋裤€?
寤鸿瀛楁锛?
```text
draft_id
case_id
parsed_fields_json
sample_rows_json
requested_testing_json
field_confidence_json
parser_warnings_json
manual_overrides_json
updated_at
```

Phase 6 鍙互鍏堢敤 JSON 瀛?draft锛岄伩鍏嶈繃鏃╄璁″鏉傝〃缁撴瀯锛涚‘璁ゆ椂鍐嶆槧灏勫埌鐜版湁 ApplicationForm 鍜?SampleInfo 琛ㄣ€?
---

## 8. 鏂囦欢瀛樺偍璁捐

瀵煎叆闃舵锛?
```text
data/
  intake/
    {package_id}/
      source/
        original.msg
      attachments/
        {asset_id}__Coolpower HD3.5MM product qualification test Request.docx
        {asset_id}__GS-12-1941_Rev1 CoolPower HD.pdf
        {asset_id}__image003.jpg
      snapshots/
        mail_body.txt
        imported_mail.json
        word_snapshot_{asset_id}.json
```

纭椤圭洰鍚庯細

```text
data/
  projects/
    {project_id}/
      assets/
        original_email.msg
        selected_application_form.docx
        specification.pdf
        supporting_attachment...
```

寤鸿绛栫暐锛?
```text
1. intake 闃舵淇濈暀鍘熷瀵煎叆鏉愭枡锛屼笉淇敼鍘熸枃浠躲€?2. confirm 鍚庡鍒舵垨鐧昏鍒?project assets銆?3. 浣跨敤 sha256 鍘婚噸锛屼絾涓嶈鍥犱负閲嶅悕瑕嗙洊鏂囦欢銆?4. 鎵€鏈夌敤鎴蜂笂浼犳垨閭欢闄勪欢閮借缁忚繃瀹夊叏鏂囦欢鍚嶆竻娲椼€?5. 鍚庣画濡傛灉寮曞叆鏂囦欢鐗堟湰绠＄悊锛孖ntakeAsset 鍜?FileAsset 閮藉彲澶嶇敤 checksum銆?```

### 8.1 IntakeStorage / StorageService 杈圭晫

涓洪伩鍏嶅悗缁瘡涓?task 鑷繁鎷艰矾寰勶紝Phase 6 搴斿湪杩涘叆 `.msg` 闄勪欢鎻愬彇鍜?intake persistence 鍓嶅缓绔嬩竴涓緢钖勭殑鏂囦欢瀛樺偍杈圭晫銆?
寤鸿鍦?`TASK_028A` 钀藉湴锛?
```text
IntakeStorage
  - sanitize_filename(original_name)
  - package_root(package_id)
  - source_dir(package_id)
  - attachments_dir(package_id)
  - snapshots_dir(package_id)
  - copy_source_file(package_id, source_path)
  - copy_attachment(package_id, asset_id, source_path, original_name)
  - sha256(path)
```

鍘熷垯锛?
```text
1. 鎵€鏈夊鍏ユ枃浠跺厛澶嶅埗鍒板彈鎺?data/intake銆?2. 涓嶈鐩栧悓鍚嶆枃浠躲€?3. 涓嶈涓氬姟 service 鏁ｈ惤纭紪鐮佽矾寰勩€?4. confirm 鍒?Project assets 鏃跺鐢ㄥ悓涓€濂楀畨鍏ㄦ枃浠跺悕鍜?checksum 閫昏緫銆?```

---

## 9. Application Form Candidate Detection

绯荤粺搴旇嚜鍔ㄧ粰闄勪欢鎵撳€欓€夊垎锛屼絾涓嶅簲缁曡繃浜哄伐閫夋嫨銆?
瑙勫垯鑽夋锛?
```text
.docx + 鏂囨。鍐呭鍖呭惈 Laboratory Testing Request        +40
.docx + 鏂囨。鍐呭鍖呭惈 SECTION 1 TO BE COMPLETED          +30
.docx + footer/header 鍖呭惈 Form No. E-3718              +30
.docx + 鏂囦欢鍚嶅寘鍚?request / application / form          +10
.docx + 鑳借В鏋愬嚭 requested_by / sample table             +20
.pdf  + 鏂囦欢鍚嶅寘鍚?GS / spec / specification             -> specification
.jpg/.png + content_id 鎴栨枃浠跺悕绫讳技 image003             -> inline_image
鍏朵粬闄勪欢                                                   -> supporting_attachment / unknown
```

杈撳嚭锛?
```text
asset_role
candidate_score
candidate_reasons[]
```

UI 鍙樉绀烘帹鑽愶紝涓嶈嚜鍔ㄥ垱寤洪」鐩€?
---

## 10. 寤鸿 API 鍚堝悓

### 10.1 瀵煎叆鍏ュ彛

```text
POST /api/intake-packages/import
```

鏍规嵁鏂囦欢绫诲瀷鍒嗘祦锛?
```text
.msg  -> Outlook email package
.docx -> Direct Word application form package
鍏朵粬  -> supporting package / rejected with message
```

### 10.2 Package 鏌ヨ

```text
GET /api/intake-packages
GET /api/intake-packages/{package_id}
GET /api/intake-packages/{package_id}/assets
```

### 10.3 閫夋嫨鐢宠鍗?
```text
POST /api/intake-packages/{package_id}/assets/{asset_id}/select-application-form
```

琛屼负锛?
```text
1. 灏嗚 IntakeAsset 鏍囪涓?selected_application_form銆?2. 璋冪敤 Word parser 鐢熸垚 draft銆?3. 鍒涘缓 IntakeCase銆?4. 杩斿洖 case_id銆?```

### 10.4 Case Review

```text
GET   /api/intake-cases/{case_id}
PATCH /api/intake-cases/{case_id}/draft
POST  /api/intake-cases/{case_id}/confirm
POST  /api/intake-cases/{case_id}/reject
```

纭鍔ㄤ綔杩斿洖锛?
```json
{
  "case_id": "...",
  "package_id": "...",
  "project_id": "...",
  "application_form_id": "...",
  "status": "confirmed"
}
```

### 10.5 鍏煎鐜版湁鎺ュ彛

淇濈暀鐜版湁鎺ュ彛锛?
```text
POST /api/projects/{project_id}/application-form
POST /api/application-forms/{application_form_id}/precheck/run
```

浣嗘柊娴佺▼搴斾紭鍏堜粠 Intake confirm 鍒涘缓 ApplicationForm銆?
---

## 11. Parser 鏈€灏忓姞鍥鸿寖鍥?
Phase 6 涓嶅仛鈥滄棤闄愭硾鍖?parser鈥濓紝鍙В鍐崇湡瀹炴牱鏈腑宸叉毚闇茬殑闂锛?
1. 璇诲彇 Word header/footer銆?2. 浠?footer 涓瘑鍒細`Form No. E-3718`銆乣Rev F/Rev H`銆乣Reference doc.`銆乣GS-03-008`銆?3. 鏀寔鍚屼竴鍗曞厓鏍煎唴鐨?`Label: value`銆?4. 鏀寔鐩搁偦鍗曞厓鏍?label/value锛屼絾璺宠繃鍚堝苟鍗曞厓鏍奸噸澶嶅€笺€?5. 鏀寔鏍峰搧琛ㄥ埆鍚嶏細
   - `Part Number / Revision`
   - `Traceability / Manufacturing Lot Info`
   - `Contact Base Material`
   - `Contact Plating`
   - `Contact Lubricant`
   - `Housing Material`
   - `Quantity`
6. 瀵规瘡涓瓧娈佃緭鍑?confidence锛歚high | medium | low | missing`銆?7. 杈撳嚭 parser warnings锛屼緥濡傦細
   - 瀛楁鐤戜技閿欎綅銆?   - 琛ㄦ牸閲嶅鎴栧悎骞跺崟鍏冩牸骞叉壈銆?   - 鍊兼潵鑷?footer/header銆?   - 鏍峰搧琛ㄥご閮ㄥ垎璇嗗埆銆?   - 鏃ユ湡涓庨偖浠舵棩鏈熷樊璺濆紓甯搞€?8. 鏀寔 requested testing 鍖哄煙涓?`Tests to be Performed` 涓?`Applicable Specifications` 鐨勬垚瀵规彁鍙栥€?
Parser 杈撳嚭涓嶅緱鐩存帴钀藉埌 ApplicationForm / SampleInfo锛屽彧鑳借繘鍏?IntakeDraft銆?
---

## 12. Frontend UX 鑼冨洿

### 12.1 瀵艰埅

宸︿晶瀵艰埅寤鸿锛?
```text
Projects
Intake
Precheck
LTR
Folder
Settings
```

### 12.2 Intake Inbox 椤甸潰

璺緞锛?
```text
/intake
```

鍔熻兘锛?
```text
1. Import Outlook Email (.msg)
2. Import Application Form (.docx)
3. Package list
4. Status filter
5. Search by subject / sender / file name
```

鍒楄〃瀛楁锛?
```text
瀵煎叆鏃堕棿 | 鏉ユ簮绫诲瀷 | 涓婚/鏂囦欢鍚?| 鍙戜欢浜?| 闄勪欢鏁?| 鐢宠鍗曞€欓€夋暟 | 鐘舵€?| 鎿嶄綔
```

### 12.3 Intake Package Detail 椤甸潰

璺緞锛?
```text
/intake/packages/{package_id}
```

甯冨眬锛?
```text
[閭欢淇℃伅]
Subject
Sender
Recipients / CC
Received Time
Body Preview

[闄勪欢鍒楄〃]
鏂囦欢鍚?| 绫诲瀷 | 澶у皬 | 绯荤粺鍒ゆ柇 | 鍊欓€夊垎 | 鎿嶄綔

鎿嶄綔锛?- 閫夋嫨涓虹敵璇峰崟
- 鏍囪涓鸿鏍间功
- 鏍囪涓烘敮鎾戦檮浠?- 蹇界暐
- 棰勮 / 涓嬭浇
```

### 12.4 Intake Case Review 椤甸潰

璺緞锛?
```text
/intake/cases/{case_id}
```

甯冨眬锛?
```text
[鍩虹淇℃伅 Review]
Requested By
Phone
Date
Email
Business Unit
Mfg Site
Project #
Requested Completion Date

[鏍峰搧淇℃伅 Review]
Product Name
Part Number
Traceability / Lot
Contact Base Material
Contact Plating
Contact Lubricant
Housing Material
Quantity

[娴嬭瘯闇€姹?Review]
Tests to be Performed
Applicable Specification
Email Body Reference
Supporting Attachments

[绯荤粺鎻愮ず]
Parser warnings
Low-confidence fields
Attachment summary
Date mismatch warning

[鍔ㄤ綔]
Save Draft
Confirm And Create Project
Reject
```

纭鍚庤烦杞細

```text
/projects/{project_id}
```

---

## 13. Attachment-Aware Precheck Bridge

褰撳墠 PrecheckEngine 宸叉湁 `registered_attachments` 鐨勬蹇碉紝浣嗕笂灞?service 娌℃湁鎶?Intake/Project 闄勪欢浼犲叆銆侾hase 6 搴旇ˉ榻愯繖涓ˉ銆?
鐩爣锛?
```text
濡傛灉 requested testing 鎴?email body 涓嚭鐜?see attachment / refer to attachment / 渚濋檮浠讹紝
涓?IntakePackage 鎴?Project 宸茬櫥璁?supporting attachment / specification锛?鍒欎笉鍐嶆姤 attachment missing warning銆?```

寤鸿鏁版嵁鏉ユ簮锛?
```text
1. selected_application_form
2. specification assets
3. supporting_attachment assets
4. email body text
```

Phase 6 鍙仛鏈€灏忔ˉ鎺ワ紝涓嶅睍寮€澶嶆潅瑙勫垯搴撱€傚畬鏁磋鍒欐墿灞曟斁鍒?6D / Phase 8銆?
---

## 14. 浠诲姟鎷嗗垎

### TASK_025 鈥?Phase 6 Scope Revision And Board Activation

鐩爣锛氭寮忔墦寮€ Phase 6锛屽苟鎶婅寖鍥翠慨璁负鐪熷疄涓氬姟鍏ュ彛銆?
鏇存柊 Phase 6 鍚嶇О锛?
```text
Phase 6A - Outlook Email Package Intake, Application Form Selection And Human Confirmation
```

楠屾敹锛?
- `docs/task_board.md` 褰撳墠闃舵鏀逛负 Phase 6A銆?- 鏂板 / 鏇存柊 Phase 6 瀹炴柦璁″垝鏂囨。銆?- 鏄庣‘鍏ュ彛鍖呮嫭 `.msg` 閭欢瀵煎叆鍜岀洿鎺?`.docx` 鐢宠鍗曞鍏ャ€?- 鏄庣‘涓€浠界敵璇峰崟鍒涘缓涓€涓」鐩€?- 鏄庣‘ OfficeFacade 涓?Phase 6 鍩虹璁炬柦杈圭晫銆?- 鍙縺娲?TASK_026锛屼笉鐩存帴缂栫爜鍚庣画浠诲姟銆?
### TASK_026 鈥?Office Integration Boundary

鐩爣锛氬缓绔?OfficeFacade / Office gateway 鍩虹杈圭晫銆?
鏂板锛?
```text
backend/infrastructure/office/
  __init__.py
  office_facade.py
  office_lifecycle.py
  outlook_msg_gateway.py
  word_document_gateway.py
  excel_workbook_gateway.py
  models.py
```

楠屾敹锛?
- application/api/frontend 涓嶇洿鎺?import win32com銆?- application/api/frontend 涓嶇洿鎺?import python-docx銆?- 鎵€鏈?Office 鏂囦欢璇诲彇浠?gateway 杩涘叆銆?- OfficeFacade 浠呰礋璐ｈ鍙栥€佹彁鍙栥€佸垎绫伙紝涓嶈礋璐ｅ垱寤洪」鐩€?- 鍗曞厓娴嬭瘯瑕嗙洊 WordDocumentSnapshot 鍜屽熀纭€ file classification銆?
### TASK_027A 鈥?Outlook `.msg` Source Import And Minimal Metadata

鐩爣锛氬疄鐜?`.msg` 鍘熸枃浠跺鍏ュ拰鏈€灏?metadata 璇诲彇锛涘け璐ユ椂淇濈暀鍘熸枃浠跺苟杩斿洖鏄庣‘閿欒銆?
杈撳嚭锛?
```text
ImportedMailPackage
  subject
  sender_name
  sender_email
  recipients
  cc
  sent_at / received_at
  body_text
  attachments[]  # 鏈换鍔″彲涓虹┖鎴栦粎淇濈暀鍗犱綅锛屼笉瑕佹眰鐪熷疄鎻愬彇
```

楠屾敹锛?
- 鑳藉鍒?`.msg` 鍘熸枃浠跺埌 `data/intake/{package_id}/source/`銆?- 鑳借鍙?subject / sender / body preview 鐨勬渶灏忛泦鍚堬紱濡傛灉瑙ｆ瀽搴撲笉鏀寔鏌愪釜鐪熷疄鏍锋湰锛屽繀椤讳繚鐣欏師鏂囦欢骞剁粰鍑烘槑纭敊璇€?- 涓嶅垱寤?Project銆?- 涓嶈姹傞檮浠舵彁鍙栥€?
### TASK_027B 鈥?Outlook `.msg` Attachment Extraction

鐩爣锛氬湪 `TASK_027A` 鍩虹涓婃彁鍙栭檮浠跺苟褰㈡垚鍩虹 asset 娓呭崟銆?
楠屾敹锛?
- 鑳芥彁鍙栭檮浠跺埌 `data/intake/{package_id}/attachments/`銆?- 鑳借瘑鍒?docx / pdf / jpg/png / xlsx / unknown 绛夊熀纭€绫诲瀷銆?- 鑳借褰曞師濮嬫枃浠跺悕銆佹墿灞曞悕銆乻ize銆乻ha256銆?- 涓嶈嚜鍔ㄩ€夋嫨鐢宠鍗曘€?- 涓嶅垱寤?Project銆?
### TASK_027C 鈥?Real `.msg` Sample Compatibility

鐩爣锛氱敤鐪熷疄 `.msg` 鏍锋湰楠岃瘉缂栫爜銆佸祵鍏ラ檮浠躲€佺鍚嶅浘鐗囥€丱LE 宸紓绛夊吋瀹归棶棰樸€?
楠屾敹锛?
- 鑷冲皯涓€涓湡瀹炴牱鏈彲瀵煎叆骞跺舰鎴愰檮浠舵竻鍗曘€?- 澶辫触鏍锋湰鏈夋槑纭敊璇拰淇濈暀绛栫暐銆?- 涓嶆墿澶у埌 Outlook inbox 鑷姩鎵弿銆?
### TASK_028A 鈥?Intake Storage Boundary

鐩爣锛氬缓绔嬪彈鎺?`data/intake/{package_id}` 鏂囦欢瀛樺偍杈圭晫锛岄伩鍏嶈矾寰勯€昏緫鏁ｈ惤銆?
楠屾敹锛?
- 鎻愪緵瀹夊叏鏂囦欢鍚嶆竻娲椼€?- 鎻愪緵 package/source/attachments/snapshots 鐩綍瑙ｆ瀽銆?- 鎻愪緵 copy + sha256 helper銆?- 涓嶅啓鏁版嵁搴撱€?
### TASK_028B 鈥?IntakePackage / IntakeAsset / IntakeCase Storage

鐩爣锛氭柊澧?intake domain + SQLAlchemy + repositories銆?
鏂板琛細

```text
intake_packages
intake_assets
intake_cases
intake_drafts
```

楠屾敹锛?
- 鏂拌〃鍙敱 init_db 鍒涘缓銆?- repository tests 瑕嗙洊 create/get/list/update銆?- 涓嶇牬鍧忕幇鏈?Project/FileAsset 璇箟銆?- `.msg` 瀵煎叆鍚庤兘淇濆瓨 package + assets metadata銆?- 鐩存帴 `.docx` 瀵煎叆鍚庝篃鑳戒繚瀛?package + selected form asset metadata銆?
### TASK_029 鈥?Application Form Candidate Detection

鐩爣锛氬閭欢闄勪欢杩涜鍊欓€夎瘑鍒拰鎵撳垎銆?
楠屾敹锛?
- Word 鐢宠鍗曡兘鏍囪涓?`application_form_candidate`銆?- PDF 瑙勬牸涔﹁兘鏍囪涓?`specification`銆?- 閭欢绛惧悕鍥剧墖鑳芥爣璁颁负 `inline_image` 鎴?`ignored`銆?- 杈撳嚭 candidate_score 鍜?candidate_reasons銆?- 澶氫釜鍊欓€夋椂涓嶈嚜鍔ㄩ€夋嫨锛屽繀椤荤敱鐢ㄦ埛纭銆?
### TASK_030 鈥?Form Selection And Draft Creation

鐩爣锛氱敤鎴烽€夋嫨鏌愪釜闄勪欢浣滀负鐢宠鍗曞悗锛屽垱寤?IntakeCase 骞剁敓鎴?IntakeDraft銆?
娴佺▼锛?
```text
selected IntakeAsset
  -> WordDocumentGateway.read_word_document
  -> ApplicationFormParser.parse
  -> IntakeDraft
  -> IntakeCase(status = needs_review)
```

楠屾敹锛?
- 涓€灏侀偖浠跺彲浠ュ垱寤哄涓?IntakeCase銆?- 姣忎釜 IntakeCase 瀵瑰簲涓€浠?selected application form銆?- parser 杈撳嚭 confidence/warnings銆?- draft 鍙 PATCH 淇敼銆?- 涓嶅垱寤?Project锛岀洿鍒?confirm銆?
### TASK_031A 鈥?Intake Inbox Frontend UX

鐩爣锛氭縺娲?Intake 瀵艰埅锛屾彁渚?Inbox 鍜屽鍏ュ叆鍙ｃ€?
楠屾敹锛?
- 鐢ㄦ埛鑳藉鍏?`.msg`銆?- 鐢ㄦ埛鑳藉鍏?`.docx` 鐩存帴鐢宠鍗曘€?- 鐢ㄦ埛鑳界湅鍒?package list銆?- 鏀寔鎸?subject / sender / file name 鎼滅储銆?- 涓嶅疄鐜?case review 琛ㄥ崟銆?
### TASK_031B 鈥?Intake Package Detail Frontend UX

鐩爣锛氭彁渚涢偖浠朵俊鎭拰闄勪欢鍒楄〃椤甸潰銆?
楠屾敹锛?
- 鐢ㄦ埛鑳界湅鍒伴偖浠朵俊鎭拰闄勪欢鍒楄〃銆?- 鐢ㄦ埛鑳界湅鍒扮郴缁熸帹鑽愮殑鐢宠鍗曞€欓€夈€?- 鐢ㄦ埛鑳戒汉宸ラ€夋嫨鐢宠鍗曘€?- 涓嶅疄鐜板畬鏁?draft editing銆?
### TASK_031C 鈥?Intake Case Review Frontend UX

鐩爣锛氭彁渚?draft review / edit / confirm 椤甸潰銆?
楠屾敹锛?
- 鐢ㄦ埛鑳界湅鍒?parser warnings 鍜?low-confidence 瀛楁銆?- 鐢ㄦ埛鑳戒慨鏀瑰瓧娈?鏍峰搧琛屻€?- 鐢ㄦ埛鐐瑰嚮 Confirm 鍚庤繘鍏?project workbench銆?
### TASK_032 鈥?Confirm Intake Case To Project

鐩爣锛氫汉宸ョ‘璁ゅ悗鎵嶇湡姝ｅ垱寤洪」鐩暟鎹€?
confirm 鍚庡垱寤猴細

```text
Project
ApplicationForm
SampleInfo
FileAsset
```

闇€瑕佺櫥璁颁负 Project FileAsset 鐨勫唴瀹癸細

```text
鍘熷 .msg
閫変腑鐨勭敵璇峰崟 docx
瑙勬牸涔?PDF
鍏朵粬 supporting attachments
```

楠屾敹锛?
- Confirm 鍓嶆病鏈?Project銆?- Confirm 鍚庣敓鎴?Project 骞惰烦杞埌 Project Workbench銆?- ApplicationForm / SampleInfo 鏉ヨ嚜浜哄伐纭鍚庣殑 draft锛岃€屼笉鏄?parser raw output銆?- IntakeCase 璁板綍 confirmed_project_id銆?- 鍚屼竴灏侀偖浠跺涓?IntakeCase 鍙互鍒嗗埆 confirm 鎴愬涓?Project銆?
### TASK_033 鈥?Direct Word Application Form Import

鐩爣锛氭敮鎸佺粫杩囬偖浠讹紝鐩存帴瀵煎叆 Word 鐢宠鍗曞紑鍚」鐩崏绋裤€?
鍐呴儴娴佺▼锛?
```text
.docx upload
  -> IntakePackage(source_type = direct_application_form)
  -> IntakeAsset(role = selected_application_form)
  -> IntakeCase
  -> IntakeDraft
  -> Review UI
  -> Confirm Project
```

楠屾敹锛?
- 鐩存帴涓婁紶 `.docx` 涓嶈蛋鏃х殑 project-scoped upload 鍏ュ彛銆?- 鐩存帴鐢宠鍗曞拰閭欢鐢宠鍗曚娇鐢ㄥ悓涓€涓?review / confirm 娴佺▼銆?- 鍚庣画 Precheck/LTR/Folder 涓庨偖浠跺叆鍙ｄ竴鑷淬€?
### TASK_034 鈥?Attachment-Aware Precheck Bridge

鐩爣锛氭妸 Intake / Project attachments 杩炴帴鍒?PrecheckEngine 鐨?`registered_attachments`銆?
楠屾敹锛?
- 濡傛灉 requested testing 鎴?email body 鍖呭惈闄勪欢寮曠敤锛屼笖闄勪欢宸茬櫥璁帮紝涓嶅啀璇姤缂哄け闄勪欢銆?- 濡傛灉鏃犻檮浠讹紝浠嶄繚鐣?warning銆?- API 鍜?unit tests 瑕嗙洊銆?- 涓嶆墿灞曞ぇ瑙勬ā瑙勫垯搴撱€?
### TASK_035 鈥?Phase 6 Validation And Docs Sync

鐩爣锛氭敹灏?Phase 6 鏂囨。銆佹祴璇曘€佹墜鍔?smoke checklist銆?
楠屾敹锛?
- backend pytest 閫氳繃銆?- frontend build 閫氳繃銆?- manual frontend smoke checklist 鏇存柊銆?- `docs/task_board.md` 鏍囪 Phase 6A 瀹屾垚鎴栧噯纭?blocked銆?- 缁欏嚭 Phase 7 鎺ㄨ崘銆?
---



## 15. 鏄庣‘涓嶅仛

Phase 6 涓嶅仛锛?
- Outlook COM 鑷姩璇诲彇閭銆?- Outlook Inbox 鑷姩鎵弿銆?- 鑷姩鏍囪閭欢宸插鐞嗐€?- 鑷姩鍙戦€侀偖浠躲€?- Matrix銆?- Test Record銆?- Report銆?- AI Review銆?- Excel 娴嬭瘯缁撴灉瀵煎叆銆?- 澶氱敤鎴锋潈闄愭垨 LAN 閮ㄧ讲銆?- 瀹屾暣 folder template registry UX銆?- 澶ц妯?precheck rule expansion銆?- 澶嶆潅杩佺Щ绯荤粺锛涘綋鍓嶄粛鍙娇鐢?init_db + SQLite dev flow銆?
---

## 16. Phase 6 瀹屾垚瀹氫箟

Phase 6 瀹屾垚鏃讹紝绯荤粺搴旀敮鎸佷互涓嬫墜鍔ㄤ笟鍔￠棴鐜細

```text
1. 鐢ㄦ埛瀵煎叆涓€灏?Outlook .msg 閭欢銆?2. 绯荤粺鏄剧ず閭欢涓婚銆佸彂浠朵汉銆佹鏂囬瑙堝拰闄勪欢鍒楄〃銆?3. 绯荤粺鎺ㄨ崘鐢宠鍗曞€欓€夊拰瑙勬牸涔﹂檮浠躲€?4. 鐢ㄦ埛閫夋嫨涓€浠?Word 鐢宠鍗曘€?5. 绯荤粺瑙ｆ瀽鐢宠鍗曞苟鐢熸垚鍙紪杈戣崏绋裤€?6. 鐢ㄦ埛淇瀛楁鍜屾牱鍝佽銆?7. 鐢ㄦ埛鐐瑰嚮 Confirm銆?8. 绯荤粺鍒涘缓 Project + ApplicationForm + SampleInfo銆?9. 绯荤粺鐧昏鍘熷閭欢銆佺敵璇峰崟銆佽鏍间功鍜屾敮鎾戦檮浠躲€?10. 鐢ㄦ埛杩涘叆 Project Workbench 骞剁户缁?Precheck / LTR / Folder銆?```

鍚屾椂鏀寔锛?
```text
鐢ㄦ埛鐩存帴瀵煎叆 Word 鐢宠鍗曪紝涔熻兘杩涘叆鍚屼竴涓?Review / Confirm / Create Project 娴佺▼銆?```

---

## 17. Phase 7 鎺ㄨ崘鏂瑰悜

Phase 6 瀹屾垚鍚庯紝鎺ㄨ崘 Phase 7 浜岄€変竴锛?
### 鏂瑰悜 A锛氬畬鏁?Phase 6B Parser Hardening

閫傚悎鍦ㄧ湡瀹炴牱鏈鍔犲悗鍋氾細

```text
1. 鏇村鐢宠鍗曠増鏈吋瀹广€?2. 鏇村己琛ㄦ牸缁撴瀯璇嗗埆銆?3. 瀛楁鍐茬獊妫€娴嬨€?4. 澶氳瑷€ / 涓嫳鏂囨贩鍚?label銆?5. parser fixture library銆?```

### 鏂瑰悜 B锛歅hase 6C Folder Template Configuration UX

閫傚悎鍦?intake 绋冲畾鍚庡仛锛?
```text
1. folder template registry銆?2. LTR/project naming preview銆?3. 瀹㈡埛/BU 缁村害閰嶇疆銆?4. 鐢熸垚璺緞鍙鍖栥€?```

涓嶅缓璁?Phase 7 鐩存帴鍋?6D 澶ц妯¤鍒欐墿灞曪紝闄ら潪 parser 鍜?intake confirmation 宸茬粡绋冲畾銆?
---

## 18. 鎺ㄨ崘鎵瑰噯璇?
鍙互鎶婁笅涓€鏉＄粰 Codex / AI 宸ュ叿锛?
```text
Read AGENTS.md first, then docs/task_board.md.

We are revising Phase 6 based on the real business workflow:
projects usually start from an Outlook email containing one or more attachments.
One selected application form creates one project.
Sometimes users directly import a Word application form without an email.

Approve and start only TASK_025:
Phase 6 Scope Revision for Outlook Email Package Intake,
Application Form Selection,
Human Confirmation,
Direct Word Form Import,
and OfficeFacade Boundary.

Do not implement Matrix, Report, Excel result ingestion, AI review,
Outlook inbox auto scan, email sending, or folder template UX.

Before coding, state:
- current phase
- current active task ID
- why this task is allowed now

After finishing TASK_025, update docs/task_board.md and stop.
```

---

## 19. TASK_026 鎺ㄨ崘鍚姩鎻愮ず璇?
TASK_025 瀹屾垚骞舵洿鏂?task board 鍚庯紝鍙互鍚姩 TASK_026锛?
```text
Read AGENTS.md first, then docs/task_board.md and docs/archive/historical_plans/ConnLab_Phase6_Implementation_Plan.md.

Start TASK_026 - Office Integration Boundary only.

Implement the infrastructure boundary for Office-related reading/extraction:
- backend/infrastructure/office/office_facade.py
- backend/infrastructure/office/office_lifecycle.py
- backend/infrastructure/office/outlook_msg_gateway.py
- backend/infrastructure/office/word_document_gateway.py
- backend/infrastructure/office/excel_workbook_gateway.py
- backend/infrastructure/office/models.py

Do not create Project, ApplicationForm, SampleInfo, IntakePackage tables, UI, Matrix, Report, or Outlook COM automation.

Use file-level parsing first. COM fallback must be centralized and must not touch user-opened Office instances.

Add focused unit tests for file classification and WordDocumentSnapshot extraction.
Update docs/task_board.md when done and stop.
```

---

## 20 Server Upgrade Readiness Principles

铏界劧褰撳墠 ConnLab 浠嶄互鏈湴鍗曚汉浣跨敤涓轰富锛屼絾 Phase 6 涔嬪悗鐨勬牳蹇冧笟鍔℃ā鍨嬨€丄PI銆佹枃浠剁鐞嗗拰 Office 闆嗘垚杈圭晫锛屽繀椤绘寜鐓ф湭鏉ュ彲鍗囩骇涓哄眬鍩熺綉鏈嶅姟鍣?/ 澶氫汉鍦ㄧ嚎绯荤粺鐨勬柟鍚戣璁°€?
鏈樁娈典笉瀹炵幇鏈嶅姟鍣ㄩ儴缃层€佸鐢ㄦ埛鐧诲綍銆佹潈闄愮郴缁熸垨鍦ㄧ嚎鍗忓悓锛屼絾蹇呴』閬垮厤鎶婄郴缁熷啓姝讳负鍗曟満涓撶敤绋嬪簭銆?
鍘熷垯濡備笅锛?
1. 鎵€鏈変笟鍔¤兘鍔涘繀椤讳粠 API / Application Service 杩涘叆锛岀姝㈠墠绔垨 UI 鐩存帴鎿嶄綔鏁版嵁搴撱€丱ffice銆侀」鐩洰褰曟垨涓氬姟鏂囦欢銆?2. 鎵€鏈?Office 鎿嶄綔蹇呴』缁熶竴璧?OfficeFacade锛岀姝?Intake銆丷eport銆丮atrix銆乀est Record銆丳recheck 绛夋ā鍧楀悇鑷洿鎺ヨ皟鐢?Word銆丒xcel 鎴?Outlook銆?3. 鎵€鏈夋枃浠跺繀椤诲厛杩涘叆鍙楁帶 StorageService / AssetRepository 绠＄悊锛岀姝笟鍔′唬鐮佹暎钀界‖缂栫爜鏈湴璺緞銆?4. 鎵€鏈夋暟鎹簱璁块棶蹇呴』璧?Repository锛屼笉鍏佽涓氬姟灞備緷璧?SQLite 涓撴湁琛屼负銆?5. SQLite 鍙綔涓?local desktop 妯″紡鏁版嵁搴擄紱鏈潵 lan_server / web_server 妯″紡搴斿彲鍒囨崲鍒?PostgreSQL銆丮ySQL 鎴?SQL Server銆?6. 鎵€鏈夌‘璁ょ被鍔ㄤ綔蹇呴』棰勭暀 actor銆乼imestamp 鍜?audit log 鎵╁睍鐐癸紝渚嬪閫夋嫨鐢宠鍗曘€佷慨鏀硅崏绋裤€佺‘璁ら」鐩€佺敵璇?LTR銆佺敓鎴愭枃浠跺す銆?7. 鏂板涓氬姟琛ㄥ簲灏介噺棰勭暀 created_at銆乽pdated_at銆乧reated_by銆乽pdated_by銆乿ersion 瀛楁銆?8. Phase 6 涓嶅疄鐜版潈闄愮郴缁燂紝浣嗕笉鑳藉湪涓氬姟閫昏緫涓亣璁炬案杩滃彧鏈変竴涓敤鎴枫€?9. Phase 6 涓嶅疄鐜版湇鍔″櫒閮ㄧ讲锛屼絾鍚庣 service 搴斿敖閲忎繚鎸佹棤鐘舵€侊紝閬垮厤渚濊禆鏌愪釜鍓嶇椤甸潰鎴栨煇涓湰鍦扮獥鍙ｇ姸鎬併€?10. 瑙ｆ瀽缁撴灉姘歌繙鍏堣繘鍏?draft锛岀粡浜哄伐纭鍚庢墠鎴愪负姝ｅ紡 Project / ApplicationForm / SampleInfo 鏁版嵁銆?
---

## 20. Future Server Upgrade Readiness

ConnLab 褰撳墠闃舵浠嶇劧鎸夌収 local desktop / local web app 妯″紡浜や粯锛屽嵆鍗曟満銆佹湰鍦版暟鎹€佹湰鍦版枃浠躲€佹湰鍦?Office 鐜銆備絾绯荤粺鐩爣涓婂簲淇濈暀鏈潵鍗囩骇涓哄眬鍩熺綉鏈嶅姟鍣ㄥ拰澶氫汉鍦ㄧ嚎绯荤粺鐨勮兘鍔涖€?
鎺ㄨ崘婕旇繘璺嚎锛?
```text
闃舵 1锛歀ocal Desktop / Local Web App
- 鍗曚汉浣跨敤
- SQLite
- 鏈湴 data/ 鏂囦欢澶?- 鏈満 OfficeFacade
- 鎵嬪姩瀵煎叆 .msg / .docx

闃舵 2锛歀AN Server
- 澶氫汉娴忚鍣ㄨ闂?- PostgreSQL / MySQL / SQL Server
- 鍏变韩鏂囦欢瀛樺偍
- 鐢ㄦ埛銆佽鑹层€佹潈闄?- 鎿嶄綔鏃ュ織
- 鍚庡彴浠诲姟

闃舵 3锛欶ull LIMS Server
- 澶氬疄楠屽 / 澶氶儴闂?- 瀹℃壒娴?- 鎶ュ憡鍦ㄧ嚎鍗忎綔
- 闃熷垪鍖栦换鍔″鐞?- 闆嗕腑澶囦唤
- SSO / LDAP / OAuth
