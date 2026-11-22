@echo off
title LogiGraph AI - Delhivery Logistics Network Intelligence
echo ======================================================================
echo    DELHIVERY LOGISTICS NETWORK INTELLIGENCE (LOGIGRAPH AI)
echo ======================================================================
echo Starting Streamlit Interactive Web Application...
echo The dashboard will automatically open in your default browser.
echo.
python -m streamlit run app/app.py --server.port 8501
pause

