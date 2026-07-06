---
name: optimize-search-wait-time
overview: 将 search_product 方法中搜索后的等待时间优化为固定 3s，去掉耗时的 wait_for_network_idle()，提升测试执行效率。
todos:
  - id: optimize-search-wait
    content: 将 enterprise_zone_page.py 中 search_product 方法搜索后的等待优化为固定 3s
    status: completed
---

## 优化目标

将企业专区搜索后的等待时间从 `wait_for_network_idle() + 2s` 优化为固定 3s。

## 当前问题

`search_product` 方法中搜索按钮点击后，先执行 `wait_for_network_idle()`（最长超时 30s），再执行 `wait_for_timeout(2000)`，总等待最长可达 32s+。

## 优化方案

去掉 `wait_for_network_idle()`，仅保留固定 `wait_for_timeout(3000)`，总等待稳定在 3s。

## 技术方案

### 修改位置

`f:\UI_AUTO\pages\enterprise_zone_page.py` 第 72-73 行

### 修改内容

将：

```python
self.wait_for_network_idle()
self.page.wait_for_timeout(2000)
```

替换为：

```python
self.page.wait_for_timeout(3000)
```

### 变更理由

- `wait_for_network_idle()` 在 SPA 长轮询场景下经常超时（30s），实际搜索返回速度远快于此
- 固定 3s 等待已足够组件渲染和搜索结果展示
- 减少不必要的超时开销，将流程总耗时缩短约 27s+