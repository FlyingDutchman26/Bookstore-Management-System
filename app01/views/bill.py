from django.shortcuts import render, redirect
from django.core.validators import RegexValidator, ValidationError
from app01 import models
from django import forms
from django.db.models import Q
from app01.utils.pagination import Pagination
from app01.utils.form import *
import datetime


def bill_list(request):
    queryset = models.Bill.objects.all().order_by('-timestamp')
    page_object = Pagination(request, queryset, page_size=8)
    balance_obj = models.SystemBalance.objects.first()
    if balance_obj:
        balance = balance_obj.balance
    else:
        balance = '--'
    context = {
        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html(),  # 生成页码
        'balance': balance,
    }
    return render(request, 'bill_list.html', context)


def bill_add(request):
    if request.method == 'GET':
        form = BillModelForm()
        return render(request, 'change.html', {'form': form, 'title': '新建账单'})
    else:  # POST
        form = BillModelForm(data=request.POST)
        balance_object = models.SystemBalance.objects.first()
        if not balance_object:
            models.SystemBalance.objects.create(balance=0)
            balance_object = models.SystemBalance.objects.first()
        if form.is_valid():
            # 如果有效
            # 时间会自动加，需要附加上用户名
            info_dict = request.session.get('info')  # 获取当前用户名
            admin = models.Admin.objects.get(username=info_dict['username'])
            bill = form.save(commit=False)
            bill.username = admin  # 外键必须关联到一个对象!
            bill.save()
            balance_object.balance += form.cleaned_data['amount']
            balance_object.save()
            return redirect('/bill/list/')
        else:
            # 错误信息附加
            return render(request, 'change.html', {'form': form, 'title': '新建账单'})


def bill_delete(request, nid):
    models.Bill.objects.filter(id=nid).delete()
    return redirect('/bill/list/')


def parse_period(period):
    """
    用于将period中的日期分割为起、止时间, 截止时间默认为当前
    """
    if '~' in period:
        start_date, end_date = period.split('~')
    else:
        start_date = period
        end_date = datetime.date.today()
    start_date = datetime.datetime.strptime(str(start_date), '%Y-%m-%d')  # 参数需为字符串
    end_date = datetime.datetime.strptime(str(end_date), '%Y-%m-%d')
    return start_date, end_date


def financial_history(request):
    """
    period: 时间段,如'2020-01'(至今), '2020-05-01~2020-05-31'
    income_expense: 收入/支出,1表示收入,2表示支出,0表示总收益
    """
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    income_expense = request.GET.get('income_expense')
    if not (start_date and end_date and income_expense):
        return render(request, 'financial_history.html')
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    start_date = datetime.datetime.combine(start_date, datetime.time.min)
    end_date = datetime.datetime.combine(end_date, datetime.time.max)
    queryset=models.Bill.objects.filter(timestamp__range=(start_date,end_date))
    total_amount=0
    type_display='总收益'
    if int(income_expense)==1:
        queryset=queryset.filter(type=1)
        type_display='收入'
    if int(income_expense)==2:
        queryset=queryset.filter(type=2)
        type_display='支出'
    for bill in queryset:
        total_amount+=bill.amount
    context={
        'bills':queryset,
        'total_amount':total_amount,
        'period':start_date.strftime('%Y-%m-%d')+'~'+end_date.strftime('%Y-%m-%d'),
        'income_expense':type_display
    }
    return render(request, 'financial_history.html', context)
