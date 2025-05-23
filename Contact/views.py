from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Message

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')
        human_verify = request.POST.get('human-verify') == 'on'

        if not human_verify:
            return render(request, 'pages/Contact.html', {
                'error': 'Please verify you are human by checking the box.'
            })

        Message.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message_text
        )

        messages.success(request, "Message sent successfully!")
        return redirect('Contact')

    return render(request, 'pages/Contact.html')