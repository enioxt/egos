@echo off
REM Convenience script to launch the Relation Extraction Service (dev reload)
cd /d %~dp0\..
poetry run uvicorn services.relation_extraction.service:app --reload --port 8000
