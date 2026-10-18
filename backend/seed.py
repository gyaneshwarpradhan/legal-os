"""Database seeding script with realistic litigation demo data."""
import sys
from datetime import date, datetime, timedelta
import uuid

from app.core.database import Base, SessionLocal, engine
from app.core.security import get_password_hash
from app.models import (
    AuditLog,
    Claim,
    Deadline,
    Event,
    Expert,
    Matter,
    MatterMember,
    Organization,
    Party,
    Task,
    User,
    Witness,
)


def seed():
    print("Creating database tables if not present...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if already seeded
        org = db.query(Organization).filter(Organization.slug == "demo-law-firm").first()
        if org:
            print("Database already seeded with demo organization. Skipping.")
            return

        print("Seeding organization...")
        org = Organization(
            name="Apex Litigation Group, LLP",
            slug="demo-law-firm",
            is_active=True,
        )
        db.add(org)
        db.flush()

        print("Seeding users...")
        admin = User(
            organization_id=org.id,
            email="admin@legalos.local",
            hashed_password=get_password_hash("admin123"),
            full_name="Sarah Jenkins, Esq. (Managing Partner)",
            role="admin",
            is_active=True,
            is_verified=True,
        )
        attorney = User(
            organization_id=org.id,
            email="attorney@legalos.local",
            hashed_password=get_password_hash("attorney123"),
            full_name="David Chen, Esq. (Senior Trial Attorney)",
            role="attorney",
            is_active=True,
            is_verified=True,
        )
        paralegal = User(
            organization_id=org.id,
            email="paralegal@legalos.local",
            hashed_password=get_password_hash("paralegal123"),
            full_name="Elena Rostova (Senior Paralegal)",
            role="paralegal",
            is_active=True,
            is_verified=True,
        )
        db.add_all([admin, attorney, paralegal])
        db.flush()

        print("Seeding flagship matter: Johnson v. Metro Properties...")
        matter = Matter(
            organization_id=org.id,
            case_number="2024-CV-08912",
            title="Johnson v. Metro Properties, LLC",
            description="Premises liability and wrongful catastrophic injury litigation arising from the structural collapse of a second-story exterior deck at a commercial complex during a corporate event. Severe spinal and orthopedic injuries.",
            matter_type="personal_injury",
            status="active",
            date_opened=date(2024, 3, 15),
            court="Superior Court of the State of California, County of Alameda",
            jurisdiction="California State Court",
            judge="Hon. Evelyn R. Marcus",
            created_by_id=attorney.id,
        )
        db.add(matter)
        db.flush()

        print("Assigning matter team members...")
        lead_member = MatterMember(
            matter_id=matter.id,
            user_id=attorney.id,
            role="lead_attorney",
            added_by_id=admin.id,
        )
        paralegal_member = MatterMember(
            matter_id=matter.id,
            user_id=paralegal.id,
            role="paralegal",
            added_by_id=attorney.id,
        )
        db.add_all([lead_member, paralegal_member])
        db.flush()

        print("Seeding parties...")
        p1 = Party(
            matter_id=matter.id,
            name="Marcus Johnson",
            party_type="plaintiff",
            entity_type="individual",
            description="Injured attendee, software executive.",
            contact_info={"represented_by": "Apex Litigation Group, LLP"},
        )
        p2 = Party(
            matter_id=matter.id,
            name="Metro Properties, LLC",
            party_type="defendant",
            entity_type="corporation",
            description="Commercial property owner and lessor of 450 Lakeside Drive complex.",
            contact_info={"counsel": "Morrison, Stern & Vance, LLP"},
        )
        p3 = Party(
            matter_id=matter.id,
            name="Apex Decking & Construction Services, Inc.",
            party_type="third_party",
            entity_type="corporation",
            description="Contractor responsible for 2021 deck retrofitting.",
            contact_info={"counsel": "Garrity & Ross Law Group"},
        )
        db.add_all([p1, p2, p3])

        print("Seeding witnesses & experts...")
        w1 = Witness(
            matter_id=matter.id,
            name="Evelyn Vance",
            witness_type="fact",
            description="Former assistant property manager on site during incident.",
            notes="Observed wood rot warnings reported by tenants in August 2023.",
        )
        w2 = Witness(
            matter_id=matter.id,
            name="Dr. Robert Sterling, M.D.",
            witness_type="expert",
            description="Board-certified orthopedic spinal surgeon, treating physician.",
            notes="Prepared initial surgical evaluation and permanent disability assessment.",
        )
        exp1 = Expert(
            matter_id=matter.id,
            name="Frank Calderon, P.E.",
            specialty="Forensic Structural Engineering",
            organization_name="Calderon Structural Forensics, LLC",
            retained_by="plaintiff",
            notes="Inspected lumber shear failure and non-code compliant joist hangers.",
        )
        db.add_all([w1, w2, exp1])

        print("Seeding claims...")
        c1 = Claim(
            matter_id=matter.id,
            title="Premises Liability & Negligent Maintenance",
            description="Failure to inspect, repair, and maintain commercial premises in a reasonably safe condition despite actual knowledge of joist deterioration.",
            claim_type="premises_liability",
            status="active",
        )
        c2 = Claim(
            matter_id=matter.id,
            title="Gross Negligence & Conscious Disregard",
            description="Willful refusal to remediate red-tagged railing and joist notices issued by municipal code enforcement inspectors in October 2023.",
            claim_type="gross_negligence",
            status="active",
        )
        db.add_all([c1, c2])

        print("Seeding timeline events...")
        e1 = Event(
            matter_id=matter.id,
            title="Catastrophic Deck Collapse Incident",
            description="Exterior commercial deck detached from structural ledger board, dropping 14 feet onto concrete walkway.",
            event_date=datetime(2024, 2, 10, 18, 45),
            event_type="other",
            is_ai_generated=False,
            created_by_id=attorney.id,
        )
        e2 = Event(
            matter_id=matter.id,
            title="Complaint Filed in Alameda Superior Court",
            description="Verified Complaint filed alleging Premises Liability and Negligence.",
            event_date=datetime(2024, 3, 15, 9, 30),
            event_type="filing",
            is_ai_generated=False,
            created_by_id=attorney.id,
        )
        e3 = Event(
            matter_id=matter.id,
            title="Metro Properties Answer & Cross-Complaint",
            description="Defendant answered and filed cross-complaint against Apex Decking for contractual indemnity.",
            event_date=datetime(2024, 4, 22, 14, 0),
            event_type="filing",
            is_ai_generated=False,
            created_by_id=attorney.id,
        )
        db.add_all([e1, e2, e3])

        print("Seeding deadlines...")
        d1 = Deadline(
            matter_id=matter.id,
            title="Close of Fact Discovery",
            description="All written discovery and non-expert depositions must be completed.",
            due_date=datetime(2024, 11, 15, 17, 0),
            deadline_type="discovery",
            status="pending",
            is_high_risk=True,
            created_by_id=attorney.id,
            assigned_to_id=attorney.id,
        )
        d2 = Deadline(
            matter_id=matter.id,
            title="Simultaneous Expert Witness Disclosure",
            description="Exchange of expert designations, CVs, and formal Rule 2034 reports.",
            due_date=datetime(2024, 12, 10, 17, 0),
            deadline_type="court",
            status="pending",
            is_high_risk=True,
            created_by_id=attorney.id,
            assigned_to_id=paralegal.id,
        )
        db.add_all([d1, d2])

        print("Seeding tasks...")
        t1 = Task(
            matter_id=matter.id,
            title="Draft Deposition Outline for Defendant PMK (Property Manager)",
            description="Focus on maintenance work orders from Q3 2023 and tenant complaint emails.",
            priority="urgent",
            status="in_progress",
            assigned_to_id=attorney.id,
            created_by_id=attorney.id,
            due_date=datetime(2024, 10, 25, 17, 0),
        )
        t2 = Task(
            matter_id=matter.id,
            title="Subpoena Municipal Code Inspection Records from Alameda City Clerk",
            description="Obtain certified copies of October 2023 building inspector notices.",
            priority="high",
            status="todo",
            assigned_to_id=paralegal.id,
            created_by_id=attorney.id,
            due_date=datetime(2024, 10, 30, 17, 0),
        )
        print("Seeding documents into matter knowledge base...")
        from app.services.document_service import process_uploaded_document

        doc1_content = (
            "SUPERIOR COURT OF CALIFORNIA, COUNTY OF ALAMEDA\n\n"
            "MARCUS JOHNSON, Plaintiff,\n"
            "v.\n"
            "METRO PROPERTIES, LLC, Defendant.\n"
            "Case No. 2024-CV-08912\n\n"
            "VERIFIED COMPLAINT FOR DAMAGES AND PREMISES LIABILITY\n"
            "JURY TRIAL DEMANDED\n\n"
            "FIRST CAUSE OF ACTION - PREMISES LIABILITY\n"
            "1. Plaintiff Marcus Johnson was an invitee on the commercial premises at 450 Lakeside Drive.\n"
            "2. On February 10, 2024, the second-story exterior viewing deck detached from the ledger board, causing Plaintiff to fall 14 feet.\n"
            "3. Plaintiff suffered catastrophic spinal disc herniations and compound fractures.\n"
            "PRAYER FOR RELIEF\n"
            "Wherefore, Plaintiff demands economic and non-economic damages according to proof at trial."
        )
        process_uploaded_document(
            db=db,
            matter_id=matter.id,
            uploaded_by_id=attorney.id,
            file_name="Verified_Complaint_Johnson.txt",
            file_bytes=doc1_content.encode("utf-8"),
        )

        doc2_content = (
            "SUPERIOR COURT OF CALIFORNIA, COUNTY OF ALAMEDA\n\n"
            "METRO PROPERTIES, LLC, Defendant.\n"
            "ANSWER AND AFFIRMATIVE DEFENSES TO VERIFIED COMPLAINT\n\n"
            "Defendant Metro Properties, LLC answers the unverified allegations of Plaintiff:\n"
            "1. Defendant denies all allegations of negligence, failure to inspect, or reckless maintenance.\n"
            "AFFIRMATIVE DEFENSES\n"
            "FIRST DEFENSE: Comparative fault of third-party contractor Apex Decking Services.\n"
            "SECOND DEFENSE: Lack of actual or constructive notice of latent joist hanger defect."
        )
        process_uploaded_document(
            db=db,
            matter_id=matter.id,
            uploaded_by_id=attorney.id,
            file_name="Defendant_Answer_and_Affirmative_Defenses.txt",
            file_bytes=doc2_content.encode("utf-8"),
        )

        doc3_content = (
            "DEPOSITION OF EVELYN VANCE\n"
            "TAKEN ON JUNE 12, 2024\n"
            "REPORTED BY CA CERTIFIED SHORTHAND REPORTER #11904\n\n"
            "Q: Ms. Vance, when were you first notified by commercial tenants regarding wood rot on the exterior deck?\n"
            "A: In late August 2023. Multiple tenant emails complained that the exterior railing felt loose and water was pooling near the structural ledger.\n"
            "Q: Did you forward those inspection concerns to regional management?\n"
            "A: Yes, I sent an email to the property asset manager on August 28, 2023, recommending an immediate structural engineering review."
        )
        process_uploaded_document(
            db=db,
            matter_id=matter.id,
            uploaded_by_id=attorney.id,
            file_name="Deposition_Excerpt_Evelyn_Vance.txt",
            file_bytes=doc3_content.encode("utf-8"),
        )

        # Audit log for seed creation
        log = AuditLog(
            organization_id=org.id,
            user_id=admin.id,
            action="system_seed_completed",
            details={"matter_title": matter.title, "seeded_at": datetime.utcnow().isoformat()},
        )
        db.add(log)

        db.commit()
        print("Database successfully seeded with realistic litigation data!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed()
