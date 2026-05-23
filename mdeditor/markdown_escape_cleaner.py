"""
Markdown 转义清理工具
用于检测和纠正 AI 生成的 Markdown 文件中过多的转义字符
"""
import re


class MarkdownEscapeCleaner:
    """Markdown 转义清理器"""
    
    def __init__(self):
        # 定义需要清理的过度转义模式
        self.escape_patterns = [
            # 1. 过度的反斜杠转义（如 \\* 应该是 *）
            (r'\\\\([*_`~#])', r'\1'),  # \\* -> *, \\_ -> _ 等
            
            # 2. HTML 实体过度转义
            (r'&lt;', '<'),
            (r'&gt;', '>'),
            (r'&amp;', '&'),
            (r'&quot;', '"'),
            (r'&#39;', "'"),
            
            # 3. JSON 字符串中的过度转义（如 \" 应该是 "）
            (r'\\"', '"'),
            
            # 4. 代码块内的过度转义（需要特殊处理）
            # 注意：这个会在后续单独处理
        ]
        
        # 定义不应该被清理的场景（保护模式）
        self.protected_patterns = [
            # 代码块内容（``` ... ```）
            r'```[\s\S]*?```',
            # 行内代码（`...`）
            r'`[^`]+`',
            # URL 中的转义
            r'https?://[^\s]+',
        ]
    
    def detect_excessive_escapes(self, text: str) -> dict:
        """
        检测文本中是否存在过度转义
        
        Args:
            text: 待检测的文本
            
        Returns:
            检测结果字典，包含：
            - has_issues: 是否发现问题
            - issues: 问题列表
            - issue_count: 问题数量
        """
        issues = []
        
        # 检查各种过度转义模式
        checks = [
            {
                'name': '双反斜杠转义',
                'pattern': r'\\\\[*_`~#\[\](){}]',
                'description': '发现 \\*、\\_ 等过度转义'
            },
            {
                'name': 'HTML 实体转义',
                'pattern': r'&(lt|gt|amp|quot|#39);',
                'description': '发现 &lt;、&gt; 等 HTML 实体'
            },
            {
                'name': 'JSON 风格转义',
                'pattern': r'\\"',
                'description': '发现 \\" 等 JSON 风格转义'
            },
            {
                'name': '过度转义的链接',
                'pattern': r'\\\[.*?\\\]\\\(.*?\\\)',
                'description': '发现 \\[text\\](url) 格式的链接'
            },
            {
                'name': '过度转义的标题',
                'pattern': r'^\\#+\s',
                'description': '发现 \\# 标题格式',
                'flags': re.MULTILINE
            },
        ]
        
        for check in checks:
            flags = check.get('flags', 0)
            matches = re.findall(check['pattern'], text, flags)
            if matches:
                issues.append({
                    'type': check['name'],
                    'count': len(matches),
                    'description': check['description'],
                    'examples': matches[:3]  # 只取前3个示例
                })
        
        return {
            'has_issues': len(issues) > 0,
            'issues': issues,
            'issue_count': sum(issue['count'] for issue in issues)
        }
    
    def clean_escapes(self, text: str) -> str:
        """
        清理文本中的过度转义 - 激进模式
        优先让 Markdown 语法生效，而非保留转义
        
        Args:
            text: 待清理的文本
            
        Returns:
            清理后的文本
        """
        # 第一步：保护代码块和行内代码
        protected_blocks = []
        
        def protect_code(match):
            """保护代码块"""
            placeholder = f"__PROTECTED_BLOCK_{len(protected_blocks)}__"
            protected_blocks.append(match.group(0))
            return placeholder
        
        # 保护 fenced 代码块
        text = re.sub(r'```[\s\S]*?```', protect_code, text)
        # 保护行内代码
        text = re.sub(r'`[^`]+`', protect_code, text)
        
        # 第二步：激进清理各种过度转义
        cleaned_text = text
        
        # 多次迭代清理，确保处理嵌套转义
        for iteration in range(10):  # 增加到10次迭代
            prev_text = cleaned_text
            
            # 1. 清理所有双反斜杠转义（最激进）
            cleaned_text = re.sub(r'\\\\([*_`~#\[\](){}>+|=-])', r'\1', cleaned_text)
            
            # 2. 清理 HTML 实体
            html_entities = {
                '&lt;': '<',
                '&gt;': '>',
                '&amp;': '&',
                '&quot;': '"',
                '&#39;': "'",
                '&nbsp;': ' ',
            }
            for entity, replacement in html_entities.items():
                cleaned_text = cleaned_text.replace(entity, replacement)
            
            # 3. 清理 JSON 风格的转义
            cleaned_text = re.sub(r'\\"', '"', cleaned_text)
            cleaned_text = re.sub(r"\\'", "'", cleaned_text)
            
            # 4. 清理链接和图片（激进模式）
            cleaned_text = re.sub(r'\\\[(.+?)\\\]\\\((.+?)\\\)', r'[\1](\2)', cleaned_text)
            cleaned_text = re.sub(r'!\\\[(.+?)\\\]\\\((.+?)\\\)', r'![\1](\2)', cleaned_text)
            
            # 5. 清理标题
            cleaned_text = re.sub(r'^\\+(#+)\s', r'\1 ', cleaned_text, flags=re.MULTILINE)
            
            # 6. 清理列表项
            cleaned_text = re.sub(r'^\\+([-*+])\s', r'\1 ', cleaned_text, flags=re.MULTILINE)
            
            # 7. 清理强调符号（粗体、斜体）
            cleaned_text = re.sub(r'\\+\*\*(.+?)\\+\*\*', r'**\1**', cleaned_text)
            cleaned_text = re.sub(r'\\+\*(.+?)\\+\*', r'*\1*', cleaned_text)
            cleaned_text = re.sub(r'\\+_(.+?)\\+_', r'_\1_', cleaned_text)
            cleaned_text = re.sub(r'\\+__(.+?)\\+__', r'__\1__', cleaned_text)
            
            # 8. 清理引用块
            cleaned_text = re.sub(r'^\\+>\s', r'> ', cleaned_text, flags=re.MULTILINE)
            
            # 9. 清理水平线
            cleaned_text = re.sub(r'^\\+[-*_]{3,}\s*$', r'---', cleaned_text, flags=re.MULTILINE)
            
            # 10. 清理表格分隔符
            cleaned_text = re.sub(r'\\+\|', '|', cleaned_text)
            
            # 如果这次迭代没有变化，提前退出
            if cleaned_text == prev_text:
                break
        
        # 第三步：清理剩余的单个反斜杠转义（针对 Markdown 特殊字符）
        # 这些字符在 Markdown 中有特殊含义，应该去掉转义让它们生效
        markdown_special_chars = r'\*\_\#\[\]\(\)\>\+\|\=\-'
        cleaned_text = re.sub(r'\\([' + markdown_special_chars + r'])', r'\1', cleaned_text)
        
        # 第四步：恢复保护的代码块
        for i, block in enumerate(protected_blocks):
            placeholder = f"__PROTECTED_BLOCK_{i}__"
            cleaned_text = cleaned_text.replace(placeholder, block)
        
        return cleaned_text
    
    def clean_and_report(self, text: str) -> dict:
        """
        清理转义并生成报告
        
        Args:
            text: 待清理的文本
            
        Returns:
            包含清理结果和报告的字典
        """
        # 检测问题
        detection = self.detect_excessive_escapes(text)
        
        # 如果有问题，进行清理
        if detection['has_issues']:
            cleaned_text = self.clean_escapes(text)
            
            # 验证清理效果
            after_detection = self.detect_excessive_escapes(cleaned_text)
            
            return {
                'success': True,
                'original_issues': detection,
                'remaining_issues': after_detection,
                'cleaned_text': cleaned_text,
                'improvement': {
                    'before_count': detection['issue_count'],
                    'after_count': after_detection['issue_count'],
                    'fixed_count': detection['issue_count'] - after_detection['issue_count']
                }
            }
        else:
            return {
                'success': True,
                'message': '未发现过度转义问题',
                'original_issues': detection,
                'cleaned_text': text
            }
    
    def format_report(self, result: dict) -> str:
        """
        格式化检测报告
        
        Args:
            result: clean_and_report 返回的结果
            
        Returns:
            格式化的报告字符串
        """
        lines = []
        lines.append("=" * 60)
        lines.append("Markdown 转义清理报告")
        lines.append("=" * 60)
        lines.append("")
        
        if result.get('message'):
            lines.append(f"✅ {result['message']}")
            return '\n'.join(lines)
        
        # 原始问题
        lines.append("📋 检测到的问题:")
        lines.append("-" * 60)
        
        for issue in result['original_issues']['issues']:
            lines.append(f"• {issue['type']}: {issue['count']} 处")
            lines.append(f"  说明: {issue['description']}")
            if issue.get('examples'):
                lines.append(f"  示例: {issue['examples'][0]}")
            lines.append("")
        
        # 清理结果
        if result.get('improvement'):
            imp = result['improvement']
            lines.append("✨ 清理结果:")
            lines.append("-" * 60)
            lines.append(f"修复前: {imp['before_count']} 个问题")
            lines.append(f"修复后: {imp['after_count']} 个问题")
            lines.append(f"已修复: {imp['fixed_count']} 个问题")
            lines.append("")
            
            if imp['after_count'] > 0:
                lines.append("⚠️  仍有未修复的问题:")
                for issue in result['remaining_issues']['issues']:
                    lines.append(f"  • {issue['type']}: {issue['count']} 处")
                lines.append("")
        
        lines.append("=" * 60)
        
        return '\n'.join(lines)


def clean_markdown_file(file_path: str, backup: bool = True) -> dict:
    """
    清理 Markdown 文件中的过度转义
    
    Args:
        file_path: 文件路径
        backup: 是否创建备份
        
    Returns:
        清理结果
    """
    import os
    from datetime import datetime
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        original_text = f.read()
    
    # 创建清理器
    cleaner = MarkdownEscapeCleaner()
    
    # 清理
    result = cleaner.clean_and_report(original_text)
    
    # 如果有改进，保存文件
    if result.get('improvement') and result['improvement']['fixed_count'] > 0:
        # 创建备份
        if backup:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{file_path}.backup_{timestamp}"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_text)
            result['backup_path'] = backup_path
        
        # 保存清理后的文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(result['cleaned_text'])
        
        result['file_saved'] = True
    else:
        result['file_saved'] = False
    
    return result


if __name__ == '__main__':
    # 测试示例
    test_text = r"""
# 测试文档

这是一个\\*测试\\*文档。

## 链接测试

\\[点击这里\\]\\(https://example.com\\)

## 代码测试

```python
# 这段代码不应该被修改
print("\\*test\\*")
```

## HTML 实体

&lt;div&gt;测试&lt;/div&gt;

## 列表

\\- 项目1
\\- 项目2
"""
    
    cleaner = MarkdownEscapeCleaner()
    result = cleaner.clean_and_report(test_text)
    
    print(cleaner.format_report(result))
    print("\n清理后的文本:")
    print(result['cleaned_text'])
