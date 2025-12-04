# riders/views.py
from decimal import Decimal
from datetime import date, timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import Q, Sum
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date

from .forms import RiderSearchForm, TicketForm
from .models import AdaRiderQ, AdaTicketPurchasesT, TicketAudit


def home(request):
    form = RiderSearchForm(initial={'by': 'name'})
    return render(request, 'home.html', {'form': form})


def search_riders(request):
    form = RiderSearchForm(request.GET or None)
    riders = []
    if form.is_valid():
        by = form.cleaned_data['by']
        if by == 'name':
            first = (form.cleaned_data.get('first_name') or '').strip()
            last = (form.cleaned_data.get('last_name') or '').strip()
            q = Q()
            if first:
                q &= Q(fname__icontains=first)
            if last:
                q &= Q(lname__icontains=last)
            riders = AdaRiderQ.objects.filter(q).order_by('lname', 'fname')[:200]
        else:
            ada_id = (form.cleaned_data.get('ada_id') or '').strip()
            riders = AdaRiderQ.objects.filter(adaid__icontains=ada_id).order_by('lname', 'fname')[:200]
    return render(request, 'search_results.html', {'form': form, 'riders': riders})


def rider_detail(request, pk):
    rider = get_object_or_404(AdaRiderQ, pk=pk)

    ticket_q = Q()
    if rider.adaid:
        ticket_q = Q(fname=rider.fname, lname=rider.lname) | Q(NEW_ID=rider.NEW_ID)
    else:
        ticket_q = Q(fname=rider.fname, lname=rider.lname)

    tickets = AdaTicketPurchasesT.objects.filter(ticket_q).order_by('-purdate')[:50]
    total_amount = AdaTicketPurchasesT.objects.filter(ticket_q).aggregate(total=Sum('puramt'))['total'] or 0
    total_qty = AdaTicketPurchasesT.objects.filter(ticket_q).aggregate(total=Sum('bkqty'))['total'] or 0

    return render(request, 'rider_detail.html', {
        'rider': rider,
        'tickets': tickets,
        'total': total_amount,
        'total_qty': total_qty,
    })


def rider_create(request):
    return render(request, 'rider_edit.html', {'form': None})


def rider_save(request, pk):
    return redirect('rider_detail', pk=pk)


def rider_inactive(request, pk):
    rider = get_object_or_404(AdaRiderQ, pk=pk)
    rider.Inactive = True
    rider.save(update_fields=['Inactive'])
    return redirect('rider_detail', pk=pk)


def finance_transmittal(request):
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')

    today = date.today()
    default_start = today - timedelta(days=30)

    start = parse_date(start_str) if start_str else default_start
    end = parse_date(end_str) if end_str else today

    if start and end and start > end:
        start, end = end, start

    qs = AdaTicketPurchasesT.objects.all()
    if start:
        qs = qs.filter(purdate__date__gte=start)
    if end:
        qs = qs.filter(purdate__date__lte=end)

    rows = (
        qs.annotate(day=TruncDate('purdate'))
        .values('day')
        .annotate(total_amount=Sum('puramt'), total_qty=Sum('bkqty'))
        .order_by('day')
    )

    purchases = list(
        qs.order_by('purdate').values('TransID', 'purdate', 'bkqty', 'puramt', 'paytype', 'chknum', 'fname', 'lname')
    )

    trans_ids = [p['TransID'] for p in purchases if p['TransID'] is not None]
    audit_by_trans = {}
    if trans_ids:
        audit_qs = TicketAudit.objects.filter(trans_id__in=trans_ids).order_by('-created_at')
        audit_by_trans = {a.trans_id: a for a in audit_qs}

    adaid_map = {}
    rider_ids = [a.rider_new_id for a in audit_by_trans.values() if a.rider_new_id]
    if rider_ids:
        adaid_map = {rid: adaid for rid, adaid in AdaRiderQ.objects.filter(NEW_ID__in=rider_ids).values_list('NEW_ID', 'adaid')}

    entry_rows = []
    for p in purchases:
        a = audit_by_trans.get(p['TransID'])
        ada_id = None
        if a and a.rider_new_id:
            ada_id = adaid_map.get(a.rider_new_id)
        if not ada_id:
            ada_id = AdaRiderQ.objects.filter(fname=p['fname'], lname=p['lname']).values_list('adaid', flat=True).first()
        entry_rows.append({
            'paytype': p['paytype'],
            'purchase_date': p['purdate'],
            'adaid': ada_id,
            'name': f"{(p['lname'] or '').strip()}, {(p['fname'] or '').strip()}",
            'qty': p['bkqty'] or 0,
            'amount': p['puramt'] or 0,
            'chknum': p['chknum'] or '',
        })

    grand = qs.aggregate(grand_total_amount=Sum('puramt'), grand_total_qty=Sum('bkqty'))
    grand_total_amount = grand.get('grand_total_amount') or 0
    grand_total_qty = grand.get('grand_total_qty') or 0

    if request.GET.get('format') == 'pdf':
        try:
            from django.template.loader import get_template
            from xhtml2pdf import pisa

            logo_uri = None
            logo_data_uri = None
            logo_path = None
            riders_logo = settings.BASE_DIR / 'riders' / 'static' / 'tc-eh-town-seal.jpeg'
            permits_logo = settings.BASE_DIR / 'permits' / 'static' / 'town_banner.png'
            if riders_logo.exists():
                logo_uri = f"file:///{riders_logo.as_posix()}"
                logo_path = str(riders_logo)
                try:
                    import base64
                    import io

                    try:
                        from PIL import Image

                        img = Image.open(riders_logo)
                        buf = io.BytesIO()
                        img.save(buf, format='PNG')
                        logo_data_uri = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode('utf-8')
                    except Exception:
                        with open(riders_logo, 'rb') as f:
                            logo_data_uri = 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode('utf-8')
                except Exception:
                    logo_data_uri = None
            elif permits_logo.exists():
                logo_uri = f"file:///{permits_logo.as_posix()}"
                logo_path = str(permits_logo)

            template = get_template('finance_transmittal_pdf.html')
            html = template.render({
                'entries': entry_rows,
                'start': start,
                'end': end,
                'grand_total_amount': grand_total_amount,
                'grand_total_qty': grand_total_qty,
                'logo_uri': logo_uri,
                'logo_data_uri': logo_data_uri,
                'logo_path': logo_path,
            })
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="finance-transmittal.pdf"'
            pisa.CreatePDF(src=html, dest=response)
            return response
        except Exception as e:
            return HttpResponse(f"PDF generation failed: {e}", status=500)

    return render(request, 'finance_transmittal.html', {
        'rows': rows,
        'entries': entry_rows,
        'start': start,
        'end': end,
        'grand_total_amount': grand_total_amount,
        'grand_total_qty': grand_total_qty,
    })


UNIT_PRICE = Decimal('28.00')


def ticket_create(request, pk):
    rider = get_object_or_404(AdaRiderQ, pk=pk)

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)

            t.fname = rider.fname
            t.lname = rider.lname
            if not t.purdate:
                t.purdate = timezone.now()

            qty = t.bkqty or 0
            t.puramt = (Decimal(qty) * UNIT_PRICE).quantize(Decimal('0.01'))

            with transaction.atomic():
                last_purchase = AdaTicketPurchasesT.objects.select_for_update().order_by('-TransID').first()
                last_trans_id = last_purchase.TransID if last_purchase and last_purchase.TransID else 0
                t.TransID = last_trans_id + 1
                t.save()

                TicketAudit.objects.create(
                    trans_id=t.TransID,
                    rider_new_id=rider.NEW_ID,
                    fname=t.fname,
                    lname=t.lname,
                    created_by=(request.user.get_username() if request.user.is_authenticated else 'anonymous'),
                    deptenter=t.deptenter,
                    paytype=t.paytype,
                    chknum=t.chknum,
                    amount=t.puramt or 0,
                    qty=t.bkqty or 0,
                    notes=getattr(t, 'Notes', None),
                )
            return redirect('receipt_view', trans_id=t.TransID)
    else:
        initial = {'purdate': timezone.now().replace(microsecond=0), 'bkqty': 1}
        form = TicketForm(initial=initial)

    return render(request, 'ticket_form.html', {'form': form, 'rider': rider})


def receipt_view(request, trans_id: int):
    purchase = get_object_or_404(AdaTicketPurchasesT, TransID=trans_id)
    audit = TicketAudit.objects.filter(trans_id=trans_id).order_by('-created_at').first()
    rider = AdaRiderQ.objects.filter(fname=purchase.fname, lname=purchase.lname).first()
    context = {'purchase': purchase, 'audit': audit, 'rider': rider}

    if request.GET.get('format') == 'pdf':
        try:
            from django.template.loader import get_template
            from xhtml2pdf import pisa

            template = get_template('receipt_pdf.html')
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="receipt-{trans_id}.pdf"'
            pisa.CreatePDF(src=html, dest=response)
            return response
        except Exception as e:
            return HttpResponse(f"PDF generation failed: {e}", status=500)

    return render(request, 'receipt.html', context)


def finance_detail_report(request):
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')

    start = parse_date(start_str) if start_str else None
    end = parse_date(end_str) if end_str else None
    if not start and not end:
        today = date.today()
        start = today - timedelta(days=30)
        end = today
    if start and end and start > end:
        start, end = end, start

    qs = TicketAudit.objects.all()
    purchases_for_range = AdaTicketPurchasesT.objects.all()
    if start:
        purchases_for_range = purchases_for_range.filter(purdate__date__gte=start)
    if end:
        purchases_for_range = purchases_for_range.filter(purdate__date__lte=end)
    purchase_ids_qs = purchases_for_range.exclude(TransID__isnull=True).values_list('TransID', flat=True)
    qs = qs.filter(trans_id__in=purchase_ids_qs)

    purchase_dates = dict(
        purchases_for_range.exclude(TransID__isnull=True)
        .values_list('TransID', 'purdate')
    )
    rider_ids = list(qs.exclude(rider_new_id=None).values_list('rider_new_id', flat=True).distinct())
    adaid_map = {}
    if rider_ids:
        for rid, adaid in AdaRiderQ.objects.filter(NEW_ID__in=rider_ids).values_list('NEW_ID', 'adaid'):
            adaid_map[rid] = adaid
    audit_entries = [
        {
            'trans_id': a.trans_id,
            'created_by': a.created_by,
            'deptenter': a.deptenter,
            'qty': a.qty,
            'amount': a.amount,
            'created_at': a.created_at,
            'purchase_date': purchase_dates.get(a.trans_id),
            'adaid': adaid_map.get(a.rider_new_id) or (AdaRiderQ.objects.filter(fname=a.fname, lname=a.lname).values_list('adaid', flat=True).first()),
        }
        for a in qs.order_by('-created_at')
    ]

    audits_by_trans = {a['trans_id']: a for a in audit_entries}
    entry_rows = []
    for p in purchases_for_range.order_by('-purdate'):
        a = audits_by_trans.get(p.TransID)
        created_by = a['created_by'] if a else (p.deptenter or 'legacy-import')
        ada_id = (a.get('adaid') if a else None) or (
            AdaRiderQ.objects.filter(fname=p.fname, lname=p.lname).values_list('adaid', flat=True).first()
        )
        entry_rows.append({
            'trans_id': p.TransID,
            'adaid': ada_id,
            'rider_name': f"{(p.lname or '').strip()}, {(p.fname or '').strip()}",
            'user': created_by,
            'dept': p.deptenter,
            'qty': p.bkqty or 0,
            'amount': p.puramt or 0,
            'purchase_date': p.purdate,
        })

    return render(request, 'finance_detail.html', {
        'entry_rows': entry_rows,
        'start': start,
        'end': end,
    })
