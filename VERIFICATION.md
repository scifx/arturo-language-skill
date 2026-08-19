# Arturo Language Skill 可用性验证报告

验证日期: 2026-08-19
验证环境: Linux amd64 沙箱 (Debian 12 风格), Python 3.11, glibc ≥ 2.36
验证对象: 仓库 `scifx/arturo-language-skill` (分支 `arena/01a019da-arturo-language-skill`, 基线 commit `1c88d647`)

## 结论摘要

**该 skill 整体可用 (PASS)**,核心承诺均兑现:

- 自带运行时可用: `bin/arturo` (Full build) 与 `bin/arturo-mini` (Mini build) 均为 `arturo 0.10.1-dev+43 (amd64/linux)`,与 README/SKILL.md 声明一致;SHA-256 与 `config.env.example` 中记录的校验值一致;`ldd` 确认依赖 `libgmp.so.10`/`libmpfr.so.6`/`libssl.so.3`/`libcrypto.so.3` 全部就位。
- 冒烟测试在两个 build 上均逐字节通过 (`tests/smoke.art` vs `tests/expected-smoke.txt`)。
- 帮助体系 (运行时 `info`、`bin/ahelp`、`scripts/arturo_help.py`、MCP server) 全部实测可用。
- 521 条库索引与离线回退路径工作正常;`info`/`info.get` 可本地取出每个符号的**官方可运行示例**。
- Full build 的宣称特性 (大整数、正则、SQLite、crypto、文件/JSON、CLI 编译打包) 实测通过或得到确认。

**发现并修复 1 个文档缺口;另报告 3 个运行时怪癖与 1 个环境限制**(详见下文),均不影响 skill 主流程。

---

## 一、逐项验证结果

| # | 组件 | 结果 | 证据 |
|---|---|---|---|
| 1 | `bin/arturo` / `bin/arturo-mini` | ✅ PASS | `--version` → `arturo 0.10.1-dev+43 (amd64/linux)`;`get-arturo.sh --check-only` 报告依赖齐全,sha256 与 config.env.example 一致 |
| 2 | 冒烟测试 `tests/smoke.art` | ✅ PASS | Full 与 Mini 均与 `tests/expected-smoke.txt` 完全一致 (exit 0) |
| 3 | `bin/ahelp read` / `'++'` | ✅ PASS | 正确调用运行时 `info`,输出签名/选项/别名;`++` 正确解析为 `append` |
| 4 | `bin/ahelp -s TERM` (离线模糊搜索) | ✅ PASS | `ahelp -s string` 返回 strings 模块 10 条结果+官方 URL |
| 5 | `bin/ahelp --latest` | ✅ PASS | 输出运行时 `info` + `/latest/` 文档 URL |
| 6 | 无运行时离线回退 | ✅ PASS | `ARTURO_BIN=/nonexistent` 时降级为索引查找并提示 |
| 7 | `scripts/arturo_help.py` | ✅ PASS | `map` / `read` / `--info --runtime` 均正常 |
| 8 | MCP server `mcp/server.py` | ✅ PASS | `initialize`/`tools/list`/`tools/call` 三个工具 (`arturo_info`/`arturo_search`/`arturo_doc_url`) 均返回正确结果 |
| 9 | 库索引 `library-index.csv` | ✅ PASS | 522 行 (含表头),521 个唯一符号;构建时记录 stable URL 全部 200,latest 有 7 个已知 404 |
| 10 | `info 'NAME` / `info.get 'NAME \example` | ✅ PASS | 本地即可取官方示例 (如 `map` 的 6 个示例块全部可运行) |
| 11 | Full build 大整数 | ✅ PASS | `123456789012345678901234567890 * 987654321098765432109876543210` 输出正确 |
| 12 | Full build 正则 | ✅ PASS | 本 fork 的正则字面量为 `{/.../}`:`match.once "xabcy" {/abc/}` → `abc`;`replace "a1b2c3" {/\d/} "X"` → `aXbXcX` |
| 13 | Full build crypto | ✅ PASS | `digest` (默认 MD5,`.sha` 为 SHA1)、`crc` (CRC32)、`encode` (base64) 输出与标准值一致 |
| 14 | Full build SQLite | ✅ PASS | `open.sqlite ":memory:"` + `query db "..."` 建表/插入/查询正常 (单条语句分别执行) |
| 15 | 文件读写 / JSON | ✅ PASS | `write content file` (参数顺序与文档一致);`write.json`/`read.json` 往返正常 |
| 16 | Mini build 特性门控 | ✅ PASS | 大整数在 Mini 中正确报 Arithmetic Error;`open.sqlite` 正确报 "not available in MINI builds" |
| 17 | CLI 模式 | ✅ PASS | `--compile`/`--execute`/`--bundle --as`/包管理/REPL 均出现在 `--help` 中 |
| 18 | `verify_links.py` | ⚠️ 环境受限 | 沙箱出网 TLS 握手被阻断 (arturo-lang.io/example.com/google.com 全部 `SSL_ERROR_SYSCALL`),521 条全部 URLError;**非链接损坏**,CSV 内构建时记录为 200 |

## 二、发现的问题

### P1 — 文档缺口: 正则字面量语法未进入 SKILL.md 主文档 (已修复)

本 fork (0.10.1-dev+43) 的正则字面量是 `{/.../}` 花括号形式,而官方 Arturo 的 `/.../` 在**本构建中被词法解析为除法**。`{/.../}` 仅在 `references/practical-rules.md` 与 `references/web-and-http-patterns.md` 中提及,`SKILL.md` 核心规则与 `references/syntax-cheatsheet.md` 均未覆盖——只读 SKILL.md 的 agent 很可能写出 `/.../`,轻则得到 "Identifier not found" 类型报错,重则 (传给 `match`/`contains?`) 让运行时**无限挂起**。

修复 (本次已提交):
- `SKILL.md` 核心规则新增一条: 正则用 `{/.../}`,`/.../` 是除法,标志位用内联 `(?i)` 而非 `/` 后追加。
- `references/syntax-cheatsheet.md` Strings 一节补充 `regex: {/.../}` 说明。

### P2 — 运行时怪癖 (fork/runtime 缺陷,非 skill 文档错误)

1. **Full build 挂起**: 把被误解析为除法的 `/.../` 表达式传给 `match`/`match?`/`contains?` 时,进程不退出且忽略 SIGTERM (需 SIGKILL)。复现: `print (match "hello123" /\d+/)?`。**规避**: 使用 `{/.../}` 语法即可 (上述 P1 修复已写入文档)。
2. **Mini build 挂起**: 遇到大整数字面量解析错误时,先打印 Arithmetic Error,随后进程死循环不退出 (file 与 `-e` 两种模式均复现;同 build 下除零/未定义名均正常 exit=1)。规避: Mini 构建用于普通脚本,避免大整数常量。
3. **JSON 字符串解析缺失**: 本构建无 `md5`/`sha1`/`crc32` 等符号名 (实为 `digest`/`crc`/`encode`);`parse.json "..."` 会**静默返回原字符串** (`parse` 仅支持 `.data` 属性,无 `.json`)。JSON 请走 `read.json` (文件) / `render.json` (输出) 路径,这与 skill 的 `web-and-http-patterns.md` 一致。

### P3 — 轻微问题

1. `bin/ahelp -s` 无匹配时提示 "(try -s for substring search)",即使已使用 `-s` 也照常显示 (文案问题)。
2. README 中 "crypto hashes" 措辞与符号名不一致 (函数是 `digest`/`crc`/`encode`,非 `md5`/`sha1`/`crc32`),信息本身正确,不影响使用。
3. SKILL.md 宣称 Full build 含 DOCGEN,但 `--help` 中未见 docgen 子命令;`info` 帮助体系本身工作正常,不影响主流程。

## 三、端到端实测示例 (按 skill 工作流)

```arturo
; 先 info 查询, 再写最小程序
data: ["arturo" "skill" "arturo" "test" "skill" "arturo"]
freq: #[]
loop data 'w [
    freq\w: (key? freq 'w)? [freq\w + 1] [1]
]
loop freq [k v] [ print ~"  |k|: |v|" ]
print digest "arturo"        ; md5
print crc "arturo"           ; crc32
print encode "arturo"        ; base64
```

输出: 词频统计正确;`digest "arturo"` → `65deafcf3c1ad1751415736c4cc11f76` (标准 MD5);`crc` → `871B343E`;`encode` → `YXJ0dXJv`。全部与 Python `hashlib`/`base64` 对照一致。

## 四、验证过程中遇到的"伪问题" (测试方误用,非 skill 缺陷)

- `write` 参数顺序为 `write content file` (skill 文档正确);我最初反序调用导致文件错名,按文档修正后正常。
- 字典迭代需用块参数 `loop dict [k v] [...]`;`info 'loop` 可查到 `params :null :literal :block`。
- `info 'match` / `info 'parse` / `info 'write` / `info 'query` 等查询均能给出真实签名,证实"先查 info 再写码"流程有效。

## 五、结论

- **可用性: 高**。运行时、帮助工具、MCP、离线索引、参考文档五条主路径全部实测通过;两个捆绑二进制零下载即可运行,冒烟测试双 build 通过。
- 建议按 P1 修复更新后的 SKILL.md/cheatsheet 使用 (本次已一并提交)。
- 生产使用提醒: 遵循 skill 自身规则——任何陌生 API 先 `info 'NAME`;正则一律 `{/.../}`;JSON 走 `read.json`;Mini 构建避免大整数常量。

---

# 第二轮:对照官方手册 + agent-shell.art 实战项目修正 (2026-08-19)

对照来源: 官方语言手册 `arturo-lang.io/documentation/language`(全部 7 段)+
实战项目 `github.com/scifx/agent-shell.art`(2541 行 .art,含 OOP/HTTP/JSON/
工具动态加载/REPL 外壳)+ 项目自带符号表。**所有新声明均在本仓库捆绑运行时
0.10.1-dev+43 上重新实测通过**;冒烟测试双 build 依旧 PASS。

## 修正的错误 (原有文档确实写错的)

| # | 文件 | 错误 | 修正 |
|---|---|---|---|
| 1 | `SKILL.md`、`syntax-cheatsheet.md` | "Evaluation is right-to-left, **except infix operators**" / "infix operators use precedence" | 手册明确**没有任何优先级规则**,中缀只是前缀函数别名,同样右到左结合。`2 * 3 + 4` = **14**(= `2*(3+4)`),不是 10 |
| 2 | `web-and-http-patterns.md` | scaffold 用 `render.json items` | `render` 在本 build 只有 `.once`/`.template` 属性,**`render.json` 不存在**(Type Error)。改为 `write.json items null` |
| 3 | `recipes.md` JSON 段 | "do not invent json.loads equivalents"——只警示不给方案 | 补上实测可用的等价物:`read.json`(字符串或文件)、`write.json v null`(返回 JSON 字符串)、`write.json v file`、`read.toml`;并警示 `parse.json` 是静默空操作(返回原字符串) |

## 新增的实测经验 (提炼自项目 + 手册,全部运行验证)

- **思维模式转换 6 条**(SKILL.md 新章节): ① 无语法只有值 ② 右到左、无优先级 ③ `=`比较/`:`绑定/符号即别名 ④ 字面量就地修改+引用传递 ⑤ 块无作用域/迭代器恢复/函数隔离/`.inline` ⑥ OOP-lite+JSON/TOML 一等公民。
- **`++` 是 `append`,只能拼字符串**: `"a" ++ "b"` ✅;`"a" ++ 0` 在 `print` 场景**静默吞参数**并给出误导性 "Not enough parameters: print",在 `type` 场景**挂起 build**(实测复现,需 SIGKILL)。修正了 in-a-nutshell 的 concat 行与各文件的拼接示例。
- **值按引用传递,`new` 复制**: `b: a` 是别名(`append 'b 9` 会改到 `a`);`c: new a` 才独立。
- **作用域模型**: 块内变量泄漏到块外;迭代器注入变量循环后恢复;函数自带作用域,`.inline` 消除(项目 `lib/py.art` 的 `function.inline` 用法)。
- **误导性诊断**: "Cannot perform: X — Not enough parameters" 但 X 明明有参数时,向左找——前面的表达式吞了操作数返回了 `:nothing`(典型是 `++` 类型不匹配)。
- **函数重命名**: 项目 `别名: $[x y][let x (var y)!]` 模式与本 build 的 `alias` 内建**都不产生可调用绑定**(实测 `Identifier not found`/绑定异常),且项目从未调用这些别名。可靠写法是包装器 `bar: $[x] -> foo x`。
- **`attr` + `??` 默认参数惯用法**(`lib/py.art`): `default: function.inline [name value][let name ((attr name) ?? value)]`,调用 `.pypy: true` 即传可选命名参数——Arturo 版关键字参数。
- **`standalone?` 主程序守卫**(Python `__main__` 等价物)、**`execute.code`** 结构化返回(`\output`/`\code`)、**动态 `import x!`**。
- **`'x` 与 `' x` 的空白坑**: 引号后空格会把 `'` 变成字符字面量起始,吞掉后续代码直到下一个 `'`(报 "Quoted string contains newline")。

## 项目代码在本捆绑运行时上的兼容性抽查

- 可独立运行: `utils.art`、`convert_utils.art`、`lib/sortutils.art`、`schema.art`、`fnschema.art`、`prompt.art`、`aiutils.art`、`complete.art` ✅
- 实测通过的项目模式: `define`/`method`/`this` OOP 与 `write.json \obj null` 序列化、`read.toml` 配置、`request.get url #[] | get 'body` 与 `request.post .headers: h .json url data`(本地 HTTP 服务器验证)、`ensure.that:`、`key?`、`loop dict [k v]`、`execute.code`、动态工具加载。
- 注意: 项目 `shell.art` 引用的 `symbols\hints`/`symbols\hits` 在本 build 的 `symbols` 字典中**不存在**(Index Error)——该项目面向的运行时更新;本 skill 无需适配,但已确认不是 skill 文档问题。
