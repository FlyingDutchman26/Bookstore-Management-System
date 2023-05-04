from django.shortcuts import render, redirect
from django.core.validators import RegexValidator, ValidationError
from app01 import models
from django import forms
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login, logout,update_session_auth_hash
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
# Create your views here.
class BookInfoModelForm(forms.ModelForm):
    isbn = forms.CharField(label="ISBN", max_length=13,
                           validators=[RegexValidator(
                               r'^(?:ISBN(?:-10)?:? )?(?=[0-9X]{10}$|(?=(?:[0-9]+[- ]){3})[- 0-9X]{13}$)[0-9]{1,5}[- ]?[0-9]+[- ]?[0-9]+[- ]?[0-9X]$',
                               'ISBN格式错误'), ])

    class Meta:
        model = models.BookInfo
        fields = ['isbn', 'name', 'press', 'author', 'retail_price', 'amount']  # 可以自己指定 也可以__all__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # 调用父类的构造函数
        for name, field in self.fields.items():  # 这个方法可以减少工作量，不需要一个一个加widget
            field.widget.attrs = {'class': 'form-control', 'placeholder': field.label}
            # if name == '': 特殊指定
            #     continue

    # 校验方法2：钩子函数 去重 不允许添加重复的isbn号书目
    def clean_isbn(self):
        txt_isbn = self.cleaned_data['isbn']
        exist = models.BookInfo.objects.filter(isbn=txt_isbn).exists()
        if not exist:
            return txt_isbn
        else:
            raise ValidationError('该ISBN对应书目信息已存在')


class BookEditInfoModelForm(forms.ModelForm):
    isbn = forms.CharField(disabled=True, label="ISBN")  # 不允许修改isbn号
    amount = forms.IntegerField(disabled=True, label='库存数量')  # 创建后即不允许修改库存数量，只能通过进出货修改

    class Meta:
        model = models.BookInfo
        fields = ['isbn', 'name', 'press', 'author', 'retail_price', 'amount']  # 可以自己指定 也可以__all__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # 调用父类的构造函数
        for name, field in self.fields.items():  # 这个方法可以减少工作量，不需要一个一个加widget
            field.widget.attrs = {'class': 'form-control', 'placeholder': field.label}
            # if name == '': 特殊指定
            #     continue

def book_list(request):
    search_data = request.GET.get('query', '')
    if search_data:
        queryset = models.BookInfo.objects.filter(
            Q(isbn__contains=search_data) | Q(name__contains=search_data) | Q(author__contains=search_data)) \
            .order_by('name')
    else:
        queryset = models.BookInfo.objects.all().order_by('name')

    return render(request, 'book_list.html', {'queryset': queryset, 'search_data': search_data})

def book_add(request):
    '''
    这个函数用户初始化书籍信息，可以定义库存
    我希望初始化时候定义的库存可以加入到进出货账单上去，便于最后记录
    :param request:
    :return:
    '''
    if request.method == 'GET':
        form = BookInfoModelForm()
        return render(request, 'book_add.html', {'form': form})
    else:
        form = BookInfoModelForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('/book/list/')
        else:
            return render(request, 'book_add.html', {'form': form})

def book_edit(request, nid):
    row_object = models.BookInfo.objects.filter(id=nid).first()
    if request.method == 'GET':
        form = BookEditInfoModelForm(instance=row_object)
        # 使用instance属性，这种方式可以实现填写默认值，相当于把value属性全部设置。还有一个功能是能找到更新的位置
        return render(request, 'book_edit.html', {'form': form})
    else:
        form = BookEditInfoModelForm(data=request.POST, instance=row_object)
        if form.is_valid():
            form.save()
            return redirect('/book/list/')
        else:
            return render(request, 'book_edit.html', {'form': form})

def book_delete(request, nid):
    models.BookInfo.objects.filter(id=nid).delete()
    return redirect('/book/list/')

def book_sale(request, nid):
    pass

def user_login(request): 
    # if request.user.is_authenticated:
    #     return redirect('/book/list/')
    # else:
        if request.method == 'POST':
            user_usernmae=request.POST.get('username')
            user_password=request.POST.get('password')
            # 在Django的authenticate方法中,输入的原始密码会使用PBKDF2算法与相应的salt进行加密运算,如果结果与存储的密文一致,则密码验证成功,否则失败
            user=authenticate(username=user_usernmae,password=user_password)
            if user is not None:
                login(request,user)
                messages.success(request,'登录成功')
                return redirect('/book/list/')
            else:
                messages.error(request,'用户名或密码错误')
                return render(request, 'user_login.html', {'error': '用户名或密码错误!'}) 
        return render(request,'user_login.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('/user_login/')

@login_required
def profile(request):
    '''用来查看用户信息，区分了普通管理员和超级管理员'''
    if request.user.is_superuser:
        users = models.UserInfo.objects.all()
    else:
        users = models.UserInfo.objects.filter(pk=request.user.pk)
    context = {
        'users': users
    }
    return render(request, 'profile.html', context) 

@login_required
def create_user(request):
    # Only superuser can create a new admin
    if not request.user.is_superuser:
        messages.error(request, '无权限操作')
        return redirect('/book_list/')

    if request.method == 'POST':
        username = request.POST.get('username')
        email=request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        realname=request.POST.get('realname')
        age=request.POST.get('age')
        gender=request.POST.get('gender')

        if password != confirm_password:
            messages.error(request, '两次密码输入不匹配')
            return redirect('/create_user/')
        if models.UserInfo.objects.filter(username=username).exists():
            messages.error(request, '用户名已被使用')
            return redirect('/create_user/')
        user=models.UserInfo.objects.create_user(username=username,password=password,email=email)
        # user = models.UserInfo.objects.create(username=username, password=md5(password.encode('utf-8')).hexdigest(),
        #                                   realname=realname,age=age,gender=gender)
        user.realname=realname
        user.age=age
        user.gender=gender
        user.is_staff=True
        user.save()
        messages.success(request, '新用户创建成功')
        return redirect('/profile/')

    return render(request, 'create_user.html')

class UserForm(forms.ModelForm):
    class Meta:
        model = models.UserInfo
        fields = ['username','password','realname','gender','age']

class CommonUserForm(UserForm):
    def __init__(self, user_pk, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_pk = user_pk

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
    

@login_required
def edit_user(request,user_pk):
    user = models.UserInfo.objects.filter(pk=user_pk).first()
    form_class = CommonUserForm
    if request.method == 'POST':
        form = form_class(request.user.id, request.POST, instance=user)
        if form.is_valid() :
            form.save()
            return redirect('/profile/')
    else:
        form = form_class(request.user.id, instance=user)

    context = {'form': form}
    return render(request, 'edit_user.html', context)

@login_required
def edit_password(request,user_pk):
    user=models.UserInfo.objects.filter(pk=user_pk).first()
    if request.method=='POST':
        password_form=PasswordChangeForm(user,request.POST)
        if password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form.user)   #根据用户的新密码重新计算session中保存的hash,刷新session
            return redirect('/profile/')
    else:
        password_form=PasswordChangeForm(user,request.POST)
    context = {'password_form': password_form}
    return render(request, 'edit_password.html', context)

@login_required
def delete_user(request, user_pk):
    models.UserInfo.objects.filter(id=user_pk).delete()
    return redirect('/profile/')