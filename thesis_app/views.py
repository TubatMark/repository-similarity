from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.contrib import messages
from .forms import (
    RepositoryForm,
    StudentForm,
    EditStudentForm,
    StudentRegistrationForm,
    TitleDefForm,
    ProposalDefForm,
    FinalDefForm,
    PanelUsersForm,
    AdminUsersForm,
)
from django.contrib.auth.models import AbstractUser
from .models import (RepositoryFiles, StudentUsers, TitleDefense, ProposalDefense,
                     FinalDefense, Student, StudentUsersManager, Panel, User, Group, PanelUsers, PanelUsersManager, Admin, AdminUsers, AdminUsersManager)
import pandas as pd
from .functions import *
import logging
import csv23
import csv
import numpy as np
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from.decorators import *


logger = logging.getLogger(__name__)

# Dashboard

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def admin_dashboard(request):
    students = StudentUsers.objects.all()
    total_students_enrolled = students.count()
    repository = RepositoryFiles.objects.all()
    total_repository = repository.count()
    title_docs = TitleDefense.objects.all()
    total_title_docs = title_docs.count()
    proposal_docs = ProposalDefense.objects.all()
    total_proposal_docs = proposal_docs.count()
    final_docs = FinalDefense.objects.all()
    total_final_docs = final_docs.count()
    
    total_docs = total_title_docs + total_proposal_docs + total_final_docs
    
    context = {
        "repository": repository,
        "total_repository": total_repository,
        "students": students,
        "total_students_enrolled": total_students_enrolled,
        "title_docs": title_docs,
        "total_title_docs": total_title_docs,
        "proposal_docs": proposal_docs,
        "total_proposal_docs": total_proposal_docs,
        "final_docs": final_docs,
        "total_final_docs": total_final_docs,
        "total_docs": total_docs,
    }
    return render(request, "base/admin_base.html", context)


# Admin views
@unauthenticate_user
def admin_register(request):
    if request.method == 'POST':
        form = AdminUsersForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = form.cleaned_data['username']

            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                password=password,
                email=email,
                group='Admin'
            )
            user.save()
            group, created = Group.objects.get_or_create(name='Admin')
            group.user_set.add(user)

            admin = Admin(user=user)
            admin.save()

            return redirect('login')
    else:
        form = AdminUsersForm()
    return render(request, 'forms/accounts/admin_register.html', {'form': form})

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def AddRepositoryFiles(request):
    if request.method == "POST":
        form = RepositoryForm(request.POST, request.FILES)
        if form.is_valid():
            repository_file = form.save()  # save the form and get the instance
            pdf_file = form.cleaned_data["pdf_file"]
            try:
                extract_pdf_text(pdf_file, repository_file)  # pass the repository_file object to the function
                logger.info(
                    f"Successfully extracted text from PDF file {pdf_file} and saved it to a .txt file")
                return redirect("TableRepository")
            except Exception as e:
                logger.error(f"Error extracting text from PDF file: {e}")
                pass
    else:
        form = RepositoryForm()
    return render(request, "forms/admin/add_files_repository.html", {"form": form})



# not yet working
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def ViewRepositoryFiles(request, id):
    obj = RepositoryFiles.objects.get(id=id)
    pdf_file = obj.pdf_file
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=my_pdf.pdf"
    return response

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def EditRepositoryFiles(request, id):
    repository = RepositoryFiles.objects.get(id=id)

    if request.method == "POST":
        # Update the task with the new data
        form = RepositoryForm(request.POST, instance=repository)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            return redirect("TableRepository")
    else:
        form = RepositoryForm(instance=task)
    return render(request, "forms/admin/edit_files_repository.html", {"form": form})

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def DeleteRepositoryFiles(request, id):
    repository = RepositoryFiles.objects.get(id=id)
    repository.delete()
    return redirect("TableRepository")

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def TableRepository(request):
    repository = RepositoryFiles.objects.all()
    total_repository = repository.count()
    students = StudentUsers.objects.all()
    total_students_enrolled = students.count()
    title_docs = TitleDefense.objects.all()
    total_title_docs = title_docs.count()
    proposal_docs = ProposalDefense.objects.all()
    total_proposal_docs = proposal_docs.count()
    final_docs = FinalDefense.objects.all()
    total_final_docs = final_docs.count()
    
    total_docs = total_title_docs + total_proposal_docs + total_final_docs
    context = {
        "total_repository": total_repository,
        "repository": repository,
        "students": students,
        "total_students_enrolled": total_students_enrolled,
        "title_docs": title_docs,
        "total_title_docs": total_title_docs,
        "proposal_docs": proposal_docs,
        "total_proposal_docs": total_proposal_docs,
        "final_docs": final_docs,
        "total_final_docs": total_final_docs,
        "total_docs": total_docs,
    }
    
    return render(request, "tables/admin/table_repository/table_repository.html", context)


# upload excel for enrolled students in thesis
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def EnrolledStudentsExcel(request):
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            # Handle the uploaded file
            csv_enrolled_students(file)
            return redirect("TableEnrolledUsers")
    else:
        form = StudentForm()
    return render(request, "tables/admin/table_users.html", {"form": form})

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def EditStudentsDetails(request, sn):
    students = StudentUsers.objects.get(sn=sn)

    if request.method == "POST":
        # Update the task with the new data
        form = EditStudentForm(request.POST, instance=repository)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            return redirect("TableEnrolledUsers")
    else:
        form = EditStudentForm(instance=task)
    return render(request, "forms/admin/edit_enrolled_students.html", {"form": form})

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def ViewStudentDetails(request):
    students = StudentUsers.objects.all()
    context = {"students": students}
    return render(request, "forms/admin/view_enrolled_students.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def DeleteEnrolledStudent(request, sn):
    students = StudentUsers.objects.get(sn=sn)
    students.delete()
    return redirect("TableEnrolledUsers")

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def TableRegisteredStudents(request):
    # add the views for the table registered users
    repository = RepositoryFiles.objects.all()
    students = StudentUsers.objects.all()
    total_students_enrolled = students.count()
    total_repository = repository.count()
    registered_student = User.objects.filter(group='Student')

    context = {
        "total_repository": total_repository,
        "repository": repository,
        "students": students,
        "total_students_enrolled": total_students_enrolled,
        "registered_student": registered_student,
    }
    return render(request, "tables/admin/table_users/table_registered_students.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def TableRegisteredPanels(request):
    # add the views for the table registered users
    repository = RepositoryFiles.objects.all()
    students = StudentUsers.objects.all()
    total_students_enrolled = students.count()
    total_repository = repository.count()
    registered_panel = User.objects.filter(group='Panel')

    context = {
        "total_repository": total_repository,
        "repository": repository,
        "students": students,
        "total_students_enrolled": total_students_enrolled,
        "registered_panel": registered_panel,
    }
    return render(request, "tables/admin/table_users/table_registered_panels.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def TableEnrolledUsers(request):
    repository = RepositoryFiles.objects.all()
    students = StudentUsers.objects.all()
    total_students_enrolled = students.count()
    total_repository = repository.count()

    context = {
        "total_repository": total_repository,
        "repository": repository,
        "students": students,
        "total_students_enrolled": total_students_enrolled,
    }
    return render(request, "tables/admin/table_users.html", context)


#DOCUMENT SIMILARITY
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def TableTitle(request):
    repository = RepositoryFiles.objects.all()
    total_repository = repository.count()
    title_docs = TitleDefense.objects.all()
    total_title_docs = title_docs.count()
    proposal_docs = ProposalDefense.objects.all()
    total_proposal_docs = proposal_docs.count()
    final_docs = FinalDefense.objects.all()
    total_final_docs = final_docs.count()
    
    total_docs = total_title_docs + total_proposal_docs + total_final_docs

    context = {
        "total_repository": total_repository,
        "repository": repository,
        "title_docs": title_docs,
        "total_title_docs": total_title_docs,
        "proposal_docs": proposal_docs,
        "total_proposal_docs": total_proposal_docs,
        "final_docs": final_docs,
        "total_final_docs": total_final_docs,
        "total_docs": total_docs,
    }
    return render(request, "tables/admin/table_docs/table_title.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def TableProposal(request):
    repository = RepositoryFiles.objects.all()
    total_repository = repository.count()
    title_docs = TitleDefense.objects.all()
    total_title_docs = title_docs.count()
    proposal_docs = ProposalDefense.objects.all()
    total_proposal_docs = proposal_docs.count()
    final_docs = FinalDefense.objects.all()
    total_final_docs = final_docs.count()
    
    total_docs = total_title_docs + total_proposal_docs + total_final_docs

    context = {
        "total_repository": total_repository,
        "repository": repository,
        "title_docs": title_docs,
        "total_title_docs": total_title_docs,
        "proposal_docs": proposal_docs,
        "total_proposal_docs": total_proposal_docs,
        "final_docs": final_docs,
        "total_final_docs": total_final_docs,
        "total_docs": total_docs,
    }
    return render(request, "tables/admin/table_docs/table_proposal.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def TableFinal(request):
    repository = RepositoryFiles.objects.all()
    total_repository = repository.count()
    title_docs = TitleDefense.objects.all()
    total_title_docs = title_docs.count()
    proposal_docs = ProposalDefense.objects.all()
    total_proposal_docs = proposal_docs.count()
    final_docs = FinalDefense.objects.all()
    total_final_docs = final_docs.count()
    
    total_docs = total_title_docs + total_proposal_docs + total_final_docs

    context = {
        "total_repository": total_repository,
        "repository": repository,
        "title_docs": title_docs,
        "total_title_docs": total_title_docs,
        "proposal_docs": proposal_docs,
        "total_proposal_docs": total_proposal_docs,
        "final_docs": final_docs,
        "total_final_docs": total_final_docs,
        "total_docs": total_docs,
    }
    return render(request, "tables/admin/table_docs/table_final.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['Student'])
def student_dashboard(request):
    repository = RepositoryFiles.objects.all()
    return render(
        request,
        "forms/student/dashboard/table_repository_student.html",
        {"repository": repository},
    )


# student user
def search_student_id(request):
    if request.method == 'POST':
        student_id = request.POST.get('search')
        students = StudentUsers.objects.filter(Student_Id=student_id)
        if students:
            message = 'Searching is done, press the view result button'
        else:
            message = 'No results found'
        return render(request, 'forms/accounts/search_student_id.html', {'students': students, 'message': message})
    else:
        return render(request, 'forms/accounts/search_student_id.html')


def register_student(request):
    if request.method == 'POST':
        student_id = request.POST['student_id']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']

        
        # Create a User instance
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            student_id=student_id,
            group='Student'
        )

        # Save the User instance
        user.save()

        # Create a Student instance
        student = Student(user=user, student_id=student_id)

        # Save the Student instance
        student.save()

        # Add the student to the group
        group, created = Group.objects.get_or_create(name='Student')
        group.user_set.add(user)
        user.save()
        return redirect('login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'forms/accounts/student_register.html', {'form': form})

@unauthenticate_user
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.groups.filter(name='Admin').exists():
                return redirect('admin_dashboard')
            elif user.groups.filter(name='Panel').exists():
                return redirect('panel_dashboard')
            elif user.groups.filter(name='Student').exists():
                print('Redirecting to student dashboard...')  # Debugging line
                return redirect('student_dashboard')
        else:
            return render(request, 'forms/accounts/login.html', {'error_message': 'Invalid login credentials'})
    else:
        print('Rendering login form...')  # Debugging line
        return render(request, 'forms/accounts/login.html')



def logout_view(request):
    logout(request)
    return redirect('login')


# Upload Title Defense
@login_required(login_url='login')
@allowed_users(allowed_roles=['Student'])
def upload_title_defense(request):
    if request.method == "POST":
        form = TitleDefForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # create a new TitleDefense object and associate it with the currently logged-in user
                title_defense = TitleDefense(user=request.user, student_title=form.cleaned_data['student_title'], student_proponents=form.cleaned_data[
                                             'student_proponents'], student_pdf_file=form.cleaned_data['student_pdf_file'])
                title_defense.save()

                # extract the text from the student's PDF file
                student_pdf_file = form.cleaned_data["student_pdf_file"]
                query_doc = student_pdf_text(student_pdf_file)
                compare_documents(query_doc)
                # read the CSV file containing the LSA matrices for the documents in the corpus into a DataFrame
                # corpus_df = read_csv()

                # compare the student's PDF file to the corpus of documents
                # similarities = compare_to_corpus(query_df, corpus_df)

                context = {"form": form}
                return render(request, "forms/student/dashboard/view_uploads/tbl_title.html", context)
            except Exception as e:
                logger.error(
                    f"Error comparing student's PDF file to corpus: {e}")
                pass
    else:
        form = TitleDefForm()
    return render(request, "forms/student/dashboard/view_uploads/tbl_title.html", {"form": form})

# Upload Proposal Defense


@login_required(login_url='login')
@allowed_users(allowed_roles=['Student'])
def upload_proposal_defense(request):
    if request.method == "POST":
        form = ProposalDefForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # create a new TitleDefense object and associate it with the currently logged-in user
                proposal_defense = ProposalDefense(user=request.user, student_title_p=form.cleaned_data['student_title_p'], student_proponents_p=form.cleaned_data[
                    'student_proponents_p'], student_pdf_file_p=form.cleaned_data['student_pdf_file_p'])
                proposal_defense.save()

                # extract the text from the student's PDF file
                student_pdf_file = form.cleaned_data["student_pdf_file_p"]
                query_df = student_pdf_text(student_pdf_file)

                # read the CSV file containing the LSA matrices for the documents in the corpus into a DataFrame
                # corpus_df = read_csv()

                # compare the student's PDF file to the corpus of documents
                # similarities = compare_to_corpus(query_df, corpus_df)

                context = {"form": form}
                return render(request, "forms/student/dashboard/view_uploads/tbl_proposal.html", context)
            except Exception as e:
                logger.error(
                    f"Error comparing student's PDF file to corpus: {e}")
                pass
    else:
        form = ProposalDefForm()
    return render(request, "forms/student/dashboard/view_uploads/tbl_proposal.html", {"form": form})

# Upload Final Defense


@login_required(login_url='login')
@allowed_users(allowed_roles=['Student'])
def upload_final_defense(request):
    if request.method == "POST":
        form = FinalDefForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # create a new TitleDefense object and associate it with the currently logged-in user
                final_defense = FinalDefense(user=request.user, student_title_f=form.cleaned_data['student_title_f'], student_proponents_f=form.cleaned_data[
                                             'student_proponents_f'], student_pdf_file_f=form.cleaned_data['student_pdf_file_f'])
                final_defense.save()

                # extract the text from the student's PDF file
                student_pdf_file = form.cleaned_data["student_pdf_file_f"]
                query_df = student_pdf_text(student_pdf_file)

                # read the CSV file containing the LSA matrices for the documents in the corpus into a DataFrame
                # corpus_df = read_csv()

                # compare the student's PDF file to the corpus of documents
                # similarities = compare_to_corpus(query_df, corpus_df)

                context = {"form": form}
                return render(request, "forms/student/dashboard/view_uploads/tbl_final.html", context)
            except Exception as e:
                logger.error(
                    f"Error comparing student's PDF file to corpus: {e}")
                pass
    else:
        form = FinalDefForm(initial={})
    return render(request, "forms/student/dashboard/view_uploads/tbl_final.html", {"form": form})


# VIEW DOCUMENTS DEFENSE - STUDENT
@login_required(login_url='login')
@allowed_users(allowed_roles=['Student'])
def view_title_defense(request):
    # Assign the queryset to a variable
    datas = TitleDefense.objects.filter(user=request.user)
    context = {"datas": datas, "user": request.user}
    return render(request, 'forms/student/dashboard/view_uploads/tbl_title.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Student'])
def view_proposal_defense(request):
    # Assign the queryset to a variable
    datas = ProposalDefense.objects.filter(user=request.user)
    context = {"datas": datas, "user": request.user}
    return render(request, 'forms/student/dashboard/view_uploads/tbl_title.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Student'])
def view_final_defense(request):
    # Assign the queryset to a variable
    datas = FinalDefense.objects.filter(user=request.user)
    context = {"datas": datas, "user": request.user}
    return render(request, 'forms/student/dashboard/view_uploads/tbl_title.html', context)


# PANEL
@login_required(login_url='login')
@allowed_users(allowed_roles=['Panel'])
def panel_dashboard(request):
    repository = RepositoryFiles.objects.all()
    context = {"repository": repository}
    return render(request, 'tables/panel/table_repository/table_repository_panel.html', context)

@unauthenticate_user
def panel_register(request):
    if request.method == 'POST':
        form = PanelUsersForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = form.cleaned_data['username']
            
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                password=password,
                email=email,
                group='Panel'
            )
            user.save()
            group, created = Group.objects.get_or_create(name='Panel')
            group.user_set.add(user)

            panel = Panel(user=user)
            panel.save()

            return redirect('login')
    else:
        form = PanelUsersForm()
    return render(request, 'forms/accounts/teacher_register.html', {'form': form})

#PANEL VIEW UPLOADED DOCS
@login_required(login_url='login')
@allowed_users(allowed_roles=['Panel'])
def uploaded_title_docs(request):
    titles = TitleDefense.objects.all()
    return render(request, 'tables/panel/table_docs/table_title.html', {'titles': titles})

@login_required(login_url='login')
@allowed_users(allowed_roles=['Panel'])
def uploaded_proposal_docs(request):
    proposals = ProposalDefense.objects.all()
    return render(request, 'tables/panel/table_docs/table_proposal.html', {'proposals': proposals})

@login_required(login_url='login')
@allowed_users(allowed_roles=['Panel'])
def uploaded_final_docs(request):
    finals = FinalDefense.objects.all()
    return render(request, 'tables/panel/table_docs/table_final.html', {'finals': finals})

    
