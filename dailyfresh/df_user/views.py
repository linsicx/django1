#coding=utf-8
from django.shortcuts import render,redirect
#加个点表示当前页面的models
from .models import *
from hashlib import sha1
from django.http import JsonResponse,HttpResponseRedirect

# Create your views here.
def register(request):
    return render(request,'df_user/register.html')

def register_handle(request):
    #接收输入
    post=request.POST
    uname=post.get('user_name')
    upwd=post.get('pwd')
    upwd2=post.get('cpwd')
    uemail=post.get('email')
    #验证密码是否两次一样,c错误就重定向返回
    if upwd!=upwd2:
        return redirect('/user/register')
    #密码加密,够钱shal对象
    s1=sha1()
    #加密
    s1.update(upwd.encode("utf8"))
    #通过方法拿到加密的结果
    upwd3=s1.hexdigest()
    #引入模型类,模型类和数据库交互存储数据
    user=UserInfo()
    user.uname=uname
    user.upwd=upwd3
    user.uemail=uemail
    user.save()
    #模型类里剩余的不谢,在后面加上default='',这时候也不用重新迁移,
    return redirect('/user/login/')

def login(request):
    uname=request.COOKIES.get('uname','')
    #uname用于自动填充,login视图函数里上下文给了error_name,防止这里js识别为(==1)
    context={'title':'用户登录','error_name':0,'error_pwd':0,'uname':uname}
    return render(request,'df_user/login.html',context)

def register_exist(request):
    uname = request.GET.get('uname')
    count = UserInfo.objects.filter(uname=uname).count()
    return JsonResponse({'count':count})

def login_handle(request):
    post=request.POST
    uname=post.get('username')
    upwd=post.get('pwd')
    #jizhu标签选中了value为一,默认选中,选中jizhu键有值并且jizhu才会被提交
    # 能接收到记住就用jizhu,没有就用0
    jizhu=post.get('jizhu',0)
    #根据用户名查询对象,用filter查不到会返回[]列表,get会抛异常
    users=UserInfo.objects.filter(uname=uname)
    if len(users)==1:
        s1=sha1()
        s1.update(upwd.encode("utf8"))
        if s1.hexdigest()==users[0].upwd:
            red = HttpResponseRedirect('/user/info')
            if jizhu!=0:
                red.set_cookie('uname',uname)
            else:
                red.set_cookie('uname','',max_age=-1)
            #登陆成功就存储,方便以后查询读取
            request.session['user_id']=users[0].id
            request.session['user_name']=uname
            #不直接用redirect转向是因为这样没有办法设置cookies,
            # HttpResponseRedirect继承于httpresponse,cookies在后者里面
            return red
        else:
            #这里的uname 和upwd能保证用户写好账号后点击提交,如果错了,用户栏之前写的账号不会消失,在login的input表单里
            context = {'title':'用户登录','error_name':0,'error_pwd':1,'uname':uname,'upwd':upwd}
            #路径规则默认找到templates,但是现在templates下有df_user文件夹
            return render(request,'df_user/login.html',context)
    else:
        context = {'title':'用户登录','error_name':1,'error_pwd':0,'uname':uname,'upwd':upwd}
        return render(request,'df_user/login.html',context)

def info(request):
    user_email=UserInfo.objects.get(id=request.session['user_id']).uemail
    context={'title':'用户中心',
             'user_email':user_email,
             'user_name':request.session['user_name']}
    return render(request,'df_user/user_center_info.html',context)

def order(request):
    #return HttpResponseRedirect('df_user/user_center_order.html')
    return render(request,'df_user/user_center_order.html')

def site(request):
    user = UserInfo.objects.get(id=request.session['user_id'])
    if request.method=='POST':
        post=request.POST
        user.ushou=post.get('ushou')
        user.uaddress = post.get('uaddress')
        user.uyoubain = post.get('uyoubian')
        user.uphone = post.get('uphone')
        user.save()
    context={'title':'用户中心','user':user}
    return render(request,'df_user/user_center_site.html',context)
