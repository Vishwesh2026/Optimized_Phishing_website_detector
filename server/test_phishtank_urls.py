"""
test_phishtank_urls.py
─────────────────────────────────────────────────────────────
Verification script to test known phishing URLs against the
Ensemble Phishing Detection API.

Tests a mix of:
  - Known phishing URLs (from PhishTank and common examples)
  - Known safe URLs (major legitimate sites)

Expected results:
  - All phishing URLs should be classified as "phishing"
  - All safe URLs should be classified as "safe"

USAGE:
  1. Start the server:  uvicorn app.main:app --reload
  2. Run this script:   python test_phishtank_urls.py
"""

import json
import sys
import requests

API_URL = "http://127.0.0.1:8000/api/v1/analyze"
TIMEOUT = 60  # seconds (infra checks can be slow)


# ── Test URLs ─────────────────────────────────────────────────────────────────

# Known phishing / suspicious URLs (typical PhishTank patterns)
# NOTE: Replace these with actual verified phishing URLs from PhishTank
#       at the time of testing. Phishing URLs go offline quickly.
PHISHING_TEST_URLS = [
    # IP-based phishing
    "http://192.168.1.100/paypal/login.php",
    # Brand impersonation with suspicious domain
    "https://paypal-secure-login.xyz/verify/account",
    "https://apple.id-verification.com/signin",
    "https://microsoft-365-update.com/login",
    # Excessive subdomains
    "https://secure.login.paypal.account.verify.evil-domain.com/signin",
    # Long URL with obfuscated params
    "https://suspicious-site.com/70ffb52d079109dca5664cce6f317373782/login.SkyPe.com/en/cgi-bin/verification/login/index.php?cmd=_profile-ach&outdated_page_tmpl=p/gen/failed-to-load&nav=0.5.1",
]

# Known safe URLs (these should always be classified as safe)
SAFE_TEST_URLS = [
    "https://www.google.com",
    "https://www.wikipedia.org",
    "https://www.github.com",
    "https://www.python.org",
    "https://www.stackoverflow.com",
]


def test_url(url: str, expected: str) -> dict:
    """Test a single URL and return result dict."""
    try:
        response = requests.post(API_URL, json={"url": url}, timeout=TIMEOUT)
        if response.status_code != 200:
            return {
                "url": url,
                "expected": expected,
                "actual": "ERROR",
                "passed": False,
                "detail": f"HTTP {response.status_code}: {response.text[:200]}",
            }

        data = response.json()
        actual = data.get("prediction", "unknown")
        confidence = data.get("confidence", 0)
        risk_level = data.get("risk_level", "UNKNOWN")
        phishtank_flagged = data.get("phishtank_flagged", False)
        heuristic_reasons = data.get("heuristic_reasons", [])

        # For phishing URLs, "invalid" (NXDOMAIN) is also acceptable
        if expected == "phishing":
            passed = actual in ("phishing", "invalid")
        else:
            passed = actual == expected

        return {
            "url": url[:80] + ("..." if len(url) > 80 else ""),
            "expected": expected,
            "actual": actual,
            "confidence": confidence,
            "risk_level": risk_level,
            "phishtank": phishtank_flagged,
            "heuristics": heuristic_reasons,
            "passed": passed,
        }
    except requests.exceptions.ConnectionError:
        return {
            "url": url[:80],
            "expected": expected,
            "actual": "CONNECTION_ERROR",
            "passed": False,
            "detail": "Cannot connect to API. Is the server running?",
        }
    except Exception as e:
        return {
            "url": url[:80],
            "expected": expected,
            "actual": "ERROR",
            "passed": False,
            "detail": str(e),
        }


def main():
    print("=" * 80)
    print("  PhishTank URL Detection Test")
    print("=" * 80)
    print()

    # Check server health
    try:
        health = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if health.status_code == 200:
            print("✓ Server is running and healthy")
        else:
            print(f"⚠ Server returned status {health.status_code}")
    except Exception:
        print("✗ Cannot connect to server at http://127.0.0.1:8000")
        print("  Please start the server first:")
        print("  cd server && uvicorn app.main:app --reload")
        sys.exit(1)

    print()
    results = []

    # Test phishing URLs
    print("─" * 80)
    print("  Testing PHISHING URLs (expected: phishing)")
    print("─" * 80)
    for url in PHISHING_TEST_URLS:
        result = test_url(url, "phishing")
        results.append(result)
        status = "✓ PASS" if result["passed"] else "✗ FAIL"
        print(f"  {status}  [{result.get('actual', '?'):>8s}]  conf={result.get('confidence', 0):.2f}  {result['url']}")
        if result.get("heuristics"):
            print(f"         Heuristics: {', '.join(result['heuristics'])}")
        if result.get("phishtank"):
            print(f"         PhishTank: FLAGGED")

    print()

    # Test safe URLs
    print("─" * 80)
    print("  Testing SAFE URLs (expected: safe)")
    print("─" * 80)
    for url in SAFE_TEST_URLS:
        result = test_url(url, "safe")
        results.append(result)
        status = "✓ PASS" if result["passed"] else "✗ FAIL"
        print(f"  {status}  [{result.get('actual', '?'):>8s}]  conf={result.get('confidence', 0):.2f}  {result['url']}")

    # Summary
    print()
    print("=" * 80)
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    print(f"  RESULTS: {passed}/{total} passed, {failed} failed")

    phish_results = [r for r in results if r["expected"] == "phishing"]
    safe_results = [r for r in results if r["expected"] == "safe"]
    phish_pass = sum(1 for r in phish_results if r["passed"])
    safe_pass = sum(1 for r in safe_results if r["passed"])

    print(f"  Phishing detection: {phish_pass}/{len(phish_results)}")
    print(f"  Safe detection:     {safe_pass}/{len(safe_results)}")
    print("=" * 80)

    if failed > 0:
        print()
        print("  FAILED TESTS:")
        for r in results:
            if not r["passed"]:
                print(f"    - {r['url']}")
                print(f"      Expected: {r['expected']}, Got: {r.get('actual', 'unknown')}")
                if r.get("detail"):
                    print(f"      Detail: {r['detail']}")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
