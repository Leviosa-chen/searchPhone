#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手机号爬取器 Web 应用
提供 Web 界面和 API 接口
"""

import os
import re
import time
import hashlib
import logging
from urllib.parse import urlparse
from flask import Flask, request, jsonify, render_template_string, Response, send_from_directory
from flask_cors import CORS

# 导入核心模块
from .phone_scraper import PhoneScraper
from .config import OUTPUT_DIR, DEFAULT_MAX_PAGES

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 任务注册表：task_id -> {'queue': [], 'done': bool, 'url': str, 'files': dict}
TASKS = {}

# URL历史记录：url_hash -> {'task_id': str, 'status': str, 'files': dict, 'timestamp': float, 'url': str}
URL_HISTORY = {}


def is_valid_http_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https') and bool(parsed.netloc)
    except Exception:
        return False


def get_url_hash(url: str) -> str:
    """生成URL的哈希值（以天为维度）"""
    # 使用URL + 当前日期作为哈希，确保同一天内相同URL只有一个任务
    today = time.strftime('%Y%m%d')
    url_with_date = f"{url}_{today}"
    return hashlib.md5(url_with_date.encode('utf-8')).hexdigest()

def check_url_history(url: str) -> dict:
    """检查URL的爬取历史（以天为维度）"""
    url_hash = get_url_hash(url)
    history = URL_HISTORY.get(url_hash, {})
    
    logger.info(f"检查URL历史: {url}")
    logger.info(f"URL哈希: {url_hash}")
    logger.info(f"历史记录: {history}")
    logger.info(f"当前TASKS: {list(TASKS.keys())}")
    
    if not history:
        logger.info(f"URL {url} 今天没有历史记录")
        return {'status': 'not_found', 'message': '今天未曾爬取'}
    
    task_id = history.get('task_id')
    logger.info(f"历史记录中的task_id: {task_id}")
    
    # 1. 检查是否有正在运行的任务
    if task_id and task_id in TASKS:
        task = TASKS[task_id]
        logger.info(f"任务 {task_id} 在TASKS中找到: {task}")
        
        if not task.get('done', False):
            # 验证任务状态的一致性
            if task.get('url') == url:  # 确保URL匹配
                logger.info(f"任务 {task_id} 正在运行中，URL: {url}")
                return {
                    'status': 'running', 
                    'message': '今天已有任务正在爬取中，请稍后',
                    'task_id': task_id
                }
            else:
                # URL不匹配，清除历史记录
                logger.warning(f"任务 {task_id} URL不匹配，清除历史记录")
                del URL_HISTORY[url_hash]
                return {'status': 'not_found', 'message': '任务状态不一致，需要重新爬取'}
        else:
            logger.info(f"任务 {task_id} 已完成")
    
    # 2. 检查历史记录中的状态
    history_status = history.get('status', '')
    logger.info(f"历史记录状态: {history_status}")
    
    # 如果历史记录显示任务正在运行，但TASKS中不存在，说明任务异常终止
    if history_status == 'running' and (not task_id or task_id not in TASKS):
        logger.warning(f"历史记录显示任务正在运行，但TASKS中不存在，清除记录")
        del URL_HISTORY[url_hash]
        return {'status': 'not_found', 'message': '任务状态异常，需要重新爬取'}
    
    # 如果历史记录显示任务失败，但时间很近（5分钟内），避免立即重新创建
    if history_status == 'failed':
        timestamp = history.get('timestamp', 0)
        time_diff = time.time() - timestamp
        logger.info(f"任务失败时间差: {time_diff}秒")
        
        if time_diff < 300:  # 5分钟内失败的任务，返回失败状态
            logger.info(f"任务最近失败，避免立即重新创建")
            return {
                'status': 'failed', 
                'message': '任务最近失败，请稍后再试',
                'task_id': task_id
            }
        else:
            # 失败时间较久，清除记录允许重新创建
            logger.info(f"任务失败时间较久，清除记录允许重新创建")
            del URL_HISTORY[url_hash]
            return {'status': 'not_found', 'message': '任务失败时间较久，可以重新爬取'}
    
    # 3. 检查是否有已完成的结果文件
    if history.get('files') and history['files'].get('docx'):
        docx_path = os.path.join(OUTPUT_DIR, os.path.basename(history['files']['docx']))
        if os.path.exists(docx_path):
            logger.info(f"今天已有爬取结果: {docx_path}")
            return {
                'status': 'completed',
                'message': '今天已有爬取结果',
                'files': history['files'],
                'task_id': task_id
            }
        else:
            # 文件不存在，清除无效的历史记录
            logger.warning(f"历史记录中的文件不存在，清除记录: {docx_path}")
            del URL_HISTORY[url_hash]
            return {'status': 'not_found', 'message': '结果文件不存在，需要重新爬取'}
    
    # 4. 如果任务已完成但没有文件，且不在TASKS中，清除无效记录
    if task_id and task_id not in TASKS:
        logger.warning(f"任务 {task_id} 在TASKS中不存在，清除历史记录")
        del URL_HISTORY[url_hash]
        return {'status': 'not_found', 'message': '任务状态异常，需要重新爬取'}
    
    # 5. 没有找到任何有效信息，但保留历史记录（可能是任务还在运行中）
    logger.info(f"URL {url} 今天没有找到有效的爬取结果，但保留历史记录")
    return {'status': 'not_found', 'message': '今天没有找到有效的爬取结果，需要重新爬取'}

def terminate_old_task(url: str) -> bool:
    """终止指定URL的旧任务"""
    url_hash = get_url_hash(url)
    history = URL_HISTORY.get(url_hash, {})
    
    if not history:
        return False
    
    task_id = history.get('task_id')
    if task_id and task_id in TASKS:
        task = TASKS[task_id]
        if not task.get('done', False):
            logger.info(f"终止旧任务: {task_id}")
            # 标记任务为终止状态
            task['terminated'] = True
            task['done'] = True
            # 清除历史记录
            del URL_HISTORY[url_hash]
            return True
    
    return False


INDEX_HTML = """
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>手机号爬取器</title>
    <style>
      :root { --primary: #0d6efd; --bg: #f6f8fa; --text: #222; --muted: #6b7280; --border: #e5e7eb; }
      * { box-sizing: border-box; }
      body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'PingFang SC', 'Noto Sans CJK SC', 'Microsoft YaHei', sans-serif; margin: 0; background: var(--bg); color: var(--text); }
      .container { max-width: 820px; margin: 40px auto; padding: 0 16px; }
      .card { background: #fff; border: 1px solid var(--border); border-radius: 14px; box-shadow: 0 6px 18px rgba(0,0,0,0.06); overflow: hidden; }
      .card-header { padding: 18px 20px; background: linear-gradient(180deg, #ffffff, #fafafa); border-bottom: 1px solid var(--border); }
      .card-title { margin: 0; font-size: 20px; }
      .card-body { padding: 18px 20px; }
      form { display: grid; grid-template-columns: 1fr 120px auto; gap: 10px; align-items: end; }
      label { font-size: 13px; color: var(--muted); display: block; margin-bottom: 6px; }
      .field { display: flex; flex-direction: column; }
      input[type=url], input[type=number] { width: 100%; padding: 10px 12px; border: 1px solid var(--border); border-radius: 8px; outline: none; transition: border-color .15s ease; background: #fff; }
      input[type=url]:focus, input[type=number]:focus { border-color: var(--primary); }
      .checkbox-field { display: flex; align-items: center; gap: 8px; }
      input[type=checkbox] { width: 16px; height: 16px; }
      button { height: 40px; padding: 0 16px; background: var(--primary); color: #fff; border: none; border-radius: 8px; cursor: pointer; transition: transform .02s ease, background .15s ease; }
      button:hover { background: #0b5ed7; }
      button:active { transform: translateY(1px); }
      button:disabled { background: #9ab5fb; cursor: not-allowed; }
      .note { color: var(--muted); font-size: 14px; margin-top: 4px; }
      .status { margin-top: 12px; color: #374151; font-size: 14px; }
      .result { margin-top: 16px; padding: 14px; border: 1px dashed var(--border); border-radius: 10px; background: #fafcff; }
      .result a { color: var(--primary); text-decoration: none; }
      .result a:hover { text-decoration: underline; }
      ul { padding-left: 18px; margin: 8px 0 0; }
      .error { color: #dc3545; font-weight: bold; }
      .debug { background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 15px; font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace; font-size: 12px; line-height: 1.5; max-height: 400px; overflow-y: auto; border: 1px solid var(--border); }
      .debug-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
      .debug-title { font-weight: 600; color: var(--text); margin: 0; }
      .debug-controls { display: flex; gap: 8px; }
      .debug-btn { padding: 4px 8px; font-size: 11px; background: var(--muted); color: white; border: none; border-radius: 4px; cursor: pointer; }
      .debug-btn:hover { background: #5a6268; }
      .debug-btn.clear { background: #dc3545; }
      .debug-btn.clear:hover { background: #c82333; }
      .log-entry { margin-bottom: 8px; padding: 6px 8px; background: #f1f3f4; border-radius: 4px; border-left: 3px solid var(--primary); }
      .log-time { color: var(--muted); font-size: 10px; margin-bottom: 2px; }
      .log-message { color: var(--text); word-break: break-word; }
      .log-entry.info { border-left-color: #17a2b8; background: #e3f2fd; }
      .log-entry.success { border-left-color: #28a745; background: #d4edda; }
      .log-entry.warning { border-left-color: #ffc107; background: #fff3cd; }
      .log-entry.error { border-left-color: #dc3545; background: #f8d7da; }
      .history-info { background: #e3f2fd; padding: 10px; border-radius: 8px; margin-top: 10px; border-left: 4px solid #2196f3; }
      .history-info.error { background: #f8d7da; border-left-color: #dc3545; }
      .log-counter { background: var(--primary); color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px; font-weight: bold; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="card">
        <div class="card-header">
          <h1 class="card-title">输入网址，抓取页面中的手机号</h1>
        </div>
        <div class="card-body">
          <div class="note">后端会验证链接是否可用。可设置最大爬取页数（默认 200）。</div>
          <form id="form">
            <div class="field">
              <label for="url">目标网址</label>
              <input id="url" type="url" placeholder="https://example.com" required />
            </div>
            <div class="field">
              <label for="maxPages">最大页数</label>
              <input id="maxPages" type="number" min="1" max="10000" value="200" />
            </div>
            <div class="field">
              <div class="checkbox-field">
                <input id="reScrape" type="checkbox" />
                <label for="reScrape">重新爬取</label>
              </div>
              <div class="note">勾选后将强制重新爬取，否则优先使用已有结果</div>
            </div>
            <button id="submit" type="submit">开始爬取</button>
          </form>
          <div id="historyInfo" class="history-info" style="display:none"></div>
          <div id="status" class="status"></div>
          <div id="result" class="result" style="display:none"></div>
          <div id="debug" class="debug" style="display:none">
            <div class="debug-header">
              <h3 class="debug-title">运行日志 <span class="log-counter" id="logCounter">0</span></h3>
              <div class="debug-controls">
                <button class="debug-btn" onclick="clearLogs()">清空日志</button>
                <button class="debug-btn" onclick="exportLogs()">导出日志</button>
                <button class="debug-btn" onclick="toggleAutoScroll()">自动滚动</button>
              </div>
            </div>
            <div id="logContainer"></div>
          </div>
        </div>
      </div>
    </div>

    <script>
      const form = document.getElementById('form');
      const urlInput = document.getElementById('url');
      const submitBtn = document.getElementById('submit');
      const statusEl = document.getElementById('status');
      const resultEl = document.getElementById('result');
      const debugEl = document.getElementById('debug');
      const historyInfoEl = document.getElementById('historyInfo');
      const reScrapeCheckbox = document.getElementById('reScrape');
      const logContainer = document.getElementById('logContainer');
      const logCounter = document.getElementById('logCounter');

      let pendingLinks = null;
      let eventSource = null;
      let logs = [];
      let autoScroll = true;

      function formatTime() {
        const now = new Date();
        return now.toLocaleTimeString('zh-CN', { 
          hour12: false, 
          hour: '2-digit', 
          minute: '2-digit', 
          second: '2-digit',
          fractionalSecondDigits: 3
        });
      }

      function addLog(message, type = 'info') {
        const timestamp = formatTime();
        const logEntry = {
          timestamp,
          message,
          type,
          id: Date.now() + Math.random()
        };
        
        // 添加到数组开头（时间降序）
        logs.unshift(logEntry);
        
        // 限制日志数量，避免内存占用过大
        if (logs.length > 1000) {
          logs = logs.slice(0, 1000);
        }
        
        // 更新日志计数
        logCounter.textContent = logs.length;
        
        // 渲染日志
        renderLogs();
        
        // 自动滚动到底部
        if (autoScroll) {
          setTimeout(() => {
            logContainer.scrollTop = 0;
          }, 100);
        }
      }

      function renderLogs() {
        logContainer.innerHTML = logs.map(log => `
          <div class="log-entry ${log.type}">
            <div class="log-time">${log.timestamp}</div>
            <div class="log-message">${escapeHtml(log.message)}</div>
          </div>
        `).join('');
      }

      function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
      }

      function clearLogs() {
        logs = [];
        logCounter.textContent = '0';
        renderLogs();
        addLog('日志已清空', 'info');
      }

      function exportLogs() {
        const logText = logs.map(log => `[${log.timestamp}] ${log.message}`).join('\\n');
        const blob = new Blob([logText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `phone-scraper-logs-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        addLog('日志已导出', 'success');
      }

      function toggleAutoScroll() {
        autoScroll = !autoScroll;
        const btn = event.target;
        btn.textContent = autoScroll ? '自动滚动' : '手动滚动';
        btn.style.background = autoScroll ? 'var(--muted)' : '#ffc107';
        addLog(`自动滚动已${autoScroll ? '启用' : '禁用'}`, 'info');
      }

      function showHistoryInfo(message, type = 'info') {
        historyInfoEl.innerHTML = message;
        historyInfoEl.style.display = 'block';
        historyInfoEl.className = `history-info ${type === 'error' ? 'error' : ''}`;
      }

      function hideHistoryInfo() {
        historyInfoEl.style.display = 'none';
      }

      function renderLinks() {
        if (!pendingLinks || !pendingLinks.docx) return;
        const href = pendingLinks.docx;
        const html = `<div>爬取成功，下载文档：</div>
          <ul><li><a href="${href}" target="_blank">下载 DOCX</a></li></ul>
          <div class="note">下载链接：<span id="dl-url">${href}</span></div>`;
        resultEl.innerHTML = html;
        resultEl.style.display = 'block';
      }

      function subscribe(taskId) {
        addLog('开始订阅事件流: ' + taskId, 'info');
        
        // 关闭之前的连接
        if (eventSource) {
          eventSource.close();
        }
        
        const evt = new EventSource(`/api/events?task_id=${encodeURIComponent(taskId)}`);
        eventSource = evt;
        
        evt.onopen = () => {
          addLog('SSE连接已建立', 'success');
        };
        
        evt.onmessage = (m) => {
          try {
            addLog('收到消息: ' + m.data, 'info');
            const evtData = JSON.parse(m.data);
            if (evtData.type === 'start') {
              const mp = evtData.max_pages == null ? '未设置' : evtData.max_pages;
              statusEl.textContent = `开始任务：${evtData.url}，页数限制：${mp}`;
              addLog(`开始任务：${evtData.url}，页数限制：${mp}`, 'info');
            } else if (evtData.type === 'site_title') {
              statusEl.textContent = `网站：${evtData.title}`;
              addLog(`网站：${evtData.title}`, 'info');
            } else if (evtData.type === 'page_start') {
              statusEl.textContent = `正在爬取第 ${evtData.index} 页... 待爬取 ${evtData.queue} 页`;
              addLog(`正在爬取第 ${evtData.index} 页... 待爬取 ${evtData.queue} 页`, 'info');
            } else if (evtData.type === 'page_result') {
              const { new_phones, new_contacts, url } = evtData;
              statusEl.textContent = `完成页面：${url}，新增手机号 ${new_phones} 个，联系人 ${new_contacts} 个`;
              addLog(`完成页面：${url}，新增手机号 ${new_phones} 个，联系人 ${new_contacts} 个`, 'success');
            } else if (evtData.type === 'progress') {
              statusEl.textContent = `进度：已爬取 ${evtData.pages} 页，待爬取 ${evtData.queue} 页；累计手机号 ${evtData.phones}，联系人 ${evtData.contacts}`;
              addLog(`进度：已爬取 ${evtData.pages} 页，待爬取 ${evtData.queue} 页；累计手机号 ${evtData.phones}，联系人 ${evtData.contacts}`, 'info');
            } else if (evtData.type === 'files') {
              pendingLinks = evtData.files || null;
              renderLinks();
              addLog('收到文件信息，显示下载链接', 'success');
            } else if (evtData.type === 'done') {
              statusEl.textContent = `完成：共 ${evtData.pages} 页，手机号 ${evtData.phones}，联系人 ${evtData.contacts}`;
              addLog(`爬取完成：共 ${evtData.pages} 页，手机号 ${evtData.phones}，联系人 ${evtData.contacts}`, 'success');
              if (evtData.files) {
                pendingLinks = evtData.files;
                renderLinks();
              }
            } else if (evtData.type === 'stream_end') {
              addLog('收到流结束信号，关闭连接', 'info');
              evt.close();
            } else if (evtData.type === 'error') {
              statusEl.textContent = `错误：${evtData.message}`;
              addLog(`错误：${evtData.message}`, 'error');
            }
          } catch (err) {
            addLog('解析消息失败: ' + err.message, 'error');
          }
        };
        
        evt.onerror = (e) => {
          addLog('SSE连接错误: ' + JSON.stringify(e), 'error');
          evt.close();
        };
      }

      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = urlInput.value.trim();
        const maxPages = parseInt(document.getElementById('maxPages').value || '200', 10);
        const reScrape = reScrapeCheckbox.checked;
        
        if (!url) return;
        
        submitBtn.disabled = true;
        statusEl.textContent = '正在提交任务，请稍候...';
        resultEl.style.display = 'none';
        resultEl.innerHTML = '';
        hideHistoryInfo();
        
        // 显示日志区域并清空之前的日志
        debugEl.style.display = 'block';
        clearLogs();
        addLog('开始新的爬取任务', 'info');
        
        try {
          addLog(`提交任务: ${url}, 最大页数: ${maxPages}, 重新爬取: ${reScrape}`, 'info');
          
          const resp = await fetch('/api/scrape', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              url, 
              max_pages: isNaN(maxPages) ? 200 : maxPages,
              re_scrape: reScrape
            })
          });
          
          addLog(`响应状态: ${resp.status}`, 'info');
          const data = await resp.json();
          addLog(`响应数据: ${JSON.stringify(data)}`, 'info');
          
          if (!resp.ok) {
            throw new Error(data.message || '请求失败');
          }
          
          // 处理不同的响应类型
          if (data.status === 'completed') {
            // 已有结果，直接显示
            showHistoryInfo('✅ ' + data.message, 'info');
            pendingLinks = data.files;
            renderLinks();
            statusEl.textContent = '使用已有结果';
            addLog('使用已有结果，无需重新爬取', 'success');
          } else if (data.status === 'running') {
            // 正在爬取中，订阅现有任务
            showHistoryInfo('⏳ ' + data.message, 'info');
            addLog('任务正在运行中，订阅现有任务', 'warning');
            if (data.task_id) {
              subscribe(data.task_id);
            }
          } else if (data.status === 'failed') {
            // 任务最近失败，显示提示
            showHistoryInfo('❌ ' + data.message, 'error');
            statusEl.textContent = '任务最近失败，请稍后再试';
            addLog('任务最近失败，避免重复创建', 'error');
          } else if (data.status === 'new_task') {
            // 新任务，开始爬取
            hideHistoryInfo();
            addLog('创建新的爬取任务', 'info');
            const taskId = data.task_id;
            if (taskId) {
              addLog(`任务ID: ${taskId}`, 'info');
              subscribe(taskId);
            }
          }
        } catch (err) {
          addLog(`错误: ${err.message}`, 'error');
          statusEl.textContent = '';
          resultEl.innerHTML = `<span class="error">${err.message}</span>`;
          resultEl.style.display = 'block';
        } finally {
          submitBtn.disabled = false;
        }
      });

      // 初始化
      addLog('页面加载完成，等待用户操作', 'info');
    </script>
  </body>
</html>
"""


# 创建Flask应用
app = Flask(__name__)
# 启用CORS支持
CORS(app)


@app.get('/')
def index():
    return render_template_string(INDEX_HTML)


@app.post('/api/scrape')
def scrape_api():
    data = request.get_json(silent=True) or {}
    url = (data.get('url') or '').strip()
    max_pages_client = data.get('max_pages')
    re_scrape = data.get('re_scrape', False)

    logger.info(f"收到爬取请求: {url}, max_pages: {max_pages_client}, re_scrape: {re_scrape}")

    if not url:
        return jsonify({ 'message': '请提供有效的网址' }), 400

    if not is_valid_http_url(url):
        return jsonify({ 'message': '请提供有效的HTTP/HTTPS网址' }), 400

    # 如果是强制重新爬取，先终止旧任务
    if re_scrape:
        logger.info("强制重新爬取，检查并终止旧任务")
        if terminate_old_task(url):
            logger.info("旧任务已终止")
        else:
            logger.info("没有找到需要终止的旧任务")
    else:
        # 如果不是强制重新爬取，先检查历史
        logger.info(f"检查URL历史: {url}")
        history_check = check_url_history(url)
        logger.info(f"历史检查结果: {history_check}")
        
        if history_check['status'] == 'completed':
            # 已有结果，直接返回
            logger.info(f"返回已有结果: {history_check['files']}")
            return jsonify({
                'status': 'completed',
                'message': history_check['message'],
                'files': history_check['files']
            })
        elif history_check['status'] == 'running':
            # 正在爬取中，返回任务ID
            logger.info(f"任务正在运行中: {history_check['task_id']}")
            return jsonify({
                'status': 'running',
                'message': history_check['message'],
                'task_id': history_check['task_id']
            })
        elif history_check['status'] == 'failed':
            # 任务最近失败，避免重复创建
            logger.info(f"任务最近失败: {history_check['message']}")
            return jsonify({
                'status': 'failed',
                'message': history_check['message'],
                'task_id': history_check.get('task_id', '')
            })
        else:
            logger.info(f"需要创建新任务: {history_check['message']}")

    # 尝试访问链接，确保可访问
    try:
        import requests
        probe = requests.head(url, timeout=10, allow_redirects=True)
        if probe.status_code >= 400:
            return jsonify({ 'message': f'链接不可访问: HTTP {probe.status_code}' }), 400
    except Exception as e:
        return jsonify({ 'message': f'链接校验失败: {e}' }), 400

    # 分配任务ID
    task_id = f"t{int(time.time()*1000)}"
    TASKS[task_id] = {'queue': [], 'done': False, 'url': url, 'terminated': False}
    
    # 记录到历史 - 立即保存，确保历史检查能正确工作
    url_hash = get_url_hash(url)
    URL_HISTORY[url_hash] = {
        'task_id': task_id,
        'status': 'running',
        'timestamp': time.time(),
        'url': url
    }
    
    logger.info(f"创建任务: {task_id}, URL: {url}")
    logger.info(f"保存到历史: {url_hash} -> {URL_HISTORY[url_hash]}")
    
    def emit(evt: dict):
        logger.info(f"任务 {task_id} 发送事件: {evt}")
        TASKS[task_id]['queue'].append(evt)

    # 立即发送任务初始化事件
    emit({'type': 'start', 'url': url, 'max_pages': max_pages_client or DEFAULT_MAX_PAGES})

    # 运行爬虫（限制页数，避免长时间执行）
    scraper = PhoneScraper(url)
    scraper.progress_callback = emit

    # 生成文件名（带时间戳，避免覆盖）
    ts = time.strftime('%Y%m%d_%H%M%S')
    safe_host = re.sub(r'[^a-zA-Z0-9_.-]', '_', urlparse(url).netloc or 'site')
    base_name = f"{safe_host}_{ts}"
    docx_name = f"{base_name}.docx"
    docx_path = os.path.join(OUTPUT_DIR, docx_name)

    # 后台线程执行抓取与导出
    import threading
    def run_task():
        try:
            logger.info(f"任务 {task_id} 开始执行")
            
            # 检查任务是否被终止
            if TASKS[task_id].get('terminated', False):
                logger.info(f"任务 {task_id} 已被终止，停止执行")
                return
            
            # 解析前端传入的页数限制
            max_pages = DEFAULT_MAX_PAGES
            try:
                if max_pages_client is not None:
                    mp = int(max_pages_client)
                    if mp > 0:
                        max_pages = mp
            except Exception:
                pass
            
            # 爬取
            scraper.crawl_website(max_pages=max_pages)
            
            # 再次检查任务是否被终止
            if TASKS[task_id].get('terminated', False):
                logger.info(f"任务 {task_id} 在爬取过程中被终止，停止执行")
                return
            
            scraper.export_to_docx(docx_path)
            
            # 仅发送 DOCX 下载链接
            if os.path.exists(docx_path):
                files_payload = {'docx': f"/download/{docx_name}"}
                TASKS[task_id]['files'] = files_payload
                
                # 更新历史记录
                URL_HISTORY[url_hash].update({
                    'status': 'completed',
                    'files': files_payload,
                    'timestamp': time.time()
                })
                
                emit({'type': 'files', 'files': files_payload})
                logger.info(f"任务 {task_id} 完成，文件: {docx_path}")
            else:
                logger.error(f"任务 {task_id} 失败，文件不存在: {docx_path}")
                # 更新历史记录为失败
                URL_HISTORY[url_hash].update({
                    'status': 'failed',
                    'timestamp': time.time()
                })
        except Exception as e:
            logger.error(f"任务 {task_id} 执行失败: {e}")
            # 更新历史记录为失败
            URL_HISTORY[url_hash].update({
                'status': 'failed',
                'timestamp': time.time()
            })
            emit({'type': 'error', 'message': str(e)})
        finally:
            TASKS[task_id]['done'] = True
            logger.info(f"任务 {task_id} 标记完成")

    threading.Thread(target=run_task, daemon=True).start()

    # 返回新任务状态
    return jsonify({ 
        'status': 'new_task',
        'task_id': task_id,
        'message': '开始新的爬取任务'
    })


@app.get('/download/<path:filename>')
def download_file(filename: str):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)


@app.get('/api/events')
def events():
    task_id = request.args.get('task_id', '')
    logger.info(f"SSE连接请求: task_id={task_id}")
    
    if not task_id:
        logger.error("SSE连接请求缺少task_id参数")
        def error_stream():
            error_event = {'type': 'error', 'message': '缺少task_id参数'}
            yield f"data: {__import__('json').dumps(error_event, ensure_ascii=False)}\n\n"
            yield f"data: {__import__('json').dumps({'type': 'stream_end'}, ensure_ascii=False)}\n\n"
        
        headers = {
            'Content-Type': 'text/event-stream; charset=utf-8',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control',
        }
        return Response(error_stream(), headers=headers)
    
    if task_id not in TASKS:
        logger.error(f"SSE连接请求的task_id不存在: {task_id}")
        # 检查是否在历史记录中
        task_found_in_history = False
        for url_hash, record in URL_HISTORY.items():
            if record.get('task_id') == task_id:
                task_found_in_history = True
                logger.warning(f"任务 {task_id} 在历史记录中找到，但TASKS中不存在")
                break
        
        if task_found_in_history:
            # 任务在历史记录中但TASKS中不存在，可能是服务重启了
            error_message = f'任务 {task_id} 状态异常，请重新提交'
        else:
            error_message = f'无效的task_id: {task_id}'
        
        def error_stream():
            error_event = {'type': 'error', 'message': error_message}
            yield f"data: {__import__('json').dumps(error_event, ensure_ascii=False)}\n\n"
            yield f"data: {__import__('json').dumps({'type': 'stream_end'}, ensure_ascii=False)}\n\n"
        
        headers = {
            'Content-Type': 'text/event-stream; charset=utf-8',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control',
        }
        return Response(error_stream(), headers=headers)

    def stream():
        try:
            # 持续推送队列中的事件，直到任务完成且队列清空
            while True:
                q = TASKS.get(task_id)
                if not q:
                    logger.warning(f"任务 {task_id} 不存在")
                    # 发送错误事件
                    error_event = {'type': 'error', 'message': f'任务 {task_id} 不存在'}
                    yield f"data: {__import__('json').dumps(error_event, ensure_ascii=False)}\n\n"
                    break
                    
                while q['queue']:
                    evt = q['queue'].pop(0)
                    data = f"data: {__import__('json').dumps(evt, ensure_ascii=False)}\n\n"
                    logger.info(f"发送事件: {evt}")
                    yield data
                    
                if q['done']:
                    # 结束前再推送一次 done（如果客户端错过）
                    done_event = {'type': 'done', 'files': q.get('files', {})}
                    yield f"data: {__import__('json').dumps(done_event, ensure_ascii=False)}\n\n"
                    # 推送流结束标记，便于前端关闭SSE
                    yield f"data: {__import__('json').dumps({'type': 'stream_end'}, ensure_ascii=False)}\n\n"
                    logger.info(f"任务 {task_id} 流结束")
                    break
                    
                time.sleep(0.5)
        except Exception as e:
            logger.error(f"SSE流错误: {e}")
            yield f"data: {__import__('json').dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    headers = {
        'Content-Type': 'text/event-stream; charset=utf-8',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Cache-Control',
    }
    return Response(stream(), headers=headers)


@app.get('/health')
def health_check():
    return jsonify({'status': 'ok', 'timestamp': time.time()})


@app.get('/api/history')
def get_history():
    """获取爬取历史"""
    try:
        # 返回所有历史记录（仅包含必要信息）
        history_summary = {}
        for url_hash, record in URL_HISTORY.items():
            # 只返回最近的信息，不包含敏感数据
            history_summary[url_hash] = {
                'status': record.get('status'),
                'timestamp': record.get('timestamp'),
                'has_files': bool(record.get('files')),
                'url': record.get('url', 'Unknown')  # 如果历史记录中没有URL，显示Unknown
            }
        
        return jsonify({
            'status': 'success',
            'total': len(history_summary),
            'history': history_summary
        })
    except Exception as e:
        logger.error(f"获取历史记录失败: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.delete('/api/history/<url_hash>')
def delete_history(url_hash):
    """删除指定URL的爬取历史"""
    try:
        if url_hash in URL_HISTORY:
            # 删除历史记录
            del URL_HISTORY[url_hash]
            logger.info(f"删除历史记录: {url_hash}")
            return jsonify({'status': 'success', 'message': '历史记录已删除'})
        else:
            return jsonify({'status': 'error', 'message': '历史记录不存在'}), 404
    except Exception as e:
        logger.error(f"删除历史记录失败: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


def main():
    port = int(os.environ.get('PORT', '5000'))
    logger.info(f"启动Web服务，端口: {port}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)


