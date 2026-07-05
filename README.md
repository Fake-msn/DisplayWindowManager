# DisplayWindowManager

> 馃枼锔?涓€閿搷鎺у鏄剧ず鍣ㄧ獥鍙?鈥斺€?杞婚噺銆佸厤璐广€佸紑婧?
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-blue)](https://www.microsoft.com/windows)
[![Version](https://img.shields.io/badge/version-v0.51-brightgreen)](https://github.com/Fake-msn/DisplayWindowManager/releases)
[![GitHub Pages](https://img.shields.io/badge/pages-鍦ㄧ嚎浣撻獙-brightgreen)](https://Fake-msn.github.io/DisplayWindowManager/)

---

## 涓轰粈涔堥渶瑕佽繖涓伐鍏凤紵

浣犳槸鍚﹂亣鍒拌繃杩欎簺鍦烘櫙锛?- 鏂紑澶栨帴鏄剧ず鍣ㄥ悗锛岀浜屽睆骞曠殑绐楀彛"鍗?鍦ㄧ湅涓嶈鐨勫湴鏂癸紝鏃犳硶鎷栧洖涓诲睆
- 杩滅▼妗岄潰鍒嗚鲸鐜囦笉鍖归厤锛岀獥鍙ｉ鍒板睆骞曞
- 鏂板紑鐨勭獥鍙ｆ€绘槸璺戝埌涓嶆兂鐢ㄧ殑鏄剧ず鍣ㄤ笂锛岄渶瑕佸弽澶嶆嫋鎷?
**DisplayWindowManager** 灏辨槸涓轰簡瑙ｅ喅杩欎簺闂鑰岀敓銆傚彧闇€涓€閿紙鎴栧揩鎹烽敭 `Ctrl+Shift+M`锛夛紝鍗冲彲灏嗘墍鏈夌獥鍙ｄ粠鍓睆绉昏嚦涓诲睆锛堟垨鍙嶅悜绉诲姩锛夛紝褰诲簳鍛婂埆"鎵句笉鍒扮獥鍙?鐨勭棝鑻︺€?
---

## 鏍稿績鍔熻兘

| 鍔熻兘 | 璇存槑 |
|------|------|
| **涓€閿Щ鍔ㄧ獥鍙?* | 鐐瑰嚮鎸夐挳鎴栨寜 `Ctrl+Shift+M`锛屾壒閲忓皢鎵€鏈夌獥鍙ｇЩ鍔ㄥ埌鐩爣鏄剧ず鍣?|
| **鍙屽悜绉诲姩** | 鏀寔鍓睆鈫掍富灞?鍜?涓诲睆鈫掑壇灞?涓ょ鏂瑰悜锛岄殢鏃跺垏鎹?|
| **鏄剧ず鍣ㄥ睆钄?* | 闃绘鏂扮獥鍙ｈ繘鍏ユ寚瀹氭樉绀哄櫒锛岃嚜鍔ㄥ皢鍏剁Щ璧帮紙`Ctrl+Shift+S` 寮€鍏筹級 |
| **DPI 鏅鸿兘缂╂斁** | 璺ㄤ笉鍚?DPI 缂╂斁姣斾緥鐨勬樉绀哄櫒绉诲姩鏃讹紝鑷姩璋冩暣绐楀彛澶у皬 |
| **绯荤粺鎵樼洏** | 鏈€灏忓寲鍒版墭鐩橈紝鍙抽敭鑿滃崟蹇嵎鎿嶄綔 |
| **鍏ㄥ眬鐑敭** | `Ctrl+Shift+M` 绉诲姩绐楀彛锛宍Ctrl+Shift+S` 鍒囨崲灞忚斀 |
| **闆朵緷璧?* | 绾?Python + Win32 API锛屾墦鍖呬负鍗曟枃浠?EXE锛堢害 10MB锛?|
| **娴忚鍣ㄧ晫闈?* | 缇庤鐨?Web UI锛岄€氳繃娴忚鍣ㄨ闂拰鎺у埗 |

---

## 蹇€熷紑濮?
### 鏂瑰紡涓€锛氫笅杞?EXE锛堟帹鑽愶級

浠?[Releases](https://github.com/Fake-msn/DisplayWindowManager/releases) 椤甸潰涓嬭浇鏈€鏂扮殑 `DisplayWindowManager.exe`锛屽弻鍑昏繍琛屽嵆鍙€?
### 鏂瑰紡浜岋細浠庢簮鐮佽繍琛?
```bash
git clone https://github.com/Fake-msn/DisplayWindowManager.git
cd DisplayWindowManager
python display_window_manager.py
```

娴忚鍣ㄤ細鑷姩鎵撳紑 `http://127.0.0.1:18888`銆?
### 鏂瑰紡涓夛細鑷鎵撳寘

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "DisplayWindowManager" display_window_manager.py
```

---

## 鐣岄潰棰勮

### 涓荤晫闈?
娓呯埥鐨?Web 鐣岄潰锛屽洓涓寜閽畬鎴愭墍鏈夋搷浣滐細

- **绉诲姩绐楀彛** 鈥?涓€閿Щ鍔ㄦ墍鏈夌獥鍙ｅ埌鐩爣鏄剧ず鍣?- **灞忚斀寮€鍏?* 鈥?寮€鍚?鍏抽棴鏄剧ず鍣ㄥ睆钄?- **璁剧疆** 鈥?淇敼绉诲姩鏂瑰悜銆侀厤缃睆钄借鍒?- **鍒锋柊** 鈥?鍒锋柊绐楀彛鐘舵€?
### 璁剧疆闈㈡澘

- 绉诲姩鏂瑰悜锛氬壇灞忊啋涓诲睆 / 涓诲睆鈫掑壇灞?- 鏄剧ず鍣ㄥ睆钄斤細閫夋嫨灞忚斀鐨勬樉绀哄櫒鍜岀洰鏍囨樉绀哄櫒
- 鍚敤鍚庯紝琚睆钄芥樉绀哄櫒涓婄殑鏂扮獥鍙ｄ細琚嚜鍔ㄧЩ璧?
### 绯荤粺鎵樼洏

- 鎵樼洏鍥炬爣鏄剧ず褰撳墠鐘舵€?- 鍙抽敭鑿滃崟锛氱Щ鍔ㄧ獥鍙?/ 鍒囨崲灞忚斀 / 鎵撳紑鐣岄潰 / 閫€鍑?
---

## 绔炲搧瀵规瘮

| 缁村害 | **DisplayWindowManager** | DisplayFusion | PowerToys FancyZones | Actual Window Manager | Dual Monitor Tools |
|------|:--:|:--:|:--:|:--:|:--:|
| **浠锋牸** | **鍏嶈垂** | 楼232 璧?| 鍏嶈垂 | 楼430 璧?| 鍏嶈垂 |
| **寮€婧?* | **MIT** | 涓撴湁 | **MIT** | 涓撴湁 | GPL |
| **瀹夎鍖呭ぇ灏?* | **~10 MB** | ~130 MB | ~253 MB鹿 | ~13 MB | ~5 MB |
| **涓€閿獥鍙ｇЩ鍔?* | **鉁?鐑敭+鎸夐挳** | 鉁?鏍囬鏍?鐑敭 | 鉂?浠呭垎鍖哄唴 | 鉁?鏍囬鏍?鐑敭 | 鉁?鐑敭 |
| **鏄剧ず鍣ㄥ睆钄?* | **鉁?鑷姩绉昏蛋鏂扮獥鍙?* | 鏄剧ず鍣ㄦ贰鍖?| 鉂?鏃?| 榧犳爣閿佸畾 | 榧犳爣閿佸畾 |
| **DPI 鏅鸿兘缂╂斁** | **鉁?鑷姩閫傞厤** | 鉁?| 鉁?| 鉁?| 鉂?|
| **绯荤粺鎵樼洏** | **鉁?* | 鉁?| 鉂?| 鉁?| 鉂?|
| **鍏ㄥ眬鐑敭** | **鉁?涓ょ粍** | 鉁?瀹屽叏鑷畾涔?| 鉁?鏈夐檺 | 鉁?瀹屽叏鑷畾涔?| 鉁?鏈夐檺 |
| **娴忚鍣?UI** | **鉁?* | 鉂?| 鉂?| 鉂?| 鉂?|
| **闆跺畨瑁?* | **鉁?鍗曟枃浠?EXE** | 鉂?闇€瀹夎 | 鉂?闇€瀹夎 | 鉂?闇€瀹夎 | 鉁?缁胯壊鐗?|
| **娲昏穬缁存姢** | **鉁?2026** | 鉁?2026 | 鉁?2026 | 鉁?2026 | 鉂?2023 |
| **涓枃鐣岄潰** | **鉁?鍘熺敓** | 閮ㄥ垎姹夊寲 | 鉁?| 鉂?| 鉂?|

> 鹿 PowerToys 鏁翠綋瀹夎鍖呭ぇ灏忥紝FancyZones 涓哄叾涓竴涓ā鍧?
### 鎴戜滑鐨勭嫭鐗逛紭鍔?
1. **鐪熸鐨勪竴閿搷浣?* 鈥?涓嶉渶瑕佸湪姣忎釜绐楀彛鏍囬鏍忎笂鎵炬寜閽紝Ctrl+Shift+M 涓€姝ュ埌浣?2. **鏄剧ず鍣ㄥ睆钄?* 鈥?鐙鍔熻兘锛屼粠婧愬ご闃绘鏂扮獥鍙ｈ繘鍏ユ寚瀹氭樉绀哄櫒锛屼笉鏄畝鍗曠殑"鍙樻殫"
3. **闆跺涔犳垚鏈?* 鈥?鍙湁涓€涓?EXE 鏂囦欢锛屽弻鍑诲嵆鐢紝鏃犻渶瀹夎閰嶇疆
4. **涓枃鍘熺敓鏀寔** 鈥?涓轰腑鍥界敤鎴疯璁★紝鐣岄潰鍜屾枃妗ｅ叏涓枃
5. **娴忚鍣?UI** 鈥?鏃犻渶瀛︿範澶嶆潅鐣岄潰锛屽湪娴忚鍣ㄤ腑鐩磋鎿嶄綔
6. **鏋佽嚧杞婚噺** 鈥?涓嶅埌 10MB 鐨勫崟鏂囦欢锛屽唴瀛樺崰鐢ㄦ瀬浣?
---

## 鎶€鏈灦鏋?
```
display_window_manager.py
鈹溾攢鈹€ WindowManager       鈥?绐楀彛鏋氫妇銆佹樉绀哄櫒淇℃伅銆佺獥鍙ｇЩ鍔?鈹溾攢鈹€ DisplayShield       鈥?鍚庡彴杞銆佽嚜鍔ㄧЩ鍔ㄦ柊绐楀彛
鈹溾攢鈹€ ConfigManager       鈥?JSON 閰嶇疆璇诲啓
鈹溾攢鈹€ RequestHandler      鈥?HTTP API 鏈嶅姟鍣?鈹溾攢鈹€ TrayWindow          鈥?绯荤粺鎵樼洏 + 鍏ㄥ眬鐑敭
鈹斺攢鈹€ App                 鈥?涓绘帶鍒跺櫒
```

- **绾?Python 3.10+**锛屾棤绗笁鏂逛緷璧?- **Win32 API (ctypes)** 鈥?鐩存帴璋冪敤绯荤粺 API锛屾棤涓棿灞傛崯鑰?- **HTTP Server + 娴忚鍣?UI** 鈥?绋冲畾鍙潬锛岄伩鍏嶅師鐢?GUI 妗嗘灦鐨勫吋瀹规€ч棶棰?- **PyInstaller** 鈥?鎵撳寘涓哄崟鏂囦欢 EXE

---

## API 鎺ュ彛

| 绔偣 | 鏂规硶 | 璇存槑 |
|------|------|------|
| `/` | GET | 涓荤晫闈?HTML |
| `/api/state` | GET | 鑾峰彇鐘舵€侊紙鏄剧ず鍣ㄣ€佺獥鍙ｃ€佸睆钄界姸鎬侊級 |
| `/api/move` | GET | 鎵ц绐楀彛绉诲姩 |
| `/api/toggle-shield` | GET | 鍒囨崲灞忚斀寮€鍏?|
| `/api/ping` | GET | 蹇冭烦妫€娴?|
| `/api/quit` | GET | 閫€鍑虹▼搴?|
| `/api/save-settings` | POST | 淇濆瓨璁剧疆 |

---

## 璺嚎鍥?
- [x] 涓€閿Щ鍔ㄧ獥鍙?- [x] 鍙屽悜绉诲姩鏂瑰悜鍒囨崲
- [x] 鏄剧ず鍣ㄥ睆钄?- [x] 鍏ㄥ眬鐑敭
- [x] 绯荤粺鎵樼洏
- [x] DPI 缂╂斁閫傞厤
- [x] 娴忚鍣?UI
- [ ] 绐楀彛鍒楄〃棰勮锛堢Щ鍔ㄥ墠纭锛?- [ ] 鑷姩鍚姩锛堝紑鏈鸿嚜鍚級
- [ ] 澶氳瑷€鏀寔锛堣嫳鏂囷級
- [ ] 绐楀彛浣嶇疆璁板繂涓庢仮澶?
---

## 璐＄尞

娆㈣繋鎻?Issue 鍜?Pull Request锛?
## 璁稿彲

MIT License &copy; 2026 Fake-msn

---

## 閾炬帴

- [鍦ㄧ嚎浣撻獙 (GitHub Pages)](https://Fake-msn.github.io/DisplayWindowManager/)
- [Release 涓嬭浇](https://github.com/Fake-msn/DisplayWindowManager/releases)
- [闂鍙嶉](https://github.com/Fake-msn/DisplayWindowManager/issues)