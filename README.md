
### 中文简介

```text
adata_doctor 是一个用于单细胞 AnnData 表达矩阵预检查的轻量级 Python 工具。
它可以在下游分析前自动判断 .X、.raw.X 和 layers 中矩阵的状态，
识别 raw counts、log-normalized matrix、log1p(raw counts)、scaled matrix 等常见情况，
并生成结构化诊断报告，帮助用户避免重复归一化、错误 log 转换和错误下游输入。
```
# `adata_doctor` 工具

## 1. 基本信息

**项目名称：** `adata_doctor`
**项目定位：** AnnData 表达矩阵状态自动诊断工具
**开发语言：** Python
**主要应用领域：** 单细胞转录组数据分析、生物信息学数据预处理、公开单细胞数据复用
**主要服务对象：** 使用 Scanpy、AnnData、CellTypist、Seurat 转换数据或公开 `.h5ad` 文件的单细胞研究者
**当前版本：** v0.1.1
**包名设计：**

```text
PyPI 包名：adata-doctor
Python 导入名：adata_doctor
命令行工具名：adata-doctor
```

一句话概括：

> `adata_doctor` 是一个用于单细胞 AnnData 对象预检查的轻量级工具，可以在正式下游分析前自动判断 `.X`、`.raw.X` 和 `layers` 中表达矩阵的真实状态，并生成结构化诊断报告。

---

## 2. 背景

在单细胞 RNA-seq 数据分析中，表达矩阵的状态决定了后续分析流程是否正确。一个 AnnData 文件中，表达数据可能存放在：

```text
adata.X
adata.raw.X
adata.layers["counts"]
adata.layers["logcounts"]
adata.layers["scale.data"]
```

但在实际公开数据中，矩阵状态往往并不清楚。用户从 GEO、Zenodo、Figshare、HCA、论文补充材料或他人 GitHub 下载 `.h5ad` 文件后，经常会遇到以下问题：

```text
1. 不知道 .X 是 raw counts 还是 log-normalized matrix；
2. 不知道数据是否已经做过 normalize_total；
3. 不知道数据是否已经做过 log1p；
4. 不知道 .X 是否已经被 scale 成含负值矩阵；
5. 不知道 .raw.X 是否真的是原始 counts；
6. 不知道 layers 中是否存在更适合下游分析的矩阵；
7. 不知道当前矩阵能否直接用于 CellTypist、Scanpy 或其他分析流程。
```

这些问题如果没有提前检查，很容易导致错误操作。例如：

```text
对已经 log1p 的矩阵再次 log1p；
对已经 normalize 的矩阵重复 normalize；
把 scaled matrix 当成表达矩阵输入 CellTypist；
把 log1p(raw counts) 误认为标准 log-normalized matrix；
找不到隐藏在 raw 或 layers 中的可恢复 counts 信息。
```

因此，在正式分析之前，需要一个自动化工具帮助用户回答一个基础但关键的问题：

> 我手里的这个 AnnData，到底是什么状态？能不能直接用？

`adata_doctor` 就是为了解决这个问题而设计的。

---

## 3. 目标

`adata_doctor` 的目标不是替代 Scanpy、CellTypist 或 Seurat，而是成为这些工具之前的一个**矩阵体检工具**。

它的核心目标包括：

```text
1. 快速检查 AnnData 对象的整体结构；
2. 自动判断 .X、.raw.X 和 layers 中矩阵的状态；
3. 区分 raw counts、log-normalized matrix、scaled matrix 等常见情况；
4. 发现可用于重新标准化的 raw counts 或可恢复 counts；
5. 给出下游分析建议；
6. 生成可读、可保存、可复现的诊断报告；
7. 提供 Python API、adata.report() 风格接口和命令行接口。
```

因此，`adata_doctor` 的定位可以概括为：

```text
不是下游分析工具，而是下游分析前的 AnnData 体检工具。
```

---

## 4. 使用条件与运行环境

### 4.1 Python 环境要求

建议环境：

```text
Python >= 3.9
推荐使用 conda / mamba 创建独立环境
支持 Jupyter Notebook / JupyterLab / Linux 服务器环境
```

基础依赖：

```text
numpy
scipy
pandas
anndata
```

常用配合依赖：

```text
scanpy
celltypist
```

其中，`adata_doctor` 本身主要依赖 `AnnData` 对象和矩阵计算。
如果用户已经通过 Scanpy 读取了 `.h5ad` 文件，例如：

```python
import scanpy as sc
adata = sc.read_h5ad("data.h5ad")
```

那么就可以直接使用 `adata_doctor` 进行诊断。

---

### 4.2 数据格式要求

当前版本主要支持：

```text
AnnData 对象
.h5ad 文件
```

重点诊断对象包括：

```text
adata.X
adata.raw.X
adata.layers
```

当前版本尚未重点支持：

```text
10x mtx
10x h5
csv 表达矩阵
loom
Seurat 原生对象
```

这些可以作为后续版本扩展方向。

---

### 4.3 硬件与性能要求

`adata_doctor` 默认采用抽样策略进行矩阵状态判断，不会对所有细胞和所有基因进行完整计算，因此适合大规模单细胞数据的快速预检查。

默认策略包括：

```text
抽样部分细胞；
对矩阵进行关键统计；
尽量保留稀疏矩阵计算；
避免不必要的全矩阵 dense 化。
```

对于几十万细胞级别的数据，通常也可以快速完成初步诊断。

但如果用户的 `.X` 本身已经是非常大的 dense matrix，仍然会受到内存限制影响。因此在超大规模数据中，建议优先使用稀疏矩阵格式。

---

## 5. 核心功能设计

### 5.1 AnnData 结构检查

`adata_doctor` 会首先读取 AnnData 的基础结构信息，包括：

```text
n_obs × n_vars
.X 矩阵类型
是否存在 .raw
layers 名称
obs 字段
var 字段
uns 信息
obsm / varm / obsp 信息
```

这一步的作用是让用户快速知道这个对象中到底包含了哪些数据。

例如：

```text
Shape: [73589, 2608]
X type: ndarray
Layers: []
Raw exists: True
```

这说明该数据没有 layers，但存在 `.raw.X`，因此工具会进一步检查 `.raw.X`。

---

### 5.2 表达矩阵状态诊断

当前版本可识别的主要矩阵状态包括：

```text
raw_counts
probably_raw_counts
normalized_to_target_sum_not_log1p
log1p_normalized_to_target_sum
probably_log1p_normalized
log1p_counts_not_normalized
scaled_or_other_transformed_matrix
other_transformed_matrix
ambiguous
empty_matrix
invalid_or_corrupted_matrix
```

其中几个关键类别的含义如下。

---

#### raw_counts

表示矩阵大概率是原始 counts。

典型特征：

```text
非零值接近整数；
最大值较大；
每个细胞总表达量不固定；
expm1(X) 可能溢出。
```

建议：

```text
通常需要先 normalize_total(target_sum=1e4)，再 log1p。
```

---

#### log1p_normalized_to_target_sum

表示矩阵大概率已经经过：

```python
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
```

典型特征：

```text
X 数值范围较小；
expm1(X) 后每个细胞总量接近 target_sum；
非零值通常不是整数。
```

建议：

```text
不要重复 normalize_total；
不要重复 log1p；
通常可以直接用于需要 log-normalized 输入的流程。
```

---

#### log1p_counts_not_normalized

这是 v0.1.1 中非常重要的新增类别。

它表示矩阵大概率是：

```text
log1p(raw counts)
```

但没有经过标准的 `normalize_total(target_sum=1e4)`。

典型特征：

```text
X 本身非零值不是整数；
expm1(X) 后非零值高度接近整数；
expm1(X) 后每个细胞总量不接近 10000。
```

这种情况在公开 `.h5ad` 文件的 `.raw.X` 中很常见。

建议：

```text
如果需要标准 log-normalized 输入，可以先 expm1(X) 还原 counts，
再执行 normalize_total(target_sum=1e4) 和 log1p。
```

---

#### scaled_or_other_transformed_matrix

表示矩阵可能已经被 scale、z-score 或其他方法转换。

典型特征：

```text
存在负值；
矩阵可能变成 dense；
最大值可能被截断为 10；
行和没有表达量意义。
```

建议：

```text
不要直接用于表达量分析；
不要直接 normalize_total/log1p；
优先寻找 raw counts、log-normalized layer 或 raw.X。
```

---

### 5.3 关键统计指标

`adata_doctor` 不只给出结论，还会输出支持判断的证据。

主要统计指标包括：

```text
finite_ratio
min
max
mean
nonzero_ratio
int_like_ratio_nonzero
row_sum_median
row_sum_close_to_target_ratio
expm1_sum_median
expm1_sum_close_to_target_ratio
expm1_int_like_ratio_nonzero
```

其中最重要的判断逻辑包括：

```text
1. 非零值是否接近整数；
2. X 中是否存在负值；
3. 每个细胞的 row sum 是否接近 target_sum；
4. expm1(X) 后的 row sum 是否接近 target_sum；
5. expm1(X) 后的非零值是否接近整数。
```

这些指标可以帮助用户理解工具为什么给出某个判断，而不是只得到一个黑箱结论。

---

## 6. 下游分析兼容性建议

`adata_doctor` 会根据诊断结果生成下游分析建议，主要包括：

```text
celltypist_like_input
renormalization
visualization_or_marker_plot
traceability
```

### 6.1 celltypist_like_input

判断当前矩阵是否适合用于 CellTypist 类输入。

可能结果：

```text
pass
needs_preprocessing
fail_or_caution
caution
```

例如：

```text
X 是 raw counts：
needs_preprocessing，需要 normalize_total + log1p。

X 是 scaled matrix：
fail_or_caution，不建议直接作为表达矩阵输入。
```

---

### 6.2 renormalization

判断是否可以找到适合重新标准化的原始矩阵。

例如：

```text
发现 raw counts：
pass。

发现 log1p(raw counts)：
recoverable_with_caution，可以尝试 expm1 还原 counts。

没有 raw-like 矩阵：
caution。
```

---

### 6.3 visualization_or_marker_plot

判断是否适合直接用于 marker gene 表达可视化。

例如：

```text
发现标准 log-normalized matrix：
pass。

只有 scaled matrix：
caution。

只有 log1p(raw counts)：
caution，可以粗略查看，但不等价于 normalize_total 后的表达矩阵。
```

---

### 6.4 traceability

判断数据处理是否具有可追溯性。

例如：

```text
有明确 raw counts：
pass。

只有 log1p(raw counts)：
caution。

虽然存在 raw.X，但状态不明确：
caution。
```

这个设计避免了一个常见误区：

> 不是只要存在 `.raw.X`，就说明数据一定可追溯。

`adata_doctor` 会进一步判断 `.raw.X` 本身是什么状态。

---

## 7. 使用方式

### 7.1 Python API

用户已经读入 AnnData 后：

```python
import scanpy as sc
import adata_doctor as doctor

adata = sc.read_h5ad("data.h5ad")

report = doctor.report(adata)

print(report.to_text())
```

---

### 7.2 保存 Markdown 报告

```python
report.to_markdown("adata_doctor_report.md")
```

---

### 7.3 保存 JSON 报告

```python
report.to_json("adata_doctor_report.json")
```

---

### 7.4 使用 `adata.report()`

为了让使用方式更自然，`adata_doctor` 支持给 AnnData 对象添加 `.report()` 方法：

```python
import adata_doctor as doctor

doctor.patch_anndata()

report = adata.report()

print(report.to_text())
```

---

### 7.5 命令行使用

安装后可以直接运行：

```bash
adata-doctor data.h5ad
```

保存报告：

```bash
adata-doctor data.h5ad --out report.md --json report.json
```

---

## 8. 项目代码结构

当前项目采用标准 Python 包结构：

```text
adata_doctor/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── adata_doctor/
│       ├── __init__.py
│       ├── api.py
│       ├── io.py
│       ├── models.py
│       ├── utils.py
│       ├── diagnose.py
│       ├── doctor.py
│       ├── compatibility.py
│       └── cli.py
└── tests/
    ├── test_diagnose.py
    └── test_api_optional.py
```

各文件职责如下：

```text
pyproject.toml
项目构建、依赖、版本和命令行入口配置。

__init__.py
包入口，暴露 report、inspect、patch_anndata 等核心接口。

api.py
用户主要 API，包括 doctor.report()、doctor.inspect() 和 patch_anndata()。

io.py
负责读取 h5ad 文件。

models.py
定义报告对象和矩阵诊断对象，支持 text、markdown、json 输出。

utils.py
放置通用工具函数。

diagnose.py
核心算法文件，负责判断单个表达矩阵的状态。

doctor.py
负责遍历 AnnData 中的 .X、.raw.X 和 layers，并整合完整报告。

compatibility.py
根据诊断结果生成下游分析建议。

cli.py
命令行入口，实现 adata-doctor 命令。

tests/
基础测试文件，用于验证核心诊断逻辑。
```

---

## 9. 技术路线

`adata_doctor` 采用启发式规则诊断矩阵状态。整体流程如下：

```text
输入 AnnData
    ↓
读取整体结构
    ↓
收集候选矩阵：.X、.raw.X、layers
    ↓
对每个矩阵抽样
    ↓
计算关键统计指标
    ↓
根据规则判断矩阵状态
    ↓
生成 evidence、warnings 和 advice
    ↓
整合 compatibility 建议
    ↓
输出 text / markdown / json 报告
```

核心判断思想包括：

```text
1. raw counts 通常具有整数特征；
2. log1p-normalized 矩阵在 expm1 后应接近线性表达量；
3. normalize_total 后每细胞总量应接近 target_sum；
4. scaled matrix 通常可能出现负值；
5. log1p(raw counts) 在 expm1 后会恢复整数特征。
```

---

## 10. 实际测试案例

### 10.1 案例一：`.X` 为 raw counts

某 pan-cancer 数据测试结果：

```text
[X]
verdict: raw_counts
confidence: 0.97
```

主要证据：

```text
nonzero integer-like ratio = 1.000
max(X) > 12
row sums close to target ratio 较低
expm1(X) 出现溢出
```

解释：

```text
该数据的 .X 大概率是原始 counts。
如果后续用于 CellTypist 或常规 log-normalized 输入流程，
应先执行 normalize_total(target_sum=1e4)，再执行 log1p。
```

---

### 10.2 案例二：`.X` 为 scaled matrix，`.raw.X` 为 log1p(raw counts)

某 HCC 数据测试结果：

```text
[X]
verdict: scaled_or_other_transformed_matrix
confidence: 0.90
```

主要证据：

```text
min(X) < 0
max(X) = 10
nonzero_ratio = 1
row_sum_median 为负值
```

解释：

```text
.X 很可能已经被 scale，不适合作为表达量矩阵直接使用。
```

同时：

```text
[raw.X]
verdict: log1p_counts_not_normalized
confidence: 0.88
```

主要证据：

```text
max(raw.X) <= 12
expm1(raw.X) 后非零值接近整数
expm1(raw.X) 后每个细胞总量不接近 10000
```

解释：

```text
.raw.X 大概率是 log1p(raw counts)，可以通过 expm1 还原 counts，
再进行 normalize_total 和 log1p。
```

该案例说明，`adata_doctor` 不仅能发现 `.X` 不可直接使用，还能进一步识别 `.raw.X` 中隐藏的可恢复表达信息。

---

## 11. 项目优势

### 11.1 直接解决公开数据复用痛点

很多单细胞公开数据没有清楚说明矩阵状态。`adata_doctor` 可以帮助用户在正式分析前快速判断，避免错误预处理。

---

### 11.2 不绑定单一下游工具

虽然项目最初来源于 CellTypist 使用前的矩阵检查需求，但它并不是 CellTypist 专用工具。

它可以服务于：

```text
Scanpy 分析前检查
CellTypist 输入前检查
Seurat 转换数据检查
marker gene 可视化前检查
差异分析前数据确认
公开数据复用
教学与数据质控
```

---

### 11.3 同时检查 `.X`、`.raw.X` 和 `layers`

许多数据的真实表达矩阵不在 `.X` 中，而是保存在 `.raw.X` 或某个 layer 中。
`adata_doctor` 会对多个候选矩阵分别诊断，而不是只检查 `.X`。

---

### 11.4 报告可解释

工具输出不仅包括最终判断，还包括：

```text
confidence
advice
evidence
warnings
statistics
compatibility
```

因此用户可以知道工具判断的依据。

---

### 11.5 易于集成和发布

项目已经具备标准 Python 包结构，支持：

```text
pip 安装
Python API
adata.report() 接口
命令行工具
Markdown 报告
JSON 报告
pytest 测试
```

适合发布到 GitHub 和 PyPI。

---



## 15. 总结

`adata_doctor` 面向单细胞公开数据复用中的一个基础但重要的问题：AnnData 中表达矩阵状态不透明。

它通过检查 `.X`、`.raw.X` 和 `layers` 中矩阵的数值特征，自动判断矩阵是否为 raw counts、log-normalized matrix、log1p(raw counts)、scaled matrix 或其他未知转换状态，并进一步给出下游分析建议。

目前测试结果表明，`adata_doctor` 已经能够识别两类非常常见的实际场景：

```text
1. .X 直接存放 raw counts；
2. .X 是 scaled matrix，而 .raw.X 是 log1p(raw counts)。
```

这说明该工具具有明确的实际使用价值，可以帮助研究者在进行 CellTypist、Scanpy、Seurat 转换、可视化或差异分析之前，快速判断当前数据是否适合直接使用。

最终，`adata_doctor` 希望成为单细胞分析流程中的第一步：

```text
先检查，再分析。
```

它帮助用户在正式分析前回答一个关键问题：

```text
这个 AnnData 文件，到底能不能直接用？
```
