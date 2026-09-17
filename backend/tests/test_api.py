import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_health():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["system"] == "VeriPack"
    assert data["status"] == "OPERATIONAL"

def test_auth_login():
    res = client.post("/api/auth/login", json={
        "email": "inspector.sharma@doca.gov.in",
        "password": "Inspector@2026"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "INSPECTOR"

def test_consumer_login():
    res = client.post("/api/auth/login", json={
        "email": "consumer.rahul@gmail.com",
        "password": "Consumer@2026"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "CONSUMER"

def test_dashboard_stats_and_rules():
    login_res = client.post("/api/auth/login", json={
        "email": "inspector.sharma@doca.gov.in",
        "password": "Inspector@2026"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    dash_res = client.get("/api/dashboard/stats", headers=headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["total_scans"] >= 5

    rules_res = client.get("/api/rules", headers=headers)
    assert rules_res.status_code == 200
    assert len(rules_res.json()) >= 8

def test_scan_demo_scenario():
    login_res = client.post("/api/auth/login", json={
        "email": "inspector.sharma@doca.gov.in",
        "password": "Inspector@2026"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    scan_res = client.post(
        "/api/scans/analyze",
        data={"demo_key": "compliant_salt", "category": "FOOD_BEVERAGE"},
        headers=headers
    )
    assert scan_res.status_code == 200
    scan_data = scan_res.json()
    assert scan_data["status"] == "COMPLIANT"
    assert "Tata Pure Refined Iodised Salt" in scan_data["product_name"]
