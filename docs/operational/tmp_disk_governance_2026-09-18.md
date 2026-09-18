# tmp/ 磁盘治理清单

- **扫描时间**: 2026-09-18
- **扫描路径**: `D://PythonProject//connlab//tmp`
- **总条目数**: 768
- **总体积**: 26.75 GB (28719490434 bytes)
- **状态**: 只读扫描，未删除任何文件

## 分类汇总

| 分类 | 数量 | 体积 | 占比 | 建议处置 |
|---|---|---|---|---|
| repo_copy | 8 | 16.12 GB | 60.3% | 逐条确认后删除或迁移 |
| task_evidence | 57 | 5.18 GB | 19.4% | 保留关键批次，过期/重复项删除 |
| pytest_artifact | 175 | 820.23 MB | 3.0% | 配置 --basetemp 后定期清理 |
| other | 425 | 4.64 GB | 17.4% | 按文件逐条审核 |
| diagnostic | 4 | 7.84 MB | 0.0% | 保留近期，删除过期 |
| log | 98 | 1.72 MB | 0.0% | 压缩或删除 7 天前日志 |
| lock | 1 | 1 B | 0.0% | 无运行任务时删除 |

## 体积 TOP 20（单文件/单目录）

| 名称 | 类型 | 分类 | 体积 | 最后修改 |
|---|---|---|---|---|
| `task366d_20260725_073240` | dir | task_evidence | 4.82 GB | 2026-07-25 07:33 |
| `serial-complex-cutover-candidate-r73-isolated` | dir | repo_copy | 2.66 GB | 2026-08-07 18:39 |
| `serial-complex-cutover-candidate-r741b-isolated` | dir | repo_copy | 2.66 GB | 2026-08-08 01:27 |
| `serial-complex-cutover-candidate` | dir | repo_copy | 2.66 GB | 2026-08-07 07:28 |
| `serial-complex-cutover-candidate-r74-isolated` | dir | repo_copy | 2.66 GB | 2026-08-07 19:19 |
| `serial-complex-cutover-candidate-r72-isolated` | dir | repo_copy | 2.66 GB | 2026-08-07 13:07 |
| `serial-complex-cutover-candidate-r741-isolated` | dir | repo_copy | 2.66 GB | 2026-08-07 20:08 |
| `wt` | dir | other | 2.40 GB | 2026-07-30 06:46 |
| `pytest-project-schedule-full-final` | dir | pytest_artifact | 439.28 MB | 2026-09-09 02:16 |
| `node_modules` | dir | other | 319.67 MB | 2026-08-23 20:55 |
| `report003c_a_baseline` | dir | other | 247.24 MB | 2026-08-31 18:17 |
| `task_project_folder_blocker_backend.log.err` | file | other | 175.65 MB | 2026-09-09 21:49 |
| `task_364b_qa_browser` | dir | other | 173.64 MB | 2026-07-19 15:07 |
| `integrator-ltr-admin-merge-probe-escalated` | dir | repo_copy | 169.61 MB | 2026-08-16 08:47 |
| `task_361g_b2_full` | dir | other | 48.45 MB | 2026-07-13 02:37 |
| `task_361g_reviewer_regate_b2` | dir | task_evidence | 48.45 MB | 2026-07-13 02:40 |
| `task_361g_integrator_full` | dir | other | 48.45 MB | 2026-07-13 02:48 |
| `task_361g_integrator_audit` | dir | other | 48.45 MB | 2026-07-13 05:17 |
| `task_361g_qa_full` | dir | other | 48.45 MB | 2026-07-13 02:44 |
| `task_361g_b1_full` | dir | other | 43.94 MB | 2026-07-13 02:30 |

## 仓库副本详情（高风险清理区）

| 名称 | 体积 | 最后修改 | 说明 |
|---|---|---|---|
| `serial-complex-cutover-candidate-r73-isolated` | 2.66 GB | 2026-08-07 18:39 | 含 .git, pyproject.toml |
| `serial-complex-cutover-candidate-r741b-isolated` | 2.66 GB | 2026-08-08 01:27 | 含 .git, pyproject.toml |
| `serial-complex-cutover-candidate` | 2.66 GB | 2026-08-07 07:28 | 含 .git, pyproject.toml |
| `serial-complex-cutover-candidate-r74-isolated` | 2.66 GB | 2026-08-07 19:19 | 含 .git, pyproject.toml |
| `serial-complex-cutover-candidate-r72-isolated` | 2.66 GB | 2026-08-07 13:07 | 含 .git, pyproject.toml |
| `serial-complex-cutover-candidate-r741-isolated` | 2.66 GB | 2026-08-07 20:08 | 含 .git, pyproject.toml |
| `integrator-ltr-admin-merge-probe-escalated` | 169.61 MB | 2026-08-16 08:47 | 含 .git |
| `reviewer-ltr-admin-frontend` | 2.24 MB | 2026-08-16 08:26 | 含 package.json |

## pytest 产物抽样（按大小排序前 10）

| 名称 | 体积 | 最后修改 |
|---|---|---|
| `pytest-project-schedule-full-final` | 439.28 MB | 2026-09-09 02:16 |
| `pytest-project-schedule-final` | 23.16 MB | 2026-09-09 01:42 |
| `task_364c_integrator_pytest` | 22.40 MB | 2026-07-19 17:09 |
| `pytest_test_record_final` | 22.22 MB | 2026-09-16 08:25 |
| `pytest_test_record_affected` | 22.22 MB | 2026-09-16 08:23 |
| `pytest-publication-diag-qa-final` | 18.23 MB | 2026-09-11 21:36 |
| `pytest-project-schedule-exact` | 17.59 MB | 2026-09-09 01:55 |
| `task_361j_qa_pytest` | 15.30 MB | 2026-07-15 07:04 |
| `task_361j_qa_full_pytest` | 15.30 MB | 2026-07-15 07:06 |
| `task_361j_qa_resmoke_pytest` | 15.30 MB | 2026-07-15 07:30 |

## task_evidence 抽样（按大小排序前 10）

| 名称 | 体积 | 最后修改 |
|---|---|---|
| `task366d_20260725_073240` | 4.82 GB | 2026-07-25 07:33 |
| `task_361g_reviewer_regate_b2` | 48.45 MB | 2026-07-13 02:40 |
| `task_361g_reviewer_regate_b1` | 43.94 MB | 2026-07-13 02:32 |
| `task_361g_reviewer` | 43.04 MB | 2026-07-13 02:26 |
| `task_361f_reviewer_regate_b1r` | 31.49 MB | 2026-07-13 01:11 |
| `task_361f_reviewer_regate` | 31.49 MB | 2026-07-13 01:06 |
| `fee_task3_final_backend` | 27.67 MB | 2026-08-22 14:36 |
| `task_361f_reviewer` | 27.02 MB | 2026-07-13 00:57 |
| `fee_task3_suite3b` | 17.72 MB | 2026-08-22 14:29 |
| `fee_task3_suite3` | 17.72 MB | 2026-08-22 14:28 |

## 建议处置优先级

1. **P0 - pytest 产物（~820.23 MB）**: 配置 `pytest --basetemp D:/PythonProject/connlab/tmp/pytest-tmp`，并批量删除历史 `pytest-cache-*` 目录。风险最低，几乎无业务价值。
2. **P1 - 仓库副本（~16.12 GB）**: 6 份疑似完整仓库副本。需你确认是否为临时 cutover/reviewer 证据；确认后可删除。
3. **P2 - 任务证据（~5.18 GB）**: 57 个目录，保留最近 1~2 个任务周期，其余删除。
4. **P3 - 其他大文件（~4.64 GB）**: 含 `task_project_folder_blocker_backend.log.err`（175.65 MB）和多个 DL-2026 报告/docx。需按业务价值逐条审核。
5. **P4 - 日志/诊断（~9.56 MB）**: 体量小，可保留近期、删除过期。

## 下一步

请逐类确认是否执行删除。我将以小批次（每次最多 10 个条目）执行，并先备份再删除。