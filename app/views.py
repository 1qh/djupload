from django.shortcuts import redirect, render

from utils.bookmarks import BookmarksExtractor

from .forms import FileUploadForm, MultipleChoiceForm


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
        edited = [line.strip().split("\"")[1] for line in edited]
        request.session['edited'] = edited
        return redirect('select')

    return render(request, 'edit.html', {'plain': plain})


def select(request):
    edited = request.session.get('edited')
    if request.method == 'POST':
        form = MultipleChoiceForm(request.POST, choices=edited)
        if form.is_valid():
            selected = form.cleaned_data['choices_field']
            print(selected)
            request.session['selected'] = selected
            # return redirect('download')
    else:
        form = MultipleChoiceForm(choices=edited)
    return render(request, 'select.html', {'form': form})
