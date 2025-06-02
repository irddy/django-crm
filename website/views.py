from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
import pandas as pd
import io
import base64
from .forms import SignUpForm, AddRecordForm, LeadImportForm
from .models import Lead, LeadComment
from django import forms


class LeadCommentForm(forms.ModelForm):
    class Meta:
        model = LeadComment
        fields = ['role', 'content']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


def home(request):
	records = Lead.objects.all()
	# Consider paginating records if the list grows large
	# from django.core.paginator import Paginator
	# paginator = Paginator(records, 25)  # Show 25 records per page
	# page_number = request.GET.get('page')
	# page_obj = paginator.get_page(page_number)
	# return render(request, 'home.html', {'records': page_obj})

	# Check to see if logging in
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		# Authenticate
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request, "You Have Been Logged In!")
			return redirect('home')
		else:
			messages.success(request, "There Was An Error Logging In, Please Try Again...")
			return redirect('home')
	else:
		return render(request, 'home.html', {'records':records})



def logout_user(request):
	logout(request)
	messages.success(request, "You Have Been Logged Out...")
	return redirect('home')


def register_user(request):
	if request.user.is_authenticated:
		return redirect('home')
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			# Authenticate and login
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, "You Have Successfully Registered! Welcome!")
			return redirect('home')
	else:
		form = SignUpForm()
	return render(request, 'register.html', {'form':form})



@login_required
def customer_record(request, pk):
    customer_record = get_object_or_404(Lead, id=pk)
    comments = customer_record.comments.select_related('author').order_by('-created_at')
    comment_form = LeadCommentForm()

    if request.method == 'POST' and 'add_comment' in request.POST:
        comment_form = LeadCommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.lead = customer_record
            new_comment.author = request.user
            new_comment.save()
            messages.success(request, "Comment added.")
            return redirect('record', pk=pk)
        else:
            messages.error(request, "There was an error adding your comment.")

    return render(request, 'record.html', {
        'customer_record': customer_record,
        'comments': comments,
        'comment_form': comment_form,
    })



@login_required
def delete_record(request, pk):
	try:
		delete_it = get_object_or_404(Lead, id=pk)
		delete_it.delete()
		messages.success(request, "Record Deleted Successfully...")
	except Exception as e:
		messages.error(request, f"Error deleting record: {e}")
	return redirect('home')


@login_required
def add_record(request):
	form = AddRecordForm(request.POST or None)
	if request.method == "POST":
		if form.is_valid():
			add_record = form.save(commit=False)
			add_record.full_clean()  # Model validation
			add_record.save()
			messages.success(request, "Record Added...")
			return redirect('home')
		else:
			# Show form errors in messages
			for field, errors in form.errors.items():
				for error in errors:
					messages.error(request, f"{field}: {error}")
	return render(request, 'add_record.html', {'form':form})

@login_required
def update_record(request, pk):
	current_record = get_object_or_404(Lead, id=pk)
	form = AddRecordForm(request.POST or None, instance=current_record)
	if form.is_valid():
		updated_record = form.save(commit=False)
		updated_record.full_clean()  # Model validation
		updated_record.save()
		messages.success(request, "Record Has Been Updated!")
		return redirect('home')
	else:
		# Show form errors in messages
		for field, errors in form.errors.items():
			for error in errors:
				messages.error(request, f"{field}: {error}")
	return render(request, 'update_record.html', {'form':form})

@staff_member_required
def upload_leads(request):
    # List all Lead model fields you want to allow mapping for
    all_fields = [
        'full_name',
        'email',
        'phone',
        'country',
        'timezone',
        'income_range',
        'agent',
        'comment',
    ]
    required_fields = ['full_name', 'email', 'phone']
    optional_fields = [f for f in all_fields if f not in required_fields]

    if request.method == 'POST':
        if 'submit_mapping' in request.POST:
            # Second POST: process mapping and insert leads
            csv_data = base64.b64decode(request.POST['csv_data'])
            df = pd.read_csv(io.StringIO(csv_data.decode('utf-8')))
            # Get mapping from POST for all fields
            mapping = {field: request.POST.get(f'mapping_{field}') for field in all_fields}

            # Validation
            if not all(mapping[f] for f in required_fields):
                messages.error(request, "Please map all required fields.")
                return redirect('upload-leads')

            # Prepare agent mapping if agent usernames are provided
            agent_map = {}
            if mapping.get('agent') and mapping['agent'] in df.columns:
                agent_usernames = df[mapping['agent']].dropna().unique()
                from django.contrib.auth.models import User
                users = User.objects.filter(username__in=agent_usernames)
                agent_map = {u.username: u for u in users}

            leads = []
            for _, row in df.iterrows():
                lead_kwargs = {
                    'full_name': row[mapping['full_name']],
                    'email': row[mapping['email']],
                    'phone': row[mapping['phone']],
                    'country': row[mapping['country']] if mapping.get('country') and mapping['country'] in df.columns else '',
                    'timezone': row[mapping['timezone']] if mapping.get('timezone') and mapping['timezone'] in df.columns else '',
                    'income_range': row[mapping['income_range']] if mapping.get('income_range') and mapping['income_range'] in df.columns else '',
                    'comment': row[mapping['comment']] if mapping.get('comment') and mapping['comment'] in df.columns else '',
                }
                # Handle agent if present
                agent_val = row[mapping['agent']] if mapping.get('agent') and mapping['agent'] in df.columns else None
                if agent_val and agent_val in agent_map:
                    lead_kwargs['agent'] = agent_map[agent_val]
                leads.append(Lead(**lead_kwargs))
            Lead.objects.bulk_create(leads)
            messages.success(request, f"{len(leads)} leads imported successfully.")
            return redirect('home')

        else:
            # First POST: handle file upload
            form = LeadImportForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES['file']
                # Support both CSV and Excel
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.name.endswith('.xlsx'):
                    df = pd.read_excel(file)
                else:
                    messages.error(request, "Unsupported file format.")
                    return redirect('upload-leads')
                csv_data = base64.b64encode(df.to_csv(index=False).encode()).decode()
                return render(request, 'upload_column_mapping.html', {
                    'columns': df.columns,
                    'csv_data': csv_data,
                    'required_fields': required_fields,
                    'optional_fields': optional_fields,
                    'all_fields': all_fields,
                })
    else:
        form = LeadImportForm()

    return render(request, 'upload_leads.html', {'form': form})
