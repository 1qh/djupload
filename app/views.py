from django.shortcuts import redirect, render

from utils.bookmarks import TAB_SIZE, BookmarksExtractor, PdfExtractor

from .forms import FileUploadForm, MultipleChoiceForm


def leading_spaces(s: str) -> int:
    return len(s) - len(s.lstrip())


def upload(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
            path = file.path
            if path.endswith('.pdf'):
                plain = BookmarksExtractor(path)()
            elif path.endswith('.txt'):
                with open(path, 'r') as f:
                    plain = f.read()
            request.session['path'] = path
            request.session['plain'] = plain
            return redirect('edit')
    else:
        form = FileUploadForm()
    return render(
        request,
        'index.html',
        {'form': form},
    )


def edit(request):
    plain = request.session.get('plain')

    if request.method == 'POST':
        edited = request.POST.get('edited').split('\n')
        edited = [i for i in edited if i != '']
        levels = [leading_spaces(i) / TAB_SIZE for i in edited]
        edited = [i.strip().split("\"")[1] if "\"" in i else i.strip() for i in edited]
        edited = [
            f'{i:04}:{int(l):02},{txt}'
            for i, (l, txt) in enumerate(zip(levels, edited))
        ]
        request.session['edited'] = edited
        request.session['levels'] = levels
        return redirect('select')

    return render(request, 'edit.html', {'plain': plain})


def select(request):
    edited = request.session.get('edited')
    if request.method == 'POST':
        form = MultipleChoiceForm(request.POST, choices=edited)
        if form.is_valid():
            selected = form.cleaned_data['choices_field']
            request.session['selected'] = selected
            return redirect('download')
    else:
        form = MultipleChoiceForm(choices=edited)
    return render(request, 'select.html', {'form': form})


def download(request):
    edited = request.session.get('edited')
    levels = request.session.get('levels')
    levels = [int(i) for i in levels]
    selected = request.session.get('selected')

    for i, s in enumerate(selected):
        prefix, txt = s.split(',', maxsplit=1)
        idx, level = prefix.split(':')
        idx, level = int(idx), int(level)
        distant = 1
        for l in levels[idx + 1 :]:
            if l <= level:
                selected[i] = (txt, edited[idx + distant].split(',')[1])
                break
            else:
                distant += 1

    extracted = {}
    path = request.session.get('path')
    for beg, end in selected:
        print(beg, end)
        extracted[beg] = PdfExtractor(path, beg, end)()
    return render(request, 'download.html', {'extracted': extracted})
