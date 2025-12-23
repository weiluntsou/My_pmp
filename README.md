[English](#mypmp) | [繁體中文](#mypmp-%E7%B9%81%E9%AB%94%E4%B8%AD%E6%96%87%E7%89%88)

# My_pmp
**A Comprehensive Project Management Tool for Digital Development Teams**

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-teal)

My_pmp is a modern, lightweight project management solution designed to streamline the workflow of digital development sections. It offers robust features for project tracking, meeting management, workload analysis, and automated reporting, all wrapped in a responsive web interface.

## 📋 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#-usage)
  - [Running on Windows](#running-on-windows)
  - [Running on Mac/Linux](#running-on-maclinux)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

- **📊 Dashboard Overview**: Get a bird's-eye view of all ongoing projects and critical metrics.
- **🚀 Project Management**: Detailed tracking of project progress, including planned vs. actual timelines and weekly status updates.
  - **Gantt Chart**: Interactive 52-week timeline view for the entire project year.
- **📅 Meeting Planner**: Integrated meeting scheduler and record keeper.
  - **Schedule View**: Weekly (Mon-Fri) calendar view sorted by time with AM/PM separators.
  - **Outlook Integration**: Generate Outlook (.ics) meeting invites directly from the log page with one click.
- **👥 Workload Analysis**: Visualize engineer workload to balance tasks effectively and avoid burnout.
- **🔄 Sync & Import/Export**: Seamless data synchronization and support for importing/exporting meeting logs and project data via Markdown.
- **📝 Automated Reports**: Generate regular statuses and comprehensive reports with a single click.

## 🛠 Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) - High performance, easy to learn, fast to code, ready for production.
- **Database**: [SQLAlchemy](https://www.sqlalchemy.org/) - The Database Toolkit for Python.
- **Frontend**: [Jinja2](https://jinja.palletsprojects.com/) Templates + [Bootstrap/Custom CSS] for a responsive UI.
- **Server**: [Uvicorn](https://www.uvicorn.org/) - A lightning-fast ASGI server.

## 📂 Project Structure

```bash
My_pmp/
├── app/                  # Main application source code
│   ├── routers/          # API routes (projects, meetings, reports, etc.)
│   ├── database.py       # Database connection and session management
│   ├── main.py           # Application entry point
│   ├── models.py         # SQLAlchemy database models
│   └── schemas.py        # Pydantic schemas for data validation
├── static/               # Static assets (CSS, JS, Images)
├── templates/            # HTML templates for the frontend
├── data/                 # Data storage (e.g., SQLite DB)
├── run.bat               # Windows startup script
├── run.sh                # Mac/Linux startup script
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

## 🚀 Getting Started

Follow these steps to get a local copy up and running.

### Prerequisites

*   Python 3.8 or higher
*   Git

### Installation

1.  **Clone the repository**
    ```sh
    git clone https://github.com/weiluntsou/My_pmp.git
    cd My_pmp
    ```

2.  **Create a Virtual Environment**
    ```sh
    # Windows
    python -m venv venv
    
    # Mac/Linux
    python3 -m venv venv
    ```

3.  **Install Dependencies**
    ```sh
    # Windows
    venv\Scripts\pip install -r requirements.txt
    
    # Mac/Linux
    ./venv/bin/pip install -r requirements.txt
    ```

## 🖥 Usage

### Running on Windows
We have provided a convenient batch script for Windows users.
Double-click `run.bat` or run it from the command line:
```cmd
run.bat
```
This will activate the virtual environment and start the server at `http://127.0.0.1:8000`.

### Running on Mac/Linux
Use the shell script to start the application:
```sh
chmod +x run.sh
./run.sh
```
Access the application at `http://127.0.0.1:8000`.

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---
Built with ❤️ by **weiluntsou**.

---

# My_pmp (繁體中文版)
**數位發展團隊的全方位專案管理工具**

My_pmp 是一個現代化、輕量級的專案管理解決方案，專為數位發展團隊的工作流程設計。它提供強大的功能來追蹤專案、管理會議、分析工作量以及自動化報告，所有這些都整合在一個響應式網頁介面中。

## 📋 目錄
- [功能特色](#-功能特色)
- [技術棧](#-技術棧)
- [專案結構](#-專案結構)
- [快速開始](#-快速開始)
  - [先決條件](#先決條件)
  - [安裝](#安裝)
- [使用方法](#-使用方法)
  - [Windows 執行](#windows-執行)
  - [Mac/Linux 執行](#maclinux-執行)
- [貢獻](#-貢獻)
- [授權](#-授權)

## ✨ 功能特色

- **📊 儀表板總覽**：一目了然地查看所有進行中的專案和關鍵指標。
- **🚀 專案管理**：詳細追蹤專案進度，包括計畫與實際時程的對比以及每週狀態更新。
  - **甘特圖**：全年度 52 週互動式時間軸視圖。
- **📅 會議規劃**：整合會議排程和記錄保存。
  - **行事曆視圖**：每週 (週一至週五) 按時間排序的會議列表，並區分上午/下午。
  - **Outlook 整合**：一鍵生成 Outlook (.ics) 會議邀請函，支援自訂主旨與內容格式。
- **👥 工作量分析**：視覺化工程師的工作量，有效平衡任務並避免過度疲勞。
- **🔄 同步與匯入/匯出**：無縫的資料同步，支援匯入/匯出 Markdown 格式的會議記錄和專案資料。
- **📝 自動化報告**：一鍵生成定期狀態和綜合報告。

## 🛠 技術棧

- **後端**：[FastAPI](https://fastapi.tiangolo.com/) - 高效能、易於學習、開發快速，且適合生產環境。
- **資料庫**：[SQLAlchemy](https://www.sqlalchemy.org/) - Python 的資料庫工具包。
- **前端**：[Jinja2](https://jinja.palletsprojects.com/) 模板 + [Bootstrap/Custom CSS] 打造響應式 UI。
- **伺服器**：[Uvicorn](https://www.uvicorn.org/) - 極速的 ASGI 伺服器。

## 📂 專案結構

```bash
My_pmp/
├── app/                  # 主要應用程式原始碼
│   ├── routers/          # API 路由 (projects, meetings, reports 等)
│   ├── database.py       # 資料庫連接與 session 管理
│   ├── main.py           # 應用程式進入點
│   ├── models.py         # SQLAlchemy 資料庫模型
│   └── schemas.py        # Pydantic 驗證模式
├── static/               # 靜態資源 (CSS, JS, Images)
├── templates/            # 前端 HTML 模板
├── data/                 # 資料儲存 (如 SQLite DB)
├── run.bat               # Windows 啟動腳本
├── run.sh                # Mac/Linux 啟動腳本
├── requirements.txt      # 專案依賴套件
└── README.md             # 專案文件
```

## 🚀 快速開始

跟隨以下步驟來建立並執行本地副本。

### 先決條件

*   Python 3.8 或更高版本
*   Git

### 安裝

1.  **Clone 儲存庫**
    ```sh
    git clone https://github.com/weiluntsou/My_pmp.git
    cd My_pmp
    ```

2.  **建立虛擬環境**
    ```sh
    # Windows
    python -m venv venv
    
    # Mac/Linux
    python3 -m venv venv
    ```

3.  **安裝依賴套件**
    ```sh
    # Windows
    venv\Scripts\pip install -r requirements.txt
    
    # Mac/Linux
    ./venv/bin/pip install -r requirements.txt
    ```

## 🖥 使用方法

### Windows 執行
我們為 Windows 使用者提供了方便的批次腳本。
雙擊 `run.bat` 或在命令列中執行：
```cmd
run.bat
```
這將啟動虛擬環境並在 `http://127.0.0.1:8000` 啟動伺服器。

### Mac/Linux 執行
使用與 shell 腳本啟動應用程式：
```sh
chmod +x run.sh
./run.sh
```
在 `http://127.0.0.1:8000` 存取應用程式。

## 🤝 貢獻

貢獻是開源社群如此美妙的原因。我們**非常感謝**您的任何貢獻。

1.  Fork 本專案
2.  建立您的 Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit 您的變更 (`git commit -m 'Add some AmazingFeature'`)
4.  Push 到 Branch (`git push origin feature/AmazingFeature`)
5.  開啟 Pull Request

## 📄 授權

本專案採用 MIT 授權。詳情請參閱 `LICENSE` 文件。

---
由 **weiluntsou** 用心打造。
