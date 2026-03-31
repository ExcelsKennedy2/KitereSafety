from django.shortcuts import render
# from django.contrib import messages
# Create your views here.

def home(request):
    return render(request, "core/index.html")

# def services(request):
#     return render(request, 'core/services.html')

# def about(request):
#     return render(request, 'core/about.html')

# def terms(request):
#     return render(request, 'core/terms.html')

# def privacy(request):
#     return render(request, 'core/privacy.html')

# def contact(request):
#     if request.method == 'POST':
#         # Handle contact form submission
#         messages.success(request, 'Thank you for contacting us. We will get back to you soon.')
#     return render(request, 'core/contact.html')