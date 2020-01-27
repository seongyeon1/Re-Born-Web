from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View, ListView, DetailView, FormView, CreateView
from .models import Notice
from users.decorators import login_message_required
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from .forms import NoticeWriteForm
from users.models import User
import mimetypes
from mimetypes import guess_type
import os
import re
from django.http import HttpResponse, HttpResponseRedirect, Http404
from urllib.parse import quote
import urllib
from django.conf import settings


class NoticeListView(ListView):
    model = Notice
    paginate_by = 10
    template_name = 'notice/notice_list.html'  #DEFAULT : <app_label>/<model_name>_list.html
    context_object_name = 'notice_list'        #DEFAULT : <app_label>_list

    def get_queryset(self):
        search_keyword = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', '')
        notice_list = Notice.objects.order_by('-id')

        if search_keyword :
            if search_type == 'all':
                notice_list = notice_list.filter(Q (title__icontains=search_keyword) | Q (content__icontains=search_keyword) | Q (writer__user_id__icontains=search_keyword))
            elif search_type == 'title_content':
                notice_list = notice_list.filter(Q (title__icontains=search_keyword) | Q (content__icontains=search_keyword))
            elif search_type == 'title':
                notice_list = notice_list.filter(title__icontains=search_keyword)    
            elif search_type == 'content':
                notice_list = notice_list.filter(content__icontains=search_keyword)    
            elif search_type == 'writer':
                notice_list = notice_list.filter(writer__user_id__icontains=search_keyword)
        if notice_list :
            return notice_list
        else:
            messages.error(self.request, '일치하는 검색 결과가 없습니다.')
            notice_list = Notice.objects.order_by('-id')
            return notice_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        page_numbers_range = 5
        max_index = len(paginator.page_range)

        page = self.request.GET.get('page')
        current_page = int(page) if page else 1

        start_index = int((current_page - 1) / page_numbers_range) * page_numbers_range
        end_index = start_index + page_numbers_range
        if end_index >= max_index:
            end_index = max_index

        page_range = paginator.page_range[start_index:end_index]
        context['page_range'] = page_range

        search_keyword = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', '')
        context['q'] = search_keyword
        context['type'] = search_type

        return context


@login_message_required
def notice_detail_view(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    # notice = Notice.objects.filter(id=pk)
    session_cookie = request.session['user_id']
    cookie_name = F'notice_hits:{session_cookie}'

    if request.user == notice.writer:
        notice_auth = True
    else:
        notice_auth = False

    context = {
        'notice': notice,
        'notice_auth': notice_auth,
    }
    response = render(request, 'notice/notice_detail.html', context)

    if request.COOKIES.get(cookie_name) is not None:
        cookies = request.COOKIES.get(cookie_name)
        cookies_list = cookies.split('|')
        if str(pk) not in cookies_list:
            response.set_cookie(cookie_name, cookies + f'|{pk}', expires=None)
            # notice.update(hits=F('hits') + 1)
            notice.hits += 1
            notice.save()
            return response
    else:
        response.set_cookie(cookie_name, pk, expires=None)
        # notice.update(hits=F('hits') + 1)
        notice.hits += 1
        notice.save()
        return response
    return render(request, 'notice/notice_detail.html', context)


@login_message_required
def notice_write_view(request):
    if request.method == "POST":
        form = NoticeWriteForm(request.POST, request.FILES)
        user = request.session['user_id']
        user_id = User.objects.get(user_id = user)
        if form.is_valid():
            # notice = Notice(
            #     title = form.data.get('title'),
            #     content = form.data.get('content'),
            #     writer = user_id,
            #     files = request.FILES['files'],
            # )
            notice = form.save(commit = False)
            notice.writer = user_id
            notice.save()
            return redirect('notice:notice_list')
    else:
        form = NoticeWriteForm()
    return render(request, "notice/notice_write.html", {'form': form})


@login_message_required
def notice_edit_view(request, pk):
    notice = Notice.objects.get(id=pk)
    if request.method == "POST" and notice.writer == request.user:
        form = NoticeWriteForm(request.POST, request.FILES, instance=notice)
        if form.is_valid():
            form.save()
            messages.success(request, "수정되었습니다.")
            return redirect('/notice/'+str(pk))
    else:
        notice = Notice.objects.get(id=pk)
        if notice.writer == request.user:
            form = NoticeWriteForm(instance=notice)
            return render(request, "notice/notice_write.html", {'form': form})
        else:
            messages.error(request, "본인 게시글이 아닙니다.")
            return redirect('/notice/'+str(pk))


@login_message_required
def notice_delete_view(request, pk):
    notice = Notice.objects.get(id=pk)
    
    if notice.writer == request.user:
        notice.delete()
        messages.success(request, "삭제되었습니다.")
        return redirect('/notice/')
    else:
        messages.error(request, "본인 게시글이 아닙니다.")
        return redirect('/notice/'+str(pk))



def notice_download_view(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    url = notice.files.url[1:]
    file_url = urllib.parse.unquote(url)
    
    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            quote_file_url = urllib.parse.quote(file_url.encode('utf-8'))
            response = HttpResponse(fh.read(), content_type=mimetypes.guess_type(file_url)[0])
            response['Content-Disposition'] = 'attachment;filename*=UTF-8\'\'%s' % quote_file_url[29:]
            return response
        raise Http404
