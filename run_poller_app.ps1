# run_poller_app.ps1
# Helper script to set environment variables and launch backend + frontend together

Write-Host "Setting environment variables..."
$env:IMAP_HOST = 'imap.gmail.com'
$env:IMAP_USER = 'decodude121@gmail.com'
$env:IMAP_PASSWORD = 'rfnzlkceodgdtmet'   # Replace with actual app password if this was just an example
$env:TRIDENT_URL = 'http://127.0.0.1:8000/detect'
$env:ALERTS_URL = 'http://127.0.0.1:8000/alerts'
$env:IMAP_POLL_INTERVAL = '15'
$env:IMAP_MARK_SEEN = 'false'
$env:PYTHONUNBUFFERED = '1'

Write-Host "Starting Backend on port 8000..."
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "main.py","api"

Write-Host "Starting Frontend on port 5173..."
Set-Location -Path ".\frontend"
Start-Process -NoNewWindow -FilePath "cmd.exe" -ArgumentList "/c","npm run dev"

Write-Host ""
Write-Host "Services are starting up!"
Write-Host " - Frontend: http://localhost:5173"
Write-Host " - Backend API: http://localhost:8000"
Write-Host "Open the frontend in your browser and use the Terminal Section to start the Poller."
Write-Host "Press Ctrl+C to exit this command prompt (you may need to manually stop python/node processes)."
