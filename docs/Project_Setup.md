
# Project Setup Guide

## Python Version
Python 3.10+

## Create Virtual Environment
python -m venv venv

## Activate
venv\Scripts\activate

## Install
pip install -r backend/requirements.txt

## Run Backend
uvicorn backend.main:app --reload