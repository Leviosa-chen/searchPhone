#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的Web服务：
- 首页提供一个表单，用户输入网址
- 提交后端校验链接并触发爬取手机号
- 生成CSV/JSON/DOCX文件并返回下载链接
"""

import os
import re
import time
from urllib.parse import urlparse
from flask import Flask, request, jsonify, send_from_directory, render_template_string, Response

from phone_scraper import PhoneScraper

app = Flask(__name__)

# 输出目录（相对于当前文件所在目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 任务注册表：task_id -> {'queue': [], 'done': bool}
TASKS = {}

# 默认最大页数（可用环境变量 MAX_PAGES 覆盖）
DEFAULT_MAX_PAGES = int(os.environ.get('MAX_PAGES', '200'))


def is_valid_http_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https') and bool(parsed.netloc)
    except Exception:
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
      form { display: grid; grid-template-columns: 1fr 120px auto; gap: 10px; align-items: center; }
      label { font-size: 13px; color: var(--muted); display: block; margin-bottom: 6px; }
      .field { display: flex; flex-direction: column; }
      input[type=url], input[type=number] { width: 100%; padding: 10px 12px; border: 1px solid var(--border); border-radius: 8px; outline: none; transition: border-color .15s ease; background: #fff; }
      input[type=url]:focus, input[type=number]:focus { border-color: var(--primary); }
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
            <button id="submit" type="submit">开始爬取</button>
          </form>
          <div id="status" class="status"></div>
          <div id="result" class="result" style="display:none"></div>
        </div>
      </div>
    </div>

    <script>
      const form = document.getElementById('form');
      const urlInput = document.getElementById('url');
      const submitBtn = document.getElementById('submit');
      const statusEl = document.getElementById('status');
      const resultEl = document.getElementById('result');

      let pendingLinks = null;

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
        const evt = new EventSource(`/api/events?task_id=${encodeURIComponent(taskId)}`);
        evt.onmessage = (m) => {
          try {
            const evtData = JSON.parse(m.data);
            if (evtData.type === 'start') {
              const mp = evtData.max_pages == null ? '未设置' : evtData.max_pages;
              statusEl.textContent = `开始任务：${evtData.url}，页数限制：${mp}`;
            } else if (evtData.type === 'site_title') {
              statusEl.textContent = `网站：${evtData.title}`;
            } else if (evtData.type === 'page_start') {
              statusEl.textContent = `正在爬取第 ${evtData.index} 页... 待爬取 ${evtData.queue} 页`;
            } else if (evtData.type === 'page_result') {
              const { new_phones, new_contacts, url } = evtData;
              statusEl.textContent = `完成页面：${url}，新增手机号 ${new_phones} 个，联系人 ${new_contacts} 个`;
            } else if (evtData.type === 'progress') {
              statusEl.textContent = `进度：已爬取 ${evtData.pages} 页，待爬取 ${evtData.queue} 页；累计手机号 ${evtData.phones}，联系人 ${evtData.contacts}`;
            } else if (evtData.type === 'files') {
              pendingLinks = evtData.files || null;
              renderLinks();
            } else if (evtData.type === 'done') {
              statusEl.textContent = `完成：共 ${evtData.pages} 页，手机号 ${evtData.phones}，联系人 ${evtData.contacts}`;
              if (evtData.files) {
                pendingLinks = evtData.files;
                renderLinks();
              }
            } else if (evtData.type === 'stream_end') {
              evt.close();
            } else if (evtData.type === 'error') {
              statusEl.textContent = `错误：${evtData.message}`;
            }
          } catch {}
        };
        evt.onerror = () => {
          evt.close();
        };
      }

      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = urlInput.value.trim();
        const maxPages = parseInt(document.getElementById('maxPages').value || '200', 10);
        if (!url) return;
        submitBtn.disabled = true;
        statusEl.textContent = '正在提交任务，请稍候...';
        resultEl.style.display = 'none';
        resultEl.innerHTML = '';
        try {
          const resp = await fetch('/api/scrape', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, max_pages: isNaN(maxPages) ? 200 : maxPages })
          });
          const data = await resp.json();
          if (!resp.ok) {
            throw new Error(data.message || '请求失败');
          }
          const taskId = data.task_id;
          if (taskId) {
            subscribe(taskId);
          }
          // 等待服务端完成导出后，通过 SSE 的 files 事件再显示下载按钮
        } catch (err) {
          statusEl.textContent = '';
          resultEl.innerHTML = `<span class="error">${err.message}</span>`;
          resultEl.style.display = 'block';
        } finally {
          submitBtn.disabled = false;
        }
      });
    </script>
  </body>
</html>
"""


@app.get('/')
def index():
    return render_template_string(INDEX_HTML)


@app.post('/api/scrape')
def scrape_api():
    data = request.get_json(silent=True) or {}
    url = (data.get('url') or '').strip()
    max_pages_client = data.get('max_pages')

    if not url:
        return jsonify({ 'message': 'url 参数不能为空' }), 400
    if not is_valid_http_url(url):
        return jsonify({ 'message': '请输入有效的 http/https 链接' }), 400

    # 先尝试探测链接是否可用
    from requests import head
    try:
        probe = head(url, timeout=8, allow_redirects=True)
        if probe.status_code >= 400:
            return jsonify({ 'message': f'链接不可访问: HTTP {probe.status_code}' }), 400
    except Exception as e:
        return jsonify({ 'message': f'链接校验失败: {e}' }), 400

    # 分配任务ID
    task_id = f"t{int(time.time()*1000)}"
    TASKS[task_id] = {'queue': [], 'done': False}

    def emit(evt: dict):
        TASKS[task_id]['queue'].append(evt)

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
            scraper.export_to_docx(docx_path)
            # 仅发送 DOCX 下载链接
            if os.path.exists(docx_path):
                files_payload = {'docx': f"/download/{docx_name}"}
                TASKS[task_id]['files'] = files_payload
                emit({'type': 'files', 'files': files_payload})
        except Exception as e:
            emit({'type': 'error', 'message': str(e)})
        finally:
            TASKS[task_id]['done'] = True

    threading.Thread(target=run_task, daemon=True).start()

    # 仅返回任务ID；下载链接将通过 SSE 的 files 事件下发
    return jsonify({ 'task_id': task_id })


@app.get('/download/<path:filename>')
def download_file(filename: str):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)


@app.get('/api/events')
def events():
    task_id = request.args.get('task_id', '')
    if not task_id or task_id not in TASKS:
        return jsonify({'message': 'task_id 无效'}), 400

    def stream():
        # 持续推送队列中的事件，直到任务完成且队列清空
        while True:
            q = TASKS.get(task_id)
            if not q:
                break
            while q['queue']:
                evt = q['queue'].pop(0)
                yield f"data: {__import__('json').dumps(evt, ensure_ascii=False)}\n\n"
            if q['done']:
                # 结束前再推送一次 done（如果客户端错过）
                yield f"data: {__import__('json').dumps({'type': 'done', 'files': q.get('files', {})}, ensure_ascii=False)}\n\n"
                # 推送流结束标记，便于前端关闭SSE
                yield f"data: {__import__('json').dumps({'type': 'stream_end'}, ensure_ascii=False)}\n\n"
                break
            time.sleep(0.5)

    headers = {
        'Content-Type': 'text/event-stream; charset=utf-8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
    }
    return Response(stream(), headers=headers)

def main():
    port = int(os.environ.get('PORT', '5000'))
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    main()


