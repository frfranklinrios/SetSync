"""Testes do fechamento de noite (liquidação de cachê)."""

from event_fees import compute_event_fee_split, compute_night_settlement


def _name(row):
    return row.get("name") or row.get("display_name") or "X"


def test_night_settlement_sideman_and_founders():
    event = {
        "fee_total": 1000,
        "fee_transport_discount": 50,
        "fee_equipment_discount": 0,
    }
    members = [
        {"user_id": "a", "name": "Alice", "settlement_role": "founder"},
        {"user_id": "b", "name": "Bob", "settlement_role": "founder"},
        {
            "user_id": "c",
            "name": "Carol",
            "settlement_role": "sideman",
            "default_fixed_fee": 150,
        },
    ]
    assignments = [
        {"user_id": "a", "name": "Alice", "response_status": "accepted"},
        {"user_id": "b", "name": "Bob", "response_status": "accepted"},
        {"user_id": "c", "name": "Carol", "response_status": "accepted"},
    ]
    expenses = [{"descricao": "Combustível", "valor": 100}]
    guests = [{"id": "g1", "name": "Sub", "fixed_fee": 80}]

    s = compute_night_settlement(
        event,
        assignments,
        members,
        guests=guests,
        event_expenses=expenses,
        fee_lines=None,
        name_for_user=_name,
    )
    assert s["mode"] == "night"
    assert s["total"] == 1000
    assert s["night_expenses"] == 100
    assert s["net"] == 850  # 1000 - 50 - 100
    assert s["fixed_total"] == 230  # 150 + 80
    assert s["pool"] == 620  # 850 - 230
    assert len(s["founder_payees"]) == 2
    assert (
        abs(s["founder_payees"][0]["amount"] + s["founder_payees"][1]["amount"] - 620)
        < 0.02
    )
    assert len(s["fixed_payees"]) == 2


def test_founder_explicit_amounts():
    """Fundadores com valor informado não dividem o resto — cada um recebe o definido."""
    event = {
        "fee_total": 1000,
        "fee_transport_discount": 0,
        "fee_equipment_discount": 0,
    }
    members = [
        {"user_id": "a", "name": "Alice", "settlement_role": "founder"},
        {"user_id": "b", "name": "Bob", "settlement_role": "founder"},
        {"user_id": "c", "name": "Carol", "settlement_role": "founder"},
    ]
    assignments = [
        {"user_id": "a", "name": "Alice", "response_status": "accepted"},
        {"user_id": "b", "name": "Bob", "response_status": "accepted"},
        {"user_id": "c", "name": "Carol", "response_status": "accepted"},
    ]
    s = compute_night_settlement(
        event,
        assignments,
        members,
        guests=[],
        event_expenses=[],
        fee_lines=None,
        name_for_user=_name,
        amount_overrides={"a": 400, "b": 350},
    )
    # Carol divide o resto: 1000 - 400 - 350 = 250
    assert s["fixed_total"] == 750
    assert s["pool"] == 250
    assert len(s["fixed_payees"]) == 2
    assert len(s["founder_payees"]) == 1
    assert s["founder_payees"][0]["user_id"] == "c"
    assert s["founder_payees"][0]["amount"] == 250.0
    by_id = {p["user_id"]: p["amount"] for p in s["payees"]}
    assert by_id["a"] == 400.0
    assert by_id["b"] == 350.0
    assert by_id["c"] == 250.0


def test_all_founders_explicit():
    event = {"fee_total": 900, "fee_transport_discount": 0, "fee_equipment_discount": 0}
    members = [
        {"user_id": "a", "name": "A", "settlement_role": "founder"},
        {"user_id": "b", "name": "B", "settlement_role": "founder"},
        {"user_id": "c", "name": "C", "settlement_role": "founder"},
    ]
    assignments = [
        {"user_id": uid, "name": uid.upper(), "response_status": "accepted"}
        for uid in ("a", "b", "c")
    ]
    s = compute_night_settlement(
        event,
        assignments,
        members,
        guests=[],
        event_expenses=[],
        fee_lines=None,
        name_for_user=_name,
        amount_overrides={"a": 500, "b": 250, "c": 150},
    )
    assert s["pool"] == 0
    assert len(s["founder_payees"]) == 0
    assert len(s["fixed_payees"]) == 3
    assert abs(sum(p["amount"] for p in s["payees"]) - 900) < 0.02


def test_orphan_pool_warning():
    event = {
        "fee_total": 1000,
        "fee_transport_discount": 0,
        "fee_equipment_discount": 0,
    }
    members = [
        {
            "user_id": "c",
            "name": "Carol",
            "settlement_role": "sideman",
            "default_fixed_fee": 200,
        },
    ]
    assignments = [
        {"user_id": "c", "name": "Carol", "response_status": "accepted"},
    ]
    s = compute_night_settlement(
        event,
        assignments,
        members,
        guests=[],
        event_expenses=[],
        fee_lines=None,
        name_for_user=_name,
    )
    assert s["pool"] == 800
    assert not s["founder_payees"]
    assert s["warning"] and "sem destinatário" in s["warning"]


def test_legacy_equal_split_unchanged():
    event = {"fee_total": 300, "fee_transport_discount": 0, "fee_equipment_discount": 0}
    members = [
        {"user_id": "a", "name": "A", "settlement_role": "founder"},
        {"user_id": "b", "name": "B", "settlement_role": "founder"},
    ]
    assignments = [
        {"user_id": "a", "name": "A", "response_status": "accepted"},
        {"user_id": "b", "name": "B", "response_status": "accepted"},
    ]
    s = compute_event_fee_split(event, assignments, members, name_for_user=_name)
    assert s["mode"] == "equal"
    assert s["share"] == 150.0
    assert len(s["payees"]) == 2


if __name__ == "__main__":
    test_night_settlement_sideman_and_founders()
    test_founder_explicit_amounts()
    test_all_founders_explicit()
    test_orphan_pool_warning()
    test_legacy_equal_split_unchanged()
    print("ok")
