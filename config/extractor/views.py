from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse

from .forms import UploadForm
from .utils import extract_text
from .gemini import summarize_text


def upload_file(request):
    extracted_text = ""
    summary_text = ""

    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            uploaded_file = request.FILES['file']

            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = fs.path(filename)

            # Extract text (image / pdf / video)
            extracted_text = extract_text(file_path)

            # AI summarization (safe fallback)
            if extracted_text.strip():
                summary_text = summarize_text(extracted_text)
            else:
                summary_text = "No readable text found."

    else:
        form = UploadForm()

    return render(request, "upload.html", {
        "form": form,
        "text": extracted_text,
        "summary": summary_text
    })


def download_text(request):
    """
    Download extracted transcript as a .txt file
    """
    if request.method == "POST":
        text = request.POST.get("text", "")

        response = HttpResponse(text, content_type="text/plain")
        response["Content-Disposition"] = 'attachment; filename="transcript.txt"'
        return response
