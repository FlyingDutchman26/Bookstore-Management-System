"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')git
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app01.views import book, admin, account, user, bill, order

urlpatterns = [
    # path('admin/', admin.site.urls),
    # 书籍信息管理
    path('book/list/', book.book_list),
    path('book/add/', book.book_add),
    path('book/<int:nid>/edit/', book.book_edit),
    path('book/<int:nid>/delete/', book.book_delete),
    path('book/<int:nid>/sale/', book.book_sale),

    # 管理员用户管理
    path('admin/list/', admin.admin_list),
    path('admin/add/', admin.admin_add),
    path('admin/<int:nid>/edit/', admin.admin_edit),
    path('admin/<int:nid>/delete/', admin.admin_delete),
    path('admin/<int:nid>/reset/', admin.admin_reset),

    # 账户: 登录与注销
    path('', book.book_list),
    path('login/', account.login),
    path('logout/', account.logout),

    # 用户编辑自身信息
    path('user/<int:nid>/edit/', user.user_edit),

    # 账单管理
    path('bill/list/', bill.bill_list),
    path('bill/add/', bill.bill_add),
    path('bill/<int:nid>/delete/', bill.bill_delete),
    path('bill/history/', bill.financial_history),

    # 图书进货: 订单管理
    path('order/list/', order.order_list),  # 列表
    path('order/add/', order.order_add),  # 添加
    path('order/<int:nid>/pay/', order.order_pay),  # 支付
    path('order/<int:nid>/cancel/', order.order_cancel),  # 取消订单: 针对未付款书籍
    path('order/<int:nid>/delete/', order.order_delete),  # 删除订单：针对已付款书籍

]
