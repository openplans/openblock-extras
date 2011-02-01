# -*- coding: utf-8 -*-
#
#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of everyblock
#
#   everyblock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   everyblock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with everyblock.  If not, see <http://www.gnu.org/licenses/>.
#

from ebdata.blobs.create_seeds import create_rss_seed
from ebdata.blobs.models import Seed
from ebpub.db.models import Schema, SchemaField, NewsItem, Lookup, DataUpdate
from django import forms
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response


class SchemaLookupsForm(forms.Form):
    def __init__(self, lookup_ids, *args, **kwargs):
        super(SchemaLookupsForm, self).__init__(*args, **kwargs)
        for look_id in lookup_ids:
            self.fields['%s-name' % look_id] = forms.CharField(widget=forms.TextInput(attrs={'size': 50}))
            self.fields['%s-name' % look_id].lookup_obj = Lookup.objects.get(id=look_id)
            self.fields['%s-description' % look_id] = forms.CharField(required=False, widget=forms.Textarea())

class BlobSeedForm(forms.Form):
    rss_url = forms.CharField(max_length=512, widget=forms.TextInput(attrs={'size': 80}))
    site_url = forms.CharField(max_length=512, widget=forms.TextInput(attrs={'size': 80}))
    rss_full_entry = forms.BooleanField(required=False)
    pretty_name = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'size': 80}))
    guess_article_text = forms.BooleanField(required=False)
    strip_noise = forms.BooleanField(required=False)

# Returns the username for a given request, taking into account our proxy
# (which sets HTTP_X_REMOTE_USER).
request_username = lambda request: request.META.get('REMOTE_USER', '') or request.META.get('HTTP_X_REMOTE_USER', '')

user_is_staff = lambda username: settings.DEBUG

def schema_list(request):
    s_list = []
    for s in Schema.objects.order_by('name'):
        s_list.append({
            'schema': s,
            'lookups': s.schemafield_set.filter(is_lookup=True).order_by('pretty_name_plural'),
        })
    return render_to_response('admin/schema_list.html', {'schema_list': s_list})

def set_staff_cookie(request):
    r = HttpResponseRedirect('../')
    r.set_cookie(settings.STAFF_COOKIE_NAME, settings.STAFF_COOKIE_VALUE)
    return r


def edit_schema_lookups(request, schema_id, schema_field_id):
    s = get_object_or_404(Schema, id=schema_id)
    sf = get_object_or_404(SchemaField, id=schema_field_id, schema__id=s.id, is_lookup=True)
    lookups = Lookup.objects.filter(schema_field__id=sf.id).order_by('name')
    lookup_ids = [look.id for look in lookups]
    if request.method == 'POST':
        form = SchemaLookupsForm(lookup_ids, request.POST)
        if form.is_valid():
            # Save any lookup values that changed.
            for look in lookups:
                name = request.POST.get('%s-name' % look.id)
                description = request.POST.get('%s-description' % look.id)
                if name is not None and description is not None and (name != look.name or description != look.description):
                    look.name = name
                    look.description = description
                    look.save()
            return HttpResponseRedirect('../../../')
    else:
        initial = {}
        for look in lookups:
            initial['%s-name' % look.id] = look.name
            initial['%s-description' % look.id] = look.description
        form = SchemaLookupsForm(lookup_ids, initial=initial)
    return render_to_response('admin/edit_schema_lookups.html', {'schema': s, 'schema_field': sf, 'form': list(form)})

def schemafield_list(request):
    sf_list = SchemaField.objects.select_related().order_by('db_schema.name', 'display_order')
    return render_to_response('admin/schemafield_list.html', {'schemafield_list': sf_list})

def geocoder_success_rates(request):
    from django.db import connection
    sql = """
        select s.plural_name, count(ni.location) as geocoded, count(*) as total
        from db_newsitem ni
        inner join db_schema s
        on s.id=ni.schema_id
        group by s.plural_name
        order by count(ni.location)::float / count(*)::float;
    """
    cursor = connection.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    schema_list = [{'name': r[0], 'geocoded': r[1], 'total': r[2], 'ratio': float(r[1]) / float(r[2])} for r in results]
    return render_to_response('admin/geocoder_success_rates.html', {'schema_list': schema_list})

def blob_seed_list(request):
    s_list = Seed.objects.order_by('autodetect_locations', 'pretty_name').filter(is_rss_feed=True)
    return render_to_response('admin/blob_seed_list.html', {'seed_list': s_list})

def add_blob_seed(request):
    if request.method == 'POST':
        form = BlobSeedForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            create_rss_seed(cd['rss_url'], cd['site_url'], cd['rss_full_entry'], cd['pretty_name'], cd['guess_article_text'], cd['strip_noise'])
            return HttpResponseRedirect('../')
    else:
        form = BlobSeedForm()
    return render_to_response('admin/add_blob_seed.html', {'form': form})

def scraper_history_list(request):
    schema_ids = [i['schema'] for i in DataUpdate.objects.select_related().order_by('schema__plural_name').distinct().values('schema')]
    s_dict = Schema.objects.in_bulk(schema_ids)
    s_list = [s_dict[i] for i in schema_ids]
    return render_to_response('admin/scraper_history_list.html', {'schema_list': s_list})

def scraper_history_schema(request, slug):
    s = get_object_or_404(Schema, slug=slug)
    du_list = DataUpdate.objects.filter(schema__id=s.id).order_by('schema__name', '-update_start')
    return render_to_response('admin/scraper_history_schema.html', {'schema': s, 'dataupdate_list': du_list})

def newsitem_details(request, news_item_id):
    """
    Shows all of the raw values in a NewsItem for debugging.
    """
    ni = get_object_or_404(NewsItem, pk=news_item_id)
    real_names = [
        'varchar01', 'varchar02', 'varchar03', 'varchar04', 'varchar05',
        'date01', 'date02', 'date03', 'date04', 'date05',
        'time01', 'time02',
        'datetime01', 'datetime02', 'datetime03', 'datetime04',
        'bool01', 'bool02', 'bool03', 'bool04', 'bool05',
        'int01', 'int02', 'int03', 'int04', 'int05', 'int06', 'int07',
        'text01'
    ]
    schema_fields = {}
    for sf in SchemaField.objects.filter(schema=ni.schema):
        schema_fields[sf.real_name] = sf
    attributes = []
    for real_name in real_names:
        schema_field = schema_fields.get(real_name, None)
        attributes.append({
            'real_name': real_name,
            'name': schema_field and schema_field.name or None,
            'raw_value': schema_field and ni.attributes[schema_field.name] or None,
            'schema_field': schema_field,
        })
    return render_to_response('admin/news_item_detail.html', {
        'news_item': ni, 'attributes': attributes
    })
