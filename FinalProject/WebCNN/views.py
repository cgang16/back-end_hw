import PIL.Image
import random, os
import urllib.request
from .detection import prediction
from .models import User, Image
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator, EmptyPage
from FinalProject.settings import IMAGE_ROOT
from .forms import UserForm, LogonForm, ImageForm, UrlForm, TimeForm


def MakePassword(pw):
    return make_password(pw, None, "pbkdf2_sha256")


def CheckPassword(opw, epw):
    return check_password(opw, epw)


def CreatePath():
    while True:
        filename = str(random.randint(0, 10000000000)) + '.jpg'
        filepath = os.path.join(IMAGE_ROOT, filename)
        if not os.path.exists(filepath):
            return [filename, filepath]


def ISJPG(filename):
    try:
        i = PIL.Image.open(filename)
        return i.format == 'JPEG'
    except IOError:
        return False


def Logon(request):
    # 已经登陆则直接进入到/index/界面
    if request.session.get('is_login', None):
        return redirect('/index/')
    # 如果是post解析请求，不是则返回logon界面
    if request.method == 'POST':
        logon_form = LogonForm(request.POST)
        message = '请检查输入'
        if logon_form.is_valid():
            username = logon_form.cleaned_data['username']
            password1 = logon_form.cleaned_data['password1']
            password2 = logon_form.cleaned_data['password2']
            if password1 != password2:
                message = '两次输入的密码不同，请重新输入'
                return render(request, 'logon.html', locals())
            else:
                ulst = User.objects.filter(username=username)
                if ulst:
                    message = '用户名已被使用，请重新选择'
                    return render(request, 'logon.html', locals())
                else:
                    user = User.objects.create(username=username, password=MakePassword(password1))
                    return redirect('/login/')
    return render(request, 'logon.html', {'logon_form': LogonForm()})


def Login(request):
    # 已经登陆则直接跳转至/index界面
    if request.session.get('is_login', None):
        return redirect('/index/')
    # 判断请求类型是否为POST，否则返回登陆界面
    if request.method == 'POST':
        login_form = UserForm(request.POST)
        message = '请检查输入'
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = User.objects.get(username=username)
                if CheckPassword(password, user.password):
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.username
                    return redirect('/index/')
                else:
                    message = '密码错误!'
            except:
                message = '用户不存在'
        return render(request, 'login.html', locals())
    return render(request, 'login.html', {'login_form': UserForm()})


def Logout(request):
    # 如果没有登陆，自然没有登出，跳转到登陆界面
    if not request.session.get('is_login', None):
        return redirect('/login/')
    request.session.flush()
    return redirect('/login/')


def Index(request):
    return Upload(request)


def History(request):
    Time_form = TimeForm()
    if request.session.get('is_login', None):
        id = request.session.get('user_id', None)
        user = User.objects.filter(id=id)
        if user:
            images = user[0].image_set.all()
            # 没有任何操作记录的情况
            if not images:
                message = '您似乎没有进行过任何操作！'
                return render(request, 'history.html', locals())
            paginator = Paginator(images, 4)
            page = request.GET.get('page', 1)
            try:
                page_obj = paginator.page(int(page))
            except ValueError or TypeError:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)
            return render(request, 'history.html', locals())
    return render(request, 'history.html', locals())


# 处理两种方式上传的图片，并且返回结果
def Upload(request):
    # 已经登陆&&POST请求
    if request.session.get('is_login', None) and request.method == 'POST':
        id = request.session.get('user_id', None)
        user = User.objects.filter(id=id)
        message = '用户不存在，意外错误！'
        # 用户确实存在
        if user:
            if 'imagebtn' in request.POST:
                Upload_form = ImageForm(request.POST, request.FILES)
                message = '表单数据不合法！'
                # 上传文件是合法的
                if Upload_form.is_valid():
                    path = Upload_form.cleaned_data['image']
                    # 上传文件要求为jpg,jpeg
                    if path.name.endswith('.jpg') or path.name.endswith('.jpeg'):
                        image_upload = Image(user=user[0], path=path, filename=user[0].username)
                        image_upload.save()
                        message = '上传并处理成功！'
                        write_path = image_upload.filename + str(image_upload.id) + '.jpg'
                        prediction(image_upload.path.url, write_path)
                        Upload_form = ImageForm()
                        Url_form = UrlForm()
                        return render(request, 'index.html', locals())
                    else:
                        message = '图片格式错误，要求.jpg/.jpeg!'
            elif 'urlbtn' in request.POST:
                Url_form = UrlForm(request.POST)
                message = '表单数据不合法'
                if Url_form.is_valid():
                    url = Url_form.cleaned_data['url']
                    message = '要求url以.jpg/.jpeg结尾！'
                    if url.endswith('.jpg') or url.endswith('.jpeg'):
                        [filename, filepath] = CreatePath()
                        try:
                            urllib.request.urlretrieve(url, filepath)
                        except:
                            message = 'url无效或者下载失败！'
                            if os.path.exists(filepath):
                                os.remove(filepath)
                        else:
                            if os.path.exists(filepath) and not ISJPG(filepath):
                                message = '不合法的url！'
                                os.remove(filepath)
                            else:
                                message = '下载并处理成功'
                                image_upload = Image(user=user[0], filename=user[0].username)
                                image_upload.path = 'origin/' + filename
                                image_upload.save()
                                write_path = image_upload.filename + str(image_upload.id) + '.jpg'
                                prediction(image_upload.path.url, write_path)
                                Url_form = UrlForm()
                                Upload_form = ImageForm()
                                return render(request, 'index.html', locals())
            else:
                message = '未知提交表单，意外错误！'
        return render(request, 'index.html', {'message': message, 'Upload_form': ImageForm(), 'Url_form': UrlForm()})
    return render(request, 'index.html', {'Upload_form': ImageForm(), 'Url_form': UrlForm()})


# 批量删除记录
def Delete(request):
    # 检测登陆状态以及请求方式
    page_id = None
    if request.session.get('is_login', None) and request.method == "POST":
        cbox_list = request.POST.getlist('del_box')
        page_id = request.POST.get('page_id', None)
        user_id = request.session.get('user_id', None)
        # 检测user_id、record_id、page_id是否存在
        if user_id and cbox_list and page_id:
            # 尝试获得图像对象
            try:
                record_id_list = list(map(int, cbox_list))
                user = User.objects.get(id=user_id)
                image_list = []
                for x in record_id_list:
                    image_list.append(user.image_set.get(id=x))
            except:
                pass
            else:
                for x in image_list:
                    x.delete()
                return redirect('/history/?page=' + str(page_id))
    # 特殊情况转到history页面，对于未登录状态，页面有自己的处理
    # 对于非post请求，会得到历史记录界面
    # 对于找不到usr_id、record_id、page_id以及没有获得图像的情况下
    # 还是回到历史界面
    return redirect('/history/?page=' + str(page_id))


# 将搜索结果显示在同一页
def Search(request):
    page_id = None
    if request.session.get('is_login', None) and request.method == 'POST':
        user_id = request.session.get('user_id', None)
        page_id = request.POST.get('page_id', None)
        if user_id:
            time_form = TimeForm(request.POST)
            message = '没有找到符合的记录！'
            if time_form.is_valid():
                start_time = time_form.cleaned_data['start_time']
                end_time = time_form.cleaned_data['end_time']
                if end_time >= start_time:
                    user = User.objects.get(id=user_id)
                    image_list = user.image_set.all()
                    results = []
                    for x in image_list:
                        if start_time <= x.createtime <= end_time:
                            results.append(x)
                    if results:
                        message = '以下为搜索结果!'
                        paginator = Paginator(results, len(results))
                        page_obj = paginator.page(1)
                        Time_form = TimeForm()
                        return render(request, 'history.html', locals())
            Time_form = TimeForm()
            return render(request, 'history.html', locals())
    return redirect('/history/?page=' + str(page_id))


def PageNotFound(request, exception):
    return render(request, '404.html', status=404)


def ServerError(request):
    return render(request, '500.html', status=500)
