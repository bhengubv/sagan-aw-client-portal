from datetime import date

from app.extensions import db
from app.models import Tenant, Client, Person


def test_age_is_computed_from_dob(app):
    with app.app_context():
        t = Tenant(name="T")
        db.session.add(t); db.session.flush()
        c = Client(tenant_id=t.id, display_name="H")
        db.session.add(c); db.session.flush()
        p = Person(client_id=c.id, role="C1", name="X", dob=date(2000, 1, 1))
        db.session.add(p); db.session.commit()
        today = date.today()
        expected = today.year - 2000 - ((today.month, today.day) < (1, 1))
        assert p.age == expected


def test_age_none_without_dob(app):
    with app.app_context():
        t = Tenant(name="T"); db.session.add(t); db.session.flush()
        c = Client(tenant_id=t.id, display_name="H"); db.session.add(c); db.session.flush()
        p = Person(client_id=c.id, role="C1", name="X"); db.session.add(p); db.session.commit()
        assert p.age is None


def test_tenant_cascade_deletes_clients(app):
    with app.app_context():
        t = Tenant(name="T"); db.session.add(t); db.session.flush()
        db.session.add(Client(tenant_id=t.id, display_name="H")); db.session.commit()
        assert Client.query.count() == 1
        db.session.delete(t); db.session.commit()
        assert Client.query.count() == 0


def test_last_report_is_none_initially(seeded, app):
    with app.app_context():
        c = db.session.get(Client, seeded["client_id"])
        assert c.last_report is None
