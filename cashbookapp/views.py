from pickle import TRUE
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CashbookForm, CommentForm, HashtagForm
import requests
from django.utils import timezone
from .models import Cashbook, Comment,  Hashtag
from django.contrib.auth.forms import AuthenticationForm
from account.models import CustomUser
from django.contrib.auth import authenticate
import json
from django.http import HttpResponse
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required

# Create your views here.

def main(request):
    return render(request, 'main.html')

def write(request, cashbook = None):
    if request.method == 'POST':
        form = CashbookForm(request.POST, request.FILES, instance=cashbook)
        if form.is_valid():
            cashbook = form.save(commit=False)
            cashbook.pub_date = timezone.now()
            cashbook.save()
            form.save_m2m()
            return redirect('main')

        else:
            context = {
                'form':form,
            }
            return render(request, 'write.html', context)
    else:
        form = CashbookForm(instance= cashbook)
        return render(request, 'write.html', {'form':form})
             
def read(request):
    sort = request.GET.get('sort', '')
    if sort == 'date':
        cashbooks = Cashbook.objects.all().order_by('-pub_date')
    else:
        cashbooks = Cashbook.objects.all().order_by('-like_count')
    return render(request, 'read.html', {'cashbooks':cashbooks, 'sort':sort})

@login_required
def detail(request, id):
    cashbooks = get_object_or_404(Cashbook, id=id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit = False)
            comment.cashbook_id = cashbooks
            comment.comment_writer = request.user
            comment.text = form.cleaned_data['text']
            comment.save()
            id=id
            return redirect('detail', id)
    else:
        form = CommentForm
        return render(request, 'detail.html', {'cashbooks':cashbooks, 'form':form})

def edit(request, id):
    cashbooks = get_object_or_404(Cashbook, id=id)
    if request.method == "POST":
        form = CashbookForm(request.POST, instance=cashbooks)
        if form.is_valid():
            form.save(commit=False)
            form.save()
            return redirect('read')

    else:
        form = CashbookForm(instance=cashbooks)
        return render(request, 'edit.html', {'form':form, 'cashbooks':cashbooks})

def delete(request, id):
    cashbooks = get_object_or_404(Cashbook, id=id)
    cashbooks.delete()
    return redirect('read')

def update_comment(request, id, com_id):
    post = get_object_or_404(Cashbook, id=id)
    comment = get_object_or_404(Comment, id=com_id)
    form = CommentForm(instance=comment)
    if request.method == "POST":
        update_form = CommentForm(request.POST, instance = comment)
        if update_form.is_valid():
            update_form.save()
            return redirect('detail', id)
    return render(request, 'update_comment.html', {'form':form, 'post':post, 'comment':comment})

def delete_comment(request, post_id, com_id):
    mycom = Comment.objects.get(id=com_id)
    mycom.delete()
    return redirect('detail', post_id)

def hashtag(request, hashtag = None):
    if request.method == 'POST':
        form = HashtagForm(request.POST, instance = hashtag)
        if form.is_valid():
            hashtag = form.save(commit = False)
            if Hashtag.objects.filter(name=form.cleaned_data['name']):
                form = HashtagForm()
                error_message = '이미 존재하는 해시태그입니다.'
                return render(request, 'hashtag.html', {'form':form, 'error_message':error_message})
            else:
                hashtag.name = form.cleaned_data['name']
                hashtag.save()
            return redirect('read')
    else:
        form = HashtagForm(instance=hashtag)
        return render(request, 'hashtag.html', {'form':form})

def likes(request, id):
    like_b = get_object_or_404(Cashbook, id=id)
    if request.user in like_b.post_like.all():
        like_b.post_like.remove(request.user)
        like_b.like_count -= 1
        like_b.save()
    else:
        like_b.post_like.add(request.user)
        like_b.like_count += 1
        like_b.save()
    return redirect('detail', like_b.id)
