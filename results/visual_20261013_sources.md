# 本轮图表视觉升级：官方来源与可执行约束

核验日期：2026-10-13。任务范围仅为只读查证和设计建议；未修改论文、数据、分析、制图脚本或已有图件。使用 sci-figures 的制作原则及 agent-reach 路由：Exa 定位官网，Jina 阅读官网全文，GitHub 官方 gh API 阅读 SciencePlots 源码。未安装新工具或技能，未下载原始材料到 D 盘。

## 调研结论

- 本文采用 Nature 的视觉语言，同时按实际投稿期刊 BMC Psychology 的成品尺寸设计。Nature 标准宽度为 89/183 mm；BMC 的最终 PDF 宽度为 85/170 mm。因此建议本文两张主图直接采用 **170 mm 宽**，保留 Nature 的字体、细线、简洁布局和可编辑矢量特征，避免排版缩小后文字再次变小。[Nature 最终制作指南](https://www.nature.com/nature/for-authors/final-submission)、[BMC Psychology 投稿指南](https://link.springer.com/journal/40359/submission-guidelines)
- Nature 普通图中文字为 **5–7 pt**；多面板字母为 **8 pt、粗体、正体、小写**。优先 Arial/Helvetica，全图统一，图中文字以黑色或近黑色为主。本文建议实际成品尺寸下标签和短说明 7 pt，面板字母 8 pt；不为容纳文字主动降至 5 pt。[Nature 研究图规范：Text](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/#text)
- Nature 要求最终尺寸下线宽 **0.25–1 pt**；BMC 要求按标准宽度缩放后的线宽 **大于 0.25 pt**。本文建议轴/刻度/边框 0.5 pt、置信区间 0.8 pt、零线 0.5 pt、主要公式或分组线不超过 1 pt。这些具体选值是本轮设计建议，不是官网逐项规定。[Nature Sizing](https://www.nature.com/nature/for-authors/final-submission)、[BMC Figure size and resolution](https://link.springer.com/journal/40359/submission-guidelines)
- 首要成果应是含可编辑文字和线条的 **PDF**，同时保留可编辑 **SVG**；PNG/TIFF 用作本用户要求的高分辨率版本。用户要求“900 dpi 以上”时可直接导出 **1200 dpi**，满足严格大于 900 的理解。不得放大旧位图伪造细节。Nature 的照片最低分辨率和在线证明分辨率不等同于用户本次交付要求。[Nature Exporting](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/#exporting)、[Nature Image resolution](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/#image-resolution)
- 现有 SciencePlots 足以提供基础样式；无需盲装额外图表工具。其 `nature` 默认宽度约 83.82 mm，字体优先级以 DejaVu Sans 开头，默认参数并不会自动完成 BMC 的 170 mm 尺寸、Arial 选择、面板字母和防重叠检查。[SciencePlots nature 源码](https://github.com/garrettj403/SciencePlots/blob/b9b16959570bd2fbc9ff5118bacc423c3bddd592/src/scienceplots/styles/journals/nature.mplstyle)

## 1. 官方约束、样式默认值与本轮选择

| 项目 | 已读官方规定/源码事实 | 本文建议 |
|---|---|---|
| 成品宽度 | Nature 89/183 mm；可用 120–136 mm 中间宽度。BMC 85/170 mm。 | 两张主图采用 170 mm 宽；先按成品尺寸排版和检查。 |
| 高度 | Nature 新版面板构建指南规定主图最大 170 mm 高。Nature 的 247 mm 是整页深度。BMC 图及图注最大高 225 mm。 | 图1约 95–115 mm、图2约 75–95 mm，按内容调整；不要为压缩高度挤字。具体高度是建议。 |
| 字体 | Nature 优先 Arial/Helvetica 无衬线。普通文字 5–7 pt，面板字母 8 pt 粗体正体小写。BMC 要求字体嵌入。 | 实际字体显式选择 Arial；普通文字以 7 pt 为基准，面板 8 pt；数学表达检查字体及上下标是否清楚。 |
| 线宽 | Nature 0.25–1 pt；BMC 成品线宽 >0.25 pt。SciencePlots nature 轴和网格 0.5 pt、普通线 1 pt。 | 轴0.5、CI0.8、零线0.5 pt；浅灰不能浅到看不清。 |
| 颜色 | Nature 推荐 RGB、可辨识的色盲友好组合；避免用彩色文字代替图形键。 | 文字黑色；估计值用近黑、蓝 `#0072B2`、朱红 `#D55E00` 加不同符号；对比和灰度检查后采用。这三个颜色来自官网示例调色板。 |
| 布局 | Nature 避免背景格线、装饰、阴影、重叠文字；面板有序、紧凑且可读。 | 白底，去除大面积灰底卡片与阴影；依靠对齐、留白和细分组线建立层级。零参考线保留，避免添加背景网格。 |
| 矢量 | Nature 要求线、箭头、盒子和文字可编辑，PDF/EPS 优选，SVG可接受；BMC优先PDF矢量。 | PDF为投稿首选，SVG为可编辑源；不把旧PNG装进PDF冒充矢量。 |
| 分辨率 | Nature 要求照片至少300 dpi，研究图导出段落建议图像至少450 dpi；用户本次要求更高。 | 从绘图源直接导出1200 dpi位图，保留PDF/SVG；DPI不是矢量清晰度指标。 |
| 文件大小 | BMC 单个图文件≤10 MB。Nature 主图指南建议尽量≤50 MB；后者不适用于替代BMC上限。 | 核查每个交付文件大小；矢量PDF通常最适合提交。若另存TIFF，使用无损LZW。 |
| 图题与图注 | BMC 图题≤15词，图注≤300词，放正文；图形键放图内；多面板作为一份合成图。 | 图内只留必要面板小标题、单位和图形键；不在图内重复全文图注。 |

表中来源：[Nature 最终制作指南](https://www.nature.com/nature/for-authors/final-submission)、[Nature 图形规范](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/)、[Nature 面板构建与导出](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/)、[BMC Psychology 投稿指南](https://link.springer.com/journal/40359/submission-guidelines)、[固定版本 nature 样式](https://github.com/garrettj403/SciencePlots/blob/b9b16959570bd2fbc9ff5118bacc423c3bddd592/src/scienceplots/styles/journals/nature.mplstyle)。

## 2. SciencePlots 源码核验及实现注意事项

读取的是仓库 `garrettj403/SciencePlots` 的 `master`，核验时最新提交为 `b9b16959570bd2fbc9ff5118bacc423c3bddd592`，提交时间 2026-06-23，提交说明为2.2.1发行日期修订。下面链接固定到该提交，避免后来默认分支变化。

- `nature` 设置画布为3.3 × 2.5 inch，普通字号7 pt、轴线0.5 pt、普通线1 pt、标记3 pt；字体候选首先是DejaVu Sans。它不能替代明确的成品尺寸和字体选择。[nature.mplstyle 全文](https://github.com/garrettj403/SciencePlots/blob/b9b16959570bd2fbc9ff5118bacc423c3bddd592/src/scienceplots/styles/journals/nature.mplstyle)
- `nature` 中保存为tight的两行已注释；但基础 `science` 实际启用 `savefig.bbox: tight`、`savefig.pad_inches: 0.05`。按README组合样式时，基础项仍然生效。因此不能仅凭 `figsize` 判断最终PDF/SVG毫米尺寸，必须检查导出边界。[science.mplstyle 全文](https://github.com/garrettj403/SciencePlots/blob/b9b16959570bd2fbc9ff5118bacc423c3bddd592/src/scienceplots/styles/science.mplstyle)、[SciencePlots README](https://github.com/garrettj403/SciencePlots/blob/b9b16959570bd2fbc9ff5118bacc423c3bddd592/README.md)
- 基础 `science` 默认开启LaTeX、上/右刻度和次刻度。本次没有必要因字体样式另外安装LaTeX；可使用已安装环境的 `no-latex` 组合或显式 `text.usetex=False`，并按图的内容关闭不必要的上/右/次刻度。其README明确样式可组合、后面的样式覆盖前面的相应参数；这些覆盖属于实现选择。[science 源码](https://github.com/garrettj403/SciencePlots/blob/b9b16959570bd2fbc9ff5118bacc423c3bddd592/src/scienceplots/styles/science.mplstyle)、[README Using the Styles](https://github.com/garrettj403/SciencePlots/blob/b9b16959570bd2fbc9ff5118bacc423c3bddd592/README.md)
- PDF采用 `pdf.fonttype=42`。Nature 官网直接给出该Matplotlib设置，以保留可编辑文字。SVG采用 `svg.fonttype='none'` 可以保留文字字符串；Matplotlib说明这会受查看机器字体影响，所以交付时仍需核对字体和PDF显示，不能声称SVG已经嵌入全部字体。[Nature Outlined text](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/#outlined-text)、[Matplotlib Fonts in SVG](https://matplotlib.org/stable/users/explain/text/fonts.html#fonts-in-svg)
- 防重叠可使用已有Matplotlib `layout='constrained'`，在建图时启用；不要随后调用 `tight_layout()`，官方文档说明后者会关闭constrained layout。自动布局主要处理轴标签、刻度、图例和色条，不保证任意手工文本与CI/箭头完全不碰撞。[Matplotlib constrained layout](https://matplotlib.org/stable/users/explain/axes/constrainedlayout_guide.html)
- `savefig` 的 `dpi` 是位图分辨率；`bbox_inches='tight'` 会按计算得到的边界裁切。需要测量真实输出宽高，而不是只读取脚本参数。170 mm宽、1200 dpi的位图约8031像素宽，取整与实际裁切会造成少量差异；这是毫米到像素换算，不是期刊规定。[Matplotlib savefig API](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html)

## 3. 针对本文两张图的设计建议

本节是结合现有制图脚本与论文内容做的设计判断，不是Nature对该论文的评价。只读定位：`scripts/make_revision_figures.py`。没有运行或修改该脚本，也没有据此改动估计值。

### Figure 1：层次分解与条件同班同学估计

- 用四个有序小面板或两行结构，编号a–d；按标题、公式、简短解释的三层顺序对齐。保持各面板明确独立，公式作为可编辑数学文本。
- 整图170 mm宽；每个面板内让公式占足够的竖向空间。标题与正文7 pt、面板字母8 pt；若某标题换成两行，应同步调整该行各面板的垂直位置，不能把文字压在边框上。
- 采用白底，浅灰细边框或简洁分隔线；去除卡片阴影和复杂装饰。公式与说明之间留空，线条不得穿过公式、下标或说明文字。
- 不以箭头图形暗示因果先后，不因视觉升级改变within、between、difference和leave-one-out sensitivity的定义。独立短面板更适合当前研究的估计量解释。

依据是Nature要求简洁、避免重叠和无功能装饰、文字可编辑；面板具体排法是本轮建议。[Nature Graphs/Text](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/)

### Figure 2：三项调查中的估计与不确定性

- 保留三个独立面板：CEPS负性情感、ECLS-K Grade8内部化问题、TIMSS Finland学校归属感。各面板都有清楚的调查及结局名称，始终使用原始分析规定的点估计和95%区间。
- 三个面板使用各自横轴、合理刻度和完整单位，不能用统一横轴或装饰性连接线暗示跨调查系数幅度可直接比较。横轴单位须说明“每增加一个预测变量分值”的原始尺度解释。
- Within、Between、Between−within用相同的行次序；近黑圆点、蓝色方点、朱红菱形可同时提供颜色与形状编码。图形键的文字仍用黑色，保证灰度下也能识别。[Nature accessible palette](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/#making-your-colours-accessible)
- 零线保持轻灰0.5 pt虚线，CI约0.8 pt、端帽约2 pt、标记约3–4 pt。零线穿过某CI是数据关系，可以保留；零线、CI或端帽碰到文字则必须重新布局。具体粗细与大小是本轮建议。
- 为三个面板的行标签预留真实宽度；不要让中间面板的长标签侵入左侧面板。优先短行标签、足够面板间距；如使用统一图形键，可减少重复文字，但不损失估计量对应关系。
- 面板字母在各面板左上方固定位置，与小标题分开。置信区间方法及条件化解释留在正文图注；图内文字只承担识别和读值任务。避免把精确数值列表再放到CI线旁制造拥挤。[Nature panel arrangement](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/#panel-arrangement)、[BMC figure legends](https://link.springer.com/journal/40359/submission-guidelines)

## 4. 交付检查与争议边界

建议生产者在最终170 mm宽下逐项验收：所有标题/标签/公式处于画布内；文字之间、文字与边框/CI/端帽/参考线之间无碰撞；面板字母与标题不重叠；CI不截断；轴单位和符号无乱码；普通文字实际成品字号不低于可读限度；PDF字体嵌入且文字可选；SVG保留文字节点；位图直接1200 dpi且文件大小符合BMC。先运行文字边界/图形边界检查，再查看实际成品尺寸预览，不能把自动布局成功等同于视觉检查通过。[Nature specifications](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/)、[Matplotlib constrained layout](https://matplotlib.org/stable/users/explain/axes/constrainedlayout_guide.html)、[BMC guidelines](https://link.springer.com/journal/40359/submission-guidelines)

Nature官网存在不同用途的格式与DPI表述：最终提交页面允许摄影图TIFF，研究图面板指南则强调主图可编辑矢量；Extended Data另有300 dpi上限。不能把某段落改写为所有图都禁止TIFF或所有图都要450/900dpi。本研究为线图和示意图，使用PDF+SVG并另外交付用户要求的1200dpi位图即可；本轮不套用Nature Extended Data上传规则。[Nature final submission](https://www.nature.com/nature/for-authors/final-submission)、[Nature main/extended-data formats](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/)

本报告只能确认来源与设计约束，不能证明新图已经达到无重叠、可编辑或数值一致；这些需要由实际生产与最终QA完成。

## 来源列表与获取层次

1. [Nature: Final submission](https://www.nature.com/nature/for-authors/final-submission)：官网全文，Jina读取；重点核对Lettering、Sizing、Image types、Electronic image formats。页面说明该指南用于Nature接受后的制作环节，本项目将其作为风格参考。
2. [Nature research figure guide: Preparing figures—our specifications](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/)：官网全文，Jina通过同域http入口读取；重点核对Graphs、Text、Outlined text、Exporting。直接https的Jina请求一次失败，http入口成功，不是登录限制。
3. [Nature research figure guide: Building and exporting figure panels](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/)：官网全文，Jina同域http入口；核对170mm图高上限、字体、色板、主图和Extended Data格式区别。
4. [Nature: Guide to preparing final artwork PDF](https://www.nature.com/documents/nature-final-artwork.pdf)：官方单页PDF正文由Jina提取，响应标示2020-02-18；本轮未视觉查看PDF版面。可佐证标准尺寸及字体；当前格式要求以较新的研究图网页为准。
5. [BMC Psychology: Submission guidelines](https://link.springer.com/journal/40359/submission-guidelines)：本轮重新从官网读取，定位Preparing illustrations and figures及Figure size and resolution；核对85/170mm、225mm、>0.25pt、嵌入字体、≤10MB和PDF优选。
6. [SciencePlots nature.mplstyle](https://github.com/garrettj403/SciencePlots/blob/b9b16959570bd2fbc9ff5118bacc423c3bddd592/src/scienceplots/styles/journals/nature.mplstyle)：gh API原始源码全文，固定提交。
7. [SciencePlots science.mplstyle](https://github.com/garrettj403/SciencePlots/blob/b9b16959570bd2fbc9ff5118bacc423c3bddd592/src/scienceplots/styles/science.mplstyle)：gh API原始源码全文，固定提交。
8. [SciencePlots README](https://github.com/garrettj403/SciencePlots/blob/b9b16959570bd2fbc9ff5118bacc423c3bddd592/README.md)：gh API全文，核对样式组合与nature用途。仓库不是Nature官方软件，本报告不声称其获得Nature认证。
9. [Matplotlib: Constrained layout guide](https://matplotlib.org/stable/users/explain/axes/constrainedlayout_guide.html)：官方文档，Jina读取并深读开头、启用及tight_layout警告；页面为3.11.2。
10. [Matplotlib: Fonts](https://matplotlib.org/stable/users/explain/text/fonts.html)：官方文档，Jina读取相关全文段落；核对SVG path/none、字体嵌入和可编辑性。
11. [Matplotlib: savefig](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html)：官方API正文，Jina读取；核对dpi、format、bbox_inches、pad_inches的含义。

本轮只使用官方指南、原仓库代码和官方技术文档支撑约束，没有采用博主图形模板或把搜索摘要当成已读全文。
