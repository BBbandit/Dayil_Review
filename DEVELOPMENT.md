# 开发指南

## Git 工作流

### 分支结构
- `master` - 主分支，存放稳定版本
- `develop` - 开发分支，用于日常开发

### 开发流程
1. 从 `develop` 分支创建特性分支
   ```bash
   git checkout develop
   git checkout -b feature/your-feature-name
   ```

2. 开发完成后提交更改
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   ```

3. 合并到开发分支
   ```bash
   git checkout develop
   git merge feature/your-feature-name
   ```

4. 定期将开发分支合并到主分支
   ```bash
   git checkout master
   git merge develop
   ```

## 提交信息规范

使用约定式提交（Conventional Commits）：

- `feat:` - 新功能
- `fix:` - 修复bug
- `docs:` - 文档更新
- `style:` - 代码格式调整
- `refactor:` - 代码重构
- `test:` - 测试相关
- `chore:` - 构建过程或辅助工具变动

示例：
```bash
git commit -m "feat: 添加连板天梯热力图功能"
git commit -m "fix: 修复数据加载性能问题"
```

## 项目结构

```
├── main.py              # 基础版本主程序
├── main_enhanced.py     # 增强版主程序（推荐使用）
├── config.py            # 配置文件
├── requirements.txt     # Python依赖
├── README.md           # 项目说明文档
├── DEVELOPMENT.md      # 开发指南（本文件）
├── .gitignore          # Git忽略文件
└── output/             # 生成的HTML文件（已忽略）
```

## 开发环境设置

1. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

2. 运行测试
   ```bash
   python main_enhanced.py
   ```

3. 代码规范
   - 遵循PEP8编码规范
   - 使用类型注解
   - 添加适当的注释

## 功能开发计划

### Phase 1 - 核心功能（已完成）
- [x] 基础框架搭建
- [x] 四个主要功能模块
- [x] 模拟数据集成
- [x] 响应式界面设计

### Phase 2 - 数据接入
- [ ] 实时数据API接入
- [ ] 数据库持久化
- [ ] 数据缓存机制

### Phase 3 - 高级功能
- [ ] 用户认证系统
- [ ] 数据导出功能
- [ ] 移动端优化
- [ ] 性能监控

## 注意事项

1. 不要将敏感信息提交到Git（API密钥、数据库密码等）
2. 定期从远程仓库拉取更新
3. 提交前运行测试确保功能正常
4. 保持提交历史的清晰和规范