from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_endpoints():
    print("Testing /api/v1/health...")
    r = client.get("/api/v1/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print("Health check OK:", r.json()["status"])

    print("Testing /api/v1/finance/summary...")
    r = client.get("/api/v1/finance/summary")
    assert r.status_code == 200, f"Summary failed: {r.text}"
    data = r.json()
    print(f"Summary OK: Total Income={data['total_income']}, Total Expense={data['total_expense']}")

    print("Testing /api/v1/finance/transactions...")
    r = client.get("/api/v1/finance/transactions")
    assert r.status_code == 200
    print(f"Transactions OK: count={len(r.json())}")

    print("Testing /api/v1/wiki/documents...")
    r = client.get("/api/v1/wiki/documents")
    assert r.status_code == 200
    print(f"Wiki docs OK: count={len(r.json())}")

    print("Testing /api/v1/checklist...")
    r = client.get("/api/v1/checklist")
    assert r.status_code == 200
    print(f"Checklist OK: count={len(r.json())}")

    print("Testing /api/v1/llm/chat...")
    r = client.post("/api/v1/llm/chat", json={"prompt": "이번달 지출 얼마야?"})
    assert r.status_code == 200
    print("LLM Chat OK Answer:", r.json()["answer"][:60], "...")

    print("Testing /api/v1/receipts/scan...")
    r = client.post("/api/v1/receipts/scan", data={"filename_override": "sample_receipt.jpg"})
    assert r.status_code == 200
    res = r.json()
    print(f"Receipt Scan OK: Store={res['store_name']}, Total={res['total_amount']}")

    print("ALL API ENDPOINT TESTS PASSED!")

if __name__ == "__main__":
    test_endpoints()

