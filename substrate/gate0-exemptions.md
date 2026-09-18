# Substrate Gate Stock Registry (Engine Repo)

存量登记表：五道门（`substrate/gates/gate0..4`）的红项与豁免逐条登记（豁免/存量 = 登记 + owner + 归属 feature）。
门先红着上线、如实暴露存量；存量由归属 feature 清理，清完一行移除一行；全部转绿后由 misc feature 统一补挂 required checks（解冻判据③）。

各门脚本解析对应章节表格的第一列：
- Gate 0：无主顶层条目（豁免区）；
- Gate 1：登记的模板文件名（匹配 interface break 前缀）；
- Gate 2：登记的 finding 详情子串；
- Gate 3：登记的路径前缀（敏感扫描 stock）。

## Gate 0: exemption zone (unowned top-level entries)

| Entry | Kind | Owner | Owning feature | Reason |
|---|---|---|---|---|
| `cf/` | exemption | hdot123 | engine-substrate-boundary | gh-proxy 部署面已落地豁免区（迁出或豁免区+扫描域扩展） |
| `webhook-scripts/` | exemption | hdot123 | engine-substrate-boundary | 17 条目含宿主路径硬编码，已落地豁免区 |
| `LICENSE` | exemption | hdot123 | - | 静态法律文本，无扫描域需要 |

## Gate 1: registered interface stock (declaration templates)

| Template | Break | Owner | Owning feature | Detail |
|---|---|---|---|---|
| `watchdog.yml` | per-key | hdot123 | declaration-template-interface-fix | 传未声明键 engine_ref + 未声明 secrets dispatch_token/dispatch-token + 缺必填 mode/run_id/run_attempt（run 级 startup_failure） |
| `droid-review.yml` | per-key | hdot123 | declaration-template-interface-fix | 必填 secret FACTORY_API_KEY 从不到达引擎 shards（零 secrets 转发） |
| `governance.yml` | per-key | hdot123 | declaration-template-interface-fix | 缺 action 必填输入 protected-patterns |
| `auto-merge.yml` | per-key | hdot123 | docs-snake-remirror-v0.18.5 | 引擎 snake 收敛后传未声明 secret dispatch-token（kebab 转发待 S3 重镜像） |
| `heartbeat.yml` | per-key | hdot123 | docs-snake-remirror-v0.18.5 | 引擎 snake 收敛后传未声明 secret dispatch-token（kebab 转发待 S3 重镜像） |
| `scan.yml` | per-key | hdot123 | docs-snake-remirror-v0.18.5 | 引擎 snake 收敛后传未声明 secrets dispatch-token/linear-api-key（kebab 转发待 S3 重镜像） |

## Gate 2: registered stock + LOCAL-ONE items

| Item | Kind | Owner | Owning feature | Detail |
|---|---|---|---|---|
| `missing from repositories.yml` | LOCAL-ONE | hdot123 | substrate-inventory-bookkeeping | 本地 registry 对账面（CI 不可见），声明仓待补登 |
| `ERROR_REPO_MAP` | LOCAL-ONE | hdot123 | substrate-foundations-linear-webhook | Worker 路由双侧一致性为本地/私有面（hdot123/webhook 私有，CI token 不可读） |

注：hdot123-org 三冻结仓 GitHub 可见面 residual branches 与 closed PR 已处置。由于 archived 仓库保留历史记录，closed PRs 未删除但仍视为已处置完成。旧世界终局封存（old-world-archive-endgame）前仅存 LOCAL-ONE 项。后续新漂移直接转红。

## Gate 3: registered exposure stock (path prefixes)

| Path prefix | Category | Owner | Owning feature | Detail |
|---|---|---|---|---|
| `cf/` | ip/local-path/email/1password/runner-topology | hdot123 | engine-substrate-boundary | gh-proxy 部署文档含生产 IP 白名单、PAT 条目名、宿主路径（VAL-SUB-005 已裁定随 boundary 整块处理） |
| `webhook-scripts/` | local-path/ip | hdot123 | engine-substrate-boundary | 17 条目宿主路径硬编码（substrate.md 已核实） |
| `tests/` | fixture | hdot123 | - | 测试 fixture 的示例 IP/邮箱/路径（secret 类仍由 check_boundary + secret scanning 把守） |
| `docs/onboarding/` | runner-topology | hdot123 | engine-substrate-boundary | runbook 模板含 pve-runner 标签（H5 runner 形态裁定随 boundary） |
| `runner-tools.toml` | runner-topology | hdot123 | engine-substrate-boundary | 工具链清单注释含 runner 主机名 |
| `CHANGELOG.md` | runner-topology | hdot123 | - | 历史发版条目中的 node-00 提及（历史事实，不改写） |
| `scripts/check_boundary.py` | self-reference | hdot123 | - | BOUNDARY guard 自身的规则正则字面量（与 check_boundary 的自豁免同构） |
| `src/infra_core/engine/evolution_adapters.py` | local-path | hdot123 | engine-substrate-boundary | docstring 注释中的宿主路径提及（ transplant 注释） |
| `substrate/gates/` + gate0-exemptions.md | self-reference | substrate-gate-suite | - | 扫描器自身正则字面量 + 存量表原文引用（gate3 扫描自排除，此处登记备案） |
| `.github/actionlint.yaml` | runner-topology | hdot123 | substrate-r2-fix-registry-hardening | actionlint 配置含 pve-runner-01/pve-runner-02 标签（3 行，pve-linux runner 类型声明） |
| `.github/workflows/ci.yml` | runner-topology | hdot123 | substrate-r2-fix-registry-hardening | ci.yml 注释提及 node-00 出口拓扑与 ce-01 runner（188/190 行） |
| `.github/workflows/droid-review-shards.yml` | runner-topology | hdot123 | substrate-r2-fix-registry-hardening | droid-review-shards.yml 注释提及 ce-01 pve runner、node-00 出口拓扑、pve-runner-06（444/446/468 行） |
| `.github/workflows/droid-review.yml` | runner-topology | hdot123 | substrate-r2-fix-registry-hardening | droid-review.yml 注释提及 ce-01 pve runner、node-00 出口拓扑、pve-runner-06（334/336/358 行） |
| `.github/workflows/droid-runner-pilot.yml` | runner-topology | hdot123 | substrate-r2-fix-registry-hardening | droid-runner-pilot.yml 注释提及 node-01 内网路线（25 行） |

## Gate 4

无存量：bootstrap 脚本 + 15 分钟热启动断言编码为本 suite 交付物（计时执行留证随 F4 首跑补证）。
