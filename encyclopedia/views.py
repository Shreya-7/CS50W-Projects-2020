from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from re import compile, search
from random import choice
from markdown2 import markdown
from . import util

class search_form(forms.Form):
    q = forms.CharField()

class new_entry_form(forms.Form):
    title = forms.CharField()
    content = forms.CharField()

class edit_entry_form(forms.Form):
    content = forms.CharField()

def entry(request, entry_name):
    my_entry = util.get_entry(entry_name)
    # if entry exists, open that page
    if(my_entry):
        return render(request, "encyclopedia/entry.html",{
            "entry": markdown(my_entry),
            "title": entry_name
        })

    #else return error page
    return render(request, "encyclopedia/error.html",{
            "error": "Requested entry does not exist :("
        })


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def search(request):

    form = search_form()
    if(request.method=="POST"):
        form = search_form(request.POST)
    elif(request.method=="GET"):
        form = search_form(request.GET)
        
    if(form.is_valid()):
        query = form.cleaned_data["q"]
        
        entries = util.list_entries()

        #if direct match is found, open the page
        for i in entries:
            if(query.lower()==i.lower()):
                return HttpResponseRedirect(reverse('entry', kwargs={"entry_name": i}))

        #else search for substring match
        results = []
        entry_regex = compile(r'[a-zA-Z]*' + query.lower() + r'[a-zA-Z]*')
        for i in entries:
            if(entry_regex.search(i.lower())):
                results.append(i)

        #if partial matches are present, list results 
        if(results):
            return render(request, "encyclopedia/results.html", {
                "results": results,
                "query": query
            })

        #else return an error page
        return render(request, "encyclopedia/error.html",{
            "error": "No matches :("
        })

def new(request):
    if(request.method=='GET'):
        return render(request, "encyclopedia/new.html")     

    #adding a new entry
    form  = new_entry_form(request.POST)
    if(form.is_valid()):
        title = form.cleaned_data["title"]
        content = form.cleaned_data["content"]

        if('/' in title):
            return render(request, "encyclopedia/new.html", {
                "old_content": content,
                "error": "Title cannot contain '/' :/"
            })

        #if title already exists, show error on the same page with an entry link
        if title.lower() in [x.lower() for x in util.list_entries()]:
            link = "Page with this title already exists. [View](/wiki/"+title+")"
            return render(request, "encyclopedia/new.html", {
                "old_content": content,
                "error": markdown(link)
            })

        #remove redundant entry title in the markdown if present before adding title
        content = util.removeh1(content, title)
        content = "#"+title+"\n\n"+content

        util.save_entry(title, content)

        #open the entry page
        return HttpResponseRedirect(reverse('entry', kwargs={"entry_name": title}))

def edit(request, entry_name):

    #if an edit is submitted
    if(request.method=='POST'):
        form  = edit_entry_form(request.POST)
        if(form.is_valid()):

            #remove redundant entry title in the edited markdown if present before adding title
            content = util.removeh1(form.cleaned_data["content"], entry_name)
            content = "#"+entry_name+"\n\n"+content

            util.save_entry(entry_name, content)

            #open the entry page
            return HttpResponseRedirect(reverse('entry', kwargs={"entry_name": entry_name}))
    #else if the edit page is opened
    else:
        #removing entry title before displaying old markdown
        content = util.removeh1(util.get_entry(entry_name), entry_name)

        #render the edit page with existing markdown content
        return render(request, "encyclopedia/edit.html",{
                "title": entry_name,
                "content": content
            })

def random(request):
    entry = choice(util.list_entries())
    return HttpResponseRedirect(reverse('entry', kwargs={"entry_name": entry}))

