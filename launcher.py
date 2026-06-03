#!/usr/bin/env python3
"""标准通爬虫桌面启动器"""
import subprocess
import sys
import os
import webbrowser
import time
import signal
import tkinter as tk
from tkinter import messagebox
import threading

def get_resource_path(relative_path):
    """获取资源文件路径（兼容 PyInstaller 打包）"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

def start_streamlit():
    """启动 Streamlit 服务"""
    app_path = get_resource_path('app.py')
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', app_path,
        '--server.headless', 'true',
        '--server.port', '8501',
        '--browser.gatherUsageStats', 'false'
    ]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

class LauncherApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("标准通爬虫")
        self.root.geometry("400x200")
        self.root.resizable(False, False)

        # 设置窗口图标（如果存在）
        try:
            icon_path = get_resource_path('icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass

        self.process = None
        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        # 标题
        title_label = tk.Label(self.root, text="标准通爬虫", font=("Arial", 20, "bold"))
        title_label.pack(pady=20)

        # 说明
        desc_label = tk.Label(self.root, text="从标准通(www.bzton.com)批量抓取标准信息", font=("Arial", 10))
        desc_label.pack()

        # 按钮框架
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=30)

        # 启动按钮
        self.start_btn = tk.Button(btn_frame, text="启动应用", command=self.start_app,
                                   font=("Arial", 12), width=15, height=2, bg="#4CAF50", fg="white")
        self.start_btn.pack(side=tk.LEFT, padx=10)

        # 退出按钮
        self.quit_btn = tk.Button(btn_frame, text="退出", command=self.quit_app,
                                  font=("Arial", 12), width=15, height=2)
        self.quit_btn.pack(side=tk.LEFT, padx=10)

        # 状态标签
        self.status_label = tk.Label(self.root, text="就绪", font=("Arial", 9), fg="gray")
        self.status_label.pack(side=tk.BOTTOM, pady=10)

    def start_app(self):
        """启动 Streamlit 应用"""
        self.start_btn.config(state=tk.DISABLED, text="启动中...")
        self.status_label.config(text="正在启动 Streamlit 服务...", fg="blue")
        self.root.update()

        # 在新线程中启动 Streamlit
        threading.Thread(target=self._start_streamlit_thread, daemon=True).start()

    def _start_streamlit_thread(self):
        """在后台线程中启动 Streamlit"""
        try:
            self.process = start_streamlit()

            # 等待服务启动
            time.sleep(5)

            # 打开浏览器
            webbrowser.open('http://localhost:8501')

            # 更新 UI
            self.root.after(0, self._update_ui_running)
        except Exception as e:
            self.root.after(0, lambda: self._update_ui_error(str(e)))

    def _update_ui_running(self):
        """更新 UI 为运行状态"""
        self.start_btn.config(text="已在浏览器中打开", state=tk.DISABLED)
        self.status_label.config(text="服务运行中，关闭此窗口将停止服务", fg="green")

    def _update_ui_error(self, error):
        """更新 UI 为错误状态"""
        self.start_btn.config(state=tk.NORMAL, text="启动应用")
        self.status_label.config(text=f"启动失败: {error}", fg="red")
        messagebox.showerror("错误", f"启动失败: {error}")

    def quit_app(self):
        """退出应用"""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
        self.root.destroy()

    def run(self):
        """运行启动器"""
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.root.mainloop()

if __name__ == '__main__':
    app = LauncherApp()
    app.run()
