from tests.conftest import login, make_org


def _owner(client, db, slug):
    make_org(db, slug, owner_email=f"owner@{slug}.pk", password="OwnerPass123!")
    assert login(client, slug, f"owner@{slug}.pk", "OwnerPass123!").status_code == 200


def _client(client, name, **extra):
    return client.post("/api/v1/clients", json={"full_name": name, **extra}).json()


def _lead(client, **body):
    return client.post("/api/v1/intake/leads", json=body)


def test_clean_lead_is_clear(client, db):
    _owner(client, db, "intake-clear")
    r = _lead(client, full_name="Ayesha Khan", opposing_party="Zubair Ahmed", matter_type="civil")
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["conflict_level"] == "clear"
    assert body["conflict_hits_json"] == []


def test_opposing_party_is_existing_client_blocks(client, db):
    _owner(client, db, "intake-block")
    _client(client, "Bilal Raza")  # we already act for Bilal Raza
    # A new lead wants to act AGAINST Bilal Raza -> hard conflict.
    body = _lead(client, full_name="Hassan Ali", opposing_party="Bilal Raza").json()
    assert body["conflict_level"] == "block"
    assert any(h["kind"] == "adverse_to_existing_client" for h in body["conflict_hits_json"])


def test_existing_client_is_info_not_block(client, db):
    _owner(client, db, "intake-info")
    _client(client, "Sara Malik", email="sara@x.pk")
    body = _lead(client, full_name="Sara Malik", opposing_party="Someone Else").json()
    # Same person returning is informational, still safe to proceed.
    assert body["conflict_level"] == "clear"
    assert any(h["kind"] == "existing_client" for h in body["conflict_hits_json"])


def test_block_refuses_convert_without_override(client, db):
    _owner(client, db, "intake-conv")
    _client(client, "Imran Shah")
    lead_id = _lead(client, full_name="New Client", opposing_party="Imran Shah").json()["id"]
    # Convert is refused while a blocking conflict stands...
    r = client.post(f"/api/v1/intake/leads/{lead_id}/convert", json={"category": "civil"})
    assert r.status_code == 409
    # ...but an explicit override converts and creates the case.
    r2 = client.post(
        f"/api/v1/intake/leads/{lead_id}/convert",
        json={"category": "civil", "override": True},
    )
    assert r2.status_code == 201, r2.text
    case = r2.json()
    assert case["opposite_party"] == "Imran Shah"
    # The lead is now marked converted.
    leads = client.get("/api/v1/intake/leads").json()
    assert any(x["id"] == lead_id and x["status"] == "converted" for x in leads)


def test_clean_lead_converts_to_case(client, db):
    _owner(client, db, "intake-ok")
    lead_id = _lead(client, full_name="Fatima Noor", matter_type="family").json()["id"]
    r = client.post(f"/api/v1/intake/leads/{lead_id}/convert", json={"category": "family"})
    assert r.status_code == 201, r.text
    assert "Fatima Noor" in r.json()["title"]


def test_intake_tenant_isolation(client, db):
    _owner(client, db, "intake-a")
    _client(client, "Org A Client")
    make_org(db, "intake-b", owner_email="owner@ib.pk", password="PassB12345!")
    client.cookies.clear()
    assert login(client, "intake-b", "owner@ib.pk", "PassB12345!").status_code == 200
    # Org B screening never sees Org A's clients -> no conflict leak.
    body = _lead(client, full_name="X", opposing_party="Org A Client").json()
    assert body["conflict_level"] == "clear"
    # And Org B sees none of Org A's leads.
    assert client.get("/api/v1/intake/leads").json() == [] or all(
        x["full_name"] == "X" for x in client.get("/api/v1/intake/leads").json()
    )
