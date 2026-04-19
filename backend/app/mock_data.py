from __future__ import annotations

from datetime import date, timedelta

from . import audit, store
from .domain import assess, run_check, screen
from .utils import utcnow
from .models import (
    Address,
    ApplicantInput,
    Application,
    Decision,
    Document,
    IdDocumentType,
    Status,
)

# --- street seed pool (reused round-robin to keep data varied but compact) ---
_STREETS = [
    "12 Rue de la Paix",
    "221B Baker Street",
    "1600 Pennsylvania Ave",
    "5 Alameda de Hércules",
    "77 Dragon Court",
    "18 Marina Boulevard",
    "9 Knightsbridge Road",
    "44 Prinsengracht",
    "3 Avenida Paulista",
    "28 Shibuya-ku",
]


def _street(idx: int) -> str:
    return _STREETS[idx % len(_STREETS)]


def _build(
    idx: int,
    first: str,
    last: str,
    email: str,
    dob: date,
    nationality: str,
    country: str,
    city: str,
    postal: str,
    id_type: IdDocumentType,
    id_number: str,
    pep: bool = False,
    status: Status = Status.PENDING,
    days_ago: int = 0,
    decision: Decision | None = None,
    with_docs: bool = True,
) -> Application:
    applicant = ApplicantInput(
        first_name=first,
        last_name=last,
        email=email,
        date_of_birth=dob,
        nationality=nationality,
        address=Address(
            line1=_street(idx), city=city, postal_code=postal, country=country
        ),
        id_document_type=id_type,
        id_document_number=id_number,
        politically_exposed=pep,
    )
    created = utcnow() - timedelta(days=days_ago)
    app = Application(
        applicant=applicant,
        status=status,
        created_at=created,
        updated_at=created,
        risk=assess(applicant),
        sanctions=screen(applicant),
        liveness=run_check(email),
        documents=[
            Document(
                type=id_type,
                filename=f"{id_type.value}_{id_number}.jpg",
                size_bytes=128_000,
                ocr_extracted={
                    "full_name": f"{first} {last}",
                    "document_number": id_number,
                    "date_of_birth": dob.isoformat(),
                },
            )
        ]
        if with_docs
        else [],
        decision=decision,
    )
    store.put(app)
    audit.record("system", "application.seeded", app.id, status=status.value)
    if decision:
        audit.record(
            decision.reviewer,
            f"application.{decision.outcome}",
            app.id,
            note=decision.note,
        )
    return app


# --- anchor cases: hand-crafted so the workshop has predictable, interesting files ---
_ANCHORS: list[dict] = [
    dict(
        first="Alice", last="Martin", email="alice.martin@example.com",
        dob=date(1992, 3, 14), nationality="FR", country="FR", city="Paris", postal="75002",
        id_type=IdDocumentType.PASSPORT, id_number="FRA-884421",
        status=Status.APPROVED, days_ago=12,
        decision=Decision(outcome="approved", reviewer="reviewer@kyc.io", note="Clean profile, docs match."),
    ),
    dict(
        first="Bruno", last="Silva", email="bruno.silva@example.com",
        dob=date(1988, 11, 2), nationality="BR", country="BR", city="Sao Paulo", postal="01310",
        id_type=IdDocumentType.NATIONAL_ID, id_number="BRA-77120",
        status=Status.IN_REVIEW, days_ago=3,
    ),
    dict(
        first="Chen", last="Wei", email="chen.wei@example.com",
        dob=date(1979, 6, 9), nationality="CN", country="CN", city="Shanghai", postal="200000",
        id_type=IdDocumentType.PASSPORT, id_number="CHN-300012",
        status=Status.IN_REVIEW, days_ago=1,
    ),
    dict(
        first="Dmitri", last="Ivanov", email="dmitri.ivanov@example.com",
        dob=date(1985, 1, 22), nationality="RU", country="RU", city="Moscow", postal="101000",
        id_type=IdDocumentType.PASSPORT, id_number="RUS-445120",
        pep=True, status=Status.IN_REVIEW, days_ago=2,
    ),
    dict(
        first="Emma", last="Johnson", email="emma.johnson@example.com",
        dob=date(2000, 7, 30), nationality="US", country="US", city="Austin", postal="73301",
        id_type=IdDocumentType.DRIVER_LICENSE, id_number="US-TX-9981122",
        status=Status.APPROVED, days_ago=20,
        decision=Decision(outcome="approved", reviewer="reviewer@kyc.io", note="Standard low-risk file."),
    ),
    dict(
        first="Farah", last="Nasser", email="farah.nasser@example.com",
        dob=date(1994, 9, 18), nationality="LB", country="LB", city="Beirut", postal="1107",
        id_type=IdDocumentType.NATIONAL_ID, id_number="LBN-88411",
        status=Status.PENDING, days_ago=0,
    ),
    dict(
        first="Giulia", last="Rossi", email="giulia.rossi@example.com",
        dob=date(1990, 2, 5), nationality="IT", country="IT", city="Milan", postal="20100",
        id_type=IdDocumentType.PASSPORT, id_number="ITA-554120",
        status=Status.PENDING, days_ago=0,
    ),
    dict(
        first="Hassan", last="Karimi", email="hassan.karimi@example.com",
        dob=date(1982, 12, 11), nationality="IR", country="IR", city="Tehran", postal="11369",
        id_type=IdDocumentType.PASSPORT, id_number="IRN-772015",
        status=Status.REJECTED, days_ago=8,
        decision=Decision(outcome="rejected", reviewer="reviewer@kyc.io", note="High-risk jurisdiction, unable to verify source of funds."),
    ),
    dict(
        first="Ines", last="Dupont", email="ines.dupont@example.com",
        dob=date(1975, 5, 27), nationality="FR", country="FR", city="Lyon", postal="69002",
        id_type=IdDocumentType.NATIONAL_ID, id_number="FRA-CNI-448120",
        pep=True, status=Status.IN_REVIEW, days_ago=5,
    ),
    dict(
        first="Jiro", last="Tanaka", email="jiro.tanaka@example.com",
        dob=date(1996, 8, 3), nationality="JP", country="JP", city="Tokyo", postal="100-0001",
        id_type=IdDocumentType.PASSPORT, id_number="JPN-990021",
        status=Status.APPROVED, days_ago=30,
        decision=Decision(outcome="approved", reviewer="reviewer@kyc.io", note="Auto-approved after clean screening."),
    ),
    # name collision with the fake OFAC watchlist entry "Ivan Volkov" — triggers a sanctions hit
    dict(
        first="Ivan", last="Volkov", email="ivan.volkov@example.com",
        dob=date(1970, 4, 18), nationality="RU", country="RU", city="Saint Petersburg", postal="190000",
        id_type=IdDocumentType.PASSPORT, id_number="RUS-112233",
        status=Status.IN_REVIEW, days_ago=4,
    ),
    # partial name overlap with "Maria Delacroix" on the EU mock list
    dict(
        first="Maria", last="Delacroix", email="maria.delacroix@example.com",
        dob=date(1986, 9, 9), nationality="BE", country="BE", city="Brussels", postal="1000",
        id_type=IdDocumentType.NATIONAL_ID, id_number="BEL-551022",
        status=Status.PENDING, days_ago=1,
    ),
]

# --- bulk profiles to reach 50. (first, last, nationality, country, city, postal, year, month, day, status_key) ---
# status_key: "p" = pending, "r" = in_review, "a" = approved, "x" = rejected
_BULK: list[tuple] = [
    ("Liam", "O'Connor", "IE", "IE", "Dublin", "D01", 1991, 6, 12, "p"),
    ("Sophia", "Papadopoulos", "GR", "GR", "Athens", "10431", 1989, 3, 28, "r"),
    ("Noah", "Andersen", "DK", "DK", "Copenhagen", "1050", 1984, 10, 4, "a"),
    ("Olivia", "Kowalski", "PL", "PL", "Warsaw", "00-001", 1993, 12, 15, "p"),
    ("Mateo", "Garcia", "ES", "ES", "Madrid", "28013", 1987, 5, 21, "a"),
    ("Amara", "Okeke", "NG", "NG", "Lagos", "100001", 1990, 7, 7, "r"),
    ("Yuki", "Sato", "JP", "JP", "Osaka", "530-0001", 1998, 1, 19, "p"),
    ("Nikolai", "Petrov", "RU", "RU", "Kazan", "420000", 1983, 2, 11, "r"),
    ("Aisha", "Khan", "PK", "PK", "Karachi", "74200", 1992, 4, 24, "r"),
    ("Diego", "Fernandez", "AR", "AR", "Buenos Aires", "C1002", 1985, 8, 8, "a"),
    ("Freya", "Lindqvist", "SE", "SE", "Stockholm", "111 20", 1994, 11, 2, "p"),
    ("Omar", "Haddad", "SY", "SY", "Damascus", "A001", 1981, 3, 30, "x"),
    ("Priya", "Sharma", "IN", "IN", "Mumbai", "400001", 1996, 9, 14, "a"),
    ("Lucas", "Mendes", "BR", "BR", "Rio de Janeiro", "20040", 1988, 6, 1, "r"),
    ("Hannah", "Schmidt", "DE", "DE", "Berlin", "10115", 1990, 2, 18, "a"),
    ("Ravi", "Patel", "IN", "IN", "Bengaluru", "560001", 1997, 10, 27, "p"),
    ("Isabella", "Conti", "IT", "IT", "Rome", "00184", 2003, 4, 4, "p"),  # young adult
    ("Henry", "Walker", "GB", "GB", "London", "EC1A", 1957, 5, 19, "a"),  # senior low-risk
    ("Zara", "Mahmoud", "EG", "EG", "Cairo", "11511", 1991, 7, 17, "r"),
    ("Pedro", "Alvarez", "CL", "CL", "Santiago", "8320000", 1986, 12, 23, "a"),
    ("Mei", "Zhang", "CN", "CN", "Beijing", "100000", 1993, 8, 11, "r"),
    ("Joon", "Park", "KR", "KR", "Seoul", "04524", 1995, 1, 6, "p"),
    ("Leila", "Hosseini", "IR", "IR", "Isfahan", "81469", 1989, 6, 25, "x"),  # high-risk country
    ("Thabo", "Nkosi", "ZA", "ZA", "Johannesburg", "2001", 1984, 3, 9, "a"),
    ("Elena", "Vasquez", "VE", "VE", "Caracas", "1010", 1988, 11, 11, "r"),  # high-risk country
    ("Carlos", "Moreno", "MX", "MX", "Mexico City", "06000", 1992, 2, 22, "p"),
    ("Ingrid", "Hansen", "NO", "NO", "Oslo", "0150", 1987, 7, 13, "a"),
    ("Vincent", "Lefevre", "FR", "FR", "Marseille", "13001", 1999, 5, 16, "p"),
    ("Helena", "Dubois", "FR", "FR", "Bordeaux", "33000", 1982, 9, 3, "r"),
    ("Aleksander", "Nowak", "PL", "PL", "Krakow", "30-001", 1990, 4, 29, "a"),
    ("Yara", "Bouchard", "CA", "CA", "Montreal", "H2X", 1996, 10, 10, "p"),
    ("Kofi", "Mensah", "GH", "GH", "Accra", "GA-001", 1985, 12, 2, "r"),
    ("Tomas", "Svoboda", "CZ", "CZ", "Prague", "110 00", 1991, 6, 6, "a"),
    ("Natasha", "Morozova", "RU", "RU", "Novosibirsk", "630000", 1983, 2, 28, "r"),
    ("Arjun", "Iyer", "IN", "IN", "Chennai", "600001", 1998, 8, 21, "p"),
    ("Beatriz", "Oliveira", "PT", "PT", "Lisbon", "1100-585", 1990, 1, 9, "a"),
    ("Kai", "Ng", "SG", "SG", "Singapore", "018956", 1989, 3, 17, "a"),
    ("Lina", "Al-Farsi", "AE", "AE", "Dubai", "00000", 1993, 11, 26, "r"),
    ("Oskar", "Virtanen", "FI", "FI", "Helsinki", "00100", 1986, 5, 2, "p"),
    ("Anh", "Nguyen", "VN", "VN", "Hanoi", "100000", 1995, 9, 30, "a"),
]

_STATUS_MAP = {
    "p": Status.PENDING,
    "r": Status.IN_REVIEW,
    "a": Status.APPROVED,
    "x": Status.REJECTED,
}


def _decision_for(status: Status, first: str, last: str) -> Decision | None:
    if status == Status.APPROVED:
        return Decision(outcome="approved", reviewer="reviewer@kyc.io", note=f"{first} {last}: documents consistent, risk acceptable.")
    if status == Status.REJECTED:
        return Decision(outcome="rejected", reviewer="reviewer@kyc.io", note=f"{first} {last}: unable to satisfy enhanced due diligence.")
    return None


# --- extra volume pool: (first, last, nationality, country, city, postal) ---
# DOB and status are derived deterministically from the index in seed() below,
# keeping the tuples compact while still producing a varied dataset.
_EXTRA: list[tuple[str, str, str, str, str, str]] = [
    ("Aleksei", "Sokolov", "RU", "RU", "Saint Petersburg", "190000"),
    ("Viktor", "Melnyk", "UA", "UA", "Kyiv", "01001"),
    ("Katarzyna", "Wisniewska", "PL", "PL", "Gdansk", "80-001"),
    ("Jaroslav", "Novak", "CZ", "CZ", "Brno", "602 00"),
    ("Zuzana", "Horvath", "SK", "SK", "Bratislava", "811 01"),
    ("Anna", "Kiraly", "HU", "HU", "Budapest", "1011"),
    ("Aleksandar", "Jovanovic", "RS", "RS", "Belgrade", "11000"),
    ("Iryna", "Shevchenko", "UA", "UA", "Lviv", "79000"),
    ("Bogdan", "Ionescu", "RO", "RO", "Bucharest", "010101"),
    ("Sebastian", "Weber", "DE", "DE", "Hamburg", "20095"),
    ("Klara", "Bauer", "DE", "DE", "Munich", "80331"),
    ("Finn", "Larsen", "DK", "DK", "Aarhus", "8000"),
    ("Astrid", "Berg", "NO", "NO", "Bergen", "5003"),
    ("Maja", "Lindgren", "SE", "SE", "Gothenburg", "411 01"),
    ("Jonas", "Koskinen", "FI", "FI", "Tampere", "33100"),
    ("Matthias", "Vandenberg", "NL", "NL", "Amsterdam", "1012"),
    ("Eva", "Janssen", "NL", "NL", "Rotterdam", "3011"),
    ("Thomas", "Laurent", "FR", "FR", "Nice", "06000"),
    ("Camille", "Moreau", "FR", "FR", "Toulouse", "31000"),
    ("Chloe", "Robert", "FR", "FR", "Nantes", "44000"),
    ("Paolo", "Bianchi", "IT", "IT", "Turin", "10100"),
    ("Martina", "Ricci", "IT", "IT", "Naples", "80100"),
    ("Javier", "Romero", "ES", "ES", "Barcelona", "08001"),
    ("Lucia", "Navarro", "ES", "ES", "Seville", "41001"),
    ("Diogo", "Santos", "PT", "PT", "Porto", "4000-001"),
    ("Catarina", "Sousa", "PT", "PT", "Faro", "8000-001"),
    ("Fiona", "Byrne", "IE", "IE", "Cork", "T12"),
    ("Edward", "Bennett", "GB", "GB", "Manchester", "M1 1AE"),
    ("Charlotte", "Hughes", "GB", "GB", "Edinburgh", "EH1 1YZ"),
    ("Michael", "Brown", "US", "US", "New York", "10001"),
    ("Jessica", "Davis", "US", "US", "Los Angeles", "90001"),
    ("Christopher", "Wilson", "US", "US", "Chicago", "60601"),
    ("Ashley", "Miller", "US", "US", "Houston", "77001"),
    ("Matthew", "Jones", "US", "US", "Phoenix", "85001"),
    ("Amanda", "Anderson", "US", "US", "Philadelphia", "19101"),
    ("Ethan", "Tremblay", "CA", "CA", "Toronto", "M5H"),
    ("Logan", "Roy", "CA", "CA", "Vancouver", "V6B"),
    ("Juan", "Hernandez", "MX", "MX", "Guadalajara", "44100"),
    ("Valeria", "Lopez", "MX", "MX", "Monterrey", "64000"),
    ("Santiago", "Vargas", "CO", "CO", "Bogota", "110111"),
    ("Camila", "Gonzalez", "CO", "CO", "Medellin", "050001"),
    ("Renata", "Ferreira", "BR", "BR", "Salvador", "40010"),
    ("Felipe", "Souza", "BR", "BR", "Brasilia", "70000"),
    ("Sebastian", "Reyes", "CL", "CL", "Valparaiso", "2340000"),
    ("Adaeze", "Chukwu", "NG", "NG", "Abuja", "900001"),
    ("Tunde", "Adewale", "NG", "NG", "Ibadan", "200001"),
    ("Fatima", "Diallo", "SN", "SN", "Dakar", "10200"),
    ("Kwame", "Boateng", "GH", "GH", "Kumasi", "00233"),
    ("Mandla", "Dlamini", "ZA", "ZA", "Cape Town", "8001"),
    ("Yusuf", "Arslan", "TR", "TR", "Istanbul", "34000"),
    ("Elif", "Demir", "TR", "TR", "Ankara", "06000"),
    ("Noor", "Al-Rashid", "SA", "SA", "Riyadh", "11564"),
    ("Ahmed", "Zaki", "EG", "EG", "Alexandria", "21500"),
    ("Karim", "Saleh", "JO", "JO", "Amman", "11118"),
    ("Satoshi", "Yamamoto", "JP", "JP", "Kyoto", "600-8001"),
    ("Haruka", "Watanabe", "JP", "JP", "Sapporo", "060-0001"),
    ("Hyun", "Lee", "KR", "KR", "Busan", "48001"),
    ("Wei", "Liu", "CN", "CN", "Guangzhou", "510000"),
    ("Xiaolong", "Wu", "CN", "CN", "Shenzhen", "518000"),
    ("Rahul", "Gupta", "IN", "IN", "Kolkata", "700001"),
    ("Kavya", "Reddy", "IN", "IN", "Hyderabad", "500001"),
    ("Siti", "Nurhaliza", "MY", "MY", "Kuala Lumpur", "50000"),
    ("Linh", "Pham", "VN", "VN", "Ho Chi Minh City", "700000"),
    ("Thida", "Aung", "MM", "MM", "Yangon", "11181"),  # MM high-risk country
    ("Somchai", "Phan", "TH", "TH", "Bangkok", "10100"),
    ("Reza", "Ahmadi", "IR", "IR", "Shiraz", "71300"),  # IR high-risk country
    ("Jack", "Williams", "AU", "AU", "Sydney", "2000"),
    ("Charlotte", "Lee", "AU", "AU", "Melbourne", "3000"),
    ("Lachlan", "Murphy", "NZ", "NZ", "Auckland", "1010"),
    ("Olga", "Kuznetsova", "RU", "RU", "Kaliningrad", "236000"),
]

# Deterministic rotation of statuses for the _EXTRA pool. Roughly tuned so the
# final dataset has a realistic mix (approved-heavy with a healthy queue).
_EXTRA_STATUS_CYCLE = ["a", "p", "r", "a", "a", "r", "p", "a", "x", "a"]


def seed() -> None:
    if len(store.all_apps()) > 0:
        return

    for i, cfg in enumerate(_ANCHORS):
        _build(idx=i, **cfg)

    # Bulk entries — deterministic but varied: rotate doc types and offsets
    doc_types = [IdDocumentType.PASSPORT, IdDocumentType.NATIONAL_ID, IdDocumentType.DRIVER_LICENSE]
    for j, row in enumerate(_BULK):
        (first, last, nat, country, city, postal, yr, mo, dy, skey) = row
        status = _STATUS_MAP[skey]
        id_type = doc_types[j % 3]
        _build(
            idx=len(_ANCHORS) + j,
            first=first,
            last=last,
            email=f"{first.lower().replace(' ', '')}.{last.lower().replace(chr(39), '').replace(' ', '')}@example.com",
            dob=date(yr, mo, dy),
            nationality=nat,
            country=country,
            city=city,
            postal=postal,
            id_type=id_type,
            id_number=f"{nat}-{100000 + j * 137}",
            status=status,
            days_ago=(j % 25),
            decision=_decision_for(status, first, last),
        )

    # Extra pool — derive DOB + status from index for a compact, reproducible dataset.
    base = len(_ANCHORS) + len(_BULK)
    for k, (first, last, nat, country, city, postal) in enumerate(_EXTRA):
        year = 1960 + (k * 7 + 3) % 46  # 1960..2005 range
        month = (k * 5) % 12 + 1
        day = (k * 11) % 28 + 1
        status = _STATUS_MAP[_EXTRA_STATUS_CYCLE[k % len(_EXTRA_STATUS_CYCLE)]]
        id_type = doc_types[(k + 1) % 3]
        _build(
            idx=base + k,
            first=first,
            last=last,
            email=f"{first.lower().replace(' ', '')}.{last.lower().replace(chr(39), '').replace('-', '').replace(' ', '')}@example.com",
            dob=date(year, month, day),
            nationality=nat,
            country=country,
            city=city,
            postal=postal,
            id_type=id_type,
            id_number=f"{nat}-{200000 + k * 173}",
            status=status,
            days_ago=(k * 3) % 60,  # spread across ~2 months for the sparkline
            decision=_decision_for(status, first, last),
        )
