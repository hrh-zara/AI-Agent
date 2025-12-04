$p = Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue
if ($p) {
    Stop-Process -Id $p.OwningProcess -Force
    Write-Output "Killed process $($p.OwningProcess) using port 8501"
} else {
    Write-Output "No process listening on port 8501"
}
Write-Output "Starting Streamlit (foreground) - press Ctrl+C to stop"
$env:DEMO_MODE = '1'
streamlit run web_app\app.py --server.port 8501
