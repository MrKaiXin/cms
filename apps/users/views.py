from django.http.response import HttpResponse


# Create your views here.
def testview(request):
    print("112244")
    return HttpResponse('这是测试')
