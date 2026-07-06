# 执行步骤 7：验证客户登录流程

## 已完成的工作
1. ✅ 修复了 `CustomerLoginPage.open()` 方法中的错误（`USERNAME_INPUT` → `USERNAME_INPUT_ALT`）
2. ✅ 创建了简单测试脚本 `test_login_simple.py`
3. ✅ 验证了代码没有语法错误

## 下一步：运行测试验证登录流程

### 方式一：运行 pytest 测试（推荐）
```bash
cd f:\UI_AUTO
python -m pytest test_quick_login.py -v -s
```

### 方式二：运行简单测试脚本（更直观）
```bash
cd f:\UI_AUTO
python test_login_simple.py
```

### 方式三：使用非 headless 模式（方便观察）
```bash
cd f:\UI_AUTO
$env:HEADLESS="false"
python -m pytest test_quick_login.py -v -s
```

## 预期结果
1. 浏览器打开登录页面：`https://zjtest.gyuncai.com/mall/view/login`
2. 输入用户名：`18501375833`
3. 输入密码：`123qwe`
4. 点击"立即登录"按钮
5. 处理可能的首次登录弹窗
6. 处理可能的公司选择（如果有多家公司）
7. 验证登录成功（看到客户首页）

##  Troubleshoothooting
如果测试失败，请检查：
1. 测试环境是否可访问：`https://zjtest.gyuncai.com/mall/view/login`
2. 账号密码是否正确：`.env` 文件中的 `CUSTOMER_USERNAME` 和 `CUSTOMER_PASSWORD`
3. 页面元素是否匹配：`pages/customer_login_page.py` 中的选择器
