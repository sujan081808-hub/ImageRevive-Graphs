# ImageRevive Graphs — Smart Image Lab

Modern HTML/CSS/JavaScript frontend and Python Flask image-processing API, prepared for Vercel.

## Features
- PNG/JPG/WEBP upload, 8 MB maximum
- Auto contrast stretching, grayscale, contrast, brightness, median filtering, sharpening, edge detection and Otsu thresholding
- Before/after previews, image dimensions, brightness, intensity variation, processing time, PNG download
- Live grayscale intensity histogram comparing original and processed pixels
- Before/after bar chart comparing mean brightness and intensity variation
- Responsive desktop/mobile interface

## Local setup (Windows / VS Code)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000. If PowerShell blocks activation, use Command Prompt and run `.venv\Scripts\activate.bat`.

## Deploy as a new, separate GitHub project
This folder is a standalone copy with live image-analysis graphs. It does not need to replace your existing ImageRevive repository.

1. Create a **new empty GitHub repository**, for example `ImageRevive-Graphs`.
2. Open PowerShell in this extracted folder.
3. Run the following commands from this folder:
```powershell
git init
git add .
git commit -m "Build ImageRevive for Vercel"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/ImageRevive-Graphs.git
git push -u origin main
```
Replace `YOUR-USERNAME` with your GitHub username. Because this is a new project folder, create its first commit and connect it to the new repository.

## Vercel deployment
1. Push the project to GitHub.
2. Open https://vercel.com/new and sign in.
3. Import the new GitHub repository `ImageRevive-Graphs`.
4. Keep the project root at the repository root. Vercel should detect the Flask `app.py` entry point.
5. Leave build command/output directory at defaults unless Vercel asks otherwise, then click Deploy.
6. Test the assigned `*.vercel.app` URL and `/health`, upload an image, process it and download the PNG.

## Notes
- Uses Flask and Pillow to keep dependencies compact for Vercel's Python runtime.
- Graphs are drawn with Chart.js loaded from a CDN, so the browser needs internet access for chart rendering.
- Uploads are processed in memory; images are not stored in a database.
- This is a learning/demo tool, not a forensic authenticity detector.
