from conftest import CONTRACT
import json


URLS = [
    "https://alpha.example/licenses/core",
    "https://beta.example/licenses/widget",
    "https://gamma.example/licenses/fonts",
]


def opened(vm, deploy, owner, commitments=None):
    vm.strict_mocks = True
    vm.check_pickling = True
    vm.sender = owner
    contract = deploy(CONTRACT)
    contract.open_review(
        "bundle-7",
        "Public kiosk distribution bundle",
        URLS,
        commitments or ["ATTRIBUTION", "PRESERVE_NOTICE", "PUBLISH_SOURCE"],
    )
    return contract


def sources(vm):
    vm.mock_web(r"alpha\.example", {"status": 200, "body": "Redistribution requires attribution and preservation of this notice."})
    vm.mock_web(r"beta\.example", {"status": 200, "body": "Binary redistribution requires a corresponding source offer."})
    vm.mock_web(r"gamma\.example", {"status": 200, "body": "Redistribution requires attribution."})


def llm(vm, rows):
    vm.mock_llm(r".*LicenseBoundary extraction.*", json.dumps({"rows": rows}))


def good_rows():
    return [
        {"index": 0, "status": "OK", "required": ["ATTRIBUTION", "PRESERVE_NOTICE"]},
        {"index": 1, "status": "OK", "required": ["PUBLISH_SOURCE"]},
        {"index": 2, "status": "OK", "required": ["ATTRIBUTION"]},
    ]


def test_compatible_bundle(direct_vm, direct_deploy, direct_alice):
    contract = opened(direct_vm, direct_deploy, direct_alice)
    sources(direct_vm)
    llm(direct_vm, good_rows())
    contract.evaluate("bundle-7")
    result = contract.get_review("bundle-7")
    assert result["state"] == "COMPATIBLE"
    assert result["required_union"] == ["ATTRIBUTION", "PRESERVE_NOTICE", "PUBLISH_SOURCE"]
    assert result["missing"] == []
    assert len(result["digests"]) == 3


def test_missing_commitment_is_conflict(direct_vm, direct_deploy, direct_alice):
    contract = opened(direct_vm, direct_deploy, direct_alice, ["ATTRIBUTION", "PRESERVE_NOTICE"])
    sources(direct_vm)
    llm(direct_vm, good_rows())
    contract.evaluate("bundle-7")
    result = contract.get_review("bundle-7")
    assert result["state"] == "CONFLICT"
    assert result["missing"] == ["PUBLISH_SOURCE"]


def test_no_redistribution_is_conflict(direct_vm, direct_deploy, direct_alice):
    contract = opened(direct_vm, direct_deploy, direct_alice)
    sources(direct_vm)
    rows = good_rows()
    rows[1] = {"index": 1, "status": "NO_REDISTRIBUTION", "required": []}
    llm(direct_vm, rows)
    contract.evaluate("bundle-7")
    assert contract.get_review("bundle-7")["state"] == "CONFLICT"


def test_ambiguity_is_inconclusive(direct_vm, direct_deploy, direct_alice):
    contract = opened(direct_vm, direct_deploy, direct_alice)
    sources(direct_vm)
    rows = good_rows()
    rows[2] = {"index": 2, "status": "AMBIGUOUS", "required": []}
    llm(direct_vm, rows)
    contract.evaluate("bundle-7")
    assert contract.get_review("bundle-7")["state"] == "INCONCLUSIVE"


def test_validator_rejects_forged_obligation_and_digest(direct_vm, direct_deploy, direct_alice):
    contract = opened(direct_vm, direct_deploy, direct_alice)
    sources(direct_vm)
    llm(direct_vm, good_rows())
    result = contract._inspect(contract.reviews["BUNDLE-7"])
    assert direct_vm.run_validator(leader_result=result) is True
    forged = {"digests": list(result["digests"]), "rows": json.loads(json.dumps(result["rows"]))}
    forged["rows"][0]["required"] = ["ATTRIBUTION"]
    assert direct_vm.run_validator(leader_result=forged) is False
    forged = {"digests": list(result["digests"]), "rows": result["rows"]}
    forged["digests"][1] = "0" * 64
    assert direct_vm.run_validator(leader_result=forged) is False


def test_duplicate_id_slots_and_unknown_obligation_rejected(direct_vm, direct_deploy, direct_alice):
    contract = opened(direct_vm, direct_deploy, direct_alice)
    with direct_vm.expect_revert("unique review id"):
        contract.open_review("bundle-7", "Duplicate", URLS, ["ATTRIBUTION"])
    with direct_vm.expect_revert("distinct license source slots"):
        contract.open_review("bundle-8", "Duplicate URL", [URLS[0], URLS[0]], ["ATTRIBUTION"])
    with direct_vm.expect_revert("known obligations"):
        contract.open_review("bundle-9", "Unknown promise", URLS[:2], ["MAGIC"])


def test_cancel_authorization_and_replay(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = opened(direct_vm, direct_deploy, direct_alice)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("owner of open review"):
        contract.cancel_open("bundle-7")
    direct_vm.sender = direct_alice
    contract.cancel_open("bundle-7")
    with direct_vm.expect_revert("open review required"):
        contract.evaluate("bundle-7")
