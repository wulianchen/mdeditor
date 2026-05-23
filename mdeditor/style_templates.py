"""
预览区风格模板
根据 style.md 中的设计系统定义
"""

def get_default_style():
    """默认风格"""
    return """
        html {
            margin: 0;
            padding: 0;
        }
        body {
            margin: 0;
            padding: 20px;
            font-family: "微软雅黑", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            -webkit-user-select: text;
            user-select: text;
        }
        ::selection {
            background-color: #b4d7ff;
            color: #000;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 24px;
            margin-bottom: 16px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
            color: #2c3e50;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: Consolas, Monaco, monospace;
            font-size: 0.9em;
        }
        pre {
            background-color: #f5f5f5;
            padding: 16px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 4px solid #ddd;
        }
        pre code {
            background-color: transparent;
            padding: 0;
        }
        blockquote {
            border-left: 4px solid #ddd;
            padding-left: 16px;
            color: #666;
            margin: 16px 0;
            font-style: italic;
        }
        a {
            color: #3498db;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        hr {
            border: none;
            border-top: 2px solid #eee;
            margin: 24px 0;
        }
        ul, ol {
            padding-left: 24px;
        }
        li {
            margin: 4px 0;
        }
"""


def get_ant_style():
    """Ant Design 阿里风格"""
    return """
        html {
            margin: 0;
            padding: 0;
        }
        body {
            margin: 0;
            padding: 24px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.5715;
            color: rgba(0, 0, 0, 0.85);
            background: #f0f2f5;
            -webkit-user-select: text;
            user-select: text;
        }
        ::selection {
            background-color: #1677ff;
            color: #fff;
        }
        h1, h2, h3, h4, h5, h6 {
            color: rgba(0, 0, 0, 0.85);
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
            background: #fff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        th, td {
            border: 1px solid #f0f0f0;
            padding: 12px 16px;
            text-align: left;
        }
        th {
            background-color: #fafafa;
            font-weight: 600;
            color: rgba(0, 0, 0, 0.85);
        }
        tr:nth-child(even) {
            background-color: #fafafa;
        }
        tr:hover {
            background-color: #e6f7ff;
        }
        code {
            background-color: #f5f5f5;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
            font-size: 0.9em;
            color: #cf222e;
        }
        pre {
            background-color: #f5f5f5;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid #d9d9d9;
        }
        pre code {
            background-color: transparent;
            padding: 0;
            color: inherit;
        }
        blockquote {
            border-left: 4px solid #1677ff;
            padding-left: 16px;
            color: rgba(0, 0, 0, 0.65);
            margin: 16px 0;
            font-style: normal;
            background: #fff;
            padding: 12px 16px;
            border-radius: 4px;
        }
        a {
            color: #1677ff;
            text-decoration: none;
        }
        a:hover {
            color: #4096ff;
        }
        hr {
            border: none;
            border-top: 1px solid #f0f0f0;
            margin: 24px 0;
        }
        ul, ol {
            padding-left: 24px;
        }
        li {
            margin: 4px 0;
        }
"""


def get_material_style():
    """Material Design 谷歌风格"""
    return """
        html {
            margin: 0;
            padding: 0;
        }
        body {
            margin: 0;
            padding: 24px;
            font-family: "Roboto", "Helvetica", "Arial", sans-serif;
            line-height: 1.6;
            color: #212121;
            background: #fafafa;
            -webkit-user-select: text;
            user-select: text;
        }
        ::selection {
            background-color: #2196F3;
            color: #fff;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #212121;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 500;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
            background: #fff;
            border-radius: 4px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        }
        th, td {
            border: none;
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        th {
            background-color: #f5f5f5;
            font-weight: 500;
            color: #212121;
            text-transform: uppercase;
            font-size: 0.875em;
        }
        tr:nth-child(even) {
            background-color: #fafafa;
        }
        tr:hover {
            background-color: #eeeeee;
        }
        code {
            background-color: #f5f5f5;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: "Roboto Mono", monospace;
            font-size: 0.9em;
            color: #d32f2f;
        }
        pre {
            background-color: #263238;
            color: #eceff1;
            padding: 16px;
            border-radius: 4px;
            overflow-x: auto;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        pre code {
            background-color: transparent;
            padding: 0;
            color: inherit;
        }
        blockquote {
            border-left: 4px solid #2196F3;
            padding-left: 16px;
            color: #757575;
            margin: 16px 0;
            font-style: italic;
            background: #fff;
            padding: 12px 16px;
            border-radius: 4px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        a {
            color: #2196F3;
            text-decoration: none;
            font-weight: 500;
        }
        a:hover {
            text-decoration: underline;
        }
        hr {
            border: none;
            border-top: 1px solid #e0e0e0;
            margin: 24px 0;
        }
        ul, ol {
            padding-left: 24px;
        }
        li {
            margin: 4px 0;
        }
"""


def get_element_style():
    """Element Plus 饿了么风格"""
    return """
        html {
            margin: 0;
            padding: 0;
        }
        body {
            margin: 0;
            padding: 20px;
            font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", Arial, sans-serif;
            line-height: 1.6;
            color: #303133;
            background: #f5f7fa;
            -webkit-user-select: text;
            user-select: text;
        }
        ::selection {
            background-color: #409eff;
            color: #fff;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #303133;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
            background: #fff;
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        }
        th, td {
            border: 1px solid #ebeef5;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f5f7fa;
            font-weight: 600;
            color: #606266;
        }
        tr:nth-child(even) {
            background-color: #fafafa;
        }
        tr:hover {
            background-color: #f5f7fa;
        }
        code {
            background-color: #f4f4f5;
            padding: 2px 6px;
            border-radius: 6px;
            font-family: Consolas, Monaco, monospace;
            font-size: 0.9em;
            color: #909399;
        }
        pre {
            background-color: #f4f4f5;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
            border: 1px solid #e4e7ed;
        }
        pre code {
            background-color: transparent;
            padding: 0;
        }
        blockquote {
            border-left: 4px solid #409eff;
            padding-left: 16px;
            color: #909399;
            margin: 16px 0;
            background: #fff;
            padding: 12px 16px;
            border-radius: 6px;
        }
        a {
            color: #409eff;
            text-decoration: none;
        }
        a:hover {
            color: #66b1ff;
        }
        hr {
            border: none;
            border-top: 1px solid #ebeef5;
            margin: 24px 0;
        }
        ul, ol {
            padding-left: 24px;
        }
        li {
            margin: 4px 0;
        }
"""


def get_arco_style():
    """Arco Design 字节风格"""
    return """
        html {
            margin: 0;
            padding: 0;
        }
        body {
            margin: 0;
            padding: 24px;
            font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #1d2129;
            background: linear-gradient(135deg, #f7f8fa 0%, #ffffff 100%);
            -webkit-user-select: text;
            user-select: text;
        }
        ::selection {
            background-color: #00b42a;
            color: #fff;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #1d2129;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
            background: #fff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03), 0 2px 8px rgba(0,0,0,0.05);
        }
        th, td {
            border: 1px solid #e5e6eb;
            padding: 12px 16px;
            text-align: left;
        }
        th {
            background-color: #f7f8fa;
            font-weight: 600;
            color: #1d2129;
        }
        tr:nth-child(even) {
            background-color: #f7f8fa;
        }
        tr:hover {
            background-color: #e8f3ff;
        }
        code {
            background-color: #f2f3f5;
            padding: 2px 6px;
            border-radius: 8px;
            font-family: "JetBrains Mono", Consolas, monospace;
            font-size: 0.9em;
            color: #f53f3f;
        }
        pre {
            background-color: #f2f3f5;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid #e5e6eb;
        }
        pre code {
            background-color: transparent;
            padding: 0;
        }
        blockquote {
            border-left: 4px solid #00b42a;
            padding-left: 16px;
            color: #86909c;
            margin: 16px 0;
            background: #fff;
            padding: 12px 16px;
            border-radius: 8px;
        }
        a {
            color: #00b42a;
            text-decoration: none;
        }
        a:hover {
            color: #00d473;
        }
        hr {
            border: none;
            border-top: 1px solid #e5e6eb;
            margin: 24px 0;
        }
        ul, ol {
            padding-left: 24px;
        }
        li {
            margin: 4px 0;
        }
"""


def get_fluent_style():
    """Fluent Design 微软风格"""
    return """
        html {
            margin: 0;
            padding: 0;
        }
        body {
            margin: 0;
            padding: 24px;
            font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
            line-height: 1.6;
            color: #202020;
            background: linear-gradient(135deg, #f3f3f3 0%, #ffffff 100%);
            -webkit-user-select: text;
            user-select: text;
        }
        ::selection {
            background-color: #0078d4;
            color: #fff;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #202020;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        th, td {
            border: 1px solid rgba(0,0,0,0.08);
            padding: 12px 16px;
            text-align: left;
        }
        th {
            background-color: rgba(243, 243, 243, 0.8);
            font-weight: 600;
            color: #202020;
        }
        tr:nth-child(even) {
            background-color: rgba(249, 249, 249, 0.6);
        }
        tr:hover {
            background-color: rgba(237, 237, 237, 0.8);
        }
        code {
            background-color: rgba(243, 243, 243, 0.8);
            padding: 2px 6px;
            border-radius: 8px;
            font-family: "Cascadia Code", Consolas, monospace;
            font-size: 0.9em;
            color: #d13438;
        }
        pre {
            background-color: rgba(243, 243, 243, 0.8);
            backdrop-filter: blur(10px);
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid rgba(0,0,0,0.08);
        }
        pre code {
            background-color: transparent;
            padding: 0;
        }
        blockquote {
            border-left: 4px solid #0078d4;
            padding-left: 16px;
            color: #605e5c;
            margin: 16px 0;
            background: rgba(255, 255, 255, 0.6);
            backdrop-filter: blur(10px);
            padding: 12px 16px;
            border-radius: 8px;
        }
        a {
            color: #0078d4;
            text-decoration: none;
        }
        a:hover {
            color: #106ebe;
        }
        hr {
            border: none;
            border-top: 1px solid rgba(0,0,0,0.08);
            margin: 24px 0;
        }
        ul, ol {
            padding-left: 24px;
        }
        li {
            margin: 4px 0;
        }
"""


def get_shadcn_style():
    """shadcn/ui 极简风格"""
    return """
        html {
            margin: 0;
            padding: 0;
        }
        body {
            margin: 0;
            padding: 32px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.7;
            color: #09090b;
            background: #ffffff;
            -webkit-user-select: text;
            user-select: text;
        }
        ::selection {
            background-color: #e4e4e7;
            color: #09090b;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #09090b;
            margin-top: 32px;
            margin-bottom: 16px;
            font-weight: 600;
            letter-spacing: -0.025em;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 24px 0;
            background: #fff;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #e4e4e7;
        }
        th, td {
            border: 1px solid #e4e4e7;
            padding: 12px 16px;
            text-align: left;
        }
        th {
            background-color: #fafafa;
            font-weight: 600;
            color: #09090b;
        }
        tr:nth-child(even) {
            background-color: #fafafa;
        }
        tr:hover {
            background-color: #f4f4f5;
        }
        code {
            background-color: #f4f4f5;
            padding: 2px 6px;
            border-radius: 8px;
            font-family: "SF Mono", "Roboto Mono", monospace;
            font-size: 0.875em;
            color: #dc2626;
            border: 1px solid #e4e4e7;
        }
        pre {
            background-color: #09090b;
            color: #fafafa;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid #27272a;
        }
        pre code {
            background-color: transparent;
            padding: 0;
            color: inherit;
            border: none;
        }
        blockquote {
            border-left: 2px solid #e4e4e7;
            padding-left: 16px;
            color: #71717a;
            margin: 24px 0;
            font-style: normal;
        }
        a {
            color: #09090b;
            text-decoration: underline;
            text-underline-offset: 2px;
        }
        a:hover {
            color: #27272a;
        }
        hr {
            border: none;
            border-top: 1px solid #e4e4e7;
            margin: 32px 0;
        }
        ul, ol {
            padding-left: 24px;
        }
        li {
            margin: 8px 0;
        }
"""


def get_glass_style():
    """玻璃拟态风格 - 柔和护眼版"""
    return """
        html {
            margin: 0;
            padding: 0;
        }
        body {
            margin: 0;
            padding: 32px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.7;
            color: #e8f0ff;
            background: #5a6fd8;
            min-height: 100vh;
            -webkit-user-select: text;
            user-select: text;
        }
        ::selection {
            background-color: rgba(200, 210, 255, 0.3);
            color: #ffffff;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            text-shadow: 0 1px 3px rgba(0,0,0,0.15);
        }
        p {
            color: #e2eaff;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
            background: rgba(255, 255, 255, 0.18);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.25);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        th, td {
            border: 1px solid rgba(255, 255, 255, 0.18);
            padding: 12px 16px;
            text-align: left;
            color: #f0f5ff;
        }
        th {
            background-color: rgba(255, 255, 255, 0.22);
            font-weight: 600;
        }
        tr:nth-child(even) {
            background-color: rgba(255, 255, 255, 0.08);
        }
        tr:hover {
            background-color: rgba(255, 255, 255, 0.15);
        }
        code {
            background-color: rgba(255, 255, 255, 0.22);
            backdrop-filter: blur(10px);
            padding: 2px 6px;
            border-radius: 12px;
            font-family: Consolas, monospace;
            font-size: 0.9em;
            color: #eaf5ff;
            border: 1px solid rgba(255, 255, 255, 0.25);
        }
        pre {
            background-color: rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            padding: 16px;
            border-radius: 12px;
            overflow-x: auto;
            border: 1px solid rgba(255, 255, 255, 0.18);
        }
        pre code {
            background-color: transparent;
            padding: 0;
            border: none;
            display: block;
            color: #e2eaff;
        }
        blockquote {
            border-left: 4px solid rgba(220, 230, 255, 0.5);
            padding-left: 16px;
            color: rgba(230, 240, 255, 0.9);
            margin: 16px 0;
            background: rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(10px);
            padding: 12px 16px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.18);
        }
        a {
            color: #d4e5ff;
            text-decoration: none;
            font-weight: 500;
        }
        a:hover {
            text-decoration: underline;
            color: #ffffff;
        }
        hr {
            border: none;
            border-top: 1px solid rgba(255, 255, 255, 0.22);
            margin: 24px 0;
        }
        ul, ol {
            padding-left: 24px;
        }
        li {
            margin: 4px 0;
            color: rgba(230, 240, 255, 0.92);
        }
"""


def get_neumorphism_style():
    """新拟态风格"""
    return """
        html {
            margin: 0;
            padding: 0;
        }
        body {
            margin: 0;
            padding: 32px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #4a5568;
            background: #e0e5ec;
            -webkit-user-select: text;
            user-select: text;
        }
        ::selection {
            background-color: #cbd5e0;
            color: #2d3748;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2d3748;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
        }
        table {
            border-collapse: separate;
            border-spacing: 0;
            width: 100%;
            margin: 16px 0;
            background: #e0e5ec;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 9px 9px 16px rgb(163,177,198,0.6), -9px -9px 16px rgba(255,255,255, 0.5);
        }
        th, td {
            border: none;
            padding: 12px 16px;
            text-align: left;
            color: #4a5568;
        }
        th {
            background-color: #e0e5ec;
            font-weight: 600;
            box-shadow: inset 4px 4px 8px rgb(163,177,198,0.4), inset -4px -4px 8px rgba(255,255,255, 0.8);
        }
        tr:nth-child(even) {
            background-color: #e0e5ec;
        }
        tr:hover td {
            background-color: #e0e5ec;
            box-shadow: inset 2px 2px 4px rgb(163,177,198,0.3), inset -2px -2px 4px rgba(255,255,255, 0.7);
        }
        code {
            background-color: #e0e5ec;
            padding: 2px 8px;
            border-radius: 16px;
            font-family: Consolas, monospace;
            font-size: 0.9em;
            color: #4a5568;
            box-shadow: inset 3px 3px 6px rgb(163,177,198,0.5), inset -3px -3px 6px rgba(255,255,255, 0.8);
        }
        pre {
            background-color: #e0e5ec;
            padding: 16px;
            border-radius: 20px;
            overflow-x: auto;
            box-shadow: 9px 9px 16px rgb(163,177,198,0.6), -9px -9px 16px rgba(255,255,255, 0.5);
        }
        pre code {
            background-color: transparent;
            padding: 0;
            box-shadow: none;
        }
        blockquote {
            border-left: none;
            padding-left: 16px;
            color: #718096;
            margin: 16px 0;
            background: #e0e5ec;
            padding: 16px;
            border-radius: 16px;
            box-shadow: 9px 9px 16px rgb(163,177,198,0.6), -9px -9px 16px rgba(255,255,255, 0.5);
        }
        a {
            color: #5a67d8;
            text-decoration: none;
        }
        a:hover {
            color: #4c51bf;
        }
        hr {
            border: none;
            margin: 24px 0;
            height: 2px;
            background: #e0e5ec;
            box-shadow: inset 2px 2px 4px rgb(163,177,198,0.5), inset -2px -2px 4px rgba(255,255,255, 0.8);
        }
        ul, ol {
            padding-left: 24px;
        }
        li {
            margin: 8px 0;
        }
"""


def get_flat_style():
    """极简扁平风"""
    return """
        html {
            margin: 0;
            padding: 0;
        }
        body {
            margin: 0;
            padding: 48px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.8;
            color: #1a1a1a;
            background: #ffffff;
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
            -webkit-user-select: text;
            user-select: text;
        }
        ::selection {
            background-color: #f0f0f0;
            color: #1a1a1a;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #1a1a1a;
            margin-top: 48px;
            margin-bottom: 24px;
            font-weight: 600;
            letter-spacing: -0.02em;
        }
        h1 {
            font-size: 2.5em;
            border-bottom: 1px solid #e5e5e5;
            padding-bottom: 16px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 32px 0;
            background: #fff;
        }
        th, td {
            border-bottom: 1px solid #e5e5e5;
            padding: 12px 16px;
            text-align: left;
        }
        th {
            font-weight: 600;
            color: #1a1a1a;
        }
        tr:nth-child(even) {
            background-color: #fafafa;
        }
        code {
            background-color: #f5f5f5;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: "SF Mono", Consolas, monospace;
            font-size: 0.875em;
            color: #e11d48;
        }
        pre {
            background-color: #f9fafb;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid #e5e7eb;
        }
        pre code {
            background-color: transparent;
            padding: 0;
        }
        blockquote {
            border-left: 2px solid #1a1a1a;
            padding-left: 20px;
            color: #666;
            margin: 32px 0;
            font-style: normal;
        }
        a {
            color: #1a1a1a;
            text-decoration: underline;
            text-underline-offset: 3px;
        }
        a:hover {
            color: #666;
        }
        hr {
            border: none;
            border-top: 1px solid #e5e5e5;
            margin: 48px 0;
        }
        ul, ol {
            padding-left: 24px;
        }
        li {
            margin: 12px 0;
        }
        p {
            margin: 16px 0;
        }
"""


def get_apple_style():
    """苹果风格"""
    return """
        :root {
            --apple-primary: #007aff;
            --apple-bg: #f5f5f7;
            --apple-card: #ffffff;
            --apple-text: #1d1d1f;
            --apple-text-light: #86868b;
            --apple-border: #e5e5e7;
            --apple-radius: 14px;
            --apple-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
            --apple-font: -apple-system, BlinkMacSystemFont, "SF Pro Text", "PingFang SC", "Microsoft YaHei", Inter, sans-serif;
        }
        html {
            margin: 0;
            padding: 0;
        }
        body {
            font-family: var(--apple-font);
            background-color: var(--apple-bg);
            color: var(--apple-text);
            line-height: 1.7;
            padding: 2rem;
            max-width: 900px;
            margin: 0 auto;
            -webkit-user-select: text;
            user-select: text;
        }
        ::selection {
            background-color: var(--apple-primary);
            color: #fff;
        }
        h1, h2, h3, h4, h5, h6 {
            font-weight: 500;
            color: var(--apple-text);
            margin-top: 1.8rem;
            margin-bottom: 1rem;
        }
        h1 { 
            font-size: 2rem; 
            border-bottom: 1px solid var(--apple-border); 
            padding-bottom: 0.5rem; 
        }
        h2 { 
            font-size: 1.6rem; 
        }
        h3 { 
            font-size: 1.3rem; 
        }
        h4 { 
            font-size: 1.15rem; 
        }
        p {
            margin: 1rem 0;
            font-size: 1rem;
        }
        blockquote {
            background: rgba(255,255,255,0.6);
            backdrop-filter: blur(10px);
            border-left: 4px solid var(--apple-primary);
            padding: 1rem 1.2rem;
            border-radius: 0 var(--apple-radius) var(--apple-radius) 0;
            margin: 1.2rem 0;
            color: var(--apple-text-light);
        }
        ul, ol {
            padding-left: 1.5rem;
            margin: 1rem 0;
        }
        li {
            margin: 0.5rem 0;
        }
        hr {
            border: 0;
            height: 1px;
            background: var(--apple-border);
            margin: 2rem 0;
        }
        code {
            background: rgba(0,122,255,0.08);
            color: var(--apple-primary);
            padding: 0.2rem 0.5rem;
            border-radius: 6px;
            font-size: 0.9em;
        }
        pre {
            background: #1d1d1f;
            color: #f5f5f7;
            padding: 1.2rem;
            border-radius: var(--apple-radius);
            overflow-x: auto;
            margin: 1.2rem 0;
            box-shadow: var(--apple-shadow);
        }
        pre code {
            background: transparent;
            color: inherit;
            padding: 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            border-radius: var(--apple-radius);
            overflow: hidden;
            box-shadow: var(--apple-shadow);
            margin: 1.2rem 0;
        }
        th, td {
            padding: 0.8rem 1rem;
            border: 1px solid var(--apple-border);
            text-align: left;
        }
        th {
            background: var(--apple-bg);
            font-weight: 500;
        }
        a {
            color: var(--apple-primary);
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        img {
            max-width: 100%;
            border-radius: var(--apple-radius);
            box-shadow: var(--apple-shadow);
            margin: 1rem 0;
        }
        strong {
            font-weight: 600;
            color: var(--apple-text);
        }
        mark {
            background: rgba(255,204,0,0.25);
            color: var(--apple-text);
            padding: 0.1rem 0.3rem;
            border-radius: 4px;
        }
"""


def get_geek_style():
    """极客复古终端风格"""
    return """
        :root {
            --bg-main: #000000;
            --text-normal: #00ff00;
            --h1-color: #ff8800;
            --h2-color: #ffff00;
            --h3-color: #d844b9;
            --h4-color: #00ffff;
            --muted-color: #009900;
            --link-color: #00ccff;
            --inline-code-color: #ff5555;
            --border-line: #006600;
        }
        html {
            margin: 0;
            padding: 0;
        }
        body {
            background: var(--bg-main);
            color: var(--text-normal);
            font-family: "Consolas", "Courier New", "Monaco", "Menlo", monospace;
            line-height: 1.65;
            letter-spacing: 0.3px;
            padding: 2rem;
            margin: 0 auto;
            -webkit-user-select: text;
            user-select: text;
        }
        ::selection {
            background-color: #003300;
            color: var(--text-normal);
        }
        h1 {
            color: var(--h1-color);
            font-weight: bold;
            border-bottom: 1px solid var(--h1-color);
            padding-bottom: 6px;
            margin: 1.8rem 0 1rem;
            font-size: 1.7rem;
        }
        h2 {
            color: var(--h2-color);
            font-weight: bold;
            margin: 1.6rem 0 0.9rem;
            font-size: 1.45rem;
        }
        h3 {
            color: var(--h3-color);
            font-weight: bold;
            margin: 1.4rem 0 0.8rem;
            font-size: 1.25rem;
        }
        h4, h5, h6 {
            color: var(--h4-color);
            font-weight: normal;
            margin: 1.2rem 0 0.7rem;
        }
        p {
            margin: 0.9rem 0;
            color: var(--text-normal);
        }
        strong {
            color: #ffffff;
            font-weight: bold;
        }
        em {
            color: var(--muted-color);
        }
        a {
            color: var(--link-color);
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        blockquote {
            border-left: 3px solid var(--border-line);
            padding: 0.7rem 1rem;
            margin: 1rem 0;
            color: var(--muted-color);
            background: #0a0a0a;
        }
        ul, ol {
            padding-left: 1.8rem;
            margin: 1rem 0;
        }
        li {
            margin: 0.4rem 0;
        }
        hr {
            border: none;
            height: 1px;
            background: var(--border-line);
            margin: 2rem 0;
        }
        code {
            color: var(--inline-code-color);
            background: #111111;
            padding: 2px 5px;
            border-radius: 1px;
            font-family: inherit;
        }
        pre {
            background: #080808;
            border: 1px solid var(--border-line);
            padding: 1rem;
            margin: 1.2rem 0;
            overflow-x: auto;
        }
        pre code {
            background: transparent;
            color: var(--text-normal);
            padding: 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.2rem 0;
            background: #0a0a0a;
        }
        th, td {
            border: 1px solid var(--border-line);
            padding: 0.6rem 0.9rem;
            text-align: left;
        }
        th {
            color: #fff;
            background: #111;
        }
        img {
            max-width: 100%;
            border: 1px solid var(--border-line);
            margin: 1rem 0;
        }
        mark {
            background: #ffff00;
            color: #000;
            padding: 1px 4px;
        }
"""


def get_dark_coder_style():
    """暗黑极简程序员风"""
    return """
        html {
            margin: 0;
            padding: 0;
        }
        body {
            margin: 0;
            padding: 2rem;
            font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", Inter, sans-serif;
            line-height: 1.7;
            background: #1a1a20;
            color: #e5e5e5;
            -webkit-user-select: text;
            user-select: text;
        }
        ::selection {
            background-color: rgba(79, 209, 197, 0.3);
            color: #fff;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #4fd1c5;
            margin-top: 1.8rem;
            margin-bottom: 0.8rem;
        }
        h1 {
            font-size: 1.8rem;
            border-bottom: 1px solid #2d2d37;
            padding-bottom: 0.5rem;
        }
        h2 { font-size: 1.5rem; }
        h3 { font-size: 1.3rem; }
        h4 { font-size: 1.15rem; }
        h5, h6 { font-size: 1rem; }
        p {
            margin: 1rem 0;
            color: #e5e5e5;
        }
        strong {
            color: #ffffff;
        }
        em {
            color: #9ca3af;
        }
        a {
            color: #4fd1c5;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
            opacity: 0.9;
        }
        blockquote {
            background: #202028;
            border-left: 4px solid #4fd1c5;
            padding: 0.9rem 1.2rem;
            margin: 1.2rem 0;
            color: #9ca3af;
            border-radius: 4px;
        }
        ul, ol {
            padding-left: 1.6rem;
            margin: 1rem 0;
        }
        li {
            margin: 0.4rem 0;
        }
        hr {
            border: none;
            height: 1px;
            background: #2d2d37;
            margin: 2rem 0;
        }
        code {
            background: #23232b;
            color: #4fd1c5;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-family: Consolas, Monaco, monospace;
            font-size: 0.9em;
        }
        pre {
            background: #23232b;
            padding: 1.2rem;
            border-radius: 6px;
            overflow-x: auto;
            margin: 1.2rem 0;
            border: 1px solid #2d2d37;
        }
        pre code {
            background: transparent;
            color: #e5e5e5;
            padding: 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.2rem 0;
            background: #1f1f27;
            border-radius: 6px;
            overflow: hidden;
        }
        th, td {
            border: 1px solid #2d2d37;
            padding: 0.7rem 1rem;
            text-align: left;
        }
        th {
            color: #4fd1c5;
            background: #23232b;
        }
        img {
            max-width: 100%;
            border-radius: 6px;
            border: 1px solid #2d2d37;
            margin: 1rem 0;
        }
        mark {
            background: rgba(79, 209, 197, 0.2);
            color: #4fd1c5;
            padding: 0.15rem 0.4rem;
            border-radius: 3px;
        }
        del {
            color: #9ca3af;
        }
"""


def get_cyber_neon_style():
    """赛博朋克霓虹风"""
    return """
        html {
            margin: 0;
            padding: 0;
        }
        body {
            margin: 0;
            padding: 2rem;
            font-family: "Consolas", "Menlo", "Monaco", monospace;
            line-height: 1.7;
            background: #000000;
            color: #e0e0e0;
            -webkit-user-select: text;
            user-select: text;
        }
        ::selection {
            background-color: rgba(0, 255, 255, 0.3);
            color: #fff;
        }
        h1 {
            color: #0ff;
            border-bottom: 1px solid #0ff;
            text-shadow: 0 0 8px #0ff;
            padding-bottom: 0.5rem;
            margin: 1.8rem 0 1rem;
            font-size: 1.8rem;
        }
        h2 {
            color: #f0f;
            text-shadow: 0 0 8px #f0f;
            margin: 1.6rem 0 0.9rem;
            font-size: 1.5rem;
        }
        h3 {
            color: #ff2e63;
            text-shadow: 0 0 8px #ff2e63;
            margin: 1.4rem 0 0.8rem;
            font-size: 1.3rem;
        }
        h4, h5, h6 {
            color: #66ffff;
            margin: 1.2rem 0 0.7rem;
        }
        p {
            margin: 1rem 0;
            color: #e0e0e0;
        }
        strong {
            color: #ffffff;
            text-shadow: 0 0 4px #fff;
        }
        em {
            color: #8888aa;
        }
        a {
            color: #0ff;
            text-decoration: none;
        }
        a:hover {
            text-shadow: 0 0 6px #0ff;
            text-decoration: underline;
        }
        blockquote {
            background: #050510;
            border-left: 3px solid #f0f;
            box-shadow: 0 0 6px #f0f;
            padding: 0.9rem 1.2rem;
            margin: 1.2rem 0;
            color: #8888aa;
        }
        ul, ol {
            padding-left: 1.8rem;
            margin: 1rem 0;
        }
        li {
            margin: 0.4rem 0;
        }
        hr {
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, #0ff, transparent);
            margin: 2rem 0;
        }
        code {
            background: #0a0a18;
            color: #ff2e63;
            padding: 2px 6px;
            border-radius: 2px;
            font-family: inherit;
        }
        pre {
            background: #0a0a18;
            border: 1px solid #0ff;
            box-shadow: 0 0 10px rgba(0,255,255,0.2);
            padding: 1.2rem;
            border-radius: 4px;
            overflow-x: auto;
            margin: 1.2rem 0;
        }
        pre code {
            background: transparent;
            color: #e0e0e0;
            padding: 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.2rem 0;
            background: #050510;
        }
        th, td {
            border: 1px solid #1f334d;
            padding: 0.7rem 1rem;
            text-align: left;
        }
        th {
            color: #0ff;
            text-shadow: 0 0 6px #0ff;
            background: #0a0a18;
        }
        img {
            max-width: 100%;
            border: 1px solid #0ff;
            box-shadow: 0 0 12px rgba(0,255,255,0.3);
            margin: 1rem 0;
            border-radius: 4px;
        }
        mark {
            background: rgba(255,46,99,0.2);
            color: #ff2e63;
            padding: 0.15rem 0.4rem;
        }
        del {
            color: #8888aa;
        }
"""


def get_paper_eye_style():
    """纸质护眼宣纸风"""
    return """
        html {
            margin: 0;
            padding: 0;
        }
        body {
            margin: 0;
            padding: 2rem;
            font-family: "Georgia", "SimSun", "宋体", "PingFang SC", sans-serif;
            line-height: 1.8;
            background: #f5f1e6;
            color: #2c2c2c;
            -webkit-user-select: text;
            user-select: text;
        }
        ::selection {
            background-color: rgba(91, 124, 153, 0.3);
            color: #2c2c2c;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #5b7c99;
            margin-top: 1.8rem;
            margin-bottom: 0.8rem;
        }
        h1 {
            font-size: 1.8rem;
            border-bottom: 1px solid #e0d8c8;
            padding-bottom: 0.5rem;
        }
        h2 { font-size: 1.5rem; }
        h3 { font-size: 1.3rem; }
        h4 { font-size: 1.15rem; }
        h5, h6 { font-size: 1rem; }
        p {
            margin: 1rem 0;
            color: #2c2c2c;
        }
        strong {
            color: #1a1a1a;
        }
        em {
            color: #666666;
        }
        a {
            color: #5b7c99;
            text-decoration: none;
            border-bottom: 1px dashed #b8c8d8;
        }
        a:hover {
            border-bottom: 1px solid #5b7c99;
        }
        blockquote {
            background: #f0ebdd;
            border-left: 4px solid #c8bba8;
            padding: 0.9rem 1.2rem;
            margin: 1.2rem 0;
            color: #666666;
            border-radius: 3px;
        }
        ul, ol {
            padding-left: 1.6rem;
            margin: 1rem 0;
        }
        li {
            margin: 0.4rem 0;
        }
        hr {
            border: none;
            height: 1px;
            background: #e0d8c8;
            margin: 2rem 0;
        }
        code {
            background: #efe9da;
            color: #a04040;
            padding: 0.2rem 0.5rem;
            border-radius: 3px;
            font-family: Consolas, monospace;
            font-size: 0.9em;
        }
        pre {
            background: #efe9da;
            padding: 1.2rem;
            border-radius: 6px;
            overflow-x: auto;
            margin: 1.2rem 0;
            border: 1px solid #e0d8c8;
        }
        pre code {
            background: transparent;
            color: #2c2c2c;
            padding: 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.2rem 0;
            background: #f2ede0;
            border-radius: 6px;
            overflow: hidden;
        }
        th, td {
            border: 1px solid #e0d8c8;
            padding: 0.7rem 1rem;
            text-align: left;
        }
        th {
            background: #e8e1d1;
            color: #5b7c99;
        }
        img {
            max-width: 100%;
            border-radius: 6px;
            border: 1px solid #e0d8c8;
            margin: 1rem 0;
        }
        mark {
            background: #ffeeba;
            color: #2c2c2c;
            padding: 0.15rem 0.4rem;
            border-radius: 3px;
        }
        del {
            color: #666666;
        }
"""


def get_magazine_bw_style():
    """极简黑白杂志风"""
    return """
        html {
            margin: 0;
            padding: 0;
        }
        body {
            margin: 0 auto;
            padding: 3rem 4rem;
            max-width: 1080px;
            font-family: "Helvetica Neue", "PingFang SC", "Microsoft YaHei", Inter, sans-serif;
            line-height: 1.8;
            background: #ffffff;
            color: #111111;
            -webkit-user-select: text;
            user-select: text;
        }
        ::selection {
            background-color: rgba(0, 0, 0, 0.1);
            color: #000;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #000000;
            margin-top: 2.5rem;
            margin-bottom: 1rem;
            letter-spacing: 0.5px;
        }
        h1 {
            font-size: 2.4rem;
            border-bottom: 1px solid #e5e5e5;
            padding-bottom: 1rem;
        }
        h2 { font-size: 1.9rem; }
        h3 { font-size: 1.5rem; }
        h4 { font-size: 1.25rem; }
        h5, h6 { font-size: 1.1rem; }
        p {
            margin: 1.2rem 0;
            color: #111111;
        }
        strong {
            color: #000000;
        }
        em {
            color: #555555;
        }
        a {
            color: #000000;
            text-decoration: underline;
            text-underline-offset: 3px;
        }
        a:hover {
            color: #555555;
        }
        blockquote {
            border-left: 3px solid #000;
            padding: 1rem 1.5rem;
            margin: 1.5rem 0;
            color: #555555;
            background: transparent;
        }
        ul, ol {
            padding-left: 2rem;
            margin: 1.2rem 0;
        }
        li {
            margin: 0.6rem 0;
        }
        hr {
            border: none;
            height: 1px;
            background: #000;
            opacity: 0.15;
            margin: 3rem 0;
        }
        code {
            background: #f7f7f7;
            color: #222;
            padding: 0.25rem 0.5rem;
            border-radius: 2px;
            font-family: Consolas, monospace;
            font-size: 0.9em;
        }
        pre {
            background: #f7f7f7;
            padding: 1.5rem;
            margin: 1.5rem 0;
            overflow-x: auto;
            border: 1px solid #e5e5e5;
        }
        pre code {
            background: transparent;
            color: #111;
            padding: 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
        }
        th, td {
            border: 1px solid #e5e5e5;
            padding: 0.9rem 1.2rem;
            text-align: left;
        }
        th {
            background: #f7f7f7;
            color: #000;
        }
        img {
            max-width: 100%;
            margin: 1.5rem 0;
            border-radius: 0;
        }
        mark {
            background: #fef2c0;
            color: #000;
            padding: 0.15rem 0.4rem;
        }
        del {
            color: #555555;
        }
"""


def get_business_blue_style():
    """蓝白商务专业风"""
    return """
        html {
            margin: 0;
            padding: 0;
        }
        body {
            margin: 0 auto;
            padding: 2.5rem 3rem;
            max-width: 1100px;
            font-family: "PingFang SC", "Microsoft YaHei", "SimHei", sans-serif;
            line-height: 1.75;
            background: #f8f9fa;
            color: #333333;
            -webkit-user-select: text;
            user-select: text;
        }
        ::selection {
            background-color: rgba(25, 103, 210, 0.3);
            color: #333;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #1967d2;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        h1 {
            font-size: 2rem;
            border-bottom: 1px solid #dee2e6;
            padding-bottom: 0.6rem;
        }
        h2 { font-size: 1.6rem; }
        h3 { font-size: 1.35rem; }
        h4 { font-size: 1.2rem; }
        h5, h6 { font-size: 1.05rem; }
        p {
            margin: 1.1rem 0;
            color: #333333;
        }
        strong {
            color: #000000;
        }
        em {
            color: #6c757d;
        }
        a {
            color: #1967d2;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        blockquote {
            background: #f2f5f9;
            border-left: 4px solid #1967d2;
            padding: 1rem 1.4rem;
            margin: 1.4rem 0;
            color: #6c757d;
            border-radius: 4px;
        }
        ul, ol {
            padding-left: 1.8rem;
            margin: 1.2rem 0;
        }
        li {
            margin: 0.5rem 0;
        }
        hr {
            border: none;
            height: 1px;
            background: #dee2e6;
            margin: 2.5rem 0;
        }
        code {
            background: #eef2f7;
            color: #1967d2;
            padding: 0.2rem 0.5rem;
            border-radius: 3px;
            font-family: Consolas, Monaco, monospace;
            font-size: 0.9em;
        }
        pre {
            background: #eef2f7;
            padding: 1.2rem;
            border-radius: 6px;
            overflow-x: auto;
            margin: 1.4rem 0;
            border: 1px solid #dee2e6;
        }
        pre code {
            background: transparent;
            color: #333333;
            padding: 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.4rem 0;
            background: #fff;
            border-radius: 6px;
            overflow: hidden;
        }
        th, td {
            border: 1px solid #dee2e6;
            padding: 0.8rem 1.1rem;
            text-align: left;
        }
        th {
            background: #e9f0fb;
            color: #1967d2;
        }
        img {
            max-width: 100%;
            border-radius: 6px;
            border: 1px solid #dee2e6;
            margin: 1.4rem 0;
        }
        mark {
            background: #ffe88b;
            color: #000;
            padding: 0.15rem 0.4rem;
            border-radius: 2px;
        }
        del {
            color: #6c757d;
        }
"""


def get_nordic_cold_style():
    """北欧冷淡风"""
    return """
        html {
            margin: 0;
            padding: 0;
        }
        body {
            margin: 0 auto;
            padding: 3rem 4rem;
            max-width: 1040px;
            font-family: "Helvetica Neue", "PingFang SC", "Microsoft YaHei", Inter, sans-serif;
            line-height: 1.8;
            background: #f7f9f8;
            color: #4a555c;
            -webkit-user-select: text;
            user-select: text;
        }
        ::selection {
            background-color: rgba(136, 153, 166, 0.3);
            color: #4a555c;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #8899a6;
            margin-top: 2.2rem;
            margin-bottom: 1rem;
            letter-spacing: 0.3px;
        }
        h1 {
            font-size: 2rem;
            border-bottom: 1px solid #e2e8e6;
            padding-bottom: 0.6rem;
        }
        h2 { font-size: 1.6rem; }
        h3 { font-size: 1.35rem; }
        h4 { font-size: 1.2rem; }
        h5, h6 { font-size: 1.05rem; }
        p {
            margin: 1.1rem 0;
            color: #4a555c;
        }
        strong {
            color: #2f383e;
        }
        em {
            color: #7c8994;
        }
        a {
            color: #b0c4b1;
            text-decoration: none;
            border-bottom: 1px solid transparent;
        }
        a:hover {
            border-bottom: 1px solid #b0c4b1;
        }
        blockquote {
            background: #f2f5f4;
            border-left: 4px solid #b0c4b1;
            padding: 1rem 1.3rem;
            margin: 1.3rem 0;
            color: #7c8994;
            border-radius: 4px;
        }
        ul, ol {
            padding-left: 1.8rem;
            margin: 1.1rem 0;
        }
        li {
            margin: 0.5rem 0;
        }
        hr {
            border: none;
            height: 1px;
            background: #e2e8e6;
            margin: 2.5rem 0;
        }
        code {
            background: #eff2f1;
            color: #8899a6;
            padding: 0.2rem 0.5rem;
            border-radius: 3px;
            font-family: Consolas, monospace;
            font-size: 0.9em;
        }
        pre {
            background: #eff2f1;
            padding: 1.2rem;
            border-radius: 6px;
            overflow-x: auto;
            margin: 1.3rem 0;
            border: 1px solid #e2e8e6;
        }
        pre code {
            background: transparent;
            color: #4a555c;
            padding: 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.3rem 0;
            background: #fff;
            border-radius: 6px;
            overflow: hidden;
        }
        th, td {
            border: 1px solid #e2e8e6;
            padding: 0.8rem 1rem;
            text-align: left;
        }
        th {
            background: #f0f3f2;
            color: #8899a6;
        }
        img {
            max-width: 100%;
            border-radius: 8px;
            border: 1px solid #e2e8e6;
            margin: 1.3rem 0;
        }
        mark {
            background: #e6e2d5;
            color: #333;
            padding: 0.15rem 0.4rem;
            border-radius: 2px;
        }
        del {
            color: #7c8994;
        }
"""


def get_old_newspaper_style():
    """复古报纸老式风"""
    return """
        html {
            margin: 0;
            padding: 0;
        }
        body {
            margin: 0 auto;
            padding: 2.5rem 3rem;
            max-width: 1000px;
            font-family: "Georgia", "Times New Roman", "SimSun", "宋体", serif;
            line-height: 1.85;
            background: #f2f0e8;
            color: #2b2b2b;
            -webkit-user-select: text;
            user-select: text;
        }
        ::selection {
            background-color: rgba(184, 181, 168, 0.3);
            color: #2b2b2b;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #1a1a1a;
            font-weight: bold;
            letter-spacing: 1px;
            margin-top: 2rem;
            margin-bottom: 0.9rem;
        }
        h1 {
            font-size: 2.2rem;
            text-align: center;
            border-bottom: 1px solid #b8b5a8;
            padding-bottom: 0.6rem;
        }
        h2 { font-size: 1.7rem; }
        h3 { font-size: 1.4rem; }
        h4 { font-size: 1.2rem; }
        h5, h6 { font-size: 1.05rem; }
        p {
            margin: 1.1rem 0;
            text-indent: 2em;
            color: #2b2b2b;
        }
        li p {
            text-indent: 0;
        }
        strong {
            color: #000;
            font-weight: 700;
        }
        em {
            color: #5c5c5c;
            font-style: italic;
        }
        a {
            color: #4a525c;
            text-decoration: none;
            border-bottom: 1px dotted #d3d0c3;
        }
        a:hover {
            color: #1a1a1a;
            border-bottom: 1px solid #888;
        }
        blockquote {
            background: #ebe8df;
            border-left: 4px solid #b8b5a8;
            padding: 1rem 1.4rem;
            margin: 1.4rem 0;
            color: #5c5c5c;
            font-style: italic;
        }
        ul, ol {
            padding-left: 2rem;
            margin: 1.2rem 0;
        }
        li {
            margin: 0.5rem 0;
            text-indent: 0;
        }
        hr {
            border: none;
            height: 1px;
            background: #b8b5a8;
            margin: 2.5rem 0;
        }
        code {
            background: #e9e6dd;
            color: #6b2e2e;
            padding: 0.2rem 0.5rem;
            border-radius: 2px;
            font-family: Consolas, monospace;
            font-size: 0.9em;
        }
        pre {
            background: #e9e6dd;
            padding: 1.2rem;
            border-radius: 4px;
            overflow-x: auto;
            margin: 1.4rem 0;
            border: 1px solid #d3d0c3;
        }
        pre code {
            background: transparent;
            color: #2b2b2b;
            padding: 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.4rem 0;
            background: #f7f5ee;
        }
        th, td {
            border: 1px solid #d3d0c3;
            padding: 0.8rem 1rem;
            text-align: left;
        }
        th {
            background: #e8e5da;
            font-weight: bold;
        }
        img {
            max-width: 100%;
            border-radius: 4px;
            border: 1px solid #d3d0c3;
            margin: 1.4rem 0;
            filter: sepia(15%);
        }
        mark {
            background: #e6d7b9;
            color: #1a1a1a;
            padding: 0.15rem 0.4rem;
        }
        del {
            color: #5c5c5c;
        }
"""


def get_school_fresh_style():
    """校园青春清新风"""
    return """
        html {
            margin: 0;
            padding: 0;
        }
        body {
            margin: 0 auto;
            padding: 2rem 2.5rem;
            max-width: 1000px;
            font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
            line-height: 1.75;
            background: #f5faff;
            color: #333333;
            -webkit-user-select: text;
            user-select: text;
        }
        ::selection {
            background-color: rgba(115, 192, 136, 0.3);
            color: #333;
        }
        h1 {
            color: #82b9e6;
            font-weight: 600;
            font-size: 1.9rem;
            border-bottom: 1px solid #e0ecf5;
            padding-bottom: 0.5rem;
            margin: 1.8rem 0 1rem;
            border-radius: 6px;
        }
        h2 {
            color: #73c088;
            font-weight: 600;
            font-size: 1.55rem;
            margin: 1.6rem 0 0.9rem;
        }
        h3, h4, h5, h6 {
            color: #629ecd;
            font-weight: 500;
            margin-top: 1.3rem;
            margin-bottom: 0.7rem;
        }
        h3 { font-size: 1.3rem; }
        h4 { font-size: 1.15rem; }
        h5, h6 { font-size: 1.05rem; }
        p {
            margin: 1rem 0;
            color: #333333;
        }
        strong {
            color: #222;
            font-weight: 600;
        }
        em {
            color: #667788;
        }
        a {
            color: #82b9e6;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        blockquote {
            background: #f0f7f3;
            border-left: 4px solid #73c088;
            padding: 0.9rem 1.2rem;
            margin: 1.2rem 0;
            color: #667788;
            border-radius: 0 10px 10px 0;
        }
        ul, ol {
            padding-left: 1.8rem;
            margin: 1rem 0;
        }
        li {
            margin: 0.45rem 0;
        }
        hr {
            border: none;
            height: 1px;
            background: #e0ecf5;
            margin: 2rem 0;
        }
        code {
            background: #edf4f9;
            color: #3474b5;
            padding: 0.2rem 0.5rem;
            border-radius: 6px;
            font-family: Consolas, monospace;
            font-size: 0.9em;
        }
        pre {
            background: #edf4f9;
            padding: 1.2rem;
            border-radius: 12px;
            overflow-x: auto;
            margin: 1.2rem 0;
            border: 1px solid #e0ecf5;
        }
        pre code {
            background: transparent;
            color: #333333;
            padding: 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.2rem 0;
            background: #fff;
            border-radius: 12px;
            overflow: hidden;
        }
        th, td {
            border: 1px solid #e0ecf5;
            padding: 0.7rem 1rem;
            text-align: left;
        }
        th {
            background: #e8f1f9;
            color: #82b9e6;
            font-weight: 600;
        }
        img {
            max-width: 100%;
            border-radius: 12px;
            border: 1px solid #e0ecf5;
            margin: 1rem 0;
        }
        mark {
            background: #e8f5d8;
            color: #222;
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
        }
        del {
            color: #667788;
        }
"""
