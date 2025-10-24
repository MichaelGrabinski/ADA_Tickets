from datetime import datetime
from django.core.management.base import BaseCommand
from riders.models import AdaTicketPurchasesT, AdaRiderQ, TicketAudit


class Command(BaseCommand):
    help = "Backfill TicketAudit rows from existing ADA_Ticket_Purchases_t entries that lack audit records."

    def add_arguments(self, parser):
        parser.add_argument(
            "--since",
            type=str,
            default=None,
            help="Only backfill purchases on/after this date (YYYY-MM-DD)."
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Don't write changes; just report what would be done.")

    def handle(self, *args, **opts):
        since = opts.get("since")
        dry = opts.get("dry_run")

        qs = AdaTicketPurchasesT.objects.all()
        if since:
            try:
                dt = datetime.strptime(since, "%Y-%m-%d").date()
                qs = qs.filter(purdate__date__gte=dt)
            except Exception:
                self.stderr.write(self.style.ERROR(f"Invalid --since date: {since}"))
                return 1

        # Precompute set of already audited TransIDs to avoid N queries
        existing_trans_ids = set(TicketAudit.objects.values_list('trans_id', flat=True))

        # Filter purchases eligible for backfill
        eligible = qs.exclude(TransID__isnull=True)
        total = eligible.count()
        self.stdout.write(f"Scanning {total} purchase rows…")

        created = 0
        skipped = 0

        for p in eligible.iterator(chunk_size=1000):
            if p.TransID in existing_trans_ids:
                skipped += 1
                continue

            rider = AdaRiderQ.objects.filter(fname=p.fname, lname=p.lname).first()
            if not dry:
                TicketAudit.objects.create(
                    trans_id=p.TransID,
                    rider_new_id=rider.NEW_ID if rider else None,
                    fname=p.fname,
                    lname=p.lname,
                    created_by=p.deptenter or "legacy-import",
                    deptenter=p.deptenter,
                    paytype=p.paytype,
                    chknum=p.chknum,
                    amount=p.puramt or 0,
                    qty=p.bkqty or 0,
                    notes=None,
                )
            created += 1

        # nothing to flush; inserted row-by-row

        self.stdout.write(self.style.SUCCESS(f"Backfill complete. Created: {created}, Skipped: {skipped}"))
        return 0
