def address_picker(request):
	term = request.GET.get('term', '')
	results = []
	if term:
		with connection.cursor() as cursor:
			sql = '''
				SELECT TOP 10
					CAST([From] AS nvarchar(20)) + '|' + [Street] + '|' + ISNULL(CAST([Parcel] AS nvarchar(50)),'') AS address_key,
					CAST([From] AS nvarchar(20)) + ' ' + [Street] +
						CASE WHEN [Parcel] IS NOT NULL AND [Parcel] <> '' THEN ' (Parcel: ' + CAST([Parcel] AS nvarchar(50)) + ')' ELSE '' END AS display
				FROM [Access].[dbo].[myassessor]
				WHERE CAST([From] AS nvarchar(20)) LIKE %s OR [Street] LIKE %s
				GROUP BY [From], [Street], [Parcel]
				ORDER BY [Street], [From]
			'''
			like_term = '%' + term + '%'
			cursor.execute(sql, [like_term, like_term])
			results = [{'key': row[0], 'display': row[1]} for row in cursor.fetchall()]
	print(f"[address_picker] term={term} results={results}")
	return JsonResponse(results, safe=False)


from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import render
from .models import Permit

def home(request):
	return render(request, 'permits/home.html')

def autocomplete(request):
	term = request.GET.get('term', '')
	# Search both parcel and contractor fields for suggestions
	qs = Permit.objects.filter(Q(parcel__icontains=term) | Q(contractor__icontains=term)).values_list('parcel', flat=True).distinct()[:10]
	suggestions = list(qs)
	return JsonResponse(suggestions, safe=False)

from django.db import connection

def history(request):
	query = request.GET.get('q', '')
	permits = []
	address = ''
	if query:
		address = query
		with connection.cursor() as cursor:
			sql = '''
				SELECT
					p.[Permit_ ID]       AS permit_id,
					p.[Permit_date]      AS permit_date,
					p.[Permit Type]      AS permit_type,
					p.[Estimate Cost]    AS estimate_cost,
					p.[Am_Paid]          AS amount_paid,
					p.[Desc]             AS permit_desc,
					p.[Expr3]            AS owner_and_mailing,
					p.[Street]           AS street,
					p.[From]             AS house_number,
					p.[Parcel]           AS parcel,
					p.[vcs]              AS vcs,
					CAST(p.[From] AS nvarchar(20)) + '|' + p.[Street] + '|' + ISNULL(CAST(p.[Parcel] AS nvarchar(50)),'') AS address_key
				FROM [Access].[dbo].[myassessor] p
				WHERE CAST(p.[From] AS nvarchar(20)) + '|' + p.[Street] + '|' + ISNULL(CAST(p.[Parcel] AS nvarchar(50)),'') = %s
				ORDER BY p.[Permit_date] DESC, p.[Permit_ ID] DESC;
			'''
			cursor.execute(sql, [query])
			columns = [col[0] for col in cursor.description]
			permits = [dict(zip(columns, row)) for row in cursor.fetchall()]
	return render(request, 'permits/history.html', {'permits': permits, 'address': address})
