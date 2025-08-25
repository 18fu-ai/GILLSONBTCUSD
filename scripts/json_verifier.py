import json, hashlib

EXPECTED = {"ANCH":"stable","VLPL":"stable","VHSH":"stable","OTSP":"stable","GOVR":"stable","JAXX":"stable","VALX":"stable","VALT":"stable","VACN":"stable","VBLK":"stable","DBLK":"stable","GILLGOLD":"stable","GILLBTC":"stable","TONY":"stable","SARA":"stable","TODD":"stable","VLRN":"stable"}

SNAPSHOT = {"ANCH":{"price":1.0,"peg":"USD"},"VLPL":{"price":1.0,"peg":"USD"},"VALT":{"price":1.0,"peg":"USD"},"VBLK":{"price":1.0,"peg":"USD"}}

class StablecoinVerifier:
    def __init__(self, snapshot, expected):
        self.snapshot = snapshot
        self.expected = expected

    def verify(self):
        results = {}
        for ticker, meta in self.expected.items():
            if ticker in self.snapshot:
                status = "PASS" if self.snapshot[ticker]["price"] == 1.0 else "FAIL"
                results[ticker] = {"status":status,"peg":self.snapshot[ticker].get("peg","?"),"hash":hashlib.sha256(json.dumps(self.snapshot[ticker]).encode()).hexdigest()}
            else:
                results[ticker] = {"status":"MISSING"}
        return results

if __name__ == "__main__":
    verifier = StablecoinVerifier(SNAPSHOT, EXPECTED)
    report = verifier.verify()
    print(json.dumps(report, indent=2))
