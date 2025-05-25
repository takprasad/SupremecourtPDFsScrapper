# 🏛️ Supreme Court Document Scraper

A robust and fault-tolerant Python scraper for downloading Supreme Court case documents (PDFs) from the official website. This tool uses **Selenium** to navigate dynamic content and **Requests** to download documents. It includes built-in **checkpoints** to resume progress in case of interruptions and **automatically renames PDFs** based on the case name for better organization.

---

## ✨ Features

- 🔍 **Automated Page Navigation** using Selenium.
- 📥 **PDF Downloading** using Requests for efficient file handling.
- ♻️ **Checkpointing System** to resume from the last successful download if interrupted.
- 🏷️ **Case-based File Renaming** for meaningful and organized filenames.
- ✅ Designed to be robust against network or browser crashes.

---

## 🛠️ Technologies Used

- **Python 3.7+**
- **Selenium** (for browser automation)
- **Requests** (for file download)
- **BeautifulSoup** (optional: for HTML parsing, if used)
- **Pickle / JSON** (for saving checkpoints)

---

## 🧠 How It Works

1. **Selenium** opens the Supreme Court website and navigates through paginated listings or search results.
2. For each document:
   - The scraper extracts the **case name**.
   - The **PDF link** is captured.
   - The document is downloaded using **Requests**.
   - A **checkpoint file** is updated with the current progress.
3. If the scraper is stopped, it loads the checkpoint and resumes from where it left off.

---

## 🧾 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

---

## 🙌 Acknowledgements

- [Selenium](https://www.selenium.dev/)
- [Requests](https://docs.python-requests.org/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) (if used)
