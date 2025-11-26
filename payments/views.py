from django.shortcuts import render

# Create your views here.
import razorpay
from django.shortcuts import render, redirect
from django.conf import settings
from .models import Payment
 
def make_payment(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        amount = request.POST.get('amount')
        if name and amount:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            # Convert amount to paise (smallest currency unit for INR)
            order_amount = int(float(amount) * 100)
            order_currency = 'INR'
            order_receipt = f'order_rcpt_{request.user.id if request.user.is_authenticated else "guest"}'

            try:
                # Create order in Razorpay
                order = client.order.create({
                    'amount': order_amount,
                    'currency': order_currency,
                    'receipt': order_receipt,
                    'payment_capture': '1'  # Auto-capture payment
                })

                # Save payment details to database
                payment = Payment.objects.create(
                    name=name,
                    amount=amount,
                    razorpay_order_id=order['id']
                )
                payment.save()

                # Pass order details to template
                context = {
                    'order': {
                        'id': order['id'],
                        'amount': order_amount,
                        'name': name
                    },
                    'razorpay_key': settings.RAZORPAY_KEY_ID
                }
                return render(request, 'faceDetection/payment_checkout.html', context)
                
            except Exception as e:
                print(f"Error creating Razorpay order: {str(e)}")
                return render(request, 'faceDetection/make_payment.html', {'error': 'Error creating payment. Please try again.'})
    
    # If not POST or missing data, show the payment form
    return render(request, 'faceDetection/make_payment.html')


def payment_success(request):
    # Handle payment success here
    return render(request, 'faceDetection/payment_success.html')