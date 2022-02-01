import re
from django import http
from django.http.response import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from random import randint

from . import util


def index(request):
    list = []
    for l in util.list_entries():
        if len(l) > 12:
            l = l[0:3]+'...'
        list.append(l)

    return render(request, "encyclopedia/index.html", {
        "entries": list,
        "names": util.list_entries()
    })


def entry(request, entry):
    entry = entry.lower()

    lowerEntrys = [x.lower() for x in util.list_entries()]
    if entry not in lowerEntrys:
        return HttpResponseNotFound()

    mkentry = util.markup(util.get_entry(entry))

    return render(request, "encyclopedia/entry.html", {
        'entry': mkentry,
        'name': entry
    })


def search(request):
    entry = request.GET['q'].lower()
    listentrys = util.list_entries()
    lowerEntrys = [x.lower() for x in listentrys]

    if entry not in lowerEntrys:
        matching = [s.capitalize() for s in lowerEntrys if entry in s]
        return render(request, "encyclopedia/index.html", {
            "entries": matching
        })

    return redirect('entry', entry=entry)


def create(request):
    if request.method == "POST":
        title = request.POST['title']
        if title == '' or request.POST['content'] == '':
            return render(request, "encyclopedia/error.html", {
                'message': "Fields can not be blank"
            })
        elif title.lower() in [x.lower() for x in util.list_entries()]:
            return render(request, "encyclopedia/error.html", {
                'message': "This entry already exist."
            })

        util.save_entry(request.POST['title'].capitalize(), request.POST['content'])
        print('POSTED!')
        return redirect('entry', entry=request.POST['title'])

    return render(request, "encyclopedia/entryform.html", {
        'header': "Create new Page!",
        'code': 'create'
    })


def edit(request):
    if request.method == 'POST':
        return render(request, "encyclopedia/entryform.html", {
            'header': "Edit " + request.POST['name'],
            'code': 'edit',
            'title': request.POST['name'].capitalize(),
            'content': util.get_entry(request.POST['name'])
        })
    return HttpResponse("Error")


def save(request):
    if request.method == 'POST':
        entry = request.POST['title']
        print(entry.lower())
        util.save_entry(entry, request.POST['content'])
        return redirect('entry', entry=entry.lower())

    return HttpResponse("Todo")


def randomentry(request):
    randEntry = randint(0, len(util.list_entries())-1)

    return redirect('entry', entry=util.list_entries()[randEntry].lower())
