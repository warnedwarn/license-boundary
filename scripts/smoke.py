import json
import re
import time
from pathlib import Path

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet
from genlayer_py.contracts import actions as contract_actions


def calldata_compat(method=None, args=None, kwargs=None):
    result = {}
    if method is not None:
        result["method"] = method
    if args:
        result["args"] = args
    if kwargs:
        result["kwargs"] = kwargs
    return result


contract_actions.make_calldata_object = calldata_compat
ROOT = Path(__file__).parents[1]
ENV = (ROOT.parents[3] / "accounts.env").read_text()
DEPLOYMENT = json.loads((ROOT / "deployment.json").read_text())
ADDRESS = DEPLOYMENT["contractAddress"]
COMMIT = DEPLOYMENT["sourceCommit"]
KEY = re.search(r'^ACCOUNT_2_GENLAYER_PRIVATE_KEY\s*=\s*"?([^"\r\n]+)', ENV, re.M).group(1).strip()
ACCOUNT = create_account(account_private_key=KEY)
CLIENT = create_client(chain=studionet, account=ACCOUNT)


def write(name, args):
    tx = CLIENT.write_contract(address=ADDRESS, function_name=name, args=args)
    print(name + "_tx=" + str(tx), flush=True)
    receipt = CLIENT.wait_for_transaction_receipt(
        transaction_hash=tx,
        wait_until="finalized",
        retries=180,
        interval=5000,
        full_transaction=True,
    )
    leaders = receipt.get("consensus_data", {}).get("leader_receipt") or []
    leaders = [leaders] if isinstance(leaders, dict) else leaders
    assert receipt.get("result_name") == "MAJORITY_AGREE"
    assert any(item.get("execution_result") == "SUCCESS" for item in leaders)
    return str(tx)


base = f"https://raw.githubusercontent.com/warnedwarn/license-boundary/{COMMIT}/evidence"
review_id = "LICENSE-" + str(int(time.time()))
urls = [
    base + "/component-core-license.md",
    base + "/component-widget-license.md",
    base + "/component-font-license.md",
]
transactions = {
    "open": write(
        "open_review",
        [
            review_id,
            "Public kiosk distribution bundle",
            urls,
            ["ATTRIBUTION", "PRESERVE_NOTICE", "PUBLISH_SOURCE"],
        ],
    )
}
transactions["evaluate"] = write("evaluate", [review_id])
state = CLIENT.read_contract(address=ADDRESS, function_name="get_review", args=[review_id])
assert state["state"] == "COMPATIBLE"
assert state["required_union"] == ["ATTRIBUTION", "PRESERVE_NOTICE", "PUBLISH_SOURCE"]
assert state["missing"] == []
assert len(state["digests"]) == 3
proof = {
    "reviewId": review_id,
    "transactions": transactions,
    "state": state,
    "fixtureDisclosure": "All license pages are operator-authored technical fixtures. They demonstrate source binding and obligation coverage and are not legal advice or independent authorities.",
}
(ROOT / "evidence" / "live-proof.json").write_text(json.dumps(proof, indent=2) + "\n")
print(json.dumps(proof, indent=2), flush=True)
